#!/usr/bin/env python
"""
test_sync_noise_regressions.py
==============================

Purpose:
    Regression tests for three recurring plugin-sync annoyances seen in
    downstream consumer repos (2026-09-24 and 2026-09-27):
    1. Rule injection appended ~1,500 lines of rules into a CLAUDE.md that is a
       deliberate pointer stub to AGENTS.md, dirtying the tree on every sync.
    2. sync_with_inventory printed "[WARNING] prune_installed_skills.py not
       found" in every consumer repo, even though plugin-pruner was removed on
       purpose in #627 (superseded by ownership desired-state sync).
    3. plugin_add printed one "missing evals/evals.json" warning per skill,
       including for remote third-party sources (e.g. obra/superpowers) the
       consumer cannot fix.

Key Input Dependencies:
    plugins/plugin-manager/scripts/plugin_installer.py — _deploy_rule_to_target()
    plugins/plugin-manager/scripts/plugin_add.py — validate_plugin(), _source_is_remote()
    plugins/plugin-manager/scripts/sync_with_inventory.py — enforce_retention_pruning()

Layer: Development / Testing

Functions:
    - test_append_rule_skips_agents_md_pointer_stub
    - test_append_rule_still_appends_to_claude_md_with_plugin_blocks
    - test_append_rule_still_appends_to_plain_claude_md
    - test_validate_plugin_summarises_missing_evals_once
    - test_validate_plugin_silent_when_evals_warning_disabled
    - test_source_is_remote
    - test_retention_step_info_not_warning_when_pruner_absent

Usage:
    python -m pytest plugins/plugin-manager/tests/test_sync_noise_regressions.py
"""

import sys
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import plugin_add
import plugin_installer
import sync_with_inventory

POINTER_STUB = "# CLAUDE.md\n\nRead [AGENTS.md](AGENTS.md).\n"


def _make_rule(tmp_path: Path) -> Path:
    """Create a plugin rule source file outside the target repo root."""
    rule = tmp_path / "plugin-src" / "my-rule.md"
    rule.parent.mkdir(parents=True)
    rule.write_text("RULE BODY\n", encoding="utf-8")
    return rule


def _make_repo(tmp_path: Path, claude_md: str) -> Path:
    """Create a consumer repo root with a .claude/ dir and the given CLAUDE.md."""
    root = tmp_path / "repo"
    (root / ".claude").mkdir(parents=True)
    (root / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
    return root


def test_append_rule_skips_agents_md_pointer_stub(tmp_path: Path):
    root = _make_repo(tmp_path, POINTER_STUB)
    result = plugin_installer._deploy_rule_to_target(
        _make_rule(tmp_path), "my-rule.md", "p", ".claude", root, dry_run=False
    )
    assert result is None
    assert (root / "CLAUDE.md").read_text(encoding="utf-8") == POINTER_STUB


def test_append_rule_still_appends_to_claude_md_with_plugin_blocks(tmp_path: Path):
    existing = POINTER_STUB + "\n<!-- plugin: other / other-rule -->\nOLD\n"
    root = _make_repo(tmp_path, existing)
    plugin_installer._deploy_rule_to_target(
        _make_rule(tmp_path), "my-rule.md", "p", ".claude", root, dry_run=False
    )
    text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- plugin: p / my-rule -->" in text
    assert "RULE BODY" in text


def test_append_rule_still_appends_to_plain_claude_md(tmp_path: Path):
    root = _make_repo(tmp_path, "# Project notes\n\nUse tabs.\n")
    plugin_installer._deploy_rule_to_target(
        _make_rule(tmp_path), "my-rule.md", "p", ".claude", root, dry_run=False
    )
    assert "RULE BODY" in (root / "CLAUDE.md").read_text(encoding="utf-8")


def _make_plugin(tmp_path: Path, skills: list[str]) -> Path:
    """Create a minimal valid plugin whose skills have no evals/evals.json."""
    plugin = tmp_path / "demo-plugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "demo-plugin"}), encoding="utf-8")
    for name in skills:
        (plugin / "skills" / name).mkdir(parents=True)
        (plugin / "skills" / name / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    return plugin


def test_validate_plugin_summarises_missing_evals_once(tmp_path: Path, capsys):
    plugin_add.validate_plugin(_make_plugin(tmp_path, ["alpha", "beta", "gamma"]))
    lines = [l for l in capsys.readouterr().out.splitlines() if "evals" in l]
    assert len(lines) == 1
    assert all(name in lines[0] for name in ("alpha", "beta", "gamma"))


def test_validate_plugin_silent_when_evals_warning_disabled(tmp_path: Path, capsys):
    plugin_add.validate_plugin(_make_plugin(tmp_path, ["alpha"]), warn_missing_evals=False)
    assert "evals" not in capsys.readouterr().out


def test_source_is_remote(tmp_path: Path):
    assert plugin_add._source_is_remote(SimpleNamespace(source="obra/superpowers"))
    assert plugin_add._source_is_remote(SimpleNamespace(source="https://github.com/obra/superpowers"))
    assert not plugin_add._source_is_remote(SimpleNamespace(source=str(tmp_path)))
    assert not plugin_add._source_is_remote(SimpleNamespace(source=None))


def test_retention_step_info_not_warning_when_pruner_absent(tmp_path: Path, capsys, monkeypatch):
    root = tmp_path
    (root / "plugin-retention.json").write_text(json.dumps({"version": 1, "plugins": {}}), encoding="utf-8")
    empty_script_dir = tmp_path / "installed-syncer-scripts"
    empty_script_dir.mkdir()
    monkeypatch.setattr(sync_with_inventory, "SCRIPT_DIR", empty_script_dir)

    with patch("subprocess.run") as mock_run:
        sync_with_inventory.enforce_retention_pruning(root, dry_run=False)
        assert not mock_run.called

    out = capsys.readouterr().out
    assert "WARNING" not in out
    assert "ownership" in out.lower()
