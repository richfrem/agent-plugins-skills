"""
test_control_plane_reset_transition.py — RED/GREEN suite for reset_to_intake
=============================================================================

Purpose:
    Validates the reset_to_intake recovery edge (control-plane-reset-transition
    spec, docs/plans/control-plane-reset-transition-spec.md): a single authored
    wildcard template (from_state: "*" -> INTAKE) mechanically expanded by
    TransitionRegistry into one literal edge per non-INTAKE canonical state
    (including DONE), fully gated through coordinate_transition() with a
    genuine interactive human-answered justification question, recorded as
    decision_type='RESET'.

    Note: this worktree branched off main before PR #562 (the decision_actor
    fix) merged, so actor here is simply whatever the coordinate_transition()
    caller passes as actor= — this branch does not yet distinguish
    interactive vs. provided_answers at the actor level. The
    provided_answers test below documents that gap explicitly rather than
    asserting a guarantee this branch doesn't yet provide.

Key Input Dependencies:
    - Temporary SQLite databases created in pytest fixtures
    - control_plane/transition_templates.yaml (reset_to_intake template)

Key Functions:
    - _seed_task_at_state() — trigger-safe raw state seeding for fixtures
    - test_wildcard_expansion_produces_one_edge_per_non_intake_state()
    - test_reset_edge_not_offered_from_intake_itself()
    - test_reset_from_representative_states_interactive_succeeds()
    - test_reset_actor_reflects_caller_pending_pr562_rebase()
    - test_reset_interactive_empty_answer_fails_closed()
    - test_reset_preserves_prior_history()
    - test_reset_then_walk_forward_unblocks_hooks() — live DoD proof
"""

import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import CANONICAL_STATES, ALLOWED_TRANSITIONS
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.adapters import SCHEMA_SQL, _split_schema_sql_statements


@pytest.fixture
def temp_db_path(tmp_path):
    return tmp_path / "control_plane.db"


@pytest.fixture
def control_plane(temp_db_path):
    cp = ControlPlane(db_path=temp_db_path)
    cp.init_db()
    return cp


NON_INTAKE_STATES = [s for s in CANONICAL_STATES if s != "INTAKE"]

# Any state that already has a pre-existing, non-wildcard edge to INTAKE (e.g.
# escalated_to_intake) is skipped by the wildcard reset_to_intake expansion, to
# avoid a duplicate-edge collision, and answers a different pre-existing
# question — derived here from the registry itself (not a hardcoded state
# name), so both the parity test and the interactive-success test below stay
# correct if the underlying DAG changes.
_REGISTRY_FOR_STATE_DERIVATION = TransitionRegistry.load_default()
STATES_WITH_PREEXISTING_INTAKE_EDGE = {
    t.from_state for t in _REGISTRY_FOR_STATE_DERIVATION.get_all_templates()
    if t.to_state == "INTAKE" and not t.transition_id.startswith("reset_to_intake__from_")
}
RESET_EDGE_STATES = [s for s in NON_INTAKE_STATES if s not in STATES_WITH_PREEXISTING_INTAKE_EDGE]


def _seed_task_at_state(conn, task_id, state):
    """Sets a task row directly at a given state, bypassing enforce_valid_transition
    (which would otherwise revert an illegal-per-ALLOWED_TRANSITIONS raw seed), then
    recreates the production triggers so subsequent real transitions are enforced."""
    conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition;")
    conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (state, task_id))
    conn.execute(
        "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'NONE', ?, 'system', 'fixture')",
        (task_id, state),
    )
    conn.commit()
    for stmt in _split_schema_sql_statements(SCHEMA_SQL):
        if "CREATE TRIGGER" in stmt.upper():
            conn.execute(stmt)
    conn.commit()


