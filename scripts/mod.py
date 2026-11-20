#!/usr/bin/env python3
"""mod.py — catálogo de mods de UI do HX (Claude Code; Codex reservado).

Uso:
  mod.py list                 lista o catálogo e o que está instalado
  mod.py install <id...>      instala (marketplace add + plugin install)
  mod.py remove <id...>       desinstala
  mod.py pick                 escolha interativa (usado pelo install.py)
A seleção fica em ~/.hx/config.yaml (chave `mods`).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hxlib import HX_HOME, MODS_DIR, load_config, mods_selected, save_config  # noqa: E402

CATALOG_PATH = MODS_DIR / "catalog.json"
CLI_TIMEOUT_S = 180


def load_catalog() -> dict[str, list[dict[str, Any]]]:
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise SystemExit(f"mod: catálogo inválido em {CATALOG_PATH}: {err}") from err
    return {"claude": list(data.get("claude", [])), "codex": list(data.get("codex", []))}


def find_mod(catalog: dict[str, list[dict[str, Any]]], mod_id: str) -> dict[str, Any] | None:
    return next((m for m in catalog["claude"] if m.get("id") == mod_id), None)


def claude_cli() -> str | None:
    return shutil.which("claude")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    exe = claude_cli()
    if exe is None:
        raise SystemExit("mod: CLI `claude` não encontrado no PATH")
    return subprocess.run(
        [exe, "plugin", *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=CLI_TIMEOUT_S, check=False,
    )


def installed_ids() -> set[str]:
    if claude_cli() is None:
        return set()
    proc = run_cli("list", "--json")
    try:
        return {str(p.get("id")) for p in json.loads(proc.stdout or "[]")}
    except ValueError:
        return set()


def marketplace_source(mod: dict[str, Any]) -> str:
    return str(mod["marketplace"]).replace("{HX_HOME}", HX_HOME.as_posix())


def _tail(proc: subprocess.CompletedProcess[str]) -> str:
    lines = (proc.stderr or proc.stdout or "").strip().splitlines()
    return lines[-1] if lines else f"rc={proc.returncode}"


def install_mod(mod: dict[str, Any]) -> bool:
    if mod.get("kind") == "manual":
        print(f"• {mod['id']}: instalação manual ({mod.get('url', '')})")
        for step in mod.get("steps", []):
            print(f"    - {step}")
        return False
    add = run_cli("marketplace", "add", marketplace_source(mod))
    if add.returncode != 0 and "already" not in (add.stdout + add.stderr).lower():
        print(f"✗ {mod['id']}: marketplace add falhou — {_tail(add)}")
        return False
    inst = run_cli("install", str(mod["plugin"]))
    if inst.returncode != 0:
        print(f"✗ {mod['id']}: install falhou — {_tail(inst)}")
        return False
    print(f"✓ {mod['id']} instalado ({mod['plugin']})")
    return True


def remove_mod(mod: dict[str, Any]) -> bool:
    if mod.get("kind") == "manual":
        print(f"• {mod['id']}: remoção manual (veja {mod.get('url', '')})")
        return False
    proc = run_cli("uninstall", str(mod["plugin"]))
    ok = proc.returncode == 0
    print(f"{'✓' if ok else '✗'} {mod['id']} {'removido' if ok else 'falhou — ' + _tail(proc)}")
    return ok


def save_selection(ids: list[str]) -> None:
    cfg = load_config()
    save_config({**cfg, "mods": ",".join(dict.fromkeys(ids))})


def cmd_list(catalog: dict[str, list[dict[str, Any]]]) -> int:
    have = installed_ids()
    print("Claude Code:")
    for mod in catalog["claude"]:
        mark = "✓" if mod.get("plugin") in have else " "
        print(f"  [{mark}] {mod['id']:<15} tokens={mod.get('tokens', 0)!s:<6} {mod.get('description', '')}")
    print("Codex:" + ("" if catalog["codex"] else " (catálogo vazio)"))
    for mod in catalog["codex"]:
        print(f"  [ ] {mod.get('id', '?'):<15} {mod.get('description', '')}")
    return 0


def pick(catalog: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Multi-seleção interativa. Nada marcado por padrão; vazio = nenhum."""
    mods = catalog["claude"]
    print("Mods de UI (opcionais, 0 token salvo onde indicado):")
    for i, mod in enumerate(mods, 1):
        print(f"  {i}. {mod['name']:<26} {mod.get('description', '')}")
    try:
        answer = input("Quais instalar? (ex.: 1,3 | all | vazio = nenhum) ").strip().lower()
    except EOFError:
        return []
    if answer in ("all", "todos", "*"):
        return [m["id"] for m in mods]
    chosen: list[str] = []
    for part in answer.replace(" ", "").split(","):
        if part.isdigit() and 1 <= int(part) <= len(mods):
            chosen.append(mods[int(part) - 1]["id"])
        elif part and find_mod(catalog, part):
            chosen.append(part)
        elif part:
            print(f"  ignorado: {part}")
    return chosen


def install_many(catalog: dict[str, list[dict[str, Any]]], ids: list[str]) -> list[str]:
    done: list[str] = []
    for mod_id in ids:
        mod = find_mod(catalog, mod_id)
        if mod is None:
            print(f"✗ {mod_id}: não está no catálogo")
            continue
        if install_mod(mod):
            done.append(mod_id)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description="mods de UI do HX")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("pick")
    for name in ("install", "remove"):
        sub.add_parser(name).add_argument("ids", nargs="+")
    args = parser.parse_args()
    catalog = load_catalog()

    if args.cmd == "list":
        return cmd_list(catalog)
    current = mods_selected(load_config())
    if args.cmd == "pick":
        done = install_many(catalog, pick(catalog))
        save_selection([*current, *done])
        return 0
    if args.cmd == "install":
        done = install_many(catalog, args.ids)
        save_selection([*current, *done])
        return 0 if len(done) == len(args.ids) else 1
    removed = [m for m in args.ids if (mod := find_mod(catalog, m)) and remove_mod(mod)]
    save_selection([m for m in current if m not in removed])
    return 0 if len(removed) == len(args.ids) else 1


if __name__ == "__main__":
    sys.exit(main())
