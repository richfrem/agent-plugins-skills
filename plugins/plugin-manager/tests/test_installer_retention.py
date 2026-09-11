import sys
import json
from pathlib import Path

# Add scripts dir to path for imports
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import plugin_installer
import plugin_add
from retention_manifest import load_manifest


def test_installer_filters_skills_and_seeds_retention(tmp_path: Path, monkeypatch):
    root = tmp_path
    plugin_dir = root / "plugins" / "sample-plugin"
    skills_dir = plugin_dir / "skills"
    (skills_dir / "skill-a").mkdir(parents=True)
    (skills_dir / "skill-a" / "SKILL.md").write_text("---\nname: skill-a\n---\n# Skill A", encoding="utf-8")
    (skills_dir / "skill-b").mkdir(parents=True)
    (skills_dir / "skill-b" / "SKILL.md").write_text("---\nname: skill-b\n---\n# Skill B", encoding="utf-8")

    manifest_json = plugin_dir / "plugin.json"
    manifest_json.write_text(json.dumps({"name": "sample-plugin", "version": "1.0.0"}), encoding="utf-8")

    monkeypatch.chdir(root)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "plugin_installer.py",
            "--plugin",
            str(plugin_dir),
            "--skills",
            "skill-a",
        ],
    )

    plugin_installer.main()

    # Verify skill-a was installed and skill-b was NOT installed
    assert (root / ".agents" / "skills" / "skill-a").exists()
    assert not (root / ".agents" / "skills" / "skill-b").exists()

    # Verify ownership manifest records only skill-a
    own_file = root / ".agents" / "ownership" / "sample-plugin.json"
    assert own_file.exists()
    own_data = json.loads(own_file.read_text(encoding="utf-8"))
    assert ".agents/skills/skill-a" in own_data["artifacts"]
    assert ".agents/skills/skill-b" not in own_data["artifacts"]

    # Verify plugin-retention.json was seeded/updated
    ret_file = root / "plugin-retention.json"
    assert ret_file.exists()
    ret_data = load_manifest(ret_file)
    assert "sample-plugin" in ret_data["plugins"]
    assert ret_data["plugins"]["sample-plugin"]["skills"]["skill-a"] is True


def test_customize_plugin_skills_tui_all_toggle(tmp_path: Path):
    # Test helper that processes 'a' key (toggle all)
    skills = ["skill-1", "skill-2", "skill-3"]
    state = plugin_add.SkillSelectionState("test-plugin", skills)
    assert state.all_selected()

    # Press 'a' to untoggle all
    plugin_add.skill_selection_process_key("a", state)
    assert not state.any_selected()
    assert state.selected == set()

    # Press 'a' to re-toggle all
    plugin_add.skill_selection_process_key("a", state)
    assert state.all_selected()

    # Press ' ' to toggle single skill
    plugin_add.skill_selection_process_key(" ", state)
    assert "skill-1" not in state.selected
    assert "skill-2" in state.selected


def test_record_install_retention_states_records_false_for_unselected(tmp_path: Path):
    root = tmp_path
    plugin_skills_map = {
        "sample-plugin": {
            "skill-a": True,
            "skill-b": False,
        }
    }
    plugin_add._record_install_retention_states(plugin_skills_map, root, dry_run=False)

    ret_file = root / "plugin-retention.json"
    assert ret_file.exists()
    ret_data = load_manifest(ret_file)
    assert "sample-plugin" in ret_data["plugins"]
    assert ret_data["plugins"]["sample-plugin"]["skills"]["skill-a"] is True
    assert ret_data["plugins"]["sample-plugin"]["skills"]["skill-b"] is False

