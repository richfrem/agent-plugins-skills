"""Tests for interactive multiselect TUI in prune_installed_skills.py."""

import json
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

# Add plugins/plugin-manager/scripts to sys.path
plugin_scripts = Path(__file__).resolve().parent.parent / "scripts"
if str(plugin_scripts) not in sys.path:
    sys.path.insert(0, str(plugin_scripts))

from prune_installed_skills import (
    toggle_component_state,
    check_dependency_advisory,
    interactive_prune_tui,
    tui_process_key,
    TUIState,
    plan_pruning,
    execute_pruning,
    main,
)


def test_toggle_component_state():
    manifest = {
        "plugins": {
            "demo": {
                "skills": {"skill-1": True, "skill-2": False},
                "rules": {},
                "agents": {},
            }
        }
    }
    updated = toggle_component_state(manifest, "demo", "skills", "skill-1")
    assert updated["plugins"]["demo"]["skills"]["skill-1"] is False
    updated = toggle_component_state(manifest, "demo", "skills", "skill-2")
    assert updated["plugins"]["demo"]["skills"]["skill-2"] is True


def test_toggle_component_state_rule_and_agent_normalization():
    manifest = {
        "plugins": {
            "demo": {
                "skills": {},
                "rules": {"rule-a.md": True, "rule-b": True},
                "agents": {"agent-a.md": True, "agent-b": True},
            }
        }
    }
    toggle_component_state(manifest, "demo", "rules", "rule-a")
    assert manifest["plugins"]["demo"]["rules"]["rule-a.md"] is False

    toggle_component_state(manifest, "demo", "rules", "rule-b.md")
    assert manifest["plugins"]["demo"]["rules"]["rule-b"] is False

    toggle_component_state(manifest, "demo", "agents", "agent-a")
    assert manifest["plugins"]["demo"]["agents"]["agent-a.md"] is False

    toggle_component_state(manifest, "demo", "agents", "agent-b.md")
    assert manifest["plugins"]["demo"]["agents"]["agent-b"] is False


