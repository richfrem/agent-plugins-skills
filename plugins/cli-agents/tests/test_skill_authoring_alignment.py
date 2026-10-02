"""Source and installed contracts for the six CLI skill navigation updates.

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
AUDITOR = PLUGIN.parent / "agent-scaffolders/scripts/audit_skill.py"
SKILLS = ("claude-cli-agent", "agy-cli-agent", "codex-cli-agent",
          "copilot-cli-agent", "update-cli-models", "project-setup")


@pytest.mark.parametrize("name", SKILLS)
def test_skill_navigation_and_installation(name, tmp_path):
    """Every resource is managed in source and independently usable after copying."""
    source = PLUGIN / "skills" / name
    text = (source / "SKILL.md").read_text()
    assert len(text.splitlines()) <= 80
    for heading in ("## Contents", "## Constraints", "## Quick start", "## Workflow", "## Verification"):
        assert heading in text
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
    if name.endswith("cli-agent"):
        for persona in ("architect-review.md", "security-auditor.md", "refactor-expert.md"):
            assert (installed / "agents" / persona).is_file()
        backend = name.removesuffix("-cli-agent")
        fake = tmp_path / "fixture-backend"
        fake.write_text(f'#!{sys.executable}\nimport sys\nif "--version" in sys.argv: print("fixture 1");sys.exit(0)\nprint("RESULT_OK")\n')
        fake.chmod(0o755)
        input_path, output_path = tmp_path / "input.md", tmp_path / "output.md"
        input_path.write_text("Bounded source for fixture review.")
        result = subprocess.run([sys.executable, "scripts/run_agent.py", "agents/security-auditor.md", str(input_path), str(output_path), "Review supplied source.", "--cli", backend, "--model", "fixture-model", "--isolated", "--require-input", "--executable", str(fake)], cwd=installed, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "RESULT_OK" in output_path.read_text()
    elif name == "update-cli-models":
        result = subprocess.run([sys.executable, "scripts/sync_cheapest_models.py", "--help"], cwd=installed, capture_output=True, text=True)
        assert result.returncode == 0
        assert "--repository" in result.stdout
    else:
        spec = importlib.util.spec_from_file_location("installed_profile_contract", installed / "scripts/capability_profile.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        assert module.load_profile(tmp_path / "missing.json").status.value == "unconfigured"


def test_sync_requires_explicit_repository_in_installed_mode(tmp_path):
    """Installed sync must not infer or write a repository from its own ancestors."""
    script = tmp_path / "scripts/sync_cheapest_models.py"
    script.parent.mkdir()
    shutil.copy2(PLUGIN / "scripts/sync_cheapest_models.py", script)
    result = subprocess.run([sys.executable, str(script), "--dry-run"], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 2
    assert "--repository" in result.stderr


def test_sync_explicit_repository_uses_supplied_master(tmp_path):
    """Real I/O verifies the selected target rather than the source checkout."""
    repo = tmp_path / "target"
    master = repo / "plugins/cli-agents/references"
    copy = repo / "plugins/consumer/references"
    master.mkdir(parents=True)
    copy.mkdir(parents=True)
    for filename in ("cheapest_models.json", "cheapest_models.md"):
        (master / filename).write_text("selected master")
        (copy / filename).write_text("old copy")
    result = subprocess.run([sys.executable, str(PLUGIN / "scripts/sync_cheapest_models.py"), "--repository", str(repo)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (copy / "cheapest_models.json").read_text() == "selected master"
