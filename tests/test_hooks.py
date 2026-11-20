"""Hook behavior through real bash (Git Bash on Windows)."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from _util import REPO, find_bash, run_hook

BASH = find_bash()


def payload(**tool_input: object) -> str:
    return json.dumps({"tool_name": "X", "tool_input": tool_input, "cwd": str(Path.cwd())})


@unittest.skipUnless(BASH, "bash not available")
class ReadGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.big, self.small = tmp / "big.txt", tmp / "small.txt"
        self.big.write_text("\n".join(map(str, range(500))) + "\n", encoding="utf-8")
        self.small.write_text("a\nb\n", encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if k not in ("HX_ALLOW_READ", "HX_READ_MAX_LINES")}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def code(self, body: str, **extra_env: str) -> int:
        return run_hook(BASH, "read-guard.sh", body, {**self.env, **extra_env}).returncode

    def test_blocks_large_file_read_whole(self) -> None:
        result = run_hook(BASH, "read-guard.sh", payload(file_path=str(self.big)), self.env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("500 lines", result.stderr)

    def test_allows_range_small_file_missing_file_and_images(self) -> None:
        self.assertEqual(self.code(payload(file_path=str(self.big), offset=10, limit=20)), 0)
        self.assertEqual(self.code(payload(file_path=str(self.small))), 0)
        self.assertEqual(self.code(payload(file_path=str(self.big.with_name("nope.txt")))), 0)
        png = self.big.with_suffix(".png")
        png.write_bytes(self.big.read_bytes())
        self.assertEqual(self.code(payload(file_path=str(png))), 0)

    def test_bypass_and_threshold_env(self) -> None:
        self.assertEqual(self.code(payload(file_path=str(self.big)), HX_ALLOW_READ="1"), 0)
        self.assertEqual(self.code(payload(file_path=str(self.big)), HX_READ_MAX_LINES="1000"), 0)


@unittest.skipUnless(BASH, "bash not available")
class BlockSpecMdTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name) / "project"
        self.project.mkdir()
        self.env = {**{k: v for k, v in os.environ.items() if k != "HX_ALLOW_MD"},
                    "HX_HOME": str(Path(self._tmp.name) / "hx")}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def code(self, name: str) -> int:
        return run_hook(BASH, "block-spec-md.sh", payload(file_path=str(self.project / name)), self.env).returncode

    def test_blocks_intermediate_plan_files(self) -> None:
        for name in ("plan.md", "feature-spec.md", "analysis.md", "notes.md", "code-review.md", "specs/x.md"):
            with self.subTest(name=name):
                self.assertEqual(self.code(name), 2)

    def test_allows_regular_markdown_and_code(self) -> None:
        for name in ("README.md", "reviewer.md", "CHANGELOG.md", "plan.ts", "docs/guide.md"):
            with self.subTest(name=name):
                self.assertEqual(self.code(name), 0)

    def test_editing_existing_file_is_allowed(self) -> None:
        (self.project / "plan.md").write_text("x", encoding="utf-8")
        self.assertEqual(self.code("plan.md"), 0)


@unittest.skipUnless(BASH, "bash not available")
class OrgOnlyTest(unittest.TestCase):
    def test_inactive_without_org_config(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            env = {**os.environ, "HX_HOME": raw}
            result = run_hook(BASH, "org-only.sh", "", env)
            self.assertEqual(result.returncode, 2)  # usage error without args
            check = subprocess.run([BASH, str(REPO / "hooks" / "org-only.sh"), "--check", raw],
                                   env=env, capture_output=True, text=True, check=False)
            self.assertEqual(check.returncode, 1)


FAKE_GRAPHIFY = """#!/usr/bin/env bash
# graphify falso: registra as chamadas; FAKE_GRAPHIFY_FAIL=1 faz tudo falhar.
printf '%s\\n' "$*" >>"$FAKE_GRAPHIFY_CALLS"
[ "${FAKE_GRAPHIFY_FAIL:-0}" = "1" ] && { echo boom >&2; exit 1; }
hook="$(git rev-parse --git-path hooks/post-commit)"
case "$1 ${2:-}" in
  "hook status") if grep -qs graphify-hook-start "$hook"; then echo "post-commit: installed"; else echo "post-commit: not installed"; fi ;;
  "hook install") mkdir -p "$(dirname "$hook")"; printf '#!/bin/sh\\n# graphify-hook-start\\n' >"$hook" ;;
  "extract "*) mkdir -p "$2/graphify-out" && echo '{}' >"$2/graphify-out/graph.json" ;;
