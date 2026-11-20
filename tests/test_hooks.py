"""Hook behavior through real bash (Git Bash on Windows)."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
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


if __name__ == "__main__":
    unittest.main()
