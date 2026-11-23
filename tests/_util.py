"""Shared helpers: isolated HX sandbox (own HX_HOME / Claude / Codex homes) and bash lookup."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

_IGNORE = shutil.ignore_patterns(
    ".git", "vendor", "backups", "__pycache__", "node_modules", "config.yaml", ".manifest.json",
    ".last_sync", ".update.*", "fallback-memory.jsonl", "*.hx-bak*", "tests",
)


def make_sandbox(tmp: Path) -> dict[str, str]:
    """Copy the harness into tmp/hx and return an env pointing every home into tmp."""
    hx = tmp / "hx"
    shutil.copytree(REPO, hx, ignore=_IGNORE)
    (tmp / "claude").mkdir()
    (tmp / "codex").mkdir()
    return sandbox_env(tmp)


def sandbox_env(tmp: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "HX_HOME": str(tmp / "hx"),
        "HX_CLAUDE_HOME": str(tmp / "claude"),
        "CODEX_HOME": str(tmp / "codex"),
        "HX_CODEX_SKILLS_HOME": str(tmp / "codex-skills"),
        "PYTHONIOENCODING": "utf-8",
        "GIT_AUTHOR_NAME": "hx-test", "GIT_AUTHOR_EMAIL": "hx-test@example.invalid",
        "GIT_COMMITTER_NAME": "hx-test", "GIT_COMMITTER_EMAIL": "hx-test@example.invalid",
    })
    return env


def run_py(script: Path, *args: str, env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args], env=env, cwd=cwd,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, check=False,
    )


def find_bash() -> str | None:
    """Git Bash on Windows (System32\\bash.exe is WSL and cannot see Windows paths the same way)."""
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            for parent in Path(git).resolve().parents:
                candidate = parent / "bin" / "bash.exe"
                if candidate.is_file():
                    return str(candidate)
        return None
    return shutil.which("bash")


def run_hook(bash: str, hook: str, payload: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [bash, str(REPO / "hooks" / hook)], input=payload, env=env or dict(os.environ),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, check=False,
    )
