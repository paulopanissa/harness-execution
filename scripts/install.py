#!/usr/bin/env python3
"""install.py — instalador interativo do harness HX.

1. Módulo org (opcional, privado): clona o preset (hx-org.yaml) e o repo de fluxo que ele aponta.
2. Grava ~/.hx/config.yaml, roda sync.py e valida links, agentes Claude e .toml do Codex.
3. Mods de UI (opcional): oferece o catálogo de ~/.hx/mods/catalog.json.
Uso: install.py [--org <url-git-do-preset> | --no-org] [--mods a,b | --no-mods]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
from hxlib import (  # noqa: E402
    CLAUDE_HOME,
    CODEX_HOME,
    FALLBACK_MEMORY,
    HX_HOME,
    ORG_PRESET_DIR,
    ORG_PRESET_FILE,
    ORG_VENDOR_DIR,
    load_config,
    load_org_preset,
    localized,
    mods_selected,
    parse_frontmatter,
    save_config,
)

SCRIPT_DIR = Path(__file__).resolve().parent
PRESET_REQUIRED = ("name", "vendor_repo", "remote_pattern", "phase_path", "phases", "branch_regex")


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def ask_org(current: str) -> str:
    hint = f" [Enter = {current}]" if current else " [vazio = não]"
    answer = ask(f"Módulo corporativo privado? URL git do preset hx-org.yaml{hint}: ")
    if answer.lower() in ("n", "nao", "não", "no", "-"):
        return ""
    return answer or current


def git(*args: str) -> int:
    return subprocess.run(["git", *args], check=False).returncode


def clone_or_pull(url: str, dest: Path) -> bool:
    if (dest / ".git").exists():
        print(f"→ atualizando {dest}")
        return git("-C", str(dest), "pull", "--ff-only") == 0
    if dest.exists() and any(dest.iterdir()):
        print(f"✗ {dest} existe e não é repositório git; remova-o e rode de novo")
        return False
    print(f"→ clonando {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    return git("clone", url, str(dest)) == 0


def install_org(preset_url: str) -> bool:
    if shutil.which("git") is None:
        print("✗ git não encontrado no PATH")
        return False
    if not clone_or_pull(preset_url, ORG_PRESET_DIR):
        return False
    preset = load_org_preset()
    missing = [k for k in PRESET_REQUIRED if not preset.get(k)]
    if missing:
        print(f"✗ {ORG_PRESET_FILE}: chaves ausentes {missing}")
        return False
    return clone_or_pull(str(preset["vendor_repo"]), ORG_VENDOR_DIR)


def make_executable() -> None:
    for pattern in ("hooks/*.sh", "scripts/*.sh", "scripts/*.py"):
        for path in HX_HOME.glob(pattern):
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def run_sync() -> bool:
    return subprocess.run([sys.executable, str(SCRIPT_DIR / "sync.py")], check=False).returncode == 0


def _same_content(a: Path, b: Path) -> bool:
    try:
        return a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def validate(org: bool) -> list[str]:
    errors: list[str] = []
    agents_md = localized("AGENTS.md", load_config())
    for link in (CLAUDE_HOME / "CLAUDE.md", CODEX_HOME / "AGENTS.md"):
        if not _same_content(agents_md, link):
            errors.append(f"{link} não aponta para {agents_md}")

    for src in sorted((HX_HOME / "agents").glob("*.md")):
        name = parse_frontmatter(src.read_text(encoding="utf-8"))[0].get("name", src.stem)
        if not (CLAUDE_HOME / "agents" / f"{name}.md").is_file():
            errors.append(f"agente Claude ausente: {name}")
        toml_path = CODEX_HOME / "agents" / f"{name}.toml"
        try:
            data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
            missing = {"name", "description", "sandbox_mode", "developer_instructions"} - data.keys()
            if missing:
                errors.append(f"{toml_path}: campos ausentes {sorted(missing)}")
        except (OSError, tomllib.TOMLDecodeError) as err:
            errors.append(f"{toml_path}: {err}")

    if not (CLAUDE_HOME / "commands" / "hx.md").is_file():
        errors.append("comando /hx ausente")
    org_cmd = CLAUDE_HOME / "commands" / "hx" / "org.md"
    if org != org_cmd.exists():
        errors.append(f"{org_cmd} {'ausente' if org else 'deveria ter sido removido'}")

    try:
        settings = json.loads((CLAUDE_HOME / "settings.json").read_text(encoding="utf-8"))
        hooks_json = json.dumps(settings.get("hooks", {}))
        for hook in ("block-spec-md.sh", "read-guard.sh", "graphify-setup.sh"):
            if hook not in hooks_json:
                errors.append(f"hook {hook} ausente em settings.json")
    except (OSError, ValueError) as err:
        errors.append(f"settings.json: {err}")

    if os.name != "nt":
        for path in [*HX_HOME.glob("hooks/*.sh"), *HX_HOME.glob("scripts/*.sh"), *HX_HOME.glob("scripts/*.py")]:
            if not os.access(path, os.X_OK):
                errors.append(f"sem permissão de execução: {path}")
    return errors


def choose_mods(args: argparse.Namespace) -> list[str]:
    if args.no_mods:
        return []
    catalog = mod.load_catalog()
    if args.mods is not None:
        wanted = [m.strip() for m in args.mods.split(",") if m.strip()]
    else:
        wanted = mod.pick(catalog)
    return mod.install_many(catalog, wanted) if wanted else []


def main() -> int:
    parser = argparse.ArgumentParser(description="instalador do harness HX")
    org_group = parser.add_mutually_exclusive_group()
    org_group.add_argument("--org", metavar="URL", help="URL git do preset privado (hx-org.yaml)")
    org_group.add_argument("--no-org", action="store_true", help="desativa o módulo org sem perguntar")
    mods_group = parser.add_mutually_exclusive_group()
    mods_group.add_argument("--mods", metavar="IDS", help="ids do catálogo separados por vírgula")
    mods_group.add_argument("--no-mods", action="store_true", help="não oferece mods")
    args = parser.parse_args()

    cfg = load_config()
    current = str(cfg.get("org_preset") or "")
    preset_url = "" if args.no_org else (args.org or ask_org(current))
    org_ok = install_org(preset_url) if preset_url else False
    if preset_url and not org_ok:
        print("✗ falha no módulo org → seguindo com org_enabled: false")

    cfg = {**cfg, "org_enabled": org_ok, "org_preset": preset_url or current}
    save_config(cfg)
    print(f"→ {HX_HOME / 'config.yaml'}: org_enabled={str(org_ok).lower()}")
    FALLBACK_MEMORY.touch(exist_ok=True)
    make_executable()

    if not run_sync():
        print("✗ sync.py falhou")
        return 1
    errors = validate(org_ok)
    if errors:
        print("✗ validação:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("✓ HX instalado: links, agentes Claude, .toml Codex, comandos e hooks OK")

    installed = choose_mods(args)
    if installed:
        save_config({**load_config(), "mods": ",".join(dict.fromkeys([*mods_selected(cfg), *installed]))})
        print(f"✓ mods: {', '.join(installed)} (reinicie o Claude Code para carregar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
