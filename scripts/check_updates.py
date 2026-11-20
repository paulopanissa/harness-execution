#!/usr/bin/env python3
"""check_updates.py — auto-update do módulo org sem bloquear o usuário.

Se org_enabled e ~/.hx/.last_sync tem >= auto_update_days, dispara em background:
  git pull --ff-only em ~/.hx/vendor/org-preset e ~/.hx/vendor/org && sync.py --quiet
Uso: check_updates.py [--force] [--foreground]
Log do background: ~/.hx/.update.log
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hxlib import HX_HOME, LAST_SYNC_PATH, ORG_PRESET_DIR, ORG_VENDOR_DIR, load_config  # noqa: E402

LOG_PATH = HX_HOME / ".update.log"
LOCK_PATH = HX_HOME / ".update.lock"
LOCK_MAX_AGE = timedelta(minutes=10)
GIT_TIMEOUT_S = 120


def last_sync() -> datetime | None:
    try:
        return datetime.fromisoformat(LAST_SYNC_PATH.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def is_due(days: int) -> bool:
    stamp = last_sync()
    return stamp is None or datetime.now() - stamp >= timedelta(days=days)


def lock_busy() -> bool:
    if not LOCK_PATH.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(LOCK_PATH.stat().st_mtime)
    return age < LOCK_MAX_AGE


def run_update() -> int:
    """Executa pull dos repos org + sync (modo foreground / processo destacado)."""
    LOCK_PATH.write_text(datetime.now().isoformat(), encoding="utf-8")
    try:
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write(f"\n== {datetime.now().isoformat(timespec='seconds')} ==\n")
            log.flush()
            for repo in (ORG_PRESET_DIR, ORG_VENDOR_DIR):
                if not (repo / ".git").exists():
                    continue
                pull = subprocess.run(
                    ["git", "-C", str(repo), "pull", "--ff-only", "--quiet"],
                    stdout=log, stderr=log, timeout=GIT_TIMEOUT_S, check=False,
                )
                if pull.returncode != 0:
                    log.write(f"git pull falhou em {repo} (rc={pull.returncode}); sync não executado\n")
                    return pull.returncode
            sync = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("sync.py")), "--quiet"],
                stdout=log, stderr=log, timeout=GIT_TIMEOUT_S, check=False,
            )
            return sync.returncode
    except (OSError, subprocess.TimeoutExpired) as err:
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write(f"erro: {err}\n")
        return 1
    finally:
        LOCK_PATH.unlink(missing_ok=True)


def spawn_background() -> None:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--foreground", "--force"]
    kwargs: dict = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, **kwargs)  # noqa: S603 — args fixos


def main() -> int:
    parser = argparse.ArgumentParser(description="auto-update do módulo org")
    parser.add_argument("--force", action="store_true", help="ignora o intervalo de dias")
    parser.add_argument("--foreground", action="store_true", help="executa no processo atual")
    args = parser.parse_args()

    cfg = load_config()
    if not cfg.get("org_enabled"):
        return 0
    if not (ORG_VENDOR_DIR / ".git").exists():
        print(f"hx: vendor org ausente em {ORG_VENDOR_DIR}; rode install.py --org <url>", file=sys.stderr)
        return 0
    if not args.force and not is_due(int(cfg.get("auto_update_days", 7))):
        return 0
    if lock_busy():
        return 0
    if args.foreground:
        return run_update()
    spawn_background()
    return 0


if __name__ == "__main__":
    sys.exit(main())
