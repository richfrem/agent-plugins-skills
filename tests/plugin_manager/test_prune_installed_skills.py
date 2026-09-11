"""Tests for core pruning script and dependency scanner."""

import json
import sys
from pathlib import Path
import pytest

# Add plugins/plugin-manager/scripts to sys.path so retention_manifest and
# prune_installed_skills can be imported cleanly despite the hyphen in plugin-manager
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
plugin_scripts = REPO_ROOT / "plugins" / "plugin-manager" / "scripts"
if str(plugin_scripts) not in sys.path:
    sys.path.insert(0, str(plugin_scripts))

from prune_installed_skills import (
    scan_dependencies,
    plan_pruning,
    execute_pruning,
    CONFIRM_TOKEN,
    main,
)


def test_scan_dependencies(tmp_path: Path):
    skills_dir = tmp_path / ".agents" / "skills"
    skill_a = skills_dir / "skill-a"
    skill_a.mkdir(parents=True)
    (skill_a / "SKILL.md").write_text(
        "---\nname: skill-a\n---\nSee .agent/rules/test-rule.md and requires skill-b.",
        encoding="utf-8"
    )

    deps = scan_dependencies(skills_dir, {"skill-a"})
    assert "test-rule.md" in deps["rules"]
    assert "skill-b" in deps["skills"]


def test_scan_dependencies_empty_and_no_deps(tmp_path: Path):
    skills_dir = tmp_path / ".agents" / "skills"
    skill_c = skills_dir / "skill-c"
    skill_c.mkdir(parents=True)
    (skill_c / "SKILL.md").write_text(
        "---\nname: skill-c\n---\nSelf contained skill with no dependencies.",
        encoding="utf-8"
    )

    deps = scan_dependencies(skills_dir, {"skill-c"})
    assert deps["rules"] == set()
    assert deps["skills"] == set()

    # Non-existent skill
    deps_non_existent = scan_dependencies(skills_dir, {"non-existent"})
    assert deps_non_existent["rules"] == set()
    assert deps_non_existent["skills"] == set()


def test_scan_dependencies_multiple_patterns(tmp_path: Path):
    skills_dir = tmp_path / ".agents" / "skills"
    skill_d = skills_dir / "skill-d"
    skill_d.mkdir(parents=True)
    (skill_d / "SKILL.md").write_text(
        """---
name: skill-d
---
Uses superpowers:brainstorming and delegates to skill companion-worker.
References rule 'plugin-architecture-policy.md' and rules/audit-rule.md.
Also invokes agent .agents/agents/helper-agent.md.
""",
        encoding="utf-8"
    )

    deps = scan_dependencies(skills_dir, {"skill-d"})
    assert "brainstorming" in deps["skills"]
    assert "companion-worker" in deps["skills"]
    assert "plugin-architecture-policy.md" in deps["rules"]
    assert "audit-rule.md" in deps["rules"]
    assert "helper-agent.md" in deps["agents"]


def test_plan_pruning_protects_defaults(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "plugin-installer").mkdir()
    (skills_dir / "unwanted-skill").mkdir()

    manifest = {
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "dummy": {
                "skills": {"plugin-installer": True, "unwanted-skill": False},
                "rules": {},
                "agents": {}
            }
        }
    }
    plan = plan_pruning(root, manifest)
    removable_names = [p.name for p in plan["skills"]]
    assert "unwanted-skill" in removable_names
    assert "plugin-installer" not in removable_names


