"""
test_control_plane_state_machine.py — State-Machine Domain Extraction (issue-524)
=====================================================================================

Purpose:
    Unit tests for control_plane/state_machine.py's StateMachine in complete isolation — no
    SQLite, no ControlPlane — proving state-machine validation (known-state check + adjacency
    legality) is genuinely independently testable domain logic. Added after external
    post-implementation review (round 2) found this validation still embedded directly in
    ControlPlane.transition(), contradicting the plan's declared "state-machine validation"
    separation. Also includes an integration test proving ControlPlane.transition() actually
    delegates to self._state_machine rather than reimplementing the checks inline.

Key Input Dependencies:
    None — pure in-memory StateMachine instance.

Key Functions:
    - test_validate_known_state_rejects_unknown_state()
    - test_validate_known_state_accepts_every_canonical_state()
    - test_validate_adjacency_rejects_illegal_edge()
    - test_validate_adjacency_accepts_every_legal_edge()
    - test_control_plane_transition_delegates_to_state_machine()
"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.state_machine import StateMachine, CANONICAL_STATES, ALLOWED_TRANSITIONS, InvalidStateTransition
from control_plane.registry import TransitionRegistry


def test_validate_known_state_rejects_unknown_state():
    sm = StateMachine()
    with pytest.raises(InvalidStateTransition, match="Unknown state: NOT_A_REAL_STATE"):
        sm.validate_known_state("NOT_A_REAL_STATE")


def test_validate_known_state_accepts_every_canonical_state():
    sm = StateMachine()
    for state in CANONICAL_STATES:
        sm.validate_known_state(state)  # must not raise


def test_validate_adjacency_rejects_illegal_edge():
    # DONE -> INTAKE is now the deliberate reset_to_intake recovery edge (added
    # for control-plane-reset-transition) — no longer illegal, so it can't be
    # used as the illegal-edge example here. DONE -> WORKTREE_REVIEW remains
    # illegal (DONE is still terminal except for the one explicit reset edge).
    sm = StateMachine()
    with pytest.raises(InvalidStateTransition, match="Cannot transition task 't1' from 'DONE' to 'WORKTREE_REVIEW'"):
        sm.validate_adjacency("t1", "DONE", "WORKTREE_REVIEW")


def test_validate_adjacency_accepts_every_legal_edge():
    sm = StateMachine()
    for from_state, to_states in ALLOWED_TRANSITIONS.items():
        for to_state in to_states:
            sm.validate_adjacency("t1", from_state, to_state)  # must not raise


def test_every_non_done_state_has_human_force_close_edge():
    for state in CANONICAL_STATES:
        if state != "DONE":
            assert "DONE" in ALLOWED_TRANSITIONS[state]


def test_direct_force_close_requires_explicit_human_authorization(tmp_path):
    from agent_control import ControlPlane
    from control_plane.ports import PersistenceInvariantViolation

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="force-1", title="Force close", runtime_tool="claude")
    with pytest.raises(PersistenceInvariantViolation, match="explicit human authorization"):
        cp.transition("force-1", "DONE", "agent", "close now")


def test_human_authorized_force_close_is_persisted_from_any_state(tmp_path):
    from agent_control import ControlPlane

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="force-2", title="Force close", runtime_tool="claude")
    record = cp.coordinate_transition(
        "force-2", "DONE", "human", "Emergency close",
        force_close=True, human_authorization="FORCE_CLOSE",
    )
    assert record.from_state == "INTAKE"
    assert cp.get_task("force-2")["state"] == "DONE"
    assert cp._persistence.get_last_transition("force-2").to_state == "DONE"


def test_every_non_done_state_exposes_human_force_done_edge():
    """HITL force completion is legal from every non-terminal state."""
    registry = TransitionRegistry.load_default()
    for state in CANONICAL_STATES:
        if state == "DONE":
            continue
        if state == "RETROSPECTIVE":
            continue  # Existing retrospective completion edge remains governed separately.
        assert "DONE" in ALLOWED_TRANSITIONS[state]
        template = registry.get_template(state, "DONE")
        assert template is not None
        assert template.authority.get("type") == "human_decision"
        assert template.human_questions[0]["accepted_answers"] == ["FORCE_DONE"]


def test_control_plane_transition_delegates_to_state_machine(tmp_path, monkeypatch):
    """Integration: ControlPlane.transition() calls self._state_machine.validate_known_state()
    and validate_adjacency() rather than checking CANONICAL_STATES/ALLOWED_TRANSITIONS inline —
    proven by monkeypatching StateMachine to record calls and confirm they happened."""
    from agent_control import ControlPlane

    calls = []
    original_validate_known = StateMachine.validate_known_state
    original_validate_adjacency = StateMachine.validate_adjacency

    def recording_validate_known(self, to_state):
        calls.append(("validate_known_state", to_state))
        return original_validate_known(self, to_state)

    def recording_validate_adjacency(self, task_id, current_state, to_state):
        calls.append(("validate_adjacency", task_id, current_state, to_state))
        return original_validate_adjacency(self, task_id, current_state, to_state)

    monkeypatch.setattr(StateMachine, "validate_known_state", recording_validate_known)
    monkeypatch.setattr(StateMachine, "validate_adjacency", recording_validate_adjacency)

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="t1", title="State Machine Delegation Task", runtime_tool="claude")
    cp.transition(task_id="t1", to_state="INTERVIEW", actor="user", reason="test")

    assert ("validate_known_state", "INTERVIEW") in calls
    assert ("validate_adjacency", "t1", "INTAKE", "INTERVIEW") in calls
