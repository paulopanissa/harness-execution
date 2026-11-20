"""update.py against a throwaway upstream: fast-forward, sync, validate; refuses dirty trees."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from _util import make_sandbox, run_py

GIT = shutil.which("git")


@unittest.skipUnless(GIT, "git not available")
class UpdateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.env = make_sandbox(self.tmp)
        upstream = self.tmp / "upstream"
        (self.tmp / "hx").rename(upstream)
        self.git("init", "-q", "-b", "main", cwd=upstream)
        self.git("add", "-A", cwd=upstream)
        self.git("commit", "-qm", "v1", cwd=upstream)
        self.git("clone", "-q", str(upstream), str(self.tmp / "hx"), cwd=self.tmp)
        (upstream / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        self.git("commit", "-qam", "v2", cwd=upstream)
        self.hx = self.tmp / "hx"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def git(self, *args: str, cwd: Path) -> None:
        subprocess.run([GIT, *args], cwd=cwd, env=self.env, check=True, capture_output=True)

    def update(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run_py(self.hx / "scripts" / "update.py", *args, env=self.env)

    def test_check_reports_without_changing(self) -> None:
        result = self.update("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 new commit", result.stdout)
        self.assertNotEqual((self.hx / "VERSION").read_text(encoding="utf-8").strip(), "9.9.9")

    def test_update_fast_forwards_syncs_and_validates(self) -> None:
        result = self.update()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.hx / "VERSION").read_text(encoding="utf-8").strip(), "9.9.9")
        self.assertIn("synced and validated", result.stdout)
        self.assertTrue((self.tmp / "claude" / "CLAUDE.md").is_file())

    def test_refuses_dirty_tracked_files_unless_autostash(self) -> None:
        readme = self.hx / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\nlocal\n", encoding="utf-8")
        refused = self.update()
        self.assertEqual(refused.returncode, 1)
        self.assertIn("--autostash", refused.stdout)
        done = self.update("--autostash")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue(readme.read_text(encoding="utf-8").endswith("local\n"))


if __name__ == "__main__":
    unittest.main()