esac
exit 0
"""


@unittest.skipUnless(BASH, "bash not available")
class GraphifySetupTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.hx, self.repo, self.bin = tmp / "hx", tmp / "repo", tmp / "bin"
        for d in (self.hx, self.repo, self.bin):
            d.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.calls = tmp / "calls.txt"
        fake = self.bin / "graphify"
        fake.write_text(FAKE_GRAPHIFY, encoding="utf-8", newline="\n")
        fake.chmod(0o755)
        # PATH sem nenhum graphify real; o falso entra só quando with_graphify=True.
        clean_path = os.pathsep.join(
            d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not any((Path(d) / n).exists() for n in ("graphify", "graphify.exe")))
        self.env = {**{k: v for k, v in os.environ.items() if not k.startswith(("HX_", "CLAUDE_PROJECT_DIR"))},
                    "HX_HOME": str(self.hx), "HX_GRAPHIFY_SYNC": "1", "PATH": clean_path,
                    "FAKE_GRAPHIFY_CALLS": str(self.calls)}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_setup(self, cwd: Path | None = None, with_graphify: bool = True, **extra: str) -> subprocess.CompletedProcess[str]:
        env = {**self.env, **extra}
        if with_graphify:
            env["PATH"] = str(self.bin) + os.pathsep + env["PATH"]
        body = json.dumps({"hook_event_name": "SessionStart", "cwd": str(cwd or self.repo)})
        return run_hook(BASH, "graphify-setup.sh", body, env)

    def call_lines(self) -> list[str]:
        return self.calls.read_text(encoding="utf-8").splitlines() if self.calls.exists() else []

    def test_non_git_dir_does_nothing(self) -> None:
        plain = Path(self._tmp.name) / "plain"
        plain.mkdir()
        result = self.run_setup(cwd=plain)
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertEqual(self.call_lines(), [])
        self.assertFalse((plain / ".gitignore").exists())

    def test_missing_graphify_warns_once_per_repo(self) -> None:
        first = self.run_setup(with_graphify=False)
        second = self.run_setup(with_graphify=False)
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        self.assertIn("uv tool install graphifyy", first.stdout)
        self.assertEqual(second.stdout, "")
        self.assertFalse((self.repo / ".gitignore").exists())

    def test_setup_is_idempotent(self) -> None:
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual(self.run_setup().returncode, 0)
        gitignore = (self.repo / ".gitignore").read_text(encoding="utf-8")
        self.assertEqual(gitignore.splitlines().count("graphify-out/"), 1)
        calls = self.call_lines()
        self.assertEqual(sum(c.startswith("extract ") and c.endswith("--code-only") for c in calls), 1)
        self.assertEqual(calls.count("hook install"), 1)
        self.assertTrue((self.repo / "graphify-out").is_dir())

    def test_build_only_without_graphify_out_and_install_only_when_missing(self) -> None:
        (self.repo / "graphify-out").mkdir()
        (self.repo / "graphify-out" / "graph.json").write_text("{}", encoding="utf-8")
        self.run_setup()
        self.assertEqual(self.call_lines(), ["hook status", "hook install"])
        self.calls.unlink()
        (self.repo / "graphify-out" / "graph.json").unlink()  # build parcial/interrompido: refaz
        self.run_setup()
        calls = self.call_lines()
        self.assertNotIn("hook install", calls)
        self.assertTrue(any(c.startswith("extract ") for c in calls))

    def test_versioned_hooks_path_is_left_alone(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "config", "core.hooksPath", ".husky"], check=True)
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual(self.run_setup().returncode, 0)
        calls = self.call_lines()
        self.assertNotIn("hook install", calls)
        self.assertNotIn("hook status", calls)
        self.assertEqual(sum(c.startswith("extract ") for c in calls), 1)
        self.assertFalse((self.repo / ".husky").exists())

    def test_gitignore_keeps_crlf_and_missing_final_newline(self) -> None:
        (self.repo / ".gitignore").write_bytes(b"node_modules/\r\ndist/")
        self.run_setup()
        self.assertEqual((self.repo / ".gitignore").read_bytes(), b"node_modules/\r\ndist/\r\ngraphify-out/\r\n")
        (self.repo / ".gitignore").write_bytes(b"/graphify-out\n")
        self.run_setup()
        self.assertEqual((self.repo / ".gitignore").read_bytes(), b"/graphify-out\n")

    def test_graphify_errors_never_fail_the_session(self) -> None:
        result = self.run_setup(FAKE_GRAPHIFY_FAIL="1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("ERRO", (self.hx / ".graphify.log").read_text(encoding="utf-8"))

    def test_bypass_env(self) -> None:
        result = self.run_setup(HX_NO_GRAPHIFY="1")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.call_lines(), [])
        self.assertFalse((self.repo / ".gitignore").exists())

    def test_background_mode_returns_fast_and_builds(self) -> None:
        env = {k: v for k, v in self.env.items() if k != "HX_GRAPHIFY_SYNC"}
        env["PATH"] = str(self.bin) + os.pathsep + env["PATH"]
        start = time.monotonic()
        body = json.dumps({"cwd": str(self.repo)})
        result = run_hook(BASH, "graphify-setup.sh", body, env)
        self.assertEqual(result.returncode, 0)
        self.assertLess(time.monotonic() - start, 5)
        deadline = time.monotonic() + 20
        while not (self.repo / "graphify-out").is_dir() and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertTrue((self.repo / "graphify-out").is_dir())
        while (self.hx / "state").exists() and any((self.hx / "state").glob("*.lock")) and time.monotonic() < deadline:
            time.sleep(0.2)  # aguarda o background soltar o lock antes do cleanup


if __name__ == "__main__":
    unittest.main()
