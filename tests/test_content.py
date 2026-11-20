"""Static checks on rules content: en/pt-BR parity, frontmatter, mods catalog."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from _util import REPO, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from hxlib import parse_frontmatter  # noqa: E402

PT = REPO / "i18n" / "pt-BR"
RULE_DIRS = ("agents", "commands", "skills")


def rel_files(root: Path) -> set[str]:
    found = {"AGENTS.md"} if (root / "AGENTS.md").is_file() else set()
    for folder in RULE_DIRS:
        found |= {p.relative_to(root).as_posix() for p in (root / folder).rglob("*.md")}
    return found


class ParityTest(unittest.TestCase):
    def test_every_rule_file_exists_in_both_languages(self) -> None:
        en, pt = rel_files(REPO), rel_files(PT)
        self.assertEqual(sorted(en - pt), [], "missing pt-BR translation")
        self.assertEqual(sorted(pt - en), [], "pt-BR file without English source")

    def test_frontmatter_keys_and_names_match(self) -> None:
        for rel in sorted(rel_files(REPO)):
            if not rel.startswith(("agents/", "commands/")):
                continue
            with self.subTest(rel=rel):
                en_meta, en_body = parse_frontmatter((REPO / rel).read_text(encoding="utf-8"))
                pt_meta, _ = parse_frontmatter((PT / rel).read_text(encoding="utf-8"))
                self.assertTrue(en_meta.get("description"), "description required")
                self.assertTrue(en_body.strip(), "empty body")
                self.assertEqual(set(en_meta), set(pt_meta))
                if rel.startswith("agents/"):
                    self.assertEqual(en_meta.get("name"), Path(rel).stem)
                    self.assertEqual(pt_meta.get("name"), en_meta.get("name"))

    def test_pt_br_rules_point_to_pt_br_paths(self) -> None:
        for rel in sorted(rel_files(PT)):
            if rel == "AGENTS.md":
                continue
            text = (PT / rel).read_text(encoding="utf-8")
            with self.subTest(rel=rel):
                self.assertNotRegex(text, r"~/\.hx/(skills|commands)/", "pt-BR file links English path")


class CatalogTest(unittest.TestCase):
    def test_catalog_entries_are_complete_and_unique(self) -> None:
        catalog = json.loads((REPO / "mods" / "catalog.json").read_text(encoding="utf-8"))
        ids: list[str] = []
        for tool in ("claude", "codex"):
            self.assertIsInstance(catalog.get(tool), list)
            for mod in catalog[tool]:
                with self.subTest(mod=mod.get("id")):
                    for key in ("id", "name", "description", "kind"):
                        self.assertTrue(mod.get(key), key)
                    if mod["kind"] == "plugin":
                        self.assertTrue(mod.get("marketplace") and mod.get("plugin"))
                    ids.append(mod["id"])
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
