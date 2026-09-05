#!/usr/bin/env python3
"""
Unit tests for audit_skill.py in agent-scaffolders.
Tests alignment checks:
1. Line budget (target <= 100 lines for Layer 1 dispatchers)
2. Evals schema (JSON array of {should_trigger: bool})
3. Frontmatter standards (name matches directory, 3rd-person description)
4. Hub-and-spoke compliance (ADR-002/003 - scripts must be symlinks)
5. Missing references (acceptance-criteria.md, fallback-tree.md)
6. Fix mode (--fix) auto-repair capability

Purpose:
    Validates audit_skill.py's checks above against synthetic sample skills.

Key Input Dependencies:
    - ../scripts/audit_skill.py (module under test)
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# We will import audit_skill from agent-scaffolders scripts
try:
    from plugins.agent_scaffolders.scripts.audit_skill import audit_skill, SkillAuditResult
except ImportError:
    # Allow local execution if sys.path adjusted
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    try:
        from audit_skill import audit_skill, SkillAuditResult
    except ImportError:
        audit_skill = None
        SkillAuditResult = None


class TestAuditSkill(unittest.TestCase):

    def setUp(self):
        """Create a synthetic sample-plugin skill tree with valid references."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_root = Path(self.temp_dir) / "plugins" / "sample-plugin"
        self.skills_dir = self.plugin_root / "skills"
        self.plugin_scripts_dir = self.plugin_root / "scripts"
        self.plugin_refs_dir = self.plugin_root / "references"
        
        self.plugin_scripts_dir.mkdir(parents=True, exist_ok=True)
        self.plugin_refs_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        (self.plugin_refs_dir / "acceptance-criteria.md").write_text("# Criteria\n", encoding="utf-8")
        (self.plugin_refs_dir / "fallback-tree.md").write_text("# Fallback\n", encoding="utf-8")

    def tearDown(self):
        """Remove the temporary sample-plugin tree."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_import_exists(self):
        """Assert audit_skill module is available."""
        self.assertIsNotNone(audit_skill, "audit_skill module must be implementable and importable")

    def test_audit_compliant_skill(self):
        """Assert a compliant skill produces 0 errors and passes."""
        skill_dir = self.skills_dir / "compliant-skill"
        skill_dir.mkdir(parents=True)
        
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: compliant-skill\n"
            "plugin: sample-plugin\n"
            "description: Processes data according to sample specification.\n"
            "---\n"
            "# Compliant Skill\n"
            "Execution instructions under 100 lines.\n",
            encoding="utf-8"
        )
        
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir()
        (evals_dir / "evals.json").write_text(json.dumps([
            {"id": "p1", "type": "positive", "prompt": "process data", "should_trigger": True},
            {"id": "n1", "type": "negative", "prompt": "delete file", "should_trigger": False}
        ]), encoding="utf-8")
        
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        os.symlink(self.plugin_refs_dir / "acceptance-criteria.md", refs_dir / "acceptance-criteria.md")
        os.symlink(self.plugin_refs_dir / "fallback-tree.md", refs_dir / "fallback-tree.md")

        result = audit_skill(skill_dir, plugin_root=self.plugin_root)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.errors), 0)

    def test_audit_detects_line_budget_overflow(self):
        """Assert SKILL.md exceeding 100 lines triggers a warning."""
        skill_dir = self.skills_dir / "bloated-skill"
        skill_dir.mkdir(parents=True)
        
        content = "---\nname: bloated-skill\ndescription: Does work.\n---\n" + ("Line\n" * 150)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        
        result = audit_skill(skill_dir, plugin_root=self.plugin_root)
        self.assertTrue(any("exceeds 100 lines" in w for w in result.warnings))

    def test_audit_detects_invalid_evals_schema(self):
        """Assert legacy or malformed evals schema triggers error."""
        skill_dir = self.skills_dir / "bad-evals-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: bad-evals-skill\ndescription: Does work.\n---\n", encoding="utf-8")
        
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir()
        (evals_dir / "evals.json").write_text(json.dumps({
            "entries": [{"id": "p1", "prompt": "do work", "expected_behavior": "work done"}]
        }), encoding="utf-8")
        
        result = audit_skill(skill_dir, plugin_root=self.plugin_root)
        self.assertFalse(result.passed)
        self.assertTrue(any("should_trigger" in e for e in result.errors))

    def test_audit_detects_hub_and_spoke_violation(self):
        """Assert real un-symlinked script in skill directory is flagged."""
        skill_dir = self.skills_dir / "impure-script-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: impure-script-skill\ndescription: Does work.\n---\n", encoding="utf-8")
        
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        # Real file, not a symlink
        (scripts_dir / "helper.py").write_text("print('hello')\n", encoding="utf-8")
        
        result = audit_skill(skill_dir, plugin_root=self.plugin_root)
        self.assertFalse(result.passed)
        self.assertTrue(any("ADR-002" in e or "not a symlink" in e for e in result.errors))

    def test_fix_mode_repairs_evals(self):
        """Assert --fix mode converts legacy dict wrapped evals to array."""
        skill_dir = self.skills_dir / "fixable-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: fixable-skill\ndescription: Does work.\n---\n", encoding="utf-8")
        
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir()
        (evals_dir / "evals.json").write_text(json.dumps({
            "entries": [{"id": "p1", "type": "positive", "prompt": "do work", "should_trigger": True}]
        }), encoding="utf-8")
        
        result = audit_skill(skill_dir, plugin_root=self.plugin_root, fix=True)
        # Should repair evals.json to root list
        repaired_data = json.loads((evals_dir / "evals.json").read_text(encoding="utf-8"))
        self.assertIsInstance(repaired_data, list)


if __name__ == "__main__":
    unittest.main()
