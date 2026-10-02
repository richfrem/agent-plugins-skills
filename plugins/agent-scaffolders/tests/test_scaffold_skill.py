"""Real CLI contracts for skill generation and portable template resolution.

Purpose: Verify preflight failures, variants and hub-owned output.
Key Input Dependencies: scripts/scaffold.py and assets/templates.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN / "scripts/scaffold.py"


def invoke(target, *extra, script=SCRIPT, name="sample-skill", description="Processes sample data. Use when checking samples."):
    """Execute the public CLI against a real temporary output tree."""
    return subprocess.run([sys.executable, str(script), "--type", "skill", "--name", name,
                           "--path", str(target), "--desc", description, *extra],
                          capture_output=True, text=True)


def test_instructional_has_valid_metadata_and_no_fake_execution(tmp_path):
    """An instructional skill has useful routing without mandatory Python."""
    result = invoke(tmp_path / "plugin/skills")
    assert result.returncode == 0, result.stderr
    skill = tmp_path / "plugin/skills/sample-skill"
    content = (skill / "SKILL.md").read_text()
    assert "name: sample-skill" in content
    assert "## Contents" in content
    assert "## Verification" in content
    assert "scripts/execute.py" not in content
    assert not (skill / "scripts/execute.py").exists()
    assert not (skill / "test").exists()


def test_invalid_name_fails_without_output(tmp_path):
    """Invalid slugs fail nonzero before creating the output directory."""
    result = invoke(tmp_path / "output", name="BAD NAME")
    assert result.returncode != 0
    assert not (tmp_path / "output").exists()


def test_missing_templates_fail_before_output(tmp_path):
    """Installed script cannot silently use source templates or placeholders."""
    isolated = tmp_path / "isolated/scripts/scaffold.py"
    isolated.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, isolated)
    result = invoke(tmp_path / "output", script=isolated)
    assert result.returncode != 0
    assert "template" in result.stderr.lower()
    assert not (tmp_path / "output").exists()


def test_description_is_safely_quoted(tmp_path):
    """YAML punctuation and format braces survive rendering as data."""
    description = 'Processes data: {rows} # safely "quoted".'
    result = invoke(tmp_path / "plugin/skills", description=description)
    assert result.returncode == 0, result.stderr
    content = (tmp_path / "plugin/skills/sample-skill/SKILL.md").read_text()
    scalar = next(line.split(": ", 1)[1] for line in content.splitlines() if line.startswith("description: "))
    assert json.loads(scalar) == description


def test_executable_has_hub_script_and_proposed_link(tmp_path):
    """Generation proposes managed links without creating spoke copies."""
    plugin = tmp_path / "plugin"
    result = invoke(plugin / "skills", "--variant", "executable", "--plugin-root", str(plugin), "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "pending_links"
    assert (plugin / "scripts/sample_skill.py").is_file()
    assert not (plugin / "skills/sample-skill/scripts/sample_skill.py").exists()
    assert any(link["dst"].endswith("scripts/sample_skill.py") for link in report["links"])


def test_collision_does_not_overwrite(tmp_path):
    """Existing content remains untouched on a repeated generation request."""
    target = tmp_path / "plugin/skills/sample-skill"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("Keep this content")
    result = invoke(target.parent)
    assert result.returncode != 0
    assert (target / "SKILL.md").read_text() == "Keep this content"
