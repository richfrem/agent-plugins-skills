#!/usr/bin/env python3
"""
Tests how audit.py finds audit_skill.py now that it lives in a sibling skill.

Purpose:
    1. When ../../authoring-skills/scripts/audit_skill.py exists next to this skill, audit.py uses it
    2. When no audit_skill.py can be found, audit.py warns loudly instead of silently skipping skill checks

Key Input Dependencies:
    - ../scripts/audit.py (copied into a temporary skills layout)
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent / "scripts" / "audit.py"
STUB = '''
class _Result:
    errors = ["stub-sibling-was-used"]
    warnings = []


def audit_skill(path, plugin_root=None, **kwargs):
    return _Result()
'''


def make_layout(root: Path, with_sibling: bool) -> Path:
    scripts = root / "skills" / "authoring-plugins" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(AUDIT, scripts / "audit.py")
    if with_sibling:
        sibling = root / "skills" / "authoring-skills" / "scripts"
        sibling.mkdir(parents=True)
        (sibling / "audit_skill.py").write_text(STUB, encoding="utf-8")
    plugin = root / "target-plugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "target-plugin", "version": "1.0.0", "description": "x", "author": {"name": "a"}}', encoding="utf-8")
    skill = plugin / "skills" / "demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: Demo.\n---\n# Demo\n", encoding="utf-8")
    return plugin


def run_audit(root: Path, plugin: Path):
    return subprocess.run([sys.executable, str(root / "skills" / "authoring-plugins" / "scripts" / "audit.py"), "--path", str(plugin)],
                          capture_output=True, text=True)


class SiblingLookupTests(unittest.TestCase):
    def test_sibling_audit_skill_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_audit(Path(tmp), make_layout(Path(tmp), with_sibling=True))
            self.assertIn("stub-sibling-was-used", result.stdout + result.stderr)

    def test_missing_audit_skill_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_audit(Path(tmp), make_layout(Path(tmp), with_sibling=False))
            self.assertIn("audit_skill.py not found", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
