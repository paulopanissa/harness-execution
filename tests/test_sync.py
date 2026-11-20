"""End-to-end sync in an isolated sandbox: links, generated agents, settings hooks, language switch."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from _util import make_sandbox, run_py

AGENT_NAMES = ("explorer", "node-ts-dev", "react-ts-dev", "python-dev", "gamedev-dev", "reviewer")


def changes(stdout: str) -> int:
    match = re.search(r"(\d+) altera", stdout)
    if not match:
        raise AssertionError(f"unexpected sync output: {stdout}")
    return int(match.group(1))


class SyncTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.env = make_sandbox(self.tmp)
        self.hx, self.claude, self.codex = self.tmp / "hx", self.tmp / "claude", self.tmp / "codex"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def sync(self) -> str:
        result = run_py(self.hx / "scripts" / "sync.py", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result.stdout

    def validate(self) -> list[str]:
        code = "import sys, json; sys.path.insert(0, sys.argv[1]); import install; print(json.dumps(install.validate(False)))"
        result = subprocess.run([sys.executable, "-c", code, str(self.hx / "scripts")], env=self.env,
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout.strip().splitlines()[-1])

    def test_fresh_sync_installs_everything_and_validates(self) -> None:
        self.sync()
        root = (self.hx / "AGENTS.md").read_bytes()
        self.assertEqual((self.claude / "CLAUDE.md").read_bytes(), root)
        self.assertEqual((self.codex / "AGENTS.md").read_bytes(), root)
        for name in AGENT_NAMES:
            self.assertTrue((self.claude / "agents" / f"{name}.md").is_file(), name)
            data = tomllib.loads((self.codex / "agents" / f"{name}.toml").read_text(encoding="utf-8"))
            self.assertEqual(data["name"], name)
            self.assertIn("developer_instructions", data)
        self.assertTrue((self.claude / "commands" / "hx.md").is_file())
        self.assertFalse((self.claude / "commands" / "hx" / "org.md").exists())
        hooks = json.dumps(json.loads((self.claude / "settings.json").read_text(encoding="utf-8"))["hooks"])
        self.assertIn("block-spec-md.sh", hooks)
        self.assertIn("read-guard.sh", hooks)
        self.assertEqual(self.validate(), [])

    def test_second_sync_is_a_no_op(self) -> None:
        self.sync()
        self.assertEqual(changes(self.sync()), 0)

    def test_language_pt_br_switches_rules_and_back(self) -> None:
        self.sync()
        config = self.hx / "config.yaml"
        config.write_text("language: pt-BR\n", encoding="utf-8")
        self.sync()
        pt = (self.hx / "i18n" / "pt-BR" / "AGENTS.md").read_bytes()
        self.assertEqual((self.claude / "CLAUDE.md").read_bytes(), pt)
        self.assertEqual((self.claude / "commands" / "hx.md").read_bytes(),
                         (self.hx / "i18n" / "pt-BR" / "commands" / "hx.md").read_bytes())
        self.assertIn("i18n/pt-BR/skills", (self.claude / "agents" / "explorer.md").read_text(encoding="utf-8"))
        self.assertEqual(self.validate(), [])

        config.write_text("language: en\n", encoding="utf-8")
        self.sync()
        self.assertEqual((self.claude / "CLAUDE.md").read_bytes(), (self.hx / "AGENTS.md").read_bytes())

    def test_existing_user_settings_are_preserved(self) -> None:
        settings = self.claude / "settings.json"
        settings.write_text(json.dumps({"theme": "dark", "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}}),
                            encoding="utf-8")
        self.sync()
        data = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(data["theme"], "dark")
        self.assertIn("echo hi", json.dumps(data["hooks"]["Stop"]))


if __name__ == "__main__":
    unittest.main()