def test_check_dependency_advisory(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    skill_caller = skills_dir / "caller-skill"
    skill_caller.mkdir()
    (skill_caller / "SKILL.md").write_text(
        "---\nname: caller-skill\n---\nReferences .agent/rules/dep-rule.md, requires companion-skill, calls agent .agents/agents/dep-agent.md.",
        encoding="utf-8",
    )

    manifest = {
        "plugins": {
            "demo": {
                "skills": {"caller-skill": True, "companion-skill": True, "isolated-skill": True},
                "rules": {"dep-rule.md": True, "isolated-rule.md": True},
                "agents": {"dep-agent.md": True, "isolated-agent.md": True},
            }
        }
    }

    adv = check_dependency_advisory(root, manifest, "demo", "skills", "companion-skill")
    assert adv is not None
    assert "companion-skill" in adv
    assert "Companion skill" in adv

    adv_rule = check_dependency_advisory(root, manifest, "demo", "rules", "dep-rule.md")
    assert adv_rule is not None
    assert "dep-rule.md" in adv_rule
    assert "Rule" in adv_rule

    adv_rule_no_ext = check_dependency_advisory(root, manifest, "demo", "rules", "dep-rule")
    assert adv_rule_no_ext is not None
    assert "dep-rule" in adv_rule_no_ext

    adv_agent = check_dependency_advisory(root, manifest, "demo", "agents", "dep-agent.md")
    assert adv_agent is not None
    assert "dep-agent.md" in adv_agent
    assert "Agent" in adv_agent

    assert check_dependency_advisory(root, manifest, "demo", "skills", "isolated-skill") is None
    assert check_dependency_advisory(root, manifest, "demo", "rules", "isolated-rule.md") is None
    assert check_dependency_advisory(root, manifest, "demo", "agents", "isolated-agent.md") is None


def test_tui_navigation_and_paging(tmp_path: Path):
    root = tmp_path
    manifest = {
        "plugins": {
            "plugin-1": {
                "skills": {"skill-1": True, "skill-2": True},
                "rules": {},
                "agents": {},
            },
            "plugin-2": {
                "skills": {"skill-3": True},
                "rules": {"rule-3.md": True},
                "agents": {},
            },
        }
    }

    state = TUIState(manifest=manifest, root=root)
    assert state.current_plugin_name == "plugin-1"
    assert len(state.current_items) == 2
    assert state.cursor == 0

    tui_process_key("DOWN", state)
    assert state.cursor == 1

    tui_process_key("DOWN", state)
    assert state.cursor == 1

    tui_process_key("UP", state)
    assert state.cursor == 0

    tui_process_key("UP", state)
    assert state.cursor == 0

    tui_process_key("n", state)
    assert state.current_plugin_name == "plugin-2"
    assert state.cursor == 0
    assert len(state.current_items) == 2

    tui_process_key("n", state)
    assert state.current_plugin_name == "plugin-2"

    tui_process_key("p", state)
    assert state.current_plugin_name == "plugin-1"
    assert state.cursor == 0

    tui_process_key("p", state)
    assert state.current_plugin_name == "plugin-1"


def test_tui_space_toggle_and_dependency_warning(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    skill_caller = skills_dir / "caller-skill"
    skill_caller.mkdir()
    (skill_caller / "SKILL.md").write_text(
        "---\nname: caller-skill\n---\nRequires companion-skill.", encoding="utf-8"
    )

    manifest = {
        "plugins": {
            "demo": {
                "skills": {"caller-skill": True, "companion-skill": True},
                "rules": {},
                "agents": {},
            }
        }
    }

    state = TUIState(manifest=manifest, root=root)
    state.cursor = 1
    assert state.current_items[1]["name"] == "companion-skill"
    assert state.current_items[1]["retained"] is True

    tui_process_key(" ", state)
    assert state.current_items[1]["retained"] is False
    assert manifest["plugins"]["demo"]["skills"]["companion-skill"] is False
    assert state.advisory is not None
    assert "companion-skill" in state.advisory

    tui_process_key(" ", state)
    assert state.current_items[1]["retained"] is True
    assert manifest["plugins"]["demo"]["skills"]["companion-skill"] is True
    assert state.advisory is None


def test_interactive_prune_tui_full_flow(tmp_path: Path):
    root = tmp_path
    manifest = {
        "plugins": {
            "plugin-1": {
                "skills": {"skill-1": True, "skill-2": True},
                "rules": {},
                "agents": {},
            },
            "plugin-2": {
                "skills": {"skill-3": True},
                "rules": {},
                "agents": {},
            },
        }
    }

    key_sequence = iter([" ", "n", " ", "\r"])

    updated_manifest = interactive_prune_tui(
        root=root, manifest=manifest, key_provider=lambda: next(key_sequence)
    )

    assert updated_manifest["plugins"]["plugin-1"]["skills"]["skill-1"] is False
    assert updated_manifest["plugins"]["plugin-1"]["skills"]["skill-2"] is True
    assert updated_manifest["plugins"]["plugin-2"]["skills"]["skill-3"] is False


def test_cli_summary_agent_advisory(tmp_path: Path, monkeypatch, capsys):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    agents_dir = root / ".agents" / "agents"
    skills_dir.mkdir(parents=True)
    agents_dir.mkdir(parents=True)

    caller_skill = skills_dir / "caller-skill"
    caller_skill.mkdir()
    (caller_skill / "SKILL.md").write_text(
        "---\nname: caller-skill\n---\nCalls agent agent-worker.md.", encoding="utf-8"
    )

    agent_file = agents_dir / "agent-worker.md"
    agent_file.write_text("agent content", encoding="utf-8")

    manifest_file = root / "plugin-retention.json"
    manifest_data = {
        "version": 1,
        "protected_defaults": [],
        "plugins": {
            "demo": {
                "skills": {"caller-skill": True},
                "rules": {},
                "agents": {"agent-worker.md": False},
            }
        },
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prune_installed_skills.py",
            "--manifest",
            str(manifest_file),
            "--root",
            str(root),
            "--dry-run",
        ],
    )
    main()
    captured = capsys.readouterr().out
    assert "[ADVISORY] Agent 'agent-worker.md' is referenced by retained skill." in captured


def test_rule_extension_normalization_in_plan_pruning(tmp_path: Path):
    root = tmp_path
    rules_dir = root / ".agent" / "rules"
    rules_dir.mkdir(parents=True)

    rule_file = rules_dir / "my-rule.md"
    rule_file.write_text("rule content", encoding="utf-8")

    manifest = {
        "protected_defaults": [],
        "plugins": {
            "demo": {
                "skills": {},
                "rules": {"my-rule": False},
                "agents": {},
            }
        },
    }

    plan = plan_pruning(root, manifest)
    assert rule_file in plan["rules"]


def test_execute_pruning_exception_does_not_increment(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    skill_to_prune = skills_dir / "fail-skill"
    skill_to_prune.mkdir()

    removals = {"skills": [skill_to_prune], "rules": [], "agents": []}

    with patch("shutil.rmtree", side_effect=PermissionError("Permission denied")):
        deleted_count = execute_pruning(removals, root=root, dry_run=False)
        assert deleted_count == 0
        assert skill_to_prune.exists()


def test_tui_protected_defaults_cannot_untoggle(tmp_path: Path):
    root = tmp_path
    manifest = {
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "demo": {
                "skills": {"plugin-installer": True, "custom-skill": True},
                "rules": {},
                "agents": {},
            }
        },
    }

    state = TUIState(manifest=manifest, root=root)
    installer_idx = next(
        i for i, item in enumerate(state.current_items) if item["name"] == "plugin-installer"
    )
    state.cursor = installer_idx
    assert state.current_items[installer_idx]["name"] == "plugin-installer"
    assert state.current_items[installer_idx]["protected"] is True

    # Press Space
    tui_process_key(" ", state)
    # Remains True
    assert manifest["plugins"]["demo"]["skills"]["plugin-installer"] is True
    assert state.advisory is not None
    assert "protected" in state.advisory.lower()


def test_tui_toggle_all_and_search(tmp_path: Path):
    root = tmp_path
    manifest = {
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "demo": {
                "skills": {
                    "plugin-installer": True,
                    "skill-alpha": True,
                    "skill-beta": True,
                },
                "rules": {},
                "agents": {},
            }
        },
    }

    state = TUIState(manifest=manifest, root=root)
    # Toggle all ('a') -> unselect all non-protected
    tui_process_key("a", state)
    assert manifest["plugins"]["demo"]["skills"]["plugin-installer"] is True
    assert manifest["plugins"]["demo"]["skills"]["skill-alpha"] is False
    assert manifest["plugins"]["demo"]["skills"]["skill-beta"] is False

    # Toggle all again -> re-select all
    tui_process_key("a", state)
    assert manifest["plugins"]["demo"]["skills"]["skill-alpha"] is True
    assert manifest["plugins"]["demo"]["skills"]["skill-beta"] is True

    # Test search
    tui_process_key("/", state)
    tui_process_key("a", state)
    tui_process_key("l", state)
    tui_process_key("p", state)
    tui_process_key("h", state)
    tui_process_key("a", state)
    assert state.search == "alpha"
    assert len(state.current_items) == 1
    assert state.current_items[0]["name"] == "skill-alpha"

    # Backspace
    tui_process_key("\x7f", state)
    assert state.search == "alph"

    # ESC clears search
    tui_process_key("ESC", state)
    assert state.search == ""
    assert len(state.current_items) == 3


