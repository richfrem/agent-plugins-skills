"""
tests/test_run_verify_exit_bundle.py
=====================================

Purpose:
    Regression coverage for control_plane/wrappers/run_verify_exit_bundle.py.
    Specifically guards against the redundant-double-pytest-run inefficiency
    found live 2026-09-18: VERIFIER_CATALOG's "pytest_unit_tests" entry was
    bare `pytest` with no path/marker scoping, so it silently collected and
    ran the EXACT SAME test set as "pytest_full_suite" -- doubling every
    VERIFY_EXIT bundle run's wall-clock time for zero additional coverage,
    since this repo has no actual unit/integration marker split (confirmed:
    `grep -rn "@pytest.mark\." tests/` finds only `parametrize`).

Key Input Dependencies:
    - agent_control.ControlPlane, a real (tmp_path) SQLite database
    - control_plane.wrappers.run_verify_exit_bundle.run_verify_exit_bundle()
    - control_plane.wrappers.run_exit_verification.VERIFIER_CATALOG, monkeypatched
      to a fast real subprocess (not pytest itself) for test speed -- per this
      repo's own TDD rule against mocking subprocess.run on a critical path,
      this substitutes a fast REAL command, it does not mock the call.

Index:
    - test_bundle_runs_pytest_full_suite_command_only_once
    - test_bundle_records_both_test_suite_and_full_test_suite_receipts
    - test_bundle_fails_fast_and_records_neither_receipt_on_nonzero_exit
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import io

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator
from control_plane.constants import (
    STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_MULTI_AGENT_REVIEW,
    STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE,
    STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT,
)
from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.wrappers import run_exit_verification as rev_module
from control_plane.wrappers.run_verify_exit_bundle import run_verify_exit_bundle


def _task_at_verify_exit(tmp_path, monkeypatch, task_id: str) -> ControlPlane:
    """Drives a real task to VERIFY_EXIT via the actual production coordinator
    path (mirrors PipelineSimulator.run_standard_happy_path up to its own
    VERIFY_EXIT entry, stopping before its exit-verification calls so this
    test's own call to run_verify_exit_bundle is the first one)."""
    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task(task_id, "Bundle test")
    repo_root = tmp_path / "simulated-repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    sim.control_plane.repo_root = repo_root
    sim.enter_interview(task_id)
    sim.stage_interview_answers(task_id, classification="STANDARD", to_state=STATE_DRAFT_PLAN)
    sim.control_plane.record_plan_mode_entry(task_id, "simulator")
    sim.transition_from_interview(task_id, STATE_DRAFT_PLAN, classification="STANDARD", expect_success=True)

    plan_dir = repo_root / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan", encoding="utf-8")

    plan_review_answers = iter(["1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(plan_review_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="human",
        reason="setup", interactive=True,
    )
    review_answers = iter(["1", "3", "claude-cli", "test-model", "medium", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(review_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_MULTI_AGENT_REVIEW, actor="human",
        reason="setup", interactive=True,
    )
    sim.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "setup")
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: "YES", output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="simulator",
        reason="setup", interactive=True,
    )
    awaiting_answers = iter(["1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(awaiting_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_AWAITING_APPROVAL, actor="simulator",
        reason="setup", interactive=True,
    )
    approval_inputs = iter(["1", "y", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(approval_inputs), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_APPROVED, actor="human",
        reason="setup", interactive=True,
    )
    sim.control_plane.record_human_approval(task_id, "simulator")

    worktree = repo_root / ".worktrees" / task_id
    worktree.mkdir(parents=True, exist_ok=True)
    sim.control_plane.update_worktree(task_id, str(worktree), f"sim/{task_id}", "written_in_worktree")
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: "YES", output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_IN_WORKTREE, actor="simulator",
        reason="setup", interactive=True,
    )
    # test_suite_deferred_to_review, not test_suite -- keeps the later assertion that
    # run_verify_exit_bundle() itself records the "test_suite" gate meaningful.
    sim.control_plane.record_verification_receipt(task_id, "test_suite_deferred_to_review", "deferred", 0)
    worktree_review_answers = iter(["1", "1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(worktree_review_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_WORKTREE_REVIEW, actor="human",
        reason="setup", interactive=True,
    )
    # Gate 3 is a human signature over the worktree's commit/diff/untracked hashes; no skip flag or typed answer exists.
    # The (test) human signer is supplied by conftest.py and signs the real request with a throwaway key.
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry, output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_VERIFY_EXIT, actor="human",
        reason="setup", interactive=True,
    )
    assert sim.control_plane.get_task(task_id)["state"] == STATE_VERIFY_EXIT
    return sim.control_plane


def _count_pytest_style_subprocess_calls(monkeypatch, exit_code: int = 0):
    """Replaces both pytest-shaped catalog commands with a fast, real, counted
    subprocess (still real subprocess.run -- never mocked) so the test proves
    the actual number of process spawns without waiting on real pytest."""
    calls = []
    original = rev_module.subprocess.run

    def counting_run(cmd_list, **kwargs):
        calls.append(list(cmd_list))
        return original(["python3", "-c", f"import sys; sys.exit({exit_code})"], **kwargs)

    monkeypatch.setattr(rev_module.subprocess, "run", counting_run)
    return calls


def test_bundle_runs_pytest_full_suite_command_only_once(tmp_path, monkeypatch):
    task_id = "bundle-single-run"
    cp = _task_at_verify_exit(tmp_path, monkeypatch, task_id)
    calls = _count_pytest_style_subprocess_calls(monkeypatch)

    result = run_verify_exit_bundle(
        task_id=task_id, asymmetric_persistence_details="test", control_plane=cp,
    )

    assert result["status"] == "COMPLETED"
    pytest_calls = [c for c in calls if c and c[0] == "pytest"]
    assert len(pytest_calls) == 1, (
        f"Expected exactly one pytest subprocess invocation, got {len(pytest_calls)}: {pytest_calls}"
    )


def test_bundle_records_both_test_suite_and_full_test_suite_receipts(tmp_path, monkeypatch):
    task_id = "bundle-both-receipts"
    cp = _task_at_verify_exit(tmp_path, monkeypatch, task_id)
    _count_pytest_style_subprocess_calls(monkeypatch)

    run_verify_exit_bundle(task_id=task_id, asymmetric_persistence_details="test", control_plane=cp)

    import sqlite3
    conn = sqlite3.connect(cp.db_path)
    gate_names = {
        row[0] for row in conn.execute(
            "SELECT gate_name FROM verification_receipts WHERE task_id = ?", (task_id,)
        ).fetchall()
    }
    conn.close()
    assert "test_suite" in gate_names, "test_suite_or_deferred_to_review depends on this receipt existing"
    assert "full_test_suite" in gate_names
    assert "leak_check" in gate_names


def test_bundle_fails_fast_and_records_neither_receipt_on_nonzero_exit(tmp_path, monkeypatch):
    """A failed verifier's own receipt is still recorded (an honest audit log entry
    with the real nonzero exit code -- receipts are never suppressed), but the
    bundle must stop immediately: no later verifier in the sequence runs or gets a
    receipt, and asymmetric persistence is never logged for a failing run."""
    task_id = "bundle-failure"
    cp = _task_at_verify_exit(tmp_path, monkeypatch, task_id)
    _count_pytest_style_subprocess_calls(monkeypatch, exit_code=1)

    result = run_verify_exit_bundle(task_id=task_id, asymmetric_persistence_details="test", control_plane=cp)

    assert result["status"] == "FAILED"
    assert result["failed_verifier"] == "pytest_full_suite"
    import sqlite3
    conn = sqlite3.connect(cp.db_path)
    rows = dict(conn.execute(
        "SELECT gate_name, exit_code FROM verification_receipts WHERE task_id = ? "
        "AND gate_name IN ('test_suite', 'full_test_suite', 'leak_check')",
        (task_id,),
    ).fetchall())
    persistence_count = conn.execute(
        "SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ?", (task_id,)
    ).fetchone()[0]
    conn.close()
    assert rows == {"full_test_suite": 1}, (
        f"Only the first (failing) verifier should have a receipt, with its real "
        f"nonzero exit code -- test_suite and leak_check must never have run. Got: {rows}"
    )
    assert persistence_count == 0, "A failing run must never log asymmetric persistence as if it completed."
