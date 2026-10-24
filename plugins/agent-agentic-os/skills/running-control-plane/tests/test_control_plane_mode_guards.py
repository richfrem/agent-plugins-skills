"""
test_control_plane_mode_guards.py - the git guards honour the declared control-plane mode.

Purpose:
    pre-commit-pipeline-guard and pre-push-review-guard must exit 0 immediately, with a
    visible note, when context/control-plane-mode says `disabled`; and must behave exactly
    as before when the file is absent or says `enabled`. A symlinked control_plane.db is the
    probe: it makes an enabled guard block, so "exit 0" can only mean "ungated by mode".
"""

import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
GUARDS = ["pre-commit-pipeline-guard", "pre-push-review-guard"]


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"  # a subfolder, so a sibling worktree stays inside this test's tmp dir
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / "context").mkdir()
    return root


def _symlink_db(repo):
    """A symlinked control_plane.db makes an enabled guard block."""
    (repo / "context" / "control_plane.db").symlink_to(repo / "elsewhere.db")


def _mode(repo, text):
    (repo / "context" / "control-plane-mode").write_text(text)


def _run(guard, repo):
    return subprocess.run(["bash", str(SCRIPTS / guard)], cwd=repo, capture_output=True, text=True)


@pytest.mark.parametrize("guard", GUARDS)
def test_disabled_mode_passes_with_a_visible_note_even_when_the_db_would_block(guard, repo):
    _symlink_db(repo)
    _mode(repo, "disabled\n")
    res = _run(guard, repo)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "DISABLED" in res.stderr and "ungated by design" in res.stderr


@pytest.mark.parametrize("guard", GUARDS)
def test_enabled_mode_still_gates(guard, repo):
    _symlink_db(repo)
    _mode(repo, "enabled\n")
    res = _run(guard, repo)
    assert res.returncode == 1 and "symlink" in res.stdout


@pytest.mark.parametrize("guard", GUARDS)
def test_missing_mode_file_behaves_exactly_as_before(guard, repo):
    _symlink_db(repo)
    res = _run(guard, repo)
    assert res.returncode == 1 and "symlink" in res.stdout


@pytest.mark.parametrize("guard", GUARDS)
def test_missing_mode_file_and_no_database_keeps_the_original_warning(guard, repo):
    res = _run(guard, repo)
    assert res.returncode == 0 and "found no control_plane.db" in res.stderr


@pytest.mark.parametrize("guard", GUARDS)
def test_mode_value_is_case_and_whitespace_tolerant(guard, repo):
    _symlink_db(repo)
    _mode(repo, "  Disabled \n\n")
    assert _run(guard, repo).returncode == 0


@pytest.mark.parametrize("guard", GUARDS)
@pytest.mark.parametrize("garbage", ["maybe\n", "", "disable\n", "off\n"])
def test_an_unrecognised_mode_never_turns_a_gate_off(guard, garbage, repo):
    _symlink_db(repo)
    _mode(repo, garbage)
    assert _run(guard, repo).returncode == 1  # fails closed: still gating


@pytest.mark.parametrize("guard", GUARDS)
def test_disabled_mode_is_found_from_a_worktree(guard, repo):
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", "x"], cwd=repo, check=True, capture_output=True)
    wt = repo.parent / "worktree"
    subprocess.run(["git", "worktree", "add", "-q", str(wt), "-b", "task"], cwd=repo, check=True, capture_output=True)
    _symlink_db(repo)
    _mode(repo, "disabled\n")
    res = _run(guard, wt)
    assert res.returncode == 0 and "DISABLED" in res.stderr
