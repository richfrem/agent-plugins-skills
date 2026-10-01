"""
test_control_plane_mode.py - behavioural tests for skills/os-control-plane-mode.

Purpose:
    Proves the status / enable / disable engine on a realistic throwaway repo:
    nothing changes without --yes, the task database is never touched, custom and
    independent hooks survive, gates are only on while their machinery exists, drift is
    reconciled, and a failed sync leaves a predictable state.

Key Input Dependencies:
    - skills/os-control-plane-mode/scripts/control_plane_mode.py
    - skills/os-control-plane-mode/control-plane.manifest.json
    - tests/helpers/control_plane_repo.py (fixture repo + fake syncer)
"""

import json
import subprocess
import sys

import pytest

from helpers.control_plane_repo import (
    BYSTANDERS, DB_BYTES, MEMBERS, make_repo, run_mode, snapshot,
)

OWNERSHIP = ".agents/ownership/agent-agentic-os.json"


def _own(root):
    return json.loads((root / OWNERSHIP).read_text())


def _member_flags(root):
    own = _own(root)
    return {f"{k}/{n}": own["components"][k][n]["should_install"] for k, ns in MEMBERS.items() for n in ns}


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
    assert "DISABLE the control plane" in res.stdout and "work-intake" in res.stdout
    assert snapshot(repo) == before


def test_without_yes_it_refuses_and_changes_nothing(repo):
    before = snapshot(repo)
    res = run_mode(repo, "disable")
    assert res.returncode == 2 and "--yes" in res.stderr
    assert snapshot(repo) == before


def test_disable_turns_everything_off_and_leaves_the_database_alone(repo):
    res = run_mode(repo, "disable", "--yes", "--actor", "tester")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "RESULT: consistent" in res.stdout

    assert (repo / "context/control-plane-mode").read_text().strip() == "disabled"
    assert all(v is False for v in _member_flags(repo).values())
    for name in MEMBERS["skills"]:
        assert not (repo / ".agents/skills" / name).exists()
    assert not (repo / ".agent/rules/state-transition-guidance-compliance.md").exists()

    hooks = repo / ".git/hooks"
    assert "pre-commit-pipeline-guard" not in (hooks / "pre-commit").read_text()
    assert "pre-push-review-guard" not in (hooks / "pre-push").read_text()
    assert (hooks / "pre-push-review-guard").is_file()  # script kept for a fast re-enable

    assert (repo / "context/control_plane.db").read_bytes() == DB_BYTES  # task history untouched

    log = (repo / "context/control-plane-mode.log").read_text().splitlines()
    assert json.loads(log[-1])["mode"] == "disabled" and json.loads(log[-1])["actor"] == "tester"
    backups = list((repo / "context/control-plane-backup").iterdir())
    assert len(backups) == 1 and (backups[0] / "agent-agentic-os.json").is_file()


def test_disable_leaves_bystanders_and_independent_hooks_alone(repo):
    run_mode(repo, "disable", "--yes")
    own = _own(repo)
    for kind, names in BYSTANDERS.items():
        for name in names:
            assert own["components"][kind][name]["should_install"] is True
    assert own["components"]["hooks"]["hooks"]["should_install"] is True  # Claude Code plugin hooks
    pre_commit = (repo / ".git/hooks/pre-commit").read_text()
    assert "pre-commit-evolution-guard" in pre_commit  # separate feature, never touched
    assert "echo custom-pre-commit-step" in pre_commit  # custom content survives


def test_enable_restores_everything_and_proves_it(repo):
    run_mode(repo, "disable", "--yes")
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "RESULT: consistent" in res.stdout
    assert (repo / "context/control-plane-mode").read_text().strip() == "enabled"
    assert all(v is True for v in _member_flags(repo).values())
    for name in MEMBERS["skills"]:
        assert (repo / ".agents/skills" / name).is_dir()
    assert "pre-commit-pipeline-guard" in (repo / ".git/hooks/pre-commit").read_text()
    assert "pre-push-review-guard" in (repo / ".git/hooks/pre-push").read_text()
    assert (repo / "context/control_plane.db").read_bytes() == DB_BYTES
    assert "echo custom-pre-commit-step" in (repo / ".git/hooks/pre-commit").read_text()


def test_disable_then_enable_round_trips_the_ownership_file_byte_for_byte(repo):
    original = (repo / OWNERSHIP).read_bytes()
    run_mode(repo, "disable", "--yes")
    assert (repo / OWNERSHIP).read_bytes() != original
    run_mode(repo, "enable", "--yes")
    assert (repo / OWNERSHIP).read_bytes() == original  # formatting preserved, only flags flipped


