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
    - test_gate3_edges_require_cryptographic_proof_not_a_soft_question (both edges)
    - test_gate3_soft_questions_are_not_synced_and_the_edges_are_proof_gated_in_sqlite
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


GATE3_EDGES = [("WORKTREE_REVIEW", "VERIFY_EXIT"), ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")]
REMOVED_SOFT_QUESTIONS = ("confirm_worktree_review_accept_implementation", "confirm_multi_agent_code_review_accept_outcome")


@pytest.mark.parametrize("from_state,to_state", GATE3_EDGES)
def test_gate3_edges_require_cryptographic_proof_not_a_soft_question(registry, from_state, to_state):
    """auth-ciba-increment-b (2026-09-20) supersedes the 2026-09-17 fix that gave these edges a human_questions
    entry (trigger-enforced on actor='human'). A typed answer, or an actor string, can no longer authorize code
    acceptance: both edges declare requires_cryptographic_proof, carry no soft confirmation question, and their
    guidance names the signature flow and no skip flag."""
    tmpl = registry.get_template(from_state, to_state)
    assert tmpl is not None
    assert (from_state, to_state) in registry.proof_required_edges()
    qids = [q["question_id"] for q in tmpl.human_questions]
    assert not set(qids) & set(REMOVED_SOFT_QUESTIONS), qids
    hint = tmpl.next_steps_hint.lower()
    assert "ssh-keygen -y sign" in hint and "allowed_signers" in hint
    assert "--skip-review" not in hint and "--skip-reason" not in hint
    assert "no additional human question is required" not in hint  # the original stale-text finding stays fixed


def test_gate3_soft_questions_are_not_synced_and_the_edges_are_proof_gated_in_sqlite(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from agent_control import ControlPlane

    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    conn = sqlite3.connect(db_path)

    for from_state, to_state in GATE3_EDGES:
        soft = conn.execute(
            "SELECT question_id FROM required_transition_questions WHERE from_state=? AND to_state=? AND question_id LIKE 'confirm_%'",
            (from_state, to_state),
        ).fetchall()
        assert soft == [], f"soft confirmation question synced for {from_state}->{to_state}: {soft}"
        row = conn.execute(
            "SELECT authorized_actor, requires_proof FROM valid_transitions WHERE from_state=? AND to_state=?",
            (from_state, to_state),
        ).fetchone()
        assert row == ("human_only", 1), f"{from_state}->{to_state} must be human_only and requires_proof, got {row}"


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
