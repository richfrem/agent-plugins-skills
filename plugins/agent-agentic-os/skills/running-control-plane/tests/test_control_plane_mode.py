"""
test_control_plane_mode.py - behavioural tests for the mode workflow of running-control-plane.

Purpose:
    `control_plane_mode.py` switches gating on or off for one clone: it declares the mode in
    context/control-plane-mode and wires or unwires the two git guards. Every test runs the script
    from a copy deployed under `.claude/skills/running-control-plane/scripts`, the way APM installs
    the skill, so a path that only works inside this repository fails here.

Key Input Dependencies:
    - scripts/control_plane_mode.py, scripts/control_plane_hooks.py, the guard scripts
    - tests/helpers/control_plane_repo.py (fixture repo)
"""

import json
import os
import subprocess
import sys

import pytest

from helpers.control_plane_repo import DB_BYTES, make_repo, mode_script, run_mode, snapshot


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path)


def test_status_of_a_fresh_install_is_enabled_and_consistent(repo):
    res = run_mode(repo, "status", "--json")
    assert res.returncode == 0, res.stdout + res.stderr
    st = json.loads(res.stdout)
    assert st["mode"] == "enabled" and st["consistent"] and st["problems"] == []
    assert not st["mode_file_present"]  # no file means enabled: pre-existing installs are unchanged


def test_dry_run_changes_nothing_and_prints_the_plan(repo):
    before = snapshot(repo)
    res = run_mode(repo, "disable", "--dry-run")
    assert res.returncode == 0
    assert "DISABLE the control plane" in res.stdout and "pre-push-review-guard" in res.stdout
    assert "syncer" not in res.stdout and "ownership" not in res.stdout
    assert snapshot(repo) == before


def test_without_yes_it_refuses_and_changes_nothing(repo):
    before = snapshot(repo)
    res = run_mode(repo, "disable")
    assert res.returncode == 2 and "--yes" in res.stderr
    assert snapshot(repo) == before


def test_disable_turns_gating_off_and_leaves_the_database_alone(repo):
    res = run_mode(repo, "disable", "--yes", "--actor", "tester")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "RESULT: consistent" in res.stdout

    assert (repo / "context/control-plane-mode").read_text().strip() == "disabled"
    hooks = repo / ".git/hooks"
    assert "pre-commit-pipeline-guard" not in (hooks / "pre-commit").read_text()
    assert "pre-push-review-guard" not in (hooks / "pre-push").read_text()
    assert (hooks / "pre-push-review-guard").is_file()  # script kept for a fast re-enable

    assert (repo / "context/control_plane.db").read_bytes() == DB_BYTES  # task history untouched

    log = (repo / "context/control-plane-mode.log").read_text().splitlines()
    assert json.loads(log[-1])["mode"] == "disabled" and json.loads(log[-1])["actor"] == "tester"
    backups = list((repo / "context/control-plane-backup").iterdir())
    assert len(backups) == 1 and (backups[0] / "pre-push").is_file()


def test_disable_leaves_independent_hooks_and_the_installed_skill_alone(repo):
    skill_before = snapshot(repo / ".claude")
    run_mode(repo, "disable", "--yes")
    pre_commit = (repo / ".git/hooks/pre-commit").read_text()
    assert "pre-commit-evolution-guard" in pre_commit  # separate feature, never touched
    assert "echo custom-pre-commit-step" in pre_commit  # custom content survives
    assert snapshot(repo / ".claude") == skill_before  # the APM-installed skill is never modified


def test_enable_restores_gating_and_proves_it(repo):
    run_mode(repo, "disable", "--yes")
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "RESULT: consistent" in res.stdout
    assert (repo / "context/control-plane-mode").read_text().strip() == "enabled"
    assert "pre-commit-pipeline-guard" in (repo / ".git/hooks/pre-commit").read_text()
    assert "pre-push-review-guard" in (repo / ".git/hooks/pre-push").read_text()
    assert (repo / "context/control_plane.db").read_bytes() == DB_BYTES


def test_repeating_a_toggle_is_a_no_op(repo):
    run_mode(repo, "disable", "--yes")
    before = snapshot(repo)
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 0 and "nothing to do" in res.stdout
    assert snapshot(repo) == before


def test_status_reports_an_unwired_guard_while_enabled_and_enable_repairs_it(repo):
    pre_push = repo / ".git/hooks/pre-push"
    pre_push.write_text('#!/usr/bin/env bash\nHOOKS_DIR="$(dirname "$0")"\nexit 0\n')
    st = run_mode(repo, "status")
    assert st.returncode == 1 and "pre-push-review-guard is not wired" in st.stdout
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "pre-push-review-guard" in pre_push.read_text()


def test_a_hand_edited_dispatcher_is_left_untouched_and_reported(repo):
    pre_push = repo / ".git/hooks/pre-push"
    weird = ('#!/usr/bin/env bash\nHOOKS_DIR="$(dirname "$0")"\n'
             '[ -x "$HOOKS_DIR/pre-push-review-guard" ] && "$HOOKS_DIR/pre-push-review-guard" || exit 1\nexit 0\n')
    pre_push.write_text(weird)
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert pre_push.read_text() == weird  # never guess at a hand-edited hook
    assert "unrecognized" in res.stdout or "does not recognise" in res.stdout


def test_corrupt_mode_file_is_reported_as_a_problem_not_silently_ignored(repo):
    (repo / "context/control-plane-mode").write_text("maybe\n")
    st = run_mode(repo, "status")
    assert st.returncode == 1 and "must contain 'enabled' or 'disabled'" in st.stdout


def test_toggle_works_from_a_git_worktree_target(repo, tmp_path):
    subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", "init"], cwd=repo, check=True, capture_output=True)
    wt = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "-q", str(wt), "-b", "feature"], cwd=repo, check=True, capture_output=True)
    res = subprocess.run([sys.executable, str(mode_script(repo)), "status", "--json", "--target", str(wt)],
                         capture_output=True, text=True,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert res.returncode == 0, res.stdout + res.stderr
    assert json.loads(res.stdout)["repo"] == str(repo.resolve())  # resolved to the main checkout


# --- APM deployed layout --------------------------------------------------------------------------


def test_installed_guards_are_stamped_with_the_deployed_script_paths(repo):
    run_mode(repo, "disable", "--yes")
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    deployed = (repo / ".claude/skills/running-control-plane/scripts").resolve()
    for name in ("pre-commit-pipeline-guard", "pre-push-review-guard"):
        text = (repo / ".git/hooks" / name).read_text()
        assert f'AGENT_CONTROL="{deployed}/agent_control.py"' in text
        assert "plugins/agent-agentic-os" not in text  # no path that exists only in this monorepo
    assert f'VERIFY_GATE_EVIDENCE="{deployed}/verify_gate_evidence.py"' in (repo / ".git/hooks/pre-push-review-guard").read_text()


def test_a_guard_stamped_for_an_old_install_location_is_reported_stale_and_enable_refreshes_it(repo):
    guard = repo / ".git/hooks/pre-push-review-guard"
    guard.write_text(guard.read_text().replace(str(repo.resolve()), "/old/install/location"))
    st = run_mode(repo, "status")
    assert st.returncode == 0 and "stale" in st.stdout  # a warning, not a problem: it still gates
    assert run_mode(repo, "enable", "--yes").returncode == 0
    assert "/old/install/location" not in guard.read_text()
    assert "stale" not in run_mode(repo, "status").stdout
