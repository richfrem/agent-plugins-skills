"""Source and installed contracts for the consolidated CLI skill navigation.

Purpose: Verify portable resources, early navigation and actual documented commands.
Key Input Dependencies: CLI skills, their managed resources and the authoring auditor.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
AUDITOR = PLUGIN.parent / "agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py"
SKILLS = ("cli-agent",)
SYNC_SCRIPT = PLUGIN / "skills/cli-agent/scripts/sync_cheapest_models.py"


@pytest.mark.parametrize("name", SKILLS)
def test_skill_navigation_and_installation(name, tmp_path):
    """Every resource is managed in source and independently usable after copying."""
    source = PLUGIN / "skills" / name
    text = (source / "SKILL.md").read_text()
    assert len(text.splitlines()) <= 100
    for heading in ("## Contents", "## Constraints", "## Quick Start", "## Workflow", "## Verification"):
        assert heading.lower() in text.lower()
    assert "plugins/cli-agents/" not in text
    assert "../../scripts/" not in text and "../../references/" not in text
    result = subprocess.run([sys.executable, str(AUDITOR), str(source), "--json"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["findings"] == []
    installed = tmp_path / name
    shutil.copytree(source, installed, symlinks=False)
    result = subprocess.run([sys.executable, str(AUDITOR), str(installed), "--mode", "installed", "--json"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["findings"] == []
    # Personas are the plugin's host sub-agents, not files bundled in the skill.
    assert not (installed / "agents").exists()
    persona = source.parents[1] / "agents" / "security-auditor.md"
    assert persona.is_file()
    fake = tmp_path / "fixture-backend"
    fake.write_text(f'#!{sys.executable}\nimport sys\nif "--version" in sys.argv: print("fixture 1");sys.exit(0)\nprint("RESULT_OK")\n')
    fake.chmod(0o755)
    input_path, output_path = tmp_path / "input.md", tmp_path / "output.md"
    input_path.write_text("Bounded source for fixture review.")
    result = subprocess.run([sys.executable, "scripts/run_agent.py", str(persona), str(input_path), str(output_path), "Review supplied source.", "--cli", "claude", "--model", "fixture-model", "--isolated", "--require-input", "--executable", str(fake)], cwd=installed, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RESULT_OK" in output_path.read_text()


def test_sync_requires_explicit_repository_in_installed_mode(tmp_path):
    """Installed sync must not infer or write a repository from its own ancestors."""
    script = tmp_path / "scripts/sync_cheapest_models.py"
    script.parent.mkdir()
    shutil.copy2(SYNC_SCRIPT, script)
    result = subprocess.run([sys.executable, str(script), "--dry-run"], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 2
    assert "--repository" in result.stderr


def test_sync_explicit_repository_uses_supplied_master(tmp_path):
    """Real I/O verifies the selected target rather than the source checkout."""
    repo = tmp_path / "target"
    master = repo / "plugins/agent-orchestration/skills/cli-agent/references"
    copy = repo / "plugins/consumer/references"
    master.mkdir(parents=True)
    copy.mkdir(parents=True)
    for filename in ("cheapest_models.json", "cheapest_models.md"):
        (master / filename).write_text("selected master")
        (copy / filename).write_text("old copy")
    result = subprocess.run([sys.executable, str(SYNC_SCRIPT), "--repository", str(repo)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (copy / "cheapest_models.json").read_text() == "selected master"