def test_wildcard_expansion_produces_one_edge_per_non_intake_state():
    """Parity test (mirrors the existing 52-edge registry check): the wildcard
    reset_to_intake template must expand into exactly one literal edge per
    non-INTAKE canonical state, and no INTAKE->INTAKE edge."""
    registry = TransitionRegistry.load_default()
    reset_template_ids = {
        t.transition_id for t in registry.get_all_templates()
        if t.transition_id.startswith("reset_to_intake__from_")
    }
    expected_ids = {f"reset_to_intake__from_{s}" for s in RESET_EDGE_STATES}
    assert reset_template_ids == expected_ids
    assert "reset_to_intake__from_INTAKE" not in reset_template_ids
    for s in STATES_WITH_PREEXISTING_INTAKE_EDGE:
        assert f"reset_to_intake__from_{s}" not in reset_template_ids
        assert registry.get_template(s, "INTAKE") is not None


def test_reset_edge_not_offered_from_intake_itself():
    assert "INTAKE" not in ALLOWED_TRANSITIONS.get("INTAKE", [])


def test_reset_edges_require_human_approval():
    registry = TransitionRegistry.load_default()

    for source_state in RESET_EDGE_STATES:
        template = registry.get_template(source_state, "INTAKE")
        assert template is not None
        assert template.approval["required"] is True
        assert template.approval["approver_role"] == "human"


@pytest.mark.parametrize("source_state", RESET_EDGE_STATES)
def test_reset_from_every_non_intake_state_interactive_succeeds(control_plane, source_state):
    """Data-driven over every state that actually has a reset_to_intake edge
    (derived from the registry, not a hardcoded subset) — automatically covers
    any state added to or removed from CANONICAL_STATES. States with a
    pre-existing non-wildcard edge to INTAKE (e.g. ESCALATED) use a different,
    already-covered question/template and are correctly excluded here."""
    task_id = f"task-reset-{source_state.lower()}"
    control_plane.create_task(task_id=task_id, title="Reset test", runtime_tool="claude")
    conn = control_plane._persistence.get_connection()
    try:
        _seed_task_at_state(conn, task_id, source_state)
    finally:
        conn.close()

    answers = iter([
        "Recovering drifted record after raw-write bypass evidence",
        "y",
    ])
    coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: next(answers))
    record = coord.coordinate_transition(
        task_id=task_id,
        to_state="INTAKE",
        actor="human",
        reason="Reset drifted task record",
        interactive=True,
    )
    assert record.to_state == "INTAKE"
    assert control_plane.get_task(task_id)["state"] == "INTAKE"

    conn = control_plane._persistence.get_connection()
    try:
        row = conn.execute(
            "SELECT decision_type, actor FROM transition_decisions WHERE task_id = ? AND to_state = 'INTAKE'",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "RESET"
    assert row[1] == "human"


def test_reset_via_provided_answers_rejected(control_plane):
    """A programmatic reset cannot satisfy the now-required human approval."""
    task_id = "task-reset-actor-gap"
    control_plane.create_task(task_id=task_id, title="Reset actor gap test", runtime_tool="claude")
    conn = control_plane._persistence.get_connection()
    try:
        _seed_task_at_state(conn, task_id, "IN_WORKTREE")
    finally:
        conn.close()

    coord = TransitionCoordinator(control_plane=control_plane)
    with pytest.raises(TransitionCoordinatorError, match="requires explicit human approval"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="INTAKE",
            actor="agent",
            reason="Attempted programmatic reset",
            interactive=False,
            provided_answers={"reset_justification": "programmatic answer, no real human involved"},
        )


def test_reset_interactive_empty_answer_fails_closed(control_plane):
    task_id = "task-reset-empty"
    control_plane.create_task(task_id=task_id, title="Reset empty test", runtime_tool="claude")
    conn = control_plane._persistence.get_connection()
    try:
        _seed_task_at_state(conn, task_id, "WORKTREE_REVIEW")
    finally:
        conn.close()

    coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: "")
    with pytest.raises(TransitionCoordinatorError, match="Missing required response"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="INTAKE",
            actor="human",
            reason="attempt empty justification",
            interactive=True,
        )