def test_repeating_a_toggle_is_a_no_op(repo):
    run_mode(repo, "disable", "--yes")
    before = snapshot(repo)
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 0 and "nothing to do" in res.stdout
    assert snapshot(repo) == before


def test_status_reports_drift_and_disable_reconciles_it(repo):
    run_mode(repo, "disable", "--yes")
    (repo / ".agents/skills/work-intake").mkdir(parents=True)  # a stray resync brought it back
    own = _own(repo)
    own["components"]["skills"]["work-intake"]["should_install"] = True
    (repo / OWNERSHIP).write_text(json.dumps(own, indent=2) + "\n")

    st = run_mode(repo, "status")
    assert st.returncode == 1 and "skills/work-intake is still installed" in st.stdout

    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 0 and "RESULT: consistent" in res.stdout
    assert not (repo / ".agents/skills/work-intake").exists()


def test_status_reports_an_unwired_guard_while_enabled_and_enable_repairs_it(repo):
    pre_push = repo / ".git/hooks/pre-push"
    pre_push.write_text('#!/usr/bin/env bash\nHOOKS_DIR="$(dirname "$0")"\nexit 0\n')
    st = run_mode(repo, "status")
    assert st.returncode == 1 and "pre-push-review-guard is not wired" in st.stdout
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "pre-push-review-guard" in pre_push.read_text()


def test_a_failed_sync_while_disabling_reports_exit_3_with_the_gates_already_off(repo):
    (repo / "fake_sync.py").write_text("import sys; print('boom'); sys.exit(1)\n")
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 3 and "plugin sync failed" in res.stderr
    assert (repo / "context/control-plane-mode").read_text().strip() == "disabled"  # safe direction
    assert "pre-push-review-guard" not in (repo / ".git/hooks/pre-push").read_text()


def test_a_failed_sync_while_enabling_never_declares_enabled(repo):
    run_mode(repo, "disable", "--yes")
    (repo / "fake_sync.py").write_text("import sys; sys.exit(1)\n")
    res = run_mode(repo, "enable", "--yes")
    assert res.returncode == 3
    # gates must not come on while the machinery behind them is missing
    assert (repo / "context/control-plane-mode").read_text().strip() == "disabled"
    assert "pre-push-review-guard" not in (repo / ".git/hooks/pre-push").read_text()


def test_manifest_member_missing_from_ownership_aborts_before_any_change(repo):
    own = _own(repo)
    del own["components"]["skills"]["transition-simulator"]
    (repo / OWNERSHIP).write_text(json.dumps(own, indent=2) + "\n")
    before = snapshot(repo)
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 2 and "transition-simulator" in res.stderr
    assert snapshot(repo) == before


def test_a_hand_edited_dispatcher_is_left_untouched_and_reported(repo):
    pre_push = repo / ".git/hooks/pre-push"
    weird = ('#!/usr/bin/env bash\nHOOKS_DIR="$(dirname "$0")"\n'
             '[ -x "$HOOKS_DIR/pre-push-review-guard" ] && "$HOOKS_DIR/pre-push-review-guard" || exit 1\nexit 0\n')
    pre_push.write_text(weird)
    res = run_mode(repo, "disable", "--yes")
    assert res.returncode == 0, res.stdout + res.stderr
    assert pre_push.read_text() == weird  # never guess at a hand-edited hook
    assert "unrecognized" in res.stdout or "does not recognise" in res.stdout


def test_missing_ownership_file_is_a_clear_error(repo):
    (repo / OWNERSHIP).unlink()
    res = run_mode(repo, "status")
    assert res.returncode == 2 and "ownership file not found" in res.stderr


def test_corrupt_mode_file_is_reported_as_a_problem_not_silently_ignored(repo):
    (repo / "context/control-plane-mode").write_text("maybe\n")
    st = run_mode(repo, "status")
    assert st.returncode == 1 and "must contain 'enabled' or 'disabled'" in st.stdout


def test_toggle_works_from_a_git_worktree_target(repo, tmp_path):
    subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", "init"], cwd=repo, check=True, capture_output=True)
    wt = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "-q", str(wt), "-b", "feature"], cwd=repo, check=True, capture_output=True)
    res = subprocess.run(
        [sys.executable, str(__import__("helpers.control_plane_repo", fromlist=["x"]).MODE_SCRIPT),
         "status", "--json", "--target", str(wt)],
        capture_output=True, text=True,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert json.loads(res.stdout)["repo"] == str(repo.resolve())  # resolved to the main checkout
