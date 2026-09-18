"""
tests/test_worktree_review_verify_exit_gate.py
================================================

Purpose:
    Adversarial regression for a live finding during auth-ciba-poc-transition-
    mechanics (2026-09-17): WORKTREE_REVIEW -> VERIFY_EXIT and
    MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT both declared zero human_questions,
    reachable via code_review_or_skip's own receipt check with no actor
    verification at all (record_review_skip's actor parameter is an
    unvalidated free-text string). Fixed by adding a real human_questions
    entry to both edges in transition_templates.yaml, which gets genuine
    SQLite-trigger-level actor='human' enforcement via the existing
    required_transition_questions mechanism (the same one that already
    governs, e.g., DRAFT_PLAN -> PLAN_REVIEW's question) -- no coordinator.py
    or policy.py changes were needed for the enforcement itself.

Key Input Dependencies:
    - control_plane/transition_templates.yaml
    - A temporary, isolated SQLite database per test

    A third bypass, IN_WORKTREE -> VERIFY_EXIT, was found the same way (zero
    questions, zero deterministic checks). It was initially closed the same
    way (a human question, "Gate 3d"), then that fix was reverted: a human
    answering that question would be approving a bypass of WORKTREE_REVIEW --
    the very step whose purpose is to show them the diff first. Correctly
    attributed to a human, but not an informed decision. The edge was removed
    entirely instead (state_machine.py + the YAML template deleted) -- all
    work must pass through WORKTREE_REVIEW before VERIFY_EXIT.

Key Input Dependencies:
    - control_plane/transition_templates.yaml
    - control_plane/state_machine.py
    - A temporary, isolated SQLite database per test

Key Functions:
    - test_worktree_review_to_verify_exit_now_has_declared_question
    - test_multi_agent_code_review_to_verify_exit_now_has_declared_question
    - test_in_worktree_direct_verify_exit_edge_removed
    - test_in_worktree_direct_verify_exit_rejected_by_state_machine
"""

import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.registry import TransitionRegistry


@pytest.fixture
def registry():
    return TransitionRegistry.load_default()


def test_worktree_review_to_verify_exit_now_has_declared_question(registry):
    tmpl = registry.get_template("WORKTREE_REVIEW", "VERIFY_EXIT")
    assert tmpl is not None
    qids = [q["question_id"] for q in tmpl.human_questions]
    assert "confirm_worktree_review_accept_implementation" in qids
    # Guidance text must no longer claim no question is required (stale-text finding).
    assert "no additional human question is required" not in tmpl.next_steps_hint.lower()


def test_multi_agent_code_review_to_verify_exit_now_has_declared_question(registry):
    tmpl = registry.get_template("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")
    assert tmpl is not None
    qids = [q["question_id"] for q in tmpl.human_questions]
    assert "confirm_multi_agent_code_review_accept_outcome" in qids


def test_required_transition_questions_synced_for_both_edges(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from agent_control import ControlPlane

    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    conn = sqlite3.connect(db_path)

    for from_state, to_state, qid in [
        ("WORKTREE_REVIEW", "VERIFY_EXIT", "confirm_worktree_review_accept_implementation"),
        ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT", "confirm_multi_agent_code_review_accept_outcome"),
    ]:
        row = conn.execute(
            "SELECT 1 FROM required_transition_questions WHERE from_state=? AND to_state=? AND question_id=?",
            (from_state, to_state, qid),
        ).fetchone()
        assert row is not None, f"{qid} not synced into required_transition_questions for {from_state}->{to_state}"


def test_in_worktree_direct_verify_exit_edge_removed(registry):
    """Third bypass found live (2026-09-17): IN_WORKTREE -> VERIFY_EXIT had zero
    human_questions AND zero deterministic_checks -- a fully open backdoor
    letting an agent skip WORKTREE_REVIEW/MULTI_AGENT_CODE_REVIEW entirely.

    Initially closed by adding a human question ('Gate 3d'), then reverted:
    a human answering that question would be approving a bypass of the very
    step (WORKTREE_REVIEW) whose purpose is to show them the diff first --
    correctly attributed to a human, but not an informed decision. The
    correct fix is removing the edge entirely, not gating it -- all work must
    pass through WORKTREE_REVIEW before VERIFY_EXIT. See
    control_plane/state_machine.py's ALLOWED_TRANSITIONS[STATE_IN_WORKTREE]."""
    tmpl = registry.get_template("IN_WORKTREE", "VERIFY_EXIT")
    assert tmpl is None, "IN_WORKTREE -> VERIFY_EXIT must not exist as a template"


def test_in_worktree_direct_verify_exit_rejected_by_state_machine(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from agent_control import ControlPlane, PersistenceInvariantViolation
    from control_plane.state_machine import InvalidStateTransition

    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    task_id = "reject-direct-bypass-001"
    cp.create_task(task_id=task_id, title="Reject direct bypass", runtime_tool="test")
    # Force the task straight to IN_WORKTREE for this isolated adjacency check.
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE tasks SET state = 'IN_WORKTREE' WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()

    with pytest.raises((InvalidStateTransition, PersistenceInvariantViolation)):
        cp.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="attempted bypass")
