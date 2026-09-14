import sys
import json
from pathlib import Path

# Add scripts dir to path for imports
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import plugin_remove


def test_clean_orphaned_artifacts(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills" / "legacy-skill"
    agents_dir = root / ".agents" / "agents"
    hooks_dir = root / ".agents" / "hooks"
    ownership_dir = root / ".agents" / "ownership"

    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")
    agents_dir.mkdir(parents=True)
    (agents_dir / "legacy-agent.md").write_text("# Agent", encoding="utf-8")
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "legacy-hooks.json").write_text("{}", encoding="utf-8")
    ownership_dir.mkdir(parents=True)
    (ownership_dir / "stale.json").write_text("{}", encoding="utf-8")

    orphans = plugin_remove._find_all_orphaned_artifacts(root)
    assert len(orphans) == 4

    removed = plugin_remove._clean_orphaned_artifacts(root, dry_run=False)
    assert removed == 4
    assert not skills_dir.exists()
    assert not (agents_dir / "legacy-agent.md").exists()
    assert not (hooks_dir / "legacy-hooks.json").exists()
    assert not (ownership_dir / "stale.json").exists()


def test_remove_from_registries_updates_sources_lock_and_retention(tmp_path: Path):
    root = tmp_path
    sources_file = root / "plugin-sources.json"
    sources_file.write_text(
        json.dumps({
            "sources": [
                {"source": "local", "plugins": ["demo-plugin", "keep-plugin"]}
            ]
        }),
        encoding="utf-8",
    )

    lock_file = root / "skills-lock.json"
    lock_file.write_text(
        json.dumps({
            "version": 1,
            "skills": {
                "demo-plugin": {"source": "local"},
                "demo-skill-1": {"source": "local"},
                "keep-skill": {"source": "local"},
            }
        }),
        encoding="utf-8",
    )

    retention_file = root / "plugin-retention.json"
    retention_file.write_text(
        json.dumps({
            "version": 1,
            "plugins": {
                "demo-plugin": {"skills": {"demo-skill-1": True}},
                "keep-plugin": {"skills": {"keep-skill": True}},
            }
        }),
        encoding="utf-8",
    )

    plugin_remove._remove_from_registries(
        "demo-plugin", root, dry_run=False, owned_skill_names={"demo-skill-1"}
    )

    # Check sources
    sources_data = json.loads(sources_file.read_text(encoding="utf-8"))
    assert sources_data["sources"][0]["plugins"] == ["keep-plugin"]

    # Check lock
    lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
    assert "demo-plugin" not in lock_data["skills"]
    assert "demo-skill-1" not in lock_data["skills"]
    assert "keep-skill" in lock_data["skills"]

    # Check retention
    retention_data = json.loads(retention_file.read_text(encoding="utf-8"))
    assert "demo-plugin" not in retention_data["plugins"]
    assert "keep-plugin" in retention_data["plugins"]


def test_remove_selected_plugins_is_all_cleans_orphans(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    ownership_dir = root / ".agents" / "ownership"
    skills_dir.mkdir(parents=True)
    ownership_dir.mkdir(parents=True)

    # Owned skill
    (skills_dir / "owned-skill").mkdir()
    own_file = ownership_dir / "my-plugin.json"
    own_file.write_text(
        json.dumps({"plugin": "my-plugin", "artifacts": [".agents/skills/owned-skill"]}),
        encoding="utf-8",
    )

    # Orphaned skill
    (skills_dir / "orphan-skill").mkdir()

    sources_file = root / "plugin-sources.json"
    sources_file.write_text(
        json.dumps({"sources": [{"source": "local", "plugins": ["my-plugin"]}]}),
        encoding="utf-8",
    )

    selected = [{"name": "my-plugin", "source": "local"}]
    plugin_remove._remove_selected_plugins(selected, root, dry_run=False, is_all=True)

    assert not (skills_dir / "owned-skill").exists()
    assert not (skills_dir / "orphan-skill").exists()
    assert not own_file.exists()


def test_main_cleans_orphans_when_no_plugins_tracked(tmp_path: Path, monkeypatch, capsys):
    root = tmp_path
    skills_dir = root / ".agents" / "skills" / "old-orphan"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Old", encoding="utf-8")

    sources_file = root / "plugin-sources.json"
    sources_file.write_text(json.dumps({"sources": []}), encoding="utf-8")

    monkeypatch.chdir(root)
    monkeypatch.setattr(
        sys, "argv", ["plugin_remove.py", "--all", "--yes"]
    )

    try:
        plugin_remove.main()
    except SystemExit as e:
        assert e.code == 0

    assert not skills_dir.exists()
    captured = capsys.readouterr()
    assert "Cleanup complete" in captured.out