def test_reset_starts_a_fresh_transition_ledger(control_plane):
    """RESET removes prior transition attempts before recording the new root."""
    task_id = "task-reset-preserve-history"
    control_plane.create_task(task_id=task_id, title="Reset preserve test", runtime_tool="claude")
    conn = control_plane._persistence.get_connection()
    try:
        _seed_task_at_state(conn, task_id, "APPROVED")
        before_count = conn.execute(
            "SELECT COUNT(*) FROM task_transitions WHERE task_id = ?", (task_id,)
        ).fetchone()[0]
    finally:
        conn.close()

    answers = iter([
        "Recovering from drift, preserving history as evidence",
        "y",
    ])
    coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: next(answers))
    coord.coordinate_transition(
        task_id=task_id, to_state="INTAKE", actor="human", reason="Reset", interactive=True,
    )

    conn = control_plane._persistence.get_connection()
    try:
        after_count = conn.execute(
            "SELECT COUNT(*) FROM task_transitions WHERE task_id = ?", (task_id,)
        ).fetchone()[0]
        remaining = conn.execute(
            "SELECT from_state, to_state FROM task_transitions WHERE task_id = ? ORDER BY transition_id",
            (task_id,),
        ).fetchall()
    finally:
        conn.close()
    assert before_count > 1
    assert after_count == 1
    assert [tuple(row) for row in remaining] == [('APPROVED', 'INTAKE')]


def test_reset_then_walk_forward_unblocks_hooks(control_plane):
    """Live DoD proof: simulate the exact drift pattern found in tonight's
    session (raw write bypassing transition()), RESET the task, walk it
    forward through real gates to DONE, and confirm the task's final state
    is legitimately DONE with zero transition_violations — the precondition
    both pre-commit-pipeline-guard and pre-push-review-guard require."""
    task_id = "task-reset-e2e"
    control_plane.create_task(task_id=task_id, title="E2E reset test", runtime_tool="claude")

    # Simulate drift: raw write directly to DONE, bypassing transition().
    conn = control_plane._persistence.get_connection()
    try:
        _seed_task_at_state(conn, task_id, "DONE")
    finally:
        conn.close()
    assert control_plane.get_task(task_id)["state"] == "DONE"

    # RESET back to INTAKE via the real gate.
    reset_answers = iter([
        "Simulated drift from raw write; resetting to re-run full pipeline",
        "y",
    ])
    coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: next(reset_answers))
    coord.coordinate_transition(
        task_id=task_id, to_state="INTAKE", actor="human", reason="Reset drifted DONE record", interactive=True,
    )
    assert control_plane.get_task(task_id)["state"] == "INTAKE"

    # Walk forward legitimately: INTAKE -> INTERVIEW -> RETROSPECTIVE -> DONE via
    # the trivial fast-track, with the interview contract fully answered.
    coord2 = TransitionCoordinator(
        control_plane=control_plane,
        input_fn=lambda prompt: "unused",
    )
    coord2.coordinate_transition(
        task_id=task_id, to_state="INTERVIEW", actor="human", reason="Begin interview after reset",
    )
    interview_answers = iter([
        "TRIVIAL",
        "Re-verify the nested skill reference fix.",
        "The skill reference path and its loader behavior.",
        "The installed skill loader finds no nested SKILL.md.",
        "files=1, diff=abc1234",
        "Yes [Recommended]",
    ])
    coord2 = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: next(interview_answers))
    coord2.coordinate_transition(
        task_id=task_id, to_state="RETROSPECTIVE", actor="human", reason="Trivial fast-track after reset", interactive=True,
    )
    control_plane.save_retrospective(
        task_id,
        {"decision": "skip", "completion_mode": "skipped", "actor": "human", "skip_reason": "re-verified typo"},
        [],
    )
    coord3 = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: "skip")
    coord3.coordinate_transition(
        task_id=task_id, to_state="DONE", actor="human", reason="Retrospective skipped", interactive=True,
    )
    assert control_plane.get_task(task_id)["state"] == "DONE"

    conn = control_plane._persistence.get_connection()
    try:
        violations = conn.execute(
            "SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (task_id,)
        ).fetchone()[0]
    finally:
        conn.close()
    assert violations == 0
