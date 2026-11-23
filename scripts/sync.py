#!/usr/bin/env python3
"""sync.py — sincroniza ~/.hx com Claude Code (~/.claude) e Codex CLI (~/.codex).

- Linka ~/.claude/CLAUDE.md e ~/.codex/AGENTS.md -> ~/.hx/AGENTS.md
  (symlink; sem permissão no Windows → hardlink; último recurso → cópia).
- Gera agentes em ~/.claude/agents/*.md e ~/.codex/agents/*.toml.
- Expõe comandos em ~/.claude/commands/ (hx.md + hx/<sub>.md => /hx:<sub>).
- Merge seguro de hooks em ~/.claude/settings.json (com backup).
- `rtk: true` + binário no PATH → hook `rtk hook claude|codex` (settings.json e ~/.codex/hooks.json).
  Desligar não remove o hook (pode ter sido instalado pelo próprio RTK): use `rtk init -g --uninstall`.
Arquivos de terceiros sobrescritos vão para ~/.hx/backups/<timestamp>/.
Uso: sync.py [--dry-run] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hxlib import (  # noqa: E402
    CLAUDE_HOME,
    CODEX_HOME,
    CODEX_SKILLS_HOME,
    HOME,
    HX_HOME,
    LAST_SYNC_PATH,
    MANIFEST_PATH,
    ORG_VENDOR_DIR,
    language,
    load_org_preset,
    localized,
    load_config,
    parse_frontmatter,
    resolve_model,
)

HOOK_MARK_SPEC = "block-spec-md.sh"
HOOK_MARK_UPDATE = "check_updates.py"
HOOK_MARK_ORG = "org-only.sh"
HOOK_MARK_READ = "read-guard.sh"
HOOK_MARK_GRAPHIFY = "graphify-setup.sh"
HOOK_MARK_RTK_CLAUDE = "claude"  # → `rtk hook claude`
HOOK_MARK_RTK_CODEX = "codex"  # → `rtk hook codex`

CODEX_TOOL_MAP = {
    "Read": "shell (`sed -n`/`cat`)",
    "Grep": "`rg`",
    "Glob": "`rg --files`",
    "Edit": "`apply_patch`",
    "MultiEdit": "`apply_patch`",
    "Write": "`apply_patch`",
    "NotebookEdit": "`apply_patch`",
    "Bash": "shell",
    "Agent": "subagente",
    "Task": "subagente",
    "AskUserQuestion": "pergunta direta ao usuário",
    "TodoWrite": "`update_plan`",
}
_CODEX_TOOL_RE = re.compile(r"`(" + "|".join(CODEX_TOOL_MAP) + r")`")


@dataclass
class Ctx:
    dry_run: bool
    quiet: bool
    cfg: dict[str, Any]
    stamp: str
    managed: dict[str, str] = field(default_factory=dict)
    seen: set[str] = field(default_factory=set)
    changes: int = 0

    def log(self, msg: str) -> None:
        if not self.quiet:
            print(("[dry-run] " if self.dry_run else "") + msg)

    def mark(self, path: Path, kind: str) -> None:
        self.managed[str(path)] = kind
        self.seen.add(str(path))


# ---------------------------------------------------------------- fs helpers
def _exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def backup(ctx: Ctx, path: Path) -> None:
    """Copia arquivo não gerenciado pelo HX para ~/.hx/backups antes de sobrescrever."""
    if not _exists(path) or str(path) in ctx.managed:
        return
    try:
        rel = path.absolute().relative_to(HOME)
    except ValueError:
        rel = Path(path.name)
    dest = HX_HOME / "backups" / ctx.stamp / rel
    ctx.log(f"backup  {path} -> {dest}")
    if ctx.dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        dest.with_suffix(dest.suffix + ".symlink").write_text(os.readlink(path), encoding="utf-8")
    elif path.is_file():
        shutil.copy2(path, dest)


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()


def _is_linked(src: Path, dst: Path) -> str | None:
    if dst.is_symlink():
        try:
            return "symlink" if dst.resolve() == src.resolve() else None
        except OSError:
            return None
    if dst.is_file():
        try:
            if os.path.samefile(src, dst):
                return "hardlink"
        except OSError:
            return None
    return None


def link_file(ctx: Ctx, src: Path, dst: Path) -> None:
    """symlink → hardlink → cópia. Idempotente."""
    current = _is_linked(src, dst)
    if current:
        ctx.mark(dst, current)
        return
    if _exists(dst) and dst.is_file() and str(dst) in ctx.managed and ctx.managed[str(dst)] == "copy":
        if dst.read_bytes() == src.read_bytes():
            ctx.mark(dst, "copy")
            return
    backup(ctx, dst)
    ctx.changes += 1
    if ctx.dry_run:
        ctx.log(f"link    {dst} -> {src}")
        ctx.mark(dst, "symlink")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    _remove(dst)
    for kind, op in (("symlink", lambda: os.symlink(src, dst)), ("hardlink", lambda: os.link(src, dst))):
        try:
            op()
            ctx.log(f"{kind:<9}{dst} -> {src}")
            ctx.mark(dst, kind)
            return
        except OSError:
            continue
    shutil.copy2(src, dst)
    ctx.log(f"copy    {dst} <- {src} (sem permissão de link; rode sync.py após editar)")
    ctx.mark(dst, "copy")


def write_generated(ctx: Ctx, dst: Path, content: str) -> None:
    if dst.is_file() and not dst.is_symlink() and dst.read_text(encoding="utf-8") == content:
        ctx.mark(dst, "generated")
        return
    backup(ctx, dst)
    ctx.changes += 1
    ctx.log(f"write   {dst}")
    if not ctx.dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        _remove(dst)
        dst.write_text(content, encoding="utf-8", newline="\n")
    ctx.mark(dst, "generated")


# ---------------------------------------------------------------- agents
def _yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_claude_agent(meta: dict[str, str], body: str, cfg: dict[str, Any]) -> str:
    lines = ["---", f"name: {meta['name']}", f"description: {_yaml_quote(meta.get('description', ''))}"]
    for key in ("tools", "disallowedTools"):
        if meta.get(key):
            lines.append(f"{key}: {meta[key]}")
    model = resolve_model(cfg, "claude", meta.get("tier", "default"))
    if model:
        lines.append(f"model: {model}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.strip() + "\n"


def _toml_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _toml_multiline(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return '"""\n' + escaped + '\n"""'


def build_codex_agent(meta: dict[str, str], body: str, cfg: dict[str, Any]) -> str:
    sandbox = meta.get("sandbox") or ("read-only" if "Edit" in meta.get("disallowedTools", "") else "workspace-write")
    instructions = _CODEX_TOOL_RE.sub(lambda m: CODEX_TOOL_MAP[m.group(1)], body.strip())
    lines = [
        "# Gerado por ~/.hx/scripts/sync.py a partir de ~/.hx/agents — não edite aqui.",
        f"name = {_toml_str(meta['name'])}",
        f"description = {_toml_str(meta.get('description', ''))}",
        f"sandbox_mode = {_toml_str(sandbox)}",
    ]
    model = resolve_model(cfg, "codex", meta.get("tier", "default"))
    if model:
        lines.append(f"model = {_toml_str(model)}")
    lines.append(f"developer_instructions = {_toml_multiline(instructions)}")
    return "\n".join(lines) + "\n"


def sync_agents(ctx: Ctx) -> None:
    for root in sorted((HX_HOME / "agents").glob("*.md")):
        src = localized(f"agents/{root.name}", ctx.cfg)
        meta, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        if not meta.get("name"):
            raise SystemExit(f"sync: {src} sem 'name' no frontmatter")
        name = meta["name"]
        write_generated(ctx, CLAUDE_HOME / "agents" / f"{name}.md", build_claude_agent(meta, body, ctx.cfg))
        write_generated(ctx, CODEX_HOME / "agents" / f"{name}.toml", build_codex_agent(meta, body, ctx.cfg))


# ---------------------------------------------------------------- commands
def command_target(stem: str) -> Path:
    if stem == "hx":
        return CLAUDE_HOME / "commands" / "hx.md"
    return CLAUDE_HOME / "commands" / "hx" / f"{stem.removeprefix('hx-')}.md"


def build_codex_skill(stem: str, text: str) -> str:
    """Codex TUI intercepta `/hx` como comando nativo; o equivalente lá é a skill `$hx`."""
    meta, body = parse_frontmatter(text)
    desc = meta.get("description", stem).replace('"', "'")
    hint = meta.get("argument-hint", "")
    body = _CODEX_TOOL_RE.sub(lambda m: CODEX_TOOL_MAP[m.group(1)], body.strip())
    return (
        "---\n"
        f"name: {stem}\n"
        f'description: "{desc}. Use only when the user explicitly invokes ${stem}."\n'
        "---\n"
        "<!-- Gerado por ~/.hx/scripts/sync.py a partir de ~/.hx/commands — não edite aqui. -->\n"
        f"Invocation: `${stem} {hint}`. `$ARGUMENTS` = text the user wrote after `${stem}` (may be empty).\n\n"
        f"{body}\n"
    )


def sync_commands(ctx: Ctx) -> None:
    org = bool(ctx.cfg.get("org_enabled"))
    for root in sorted((HX_HOME / "commands").glob("hx*.md")):
        if root.stem == "hx-org" and not org:
            continue
        src = localized(f"commands/{root.name}", ctx.cfg)
        link_file(ctx, src, command_target(root.stem))
        skill = build_codex_skill(root.stem, src.read_text(encoding="utf-8"))
        write_generated(ctx, CODEX_SKILLS_HOME / root.stem / "SKILL.md", skill)


# ---------------------------------------------------------------- settings.json
def _python_cmd() -> str:
    return '"' + Path(sys.executable).as_posix() + '"'


def _has_hook(settings: dict[str, Any], event: str, marker: str) -> bool:
    for group in settings.get("hooks", {}).get(event, []):
        for hook in group.get("hooks", []):
            if marker in str(hook.get("command", "")):
                return True
    return False


def _drop_hook(settings: dict[str, Any], event: str, marker: str) -> dict[str, Any]:
    groups = []
    for group in settings.get("hooks", {}).get(event, []):
        hooks = [h for h in group.get("hooks", []) if marker not in str(h.get("command", ""))]
        if hooks:
            groups.append({**group, "hooks": hooks})
    new_hooks = {**settings.get("hooks", {}), event: groups}
    if not groups:
        new_hooks.pop(event)
    return {**settings, "hooks": new_hooks}


def _add_hook(settings: dict[str, Any], event: str, matcher: str | None, command: str, timeout: int) -> dict[str, Any]:
    group: dict[str, Any] = {"hooks": [{"type": "command", "command": command, "timeout": timeout}]}
    if matcher:
        group = {"matcher": matcher, **group}
    hooks = settings.get("hooks", {})
    return {**settings, "hooks": {**hooks, event: [*hooks.get(event, []), group]}}


def find_org_guards() -> list[tuple[Path, str]]:
    """Hooks guard do vendor org listados em `guard_hooks` do preset (ex.: test-db-guard.js),
    com o matcher que o próprio vendor declara (padrão: Bash)."""
    names = [n.strip() for n in str(load_org_preset().get("guard_hooks") or "").split(",") if n.strip()]
    if not names or not ORG_VENDOR_DIR.is_dir():
        return []
    found: list[tuple[Path, str]] = []
    for name in names:
        guards = sorted(p for p in ORG_VENDOR_DIR.rglob(name) if ".git" not in p.parts)
        if not guards:
            continue
        matcher = "Bash"
        for cfg_file in ORG_VENDOR_DIR.rglob("settings*.json"):
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            for groups in data.get("hooks", {}).values():
                for group in groups if isinstance(groups, list) else []:
                    if any(name in str(h.get("command", "")) for h in group.get("hooks", [])):
                        matcher = group.get("matcher", matcher)
        found.append((guards[0], matcher))
    return found


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8") or "{}")
    except ValueError as err:
        raise SystemExit(f"sync: {path} inválido ({err}); corrija antes de sincronizar")


def _save_json(ctx: Ctx, path: Path, original: dict[str, Any], data: dict[str, Any]) -> None:
    if data == original:
        return
    backup_path = path.with_name(f"{path.name}.hx-bak-{ctx.stamp}")
    ctx.changes += 1
    ctx.log(f"merge   {path} (backup: {backup_path.name})")
    if ctx.dry_run:
        return
    if path.exists():
        shutil.copy2(path, backup_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rtk_enabled(cfg: dict[str, Any]) -> bool:
    """Hook do RTK só com `rtk: true` E binário no PATH (hook sem binário quebraria todo Bash)."""
    return bool(cfg.get("rtk")) and shutil.which("rtk") is not None


def _with_rtk_hook(data: dict[str, Any], agent: str) -> dict[str, Any]:
    # Registro direto (não `rtk init`): o init anexa @RTK.md ao CLAUDE.md/AGENTS.md, que são links p/ ~/.hx/AGENTS.md.
    # Marcador sem o nome do binário: detecta também hook já instalado pelo próprio `rtk init` (rtk.exe, caminho absoluto).
    if _has_hook(data, "PreToolUse", f"hook {agent}"):
        return data
    # Sem caminho absoluto: o comando reescrito (`rtk git ...`) depende do PATH de qualquer forma; com `rtk`
    # fora do PATH o hook falha aberto (comando roda cru). Forma exata que `rtk init --show` reconhece.
    return _add_hook(data, "PreToolUse", "Bash", f"rtk hook {agent}", 10)


def sync_codex_hooks(ctx: Ctx) -> None:
    """Codex lê hooks de $CODEX_HOME/hooks.json (mesmo formato do settings.json do Claude)."""
    if not rtk_enabled(ctx.cfg):
        return
    path = CODEX_HOME / "hooks.json"
    original = _load_json(path)
    _save_json(ctx, path, original, _with_rtk_hook(original, HOOK_MARK_RTK_CODEX))


def sync_settings(ctx: Ctx) -> None:
    path = CLAUDE_HOME / "settings.json"
    original = _load_json(path)
    settings = original
    hooks_dir = (HX_HOME / "hooks").as_posix()

    if not _has_hook(settings, "PreToolUse", HOOK_MARK_SPEC):
        settings = _add_hook(settings, "PreToolUse", "Write|Edit|MultiEdit", f'bash "{hooks_dir}/{HOOK_MARK_SPEC}"', 10)
    if not _has_hook(settings, "PreToolUse", HOOK_MARK_READ):
        settings = _add_hook(settings, "PreToolUse", "Read", f'bash "{hooks_dir}/{HOOK_MARK_READ}"', 10)
    if not _has_hook(settings, "SessionStart", HOOK_MARK_GRAPHIFY):
        settings = _add_hook(settings, "SessionStart", None, f'bash "{hooks_dir}/{HOOK_MARK_GRAPHIFY}"', 5)
    if rtk_enabled(ctx.cfg):
        settings = _with_rtk_hook(settings, HOOK_MARK_RTK_CLAUDE)

    org = bool(ctx.cfg.get("org_enabled"))
    if org and not _has_hook(settings, "SessionStart", HOOK_MARK_UPDATE):
        script = (HX_HOME / "scripts" / HOOK_MARK_UPDATE).as_posix()
        settings = _add_hook(settings, "SessionStart", None, f'{_python_cmd()} "{script}"', 10)
    if not org and _has_hook(settings, "SessionStart", HOOK_MARK_UPDATE):
        settings = _drop_hook(settings, "SessionStart", HOOK_MARK_UPDATE)

    for guard_path, matcher in (find_org_guards() if org else []):
        if not _has_hook(settings, "PreToolUse", guard_path.name):
            cmd = f'bash "{hooks_dir}/{HOOK_MARK_ORG}" node "{guard_path.as_posix()}"'
            settings = _add_hook(settings, "PreToolUse", matcher, cmd, 15)
    if not org and _has_hook(settings, "PreToolUse", HOOK_MARK_ORG):
        settings = _drop_hook(settings, "PreToolUse", HOOK_MARK_ORG)

    _save_json(ctx, path, original, settings)


# ---------------------------------------------------------------- manifest / cleanup
def load_manifest() -> dict[str, str]:
    try:
        return dict(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get("managed", {}))
    except (OSError, ValueError):
        return {}


def prune_stale(ctx: Ctx, previous: dict[str, str]) -> None:
    """Remove arquivos que o HX gerou antes e não gera mais (ex.: /hx:org desativado)."""
    for raw in sorted(set(previous) - ctx.seen):
        path = Path(raw)
        ctx.managed.pop(raw, None)
        if _exists(path):
            ctx.changes += 1
            ctx.log(f"remove  {path}")
            if not ctx.dry_run:
                _remove(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="mostra ações sem gravar")
    parser.add_argument("--quiet", action="store_true", help="sem log por arquivo")
    args = parser.parse_args()

    cfg = load_config()
    agents_md = localized("AGENTS.md", cfg)
    if not agents_md.is_file():
        print(f"sync: {agents_md} não existe", file=sys.stderr)
        return 1

    previous = load_manifest()
    ctx = Ctx(args.dry_run, args.quiet, cfg, datetime.now().strftime("%Y%m%d-%H%M%S"), dict(previous))
    try:
        link_file(ctx, agents_md, CLAUDE_HOME / "CLAUDE.md")
        link_file(ctx, agents_md, CODEX_HOME / "AGENTS.md")
        sync_agents(ctx)
        sync_commands(ctx)
        prune_stale(ctx, previous)
        sync_settings(ctx)
        sync_codex_hooks(ctx)
    except OSError as err:
        print(f"sync: erro de I/O: {err}", file=sys.stderr)
        return 1

    if not args.dry_run:
        MANIFEST_PATH.write_text(json.dumps({"managed": ctx.managed}, indent=2) + "\n", encoding="utf-8")
        LAST_SYNC_PATH.write_text(datetime.now().isoformat(timespec="seconds") + "\n", encoding="utf-8")
    print(f"sync: {'dry-run' if args.dry_run else 'ok'} — {ctx.changes} alteração(ões); org_enabled={bool(ctx.cfg.get('org_enabled'))}; language={language(cfg)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
