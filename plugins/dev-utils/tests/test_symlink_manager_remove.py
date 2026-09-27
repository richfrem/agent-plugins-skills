#!/usr/bin/env python
"""
test_symlink_manager_remove.py
==============================

Purpose:
    Regression tests for `symlink_manager.py remove`. When a skill directory
    was deleted with git (e.g. plugin-pruner in #627), its links were already
    gone from disk, and `remove` refused to drop the matching symlinks.json
    entries ("destination does not exist", exit 0), leaving stale manifest
    entries with no supported way to clean them up.

Key Input Dependencies:
    plugins/dev-utils/scripts/symlink_manager.py — `remove` subcommand under test
    git (tmp repo is initialised so find_repo_root() resolves to it)

Layer: Development / Testing

Functions:
    - test_remove_drops_manifest_entry_when_link_already_deleted
    - test_remove_still_deletes_existing_link_and_entry

Usage:
    python -m pytest plugins/dev-utils/tests/test_symlink_manager_remove.py
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "symlink_manager.py"


def _init_repo(tmp_path: Path, links: list[dict]) -> Path:
    """Create a git repo containing a symlinks.json manifest with the given links."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "symlinks.json").write_text(json.dumps({"version": 1, "links": links}, indent=2), encoding="utf-8")
    return tmp_path


def _run_remove(repo: Path, dst: str) -> subprocess.CompletedProcess:
    """Invoke the real CLI from inside the repo."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), "remove", "--dst", dst],
        cwd=repo, capture_output=True, text=True,
    )


def _manifest_dsts(repo: Path) -> list[str]:
    return [e["dst"] for e in json.loads((repo / "symlinks.json").read_text(encoding="utf-8"))["links"]]


def test_remove_drops_manifest_entry_when_link_already_deleted(tmp_path: Path):
    gone = "skills/old-skill/scripts/tool.py"
    keep = "skills/other/scripts/tool.py"
    repo = _init_repo(tmp_path, [
        {"src": "scripts/tool.py", "dst": gone, "strategy": "symlink"},
        {"src": "scripts/tool.py", "dst": keep, "strategy": "symlink"},
    ])

    result = _run_remove(repo, gone)

    assert result.returncode == 0, result.stderr
    assert _manifest_dsts(repo) == [keep]


def test_remove_still_deletes_existing_link_and_entry(tmp_path: Path):
    dst = "skills/live/scripts/tool.py"
    repo = _init_repo(tmp_path, [{"src": "scripts/tool.py", "dst": dst, "strategy": "symlink"}])
    (repo / "scripts").mkdir()
    (repo / "scripts" / "tool.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "skills" / "live" / "scripts").mkdir(parents=True)
    (repo / dst).symlink_to("../../../scripts/tool.py")

    result = _run_remove(repo, dst)

    assert result.returncode == 0, result.stderr
    assert not (repo / dst).is_symlink()
    assert _manifest_dsts(repo) == []