def test_cli_interactive_flag(tmp_path: Path, monkeypatch, capsys):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)
    unwanted = skills_dir / "unwanted-skill"
    unwanted.mkdir()

    manifest_file = root / "plugin-retention.json"
    manifest_data = {
        "version": 1,
        "protected_defaults": [],
        "plugins": {
            "demo": {
                "skills": {"unwanted-skill": True},
                "rules": {},
                "agents": {},
            }
        },
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # Mock interactive_prune_tui to untoggle unwanted-skill
    def mock_tui(r, m, key_provider=None):
        m["plugins"]["demo"]["skills"]["unwanted-skill"] = False
        return m

    monkeypatch.setattr("prune_installed_skills.interactive_prune_tui", mock_tui)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prune_installed_skills.py",
            "--manifest",
            str(manifest_file),
            "--root",
            str(root),
            "--interactive",
            "--dry-run",
        ],
    )
    exit_code = main()
    assert exit_code == 0
    # Verify manifest was updated on disk
    updated = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert updated["plugins"]["demo"]["skills"]["unwanted-skill"] is False


def test_render_tui_page_last_line_count(tmp_path: Path):
    from prune_installed_skills import _render_tui_page, _clear_lines

    manifest = {
        "plugins": {
            "demo": {
                "skills": {"skill-1": True},
                "rules": {},
                "agents": {},
            }
        }
    }
    state = TUIState(manifest=manifest, root=tmp_path)
    # First render (last_line_count = 0)
    lines_count_1 = _render_tui_page(state, last_line_count=0)
    assert lines_count_1 > 0

    # Second render passing last_line_count
    with patch("prune_installed_skills._clear_lines") as mock_clear:
        lines_count_2 = _render_tui_page(state, last_line_count=lines_count_1)
        mock_clear.assert_called_once_with(lines_count_1)
        assert lines_count_2 == lines_count_1


