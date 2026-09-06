"""
test_init_agentic_os_scaffolding.py — Contract & Unit Tests for os-init Scaffolding Parity
========================================================================================

Purpose:
    Verifies that init_agentic_os.py (both fresh setup and --retrofit) correctly:
    1. Scaffolds repository-level substrates (control_plane.db, hooks.json, evolution guard, 3-layer memory)
    2. Identifies and scaffolds missing plugin-level evolution substrates (references/evolution-log.md)
       when local plugins exist under plugins/
    3. Directs the user/agent to run os-health-check in print_next_steps()

Key Input Dependencies:
    - plugins/agent-agentic-os/scripts/init_agentic_os.py
"""

import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INIT_SCRIPT = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts" / "init_agentic_os.py"


@pytest.fixture
def target_repo(tmp_path):
    """Creates a throwaway repository directory for testing os-init."""
    repo = tmp_path / "test_project"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    # create dummy README to allow commit
    (repo / "README.md").write_text("# Test Project\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)
    return repo


def test_retrofit_scaffolds_plugin_evolution_logs_when_plugins_exist(target_repo):
    """When plugins/ exists, --retrofit must ensure each plugin has references/evolution-log.md."""
    # Create two sample plugins
    p1 = target_repo / "plugins" / "sample-plugin-a"
    (p1 / "skills" / "skill-a").mkdir(parents=True)
    (p1 / "skills" / "skill-a" / "SKILL.md").write_text("---\nname: skill-a\n---\n", encoding="utf-8")

    p2 = target_repo / "plugins" / "sample-plugin-b"
    (p2 / "references").mkdir(parents=True)
    existing_log = p2 / "references" / "evolution-log.md"
    existing_log.write_text("# Existing Log\n", encoding="utf-8")

    # Run init_agentic_os.py --target <target_repo> --retrofit
    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Retrofit failed with stdout:\n{res.stdout}\nstderr:\n{res.stderr}"

    # Verify plugin A received references/evolution-log.md
    p1_log = p1 / "references" / "evolution-log.md"
    assert p1_log.exists(), "sample-plugin-a should have references/evolution-log.md scaffolded"
    assert "sample-plugin-a" in p1_log.read_text(encoding="utf-8")

    # Verify plugin B's existing log was preserved (not clobbered)
    assert existing_log.read_text(encoding="utf-8") == "# Existing Log\n"


def test_next_steps_directs_to_os_health_check(target_repo):
    """Completion output of init_agentic_os.py must direct agent to run os-health-check."""
    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "os-health-check" in res.stdout, "Completion output must direct user/agent to run os-health-check"


def test_scaffolds_github_ci_evolution_workflow(target_repo):
    """Both fresh setup and retrofit must scaffold .github/workflows/verify-evolution-integrity.yml."""
    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    ci_workflow = target_repo / ".github" / "workflows" / "verify-evolution-integrity.yml"
    assert ci_workflow.exists(), "CI workflow verify-evolution-integrity.yml must be scaffolded"
    assert "Verify Evolution & Map Debt Compliance" in ci_workflow.read_text(encoding="utf-8")



def test_retrofit_enriches_claude_md_with_phase0_and_control_plane(target_repo):
    """--retrofit must enrich CLAUDE.md with Phase 0 intake rule and control plane instructions."""
    # Seed a basic CLAUDE.md
    claude_md = target_repo / "CLAUDE.md"
    claude_md.write_text("# Project Instructions\n\n## Overview\nSome custom domain context.\n", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    content = claude_md.read_text(encoding="utf-8")
    assert "Phase 0 Intake & Socratic Gate" in content, "CLAUDE.md must be enriched with Phase 0 Intake Gate"
    assert "interview-spec" in content, "CLAUDE.md must reference interview-spec"
    assert "Some custom domain context." in content, "Original project context must be preserved"


def test_scaffolds_plugin_config_with_contribution_mode(target_repo):
    """init_agentic_os.py must scaffold context/plugin-config.json with selected mode."""
    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit", "--contribution-mode", "local-patch-and-issue"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    config_file = target_repo / "context" / "plugin-config.json"
    assert config_file.exists(), "context/plugin-config.json must be scaffolded"
    import json
    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data.get("contribution_mode") == "local-patch-and-issue"
    assert "https://github.com/richfrem/agent-plugins-skills" in data.get("upstream_repo", "")


def test_notifies_consuming_agent_of_backup_files(target_repo):
    """When backup files (.bak) are created during --force or --retrofit, print_next_steps must warn agent to review before deleting."""
    # Create an initial CLAUDE.md with standard Overview section
    (target_repo / "CLAUDE.md").write_text("# Initial CLAUDE.md\n\n## Overview\nTest project overview.\n", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--target", str(target_repo), "--retrofit"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "ATTENTION: Temporary Backup Files Created (.bak)" in res.stdout
    assert "Consuming Agent Directive for Backup Cleanup" in res.stdout
    assert "DO NOT blindly delete these .bak files" in res.stdout

