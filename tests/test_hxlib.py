from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _util import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import hxlib  # noqa: E402


class YamlTest(unittest.TestCase):
    def test_dump_then_parse_round_trips_scalars_and_nested_maps(self) -> None:
        cfg = {"language": "pt-BR", "org_enabled": True, "auto_update_days": 7, "mods": "",
               "models": {"claude_fast": "haiku", "codex_fast": ""}}
        self.assertEqual(hxlib.parse_yaml(hxlib.dump_yaml(cfg)), cfg)

    def test_merge_config_keeps_defaults_for_missing_nested_keys(self) -> None:
        merged = hxlib.merge_config(hxlib.DEFAULT_CONFIG, {"models": {"claude_fast": "x"}})
        self.assertEqual(merged["models"]["claude_fast"], "x")
        self.assertEqual(merged["models"]["claude_default"], hxlib.DEFAULT_CONFIG["models"]["claude_default"])
        self.assertEqual(merged["language"], "en")


class ModelTest(unittest.TestCase):
    def test_empty_model_falls_back(self) -> None:
        cfg = {"models": {"claude_fast": ""}, "fallbacks": {"claude_fast": "sonnet"}}
        self.assertEqual(hxlib.resolve_model(cfg, "claude", "fast"), "sonnet")

    def test_unknown_tier_uses_default_and_empty_inherits(self) -> None:
        cfg = {"models": {"codex_default": ""}, "fallbacks": {}}
        self.assertEqual(hxlib.resolve_model(cfg, "codex", "bogus"), "")


class FrontmatterTest(unittest.TestCase):
    def test_parses_quoted_values_and_body(self) -> None:
        meta, body = hxlib.parse_frontmatter('---\nname: "explorer"\ndescription: Read-only\n---\n\nBody\n')
        self.assertEqual(meta, {"name": "explorer", "description": "Read-only"})
        self.assertEqual(body, "Body\n")

    def test_without_frontmatter_returns_text(self) -> None:
        self.assertEqual(hxlib.parse_frontmatter("plain"), ({}, "plain"))


class LanguageTest(unittest.TestCase):
    def test_invalid_language_is_english(self) -> None:
        self.assertEqual(hxlib.language({"language": "klingon"}), "en")
        self.assertEqual(hxlib.language({}), "en")

    def test_localized_prefers_translation_and_falls_back_to_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            (home / "i18n" / "pt-BR" / "agents").mkdir(parents=True)
            (home / "i18n" / "pt-BR" / "agents" / "a.md").write_text("pt", encoding="utf-8")
            with mock.patch.object(hxlib, "HX_HOME", home), mock.patch.object(hxlib, "I18N_DIR", home / "i18n"):
                pt = {"language": "pt-BR"}
                self.assertEqual(hxlib.localized("agents/a.md", pt), home / "i18n" / "pt-BR" / "agents" / "a.md")
                self.assertEqual(hxlib.localized("agents/b.md", pt), home / "agents" / "b.md")
                self.assertEqual(hxlib.localized("agents/a.md", {"language": "en"}), home / "agents" / "a.md")


if __name__ == "__main__":
    unittest.main()
