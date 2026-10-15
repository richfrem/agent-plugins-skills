#!/usr/bin/env python
"""
test_pointer_resolution.py
==========================

Purpose:
    Verify plugin installation resolves nested relative-path pointer files.

Key Input Dependencies:
    plugins/plugin-manager/scripts/plugin_installer.py — pointer copy helpers

Functions:
    - test_copy_resolving_pointers_follows_nested_pointer_files()
    - test_copy_resolving_pointers_reports_pointer_cycles()

Usage:
    python -m pytest plugins/plugin-manager/tests/test_pointer_resolution.py
"""

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import plugin_installer


# Verify that installation copies code rather than a nested pointer stub.
def test_copy_resolving_pointers_follows_nested_pointer_files(tmp_path: Path) -> None:
    """Copy the final script body when a pointer targets another pointer."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    scripts = source / "scripts"
    middle = source / "middle"
    scripts.mkdir(parents=True)
    middle.mkdir()

    (scripts / "helper.ps1").write_text("../middle/second.ps1", encoding="utf-8")
    (middle / "second.ps1").write_text("../helper.ps1", encoding="utf-8")
    (source / "helper.ps1").write_text("Write-Output 'resolved body'\n", encoding="utf-8")

    plugin_installer._copy_resolving_pointers(source, destination)

    assert (destination / "scripts" / "helper.ps1").read_text(encoding="utf-8") == (
        "Write-Output 'resolved body'\n"
    )


# Verify a malformed pointer chain terminates with an actionable warning.
def test_copy_resolving_pointers_reports_pointer_cycles(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Report cyclic pointer files instead of copying unresolved pointer text."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    scripts = source / "scripts"
    middle = source / "middle"
    scripts.mkdir(parents=True)
    middle.mkdir()

    (scripts / "helper.ps1").write_text("../middle/second.ps1", encoding="utf-8")
    (middle / "second.ps1").write_text("../scripts/helper.ps1", encoding="utf-8")

    plugin_installer._copy_resolving_pointers(source, destination)

    assert not (destination / "scripts" / "helper.ps1").exists()
    assert "pointer cycle" in capsys.readouterr().out.lower()


# Verify a pointer reached through a skill symlink resolves from the link's directory.
def test_symlink_to_pointer_resolves_relative_to_link_directory(tmp_path: Path) -> None:
    """Copy the real body when a pointer's path is written relative to the skill link."""
    plugin = tmp_path / "plugin"
    hub = plugin / "references"
    (hub / "architecture").mkdir(parents=True)
    (hub / "architecture" / "architecture.md").write_text("# real body\n", encoding="utf-8")
    (hub / "architecture.md").write_text("../../../references/architecture/architecture.md", encoding="utf-8")
    skill_refs = plugin / "skills" / "demo" / "references"
    skill_refs.mkdir(parents=True)
    link = skill_refs / "architecture.md"
    link.symlink_to("../../../references/architecture.md")
    destination = tmp_path / "installed.md"

    plugin_installer._process_symlink_item(link, destination)

    assert destination.read_text(encoding="utf-8") == "# real body\n"
