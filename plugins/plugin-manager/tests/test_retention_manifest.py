"""Tests for retention manifest template and data model helpers."""

import json
import sys
from pathlib import Path
import pytest

# Add plugins/plugin-manager/scripts to sys.path so retention_manifest can be imported cleanly
plugin_scripts = Path(__file__).resolve().parent.parent / "scripts"
if str(plugin_scripts) not in sys.path:
    sys.path.insert(0, str(plugin_scripts))

from retention_manifest import (
    load_manifest,
    save_manifest,
    merge_installed_components,
    get_component_states,
)


def test_load_and_merge_manifest(tmp_path: Path):
    template_path = tmp_path / "template.json"
    template_data = {
        "version": 1,
        "updated_at": "2026-09-11T00:00:00Z",
        "protected_defaults": ["plugin-installer", "plugin-remover", "plugin-syncer", "plugin-pruner"],
        "plugins": {}
    }
    template_path.write_text(json.dumps(template_data), encoding="utf-8")

    manifest = load_manifest(template_path)
    assert manifest["version"] == 1

    artifacts = [
        ".agents/skills/os-architect",
        ".agents/skills/evo-smoketest",
        ".agent/rules/self-evolution-policy.md",
        ".agents/agents/agent-agentic-os-os-architect-agent.md"
    ]
    updated = merge_installed_components(manifest, "agent-agentic-os", artifacts)
    assert "agent-agentic-os" in updated["plugins"]
    assert updated["plugins"]["agent-agentic-os"]["skills"]["os-architect"] is True
    assert updated["plugins"]["agent-agentic-os"]["skills"]["evo-smoketest"] is True
    assert updated["plugins"]["agent-agentic-os"]["rules"]["self-evolution-policy.md"] is True
    assert updated["plugins"]["agent-agentic-os"]["agents"]["agent-agentic-os-os-architect-agent.md"] is True


def test_save_and_reload_manifest(tmp_path: Path):
    manifest_path = tmp_path / "plugin-retention.json"
    data = {
        "version": 1,
        "updated_at": "2026-09-11T00:00:00Z",
        "protected_defaults": ["plugin-installer", "plugin-remover"],
        "plugins": {
            "test-plugin": {
                "skills": {"test-skill": True},
                "rules": {"test-rule.md": True},
                "agents": {}
            }
        }
    }
    save_manifest(manifest_path, data)
    assert manifest_path.exists()

    reloaded = load_manifest(manifest_path)
    assert reloaded == data


def test_get_component_states():
    manifest = {
        "version": 1,
        "plugins": {
            "plugin-a": {
                "skills": {"skill-1": True, "skill-2": False},
                "rules": {"rule-a.md": True},
                "agents": {"agent-a.md": True}
            },
            "plugin-b": {
                "skills": {"skill-3": True},
                "rules": {"rule-b.md": False},
                "agents": {"agent-b.md": False}
            }
        }
    }
    skills, rules, agents = get_component_states(manifest)
    assert skills == {"skill-1": True, "skill-2": False, "skill-3": True}
    assert rules == {"rule-a.md": True, "rule-b.md": False}
    assert agents == {"agent-a.md": True, "agent-b.md": False}


def test_merge_preserves_unrelated_components():
    manifest = {
        "version": 1,
        "plugins": {
            "plugin-existing": {
                "skills": {"existing-skill": True},
                "rules": {},
                "agents": {}
            },
            "agent-agentic-os": {
                "skills": {"pruned-skill": False},
                "rules": {},
                "agents": {}
            }
        }
    }
    artifacts = [".agents/skills/new-skill"]
    updated = merge_installed_components(manifest, "agent-agentic-os", artifacts)
    # Existing plugin is untouched
    assert updated["plugins"]["plugin-existing"]["skills"]["existing-skill"] is True
    # Pruned skill remains False
    assert updated["plugins"]["agent-agentic-os"]["skills"]["pruned-skill"] is False
    # Newly installed skill is True
    assert updated["plugins"]["agent-agentic-os"]["skills"]["new-skill"] is True


def test_merge_ignores_non_component_artifacts():
    manifest = {"version": 1, "plugins": {}}
    artifacts = [
        ".agents/hooks/agent-agentic-os-hooks.json",
        ".agents/commands/some-command.md",
        "random/unrelated/path.txt"
    ]
    updated = merge_installed_components(manifest, "agent-agentic-os", artifacts)
    assert updated["plugins"]["agent-agentic-os"]["skills"] == {}
    assert updated["plugins"]["agent-agentic-os"]["rules"] == {}
    assert updated["plugins"]["agent-agentic-os"]["agents"] == {}


def test_canonical_template_file():
    template_path = Path(__file__).resolve().parent.parent / "assets" / "templates" / "plugin-retention.template.json"
    assert template_path.exists(), "Template file must exist"
    data = load_manifest(template_path)
    assert data["version"] == 1
    assert "protected_defaults" in data
    assert isinstance(data["protected_defaults"], list)
    assert "plugins" in data
    assert isinstance(data["plugins"], dict)
