"""
test_next_number_worktree_resolution.py — Contract Test for Cross-Worktree Project-Root Resolution
====================================================================================================

Purpose:
    Verifies next_number.py's project-root discovery resolves the same repo root whether
    invoked from the main checkout or from a git worktree of the same repo — previously it
    walked up for the nearest `.git` directory, which is a FILE (not a directory) inside a
    worktree, so `.is_dir()` was always False there and the walk silently skipped past the
    worktree to whatever ancestor directory happened to have a real `.git` dir (or fell back
    to `script_path.parents[2]`), giving wrong/stale results when run from inside a worktree.

Key Input Dependencies:
    - plugins/dev-utils/scripts/next_number.py (copied into a throwaway repo)
    - git CLI (init, worktree add)
"""

import shutil
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
NEXT_NUMBER_SRC = REPO_ROOT / "plugins" / "dev-utils" / "scripts" / "next_number.py"


@pytest.fixture
def repo_with_worktree(tmp_path):
    """Creates a throwaway git repo with next_number.py and a docs/ADRs/ dir, plus a real
    git worktree checked out from it."""
    main_repo = tmp_path / "main_repo"
    main_repo.mkdir()
    subprocess.run(["git", "init"], cwd=main_repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=main_repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=main_repo, check=True)

    scripts_dir = main_repo / "plugins" / "dev-utils" / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy(NEXT_NUMBER_SRC, scripts_dir / "next_number.py")

    adrs_dir = main_repo / "docs" / "ADRs"
    adrs_dir.mkdir(parents=True)
    (adrs_dir / "001_first.md").write_text("# ADR 1\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=main_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=main_repo, check=True, capture_output=True)

    worktree_dir = tmp_path / "worktree_copy"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_dir), "-b", "feat/test-branch"],
        cwd=main_repo, check=True, capture_output=True
    )
    return main_repo, worktree_dir


def _run_cli(cwd: Path):
    """Invokes the copied next_number.py CLI as a subprocess with cwd set to the given repo/worktree."""
    script = cwd / "plugins" / "dev-utils" / "scripts" / "next_number.py"
    return subprocess.run([sys.executable, str(script), "--type", "adr"], cwd=str(cwd), capture_output=True, text=True)


def test_worktree_resolves_same_project_root_as_main_checkout(repo_with_worktree):
    """next_number.py run from inside a worktree must scan that worktree's own docs/ADRs/
    (which it has, being a full checkout) — not silently resolve to some unrelated ancestor
    directory or fall back to a wrong default."""
    main_repo, worktree_dir = repo_with_worktree

    res_main = _run_cli(main_repo)
    assert res_main.returncode == 0, res_main.stderr
    assert res_main.stdout.strip() == "002"

    res_worktree = _run_cli(worktree_dir)
    assert res_worktree.returncode == 0, res_worktree.stderr
    assert res_worktree.stdout.strip() == "002", (
        f"Expected the worktree to resolve its own docs/ADRs/ (next=002), got {res_worktree.stdout!r}"
    )
