#!/usr/bin/env python3
"""Regression tests for plugin structure discovery boundaries."""

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from audit_plugin_structure import audit_plugin


class TestAuditPluginStructure(unittest.TestCase):
    """Ensures nested SKILL.md files cannot become discoverable skills."""

    def test_nested_skill_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "plugin"
            skill_root = plugin_root / "skills" / "example"
            (skill_root / "references").mkdir(parents=True)
            (skill_root / "SKILL.md").write_text("---\nname: example\n---\n", encoding="utf-8")
            (skill_root / "references" / "SKILL.md").write_text("---\nname: nested\n---\n", encoding="utf-8")

            findings = audit_plugin(plugin_root)

        nested = [finding for finding in findings if finding["type"] == "nested_skill_file"]
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0]["severity"], "error")


if __name__ == "__main__":
    unittest.main()