def test_plan_pruning_handles_skills_rules_agents(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    rules_dir = root / ".agent" / "rules"
    agents_dir = root / ".agents" / "agents"
    skills_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)
    agents_dir.mkdir(parents=True)

    (skills_dir / "prune-skill").mkdir()
    (skills_dir / "keep-skill").mkdir()
    (rules_dir / "prune-rule.md").write_text("rule", encoding="utf-8")
    (rules_dir / "keep-rule.md").write_text("rule", encoding="utf-8")
    (agents_dir / "prune-agent.md").write_text("agent", encoding="utf-8")
    (agents_dir / "keep-agent.md").write_text("agent", encoding="utf-8")

    manifest = {
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "test-plugin": {
                "skills": {"prune-skill": False, "keep-skill": True},
                "rules": {"prune-rule.md": False, "keep-rule.md": True},
                "agents": {"prune-agent.md": False, "keep-agent.md": True}
            }
        }
    }

    plan = plan_pruning(root, manifest)
    skill_names = [p.name for p in plan["skills"]]
    rule_names = [p.name for p in plan["rules"]]
    agent_names = [p.name for p in plan["agents"]]

    assert "prune-skill" in skill_names
    assert "keep-skill" not in skill_names
    assert "prune-rule.md" in rule_names
    assert "keep-rule.md" not in rule_names
    assert "prune-agent.md" in agent_names
    assert "keep-agent.md" not in agent_names


def test_execute_pruning_physical_deletion(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    rules_dir = root / ".agent" / "rules"
    skills_dir.mkdir(parents=True)
    rules_dir.mkdir(parents=True)

    skill_to_prune = skills_dir / "prune-skill"
    skill_to_prune.mkdir()
    (skill_to_prune / "SKILL.md").write_text("skill", encoding="utf-8")

    rule_to_prune = rules_dir / "prune-rule.md"
    rule_to_prune.write_text("rule", encoding="utf-8")

    # Set up skills-lock.json
    lock_file = root / "skills-lock.json"
    lock_data = {
        "version": 1,
        "skills": {
            "prune-skill": {"source": "local"},
            "keep-skill": {"source": "local"}
        }
    }
    lock_file.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")

    removals = {
        "skills": [skill_to_prune],
        "rules": [rule_to_prune],
        "agents": []
    }

    deleted_count = execute_pruning(removals, root=root, dry_run=False)
    assert deleted_count == 2
    assert not skill_to_prune.exists()
    assert not rule_to_prune.exists()

    # Verify skills-lock.json updated
    updated_lock = json.loads(lock_file.read_text(encoding="utf-8"))
    assert "prune-skill" not in updated_lock["skills"]
    assert "keep-skill" in updated_lock["skills"]


def test_execute_pruning_dry_run(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    skill_to_prune = skills_dir / "prune-skill"
    skill_to_prune.mkdir()

    removals = {
        "skills": [skill_to_prune],
        "rules": [],
        "agents": []
    }

    deleted_count = execute_pruning(removals, root=root, dry_run=True)
    assert deleted_count == 1
    assert skill_to_prune.exists()  # Dry run leaves file intact


def test_confirm_token_constant():
    assert CONFIRM_TOKEN == "PRUNE-INSTALLED-SKILLS"


def test_cli_execution_with_token(tmp_path: Path, monkeypatch, capsys):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)
    unwanted = skills_dir / "unwanted-skill"
    unwanted.mkdir()

    manifest_file = root / "plugin-retention.json"
    manifest_data = {
        "version": 1,
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "demo": {
                "skills": {"unwanted-skill": False},
                "rules": {},
                "agents": {}
            }
        }
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # CLI call without confirm token when executing should fail / refuse
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prune_installed_skills.py",
            "--manifest",
            str(manifest_file),
            "--root",
            str(root),
            "--execute",
        ],
    )
    # Mock sys.stdin.isatty to False to simulate non-interactive CLI failure
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    exit_code = main()
    assert exit_code != 0
    assert unwanted.exists()

    # CLI call with confirm token should succeed
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prune_installed_skills.py",
            "--manifest",
            str(manifest_file),
            "--root",
            str(root),
            "--execute",
            "--confirm-token",
            CONFIRM_TOKEN,
        ],
    )
    exit_code = main()
    assert exit_code == 0
    assert not unwanted.exists()