def test_read_key_standalone_esc(monkeypatch):
    import prune_installed_skills
    from prune_installed_skills import _read_key

    if sys.platform == "win32":
        monkeypatch.setattr("msvcrt.getwch", lambda: "\x1b")
        assert _read_key() == "ESC"
    else:
        # Mock sys.stdin.fileno and termios to test select escape logic
        monkeypatch.setattr(sys.stdin, "fileno", lambda: 0)
        monkeypatch.setattr("tty.setraw", lambda fd: None)
        monkeypatch.setattr("termios.tcgetattr", lambda fd: [])
        monkeypatch.setattr("termios.tcsetattr", lambda fd, when, old: None)
        monkeypatch.setattr("os.read", lambda fd, n: b"\x1b")
        assert _read_key() == "ESC"


def test_cli_interactive_missing_manifest_auto_seeds(tmp_path: Path, monkeypatch, capsys):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    ownership_dir = root / ".agents" / "ownership"
    skills_dir.mkdir(parents=True)
    ownership_dir.mkdir(parents=True)

    (skills_dir / "my-skill").mkdir()
    own_file = ownership_dir / "demo-plugin.json"
    own_file.write_text(
        json.dumps({
            "plugin": "demo-plugin",
            "artifacts": [".agents/skills/my-skill"],
        }),
        encoding="utf-8",
    )

    manifest_file = root / "plugin-retention.json"
    assert not manifest_file.exists()

    def mock_tui(r, m, key_provider=None):
        assert "demo-plugin" in m.get("plugins", {})
        assert "my-skill" in m["plugins"]["demo-plugin"]["skills"]
        return m

    monkeypatch.setattr("prune_installed_skills.interactive_prune_tui", mock_tui)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prune_installed_skills.py",
            "--manifest",
            str(manifest_file),
            "--root",
            str(root),
            "--interactive",
            "--dry-run",
        ],
    )
    exit_code = main()
    assert exit_code == 0
    assert manifest_file.exists()
    saved = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert "demo-plugin" in saved["plugins"]
    assert saved["plugins"]["demo-plugin"]["skills"]["my-skill"] is True


def test_read_key_arrow_sequences(monkeypatch):
    from prune_installed_skills import _read_key

    if sys.platform != "win32":
        monkeypatch.setattr(sys.stdin, "fileno", lambda: 0)
        monkeypatch.setattr("tty.setraw", lambda fd: None)
        monkeypatch.setattr("termios.tcgetattr", lambda fd: [])
        monkeypatch.setattr("termios.tcsetattr", lambda fd, when, old: None)

        monkeypatch.setattr("os.read", lambda fd, n: b"\x1b[A")
        assert _read_key() == "UP"

        monkeypatch.setattr("os.read", lambda fd, n: b"\x1bOA")
        assert _read_key() == "UP"

        monkeypatch.setattr("os.read", lambda fd, n: b"\x1b[B")
        assert _read_key() == "DOWN"

        monkeypatch.setattr("os.read", lambda fd, n: b"\x1bOB")
        assert _read_key() == "DOWN"


def test_tui_process_key_jk_navigation():
    manifest = {
        "plugins": {
            "p1": {"skills": {"s1": True, "s2": True, "s3": True}, "rules": {}, "agents": {}}
        }
    }
    state = TUIState(manifest=manifest, root=Path("."))
    assert state.cursor == 0
    tui_process_key("j", state)
    assert state.cursor == 1
    tui_process_key("j", state)
    assert state.cursor == 2
    tui_process_key("k", state)
    assert state.cursor == 1
    tui_process_key("k", state)
    assert state.cursor == 0
