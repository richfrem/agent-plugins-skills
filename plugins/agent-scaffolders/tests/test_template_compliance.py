"""Tests for canonical skill template compliance auditing."""
import json
import pytest
from pathlib import Path

import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from audit_template_compliance import audit_template_compliance


def test_compliant_synthetic_skill(tmp_path: Path):
    skill = tmp_path / "test-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: test-skill\n"
        "description: Provides automated test skill capabilities. Use when testing.\n"
        "---\n\n"
        "# Test Skill (test-skill)\n\n"
        "Provides automated test capabilities.\n\n"
        "## Contents\n\n"
        "- [Critical Constraints](#critical-constraints)\n"
        "- [Quick start](#quick-start)\n"
        "- [Workflow](#workflow)\n"
        "- [Verification](#verification)\n\n"
        "## Critical Constraints\n\n"
        "- Never bypass verification.\n\n"
        "## Quick start\n\n"
        "```bash\n"
        "echo test\n"
        "```\n\n"
        "## Workflow\n\n"
        "1. Step one.\n"
        "2. Step two.\n\n"
        "## Verification\n\n"
        "1. Check output.\n",
        encoding="utf-8"
    )
    (skill / "evals").mkdir()
    (skill / "evals/evals.json").write_text(
        json.dumps([{"query": "run test", "should_trigger": True}]),
        encoding="utf-8"
    )

    result = audit_template_compliance(skill)
    assert result.is_compliant is True
    assert result.is_content_compliant is True
    assert result.is_folder_compliant is True
    assert result.missing_sections == []
    assert result.legacy_sections == []
    assert result.content_issues == []
    assert result.folder_issues == []


def test_non_compliant_synthetic_skill_flags_missing_and_legacy(tmp_path: Path):
    skill = tmp_path / "bad-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: bad-skill\n"
        "description: Bad skill missing sections.\n"
        "---\n\n"
        "# Bad Skill\n\n"
        "## Available Commands\n\n"
        "```bash\n"
        "echo bad\n"
        "```\n",
        encoding="utf-8"
    )
    (skill / "evals").mkdir()
    (skill / "evals/evals.json").write_text(
        json.dumps([{"query": "run bad", "should_trigger": True}]),
        encoding="utf-8"
    )

    result = audit_template_compliance(skill)
    assert result.is_compliant is False
    assert result.is_content_compliant is False
    assert "## Contents" in result.missing_sections
    assert "## Constraints (or ## Critical Constraints)" in result.missing_sections
    assert "## Quick start" in result.missing_sections
    assert "## Workflow" in result.missing_sections
    assert "## Verification" in result.missing_sections
    assert any("Available Commands" in legacy for legacy in result.legacy_sections)


def test_folder_structure_flags_loose_files_and_missing_evals(tmp_path: Path):
    skill = tmp_path / "bad-folder-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: bad-folder-skill\n"
        "description: Tests folder structure flaws.\n"
        "---\n\n"
        "# Bad Folder Skill\n\n"
        "## Contents\n\n"
        "- [Critical Constraints](#critical-constraints)\n"
        "- [Quick start](#quick-start)\n"
        "- [Workflow](#workflow)\n"
        "- [Verification](#verification)\n\n"
        "## Critical Constraints\n\n"
        "- Constraints.\n\n"
        "## Quick start\n\n"
        "echo test\n\n"
        "## Workflow\n\n"
        "1. Step.\n\n"
        "## Verification\n\n"
        "1. Verify.\n",
        encoding="utf-8"
    )
    # Loose file in root
    (skill / "acceptance-criteria.md").write_text("loose criteria")
    (skill / "scratch.py").write_text("print(1)")
    # Missing evals directory

    result = audit_template_compliance(skill)
    assert result.is_compliant is False
    assert result.is_folder_compliant is False
    assert any("Loose files" in issue for issue in result.folder_issues)
    assert any("Missing required evals" in issue for issue in result.folder_issues)
