#!/usr/bin/env python3
"""update.py — update an existing HX install in place (no reinstall).

  update.py            pull ~/.hx (fast-forward only), pull org repos if enabled, sync, validate
  update.py --check    fetch and report whether an update exists; changes nothing
  update.py --autostash  stash local edits to tracked files during the pull

Your config.yaml, mods and memory are untouched (all git-ignored).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hxlib import HX_HOME, ORG_PRESET_DIR, ORG_VENDOR_DIR, load_config  # noqa: E402

GIT_TIMEOUT_S = 120
VERSION_FILE = HX_HOME / "VERSION"


def git(*args: str, repo: Path = HX_HOME) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=GIT_TIMEOUT_S, check=False,
    )


def out(*args: str, repo: Path = HX_HOME) -> str:
    result = git(*args, repo=repo)
    return result.stdout.strip() if result.returncode == 0 else ""


def version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "?"


def fetch() -> bool:
    result = git("fetch", "--quiet")
    if result.returncode != 0:
        print(f"✗ git fetch failed: {result.stderr.strip()}")
        return False
    return True


def pending_commits() -> list[str]:
    log = out("log", "--oneline", "HEAD..@{u}")
    return log.splitlines() if log else []


def dirty_tracked() -> list[str]:
    status = out("status", "--porcelain", "--untracked-files=no")
    return [line[3:] for line in status.splitlines() if line.strip()]


def cmd_check() -> int:
    if not fetch():
        return 1
    commits = pending_commits()
    if not commits:
        print(f"✓ HX {version()} is up to date")
        return 0
    print(f"↑ {len(commits)} new commit(s) available (current {version()}):")
    for line in commits[:20]:
        print(f"  {line}")
    print("Run: python ~/.hx/scripts/update.py")
    return 0


def pull_self(autostash: bool) -> bool:
    dirty = dirty_tracked()
    if dirty and not autostash:
        print("✗ local edits in tracked HX files; commit them or rerun with --autostash:")
        for path in dirty[:10]:
            print(f"  {path}")
        return False
    args = ["pull", "--ff-only", "--quiet"] + (["--autostash"] if autostash else [])
    result = git(*args)
    if result.returncode != 0:
        print(f"✗ git pull failed (history diverged?): {result.stderr.strip()}")
        print("  Fix manually in ~/.hx (git status / git log), then rerun.")
        return False
    return True


def pull_org() -> bool:
    ok = True
    for repo in (ORG_PRESET_DIR, ORG_VENDOR_DIR):
        if not (repo / ".git").exists():
            continue
        result = git("pull", "--ff-only", "--quiet", repo=repo)
        if result.returncode != 0:
            print(f"✗ org repo pull failed ({repo.name}): {result.stderr.strip()}")
            ok = False
        else:
            print(f"✓ org repo {repo.name} updated")
    return ok


def run_sync() -> bool:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("sync.py")), "--quiet"],
        timeout=GIT_TIMEOUT_S, check=False,
    )
    return result.returncode == 0


def validate(org: bool) -> list[str]:
    # Imported after the pull so the new install.py is the one used.
    import install  # noqa: PLC0415

    return install.validate(org)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="only report whether an update exists")
    parser.add_argument("--autostash", action="store_true", help="stash local edits to tracked files during the pull")
    args = parser.parse_args()

    if not (HX_HOME / ".git").exists():
        print(f"✗ {HX_HOME} is not a git clone; reinstall with: git clone <repo> ~/.hx && python ~/.hx/scripts/install.py")
        return 1
    if args.check:
        return cmd_check()

    before_sha, before_ver = out("rev-parse", "--short", "HEAD"), version()
    if not fetch() or not pull_self(args.autostash):
        return 1
    after_sha, after_ver = out("rev-parse", "--short", "HEAD"), version()
    if before_sha == after_sha:
        print(f"✓ HX {after_ver} already up to date ({after_sha})")
    else:
        print(f"✓ HX {before_ver} ({before_sha}) → {after_ver} ({after_sha})")
        for line in out("log", "--oneline", f"{before_sha}..{after_sha}").splitlines()[:20]:
            print(f"  {line}")

    org = bool(load_config().get("org_enabled"))
    org_ok = pull_org() if org else True

    if not run_sync():
        print("✗ sync.py failed")
        return 1
    errors = validate(org)
    if errors:
        print("✗ validation:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("✓ synced and validated" + ("" if org_ok else " (org repos not updated, see above)"))
    print("Restart Claude Code / Codex to load updated rules.")
    return 0 if org_ok else 1


if __name__ == "__main__":
    sys.exit(main())
