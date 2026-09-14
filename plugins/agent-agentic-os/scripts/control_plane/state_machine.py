"""
control_plane/state_machine.py — Pure Domain State-Machine Validation (issue-524)
=====================================================================================

Purpose:
    Extracts task-lifecycle state validation (known-state check + adjacency/DAG legality)
    out of ControlPlane into an independently testable domain component. Added after external
    post-implementation review (round 2) found `CANONICAL_STATES`/`ALLOWED_TRANSITIONS` and
    their validation logic still lived directly in `ControlPlane.transition()` — domain logic,
    not merely facade delegation, and one of the plan's originally-declared 7 responsibilities
    ("state-machine validation") that had not actually been separated. This is deliberately a
    plain domain class, not a port/adapter pair — it has no infrastructure dependency to
    abstract (it's pure data + control flow over that data), so forcing it into the
    ports/adapters pattern would be structure for its own sake.

Layer:
    OS Kernel / Execution Control Plane Substrate — Domain (state machine)

Key Input Dependencies:
    None — pure logic over the module-level CANONICAL_STATES/ALLOWED_TRANSITIONS constants.

Key Functions:
    - CANONICAL_STATES — the 15 canonical task lifecycle states
    - ALLOWED_TRANSITIONS — the adjacency DAG (from_state -> list of legal to_states)
    - InvalidStateTransition — exception raised on an unknown state or illegal edge
    - StateMachine.validate_known_state() — raises if to_state isn't a recognized state at all
    - StateMachine.validate_adjacency() — raises if (current_state, to_state) isn't a legal edge
"""

# State names are defined once in the shared control_plane/constants.py and re-exported
# here so existing `from control_plane.state_machine import STATE_INTERVIEW`-style
# imports keep working; this module owns the DAG shape (CANONICAL_STATES/
# ALLOWED_TRANSITIONS) built from those shared names, not the names themselves.
from control_plane.constants import (
    STATE_INTAKE,
    STATE_INTERVIEW,
    STATE_DRAFT_PLAN,
    STATE_MULTI_AGENT_REVIEW,
    STATE_PLAN_REVIEW,
    STATE_AWAITING_APPROVAL,
    STATE_APPROVED,
    STATE_IN_WORKTREE,
    STATE_WORKTREE_REVIEW,
    STATE_MULTI_AGENT_CODE_REVIEW,
    STATE_VERIFY_EXIT,
    STATE_RETROSPECTIVE,
    STATE_DONE,
    STATE_ROLLED_BACK,
    STATE_ESCALATED,
    CANONICAL_STATE_NAMES,
)

CANONICAL_STATES = list(CANONICAL_STATE_NAMES)

ALLOWED_TRANSITIONS = {
    STATE_INTAKE: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_ESCALATED, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_INTERVIEW: [STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_RETROSPECTIVE, STATE_ESCALATED, STATE_INTAKE, STATE_DONE],
    STATE_DRAFT_PLAN: [STATE_PLAN_REVIEW, STATE_INTERVIEW, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_MULTI_AGENT_REVIEW: [STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_PLAN_REVIEW: [STATE_MULTI_AGENT_REVIEW, STATE_AWAITING_APPROVAL, STATE_DRAFT_PLAN, STATE_INTERVIEW, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_AWAITING_APPROVAL: [STATE_APPROVED, STATE_PLAN_REVIEW, STATE_DRAFT_PLAN, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_APPROVED: [STATE_IN_WORKTREE, STATE_RETROSPECTIVE, STATE_ESCALATED, STATE_INTAKE, STATE_DONE],
    STATE_IN_WORKTREE: [STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT, STATE_ROLLED_BACK, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_WORKTREE_REVIEW: [STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT, STATE_IN_WORKTREE, STATE_ROLLED_BACK, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_MULTI_AGENT_CODE_REVIEW: [STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT, STATE_IN_WORKTREE, STATE_ROLLED_BACK, STATE_ESCALATED, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_VERIFY_EXIT: [STATE_RETROSPECTIVE, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_ROLLED_BACK, STATE_ESCALATED, STATE_INTAKE, STATE_DONE],
    STATE_RETROSPECTIVE: [STATE_DONE, STATE_ESCALATED, STATE_INTAKE],
    STATE_DONE: [STATE_INTAKE, STATE_RETROSPECTIVE],
    STATE_ROLLED_BACK: [STATE_ESCALATED, STATE_PLAN_REVIEW, STATE_INTAKE, STATE_DONE, STATE_RETROSPECTIVE],
    STATE_ESCALATED: [STATE_INTAKE, STATE_PLAN_REVIEW, STATE_DONE, STATE_RETROSPECTIVE],
}


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachine:
    """Pure domain state-machine validation. Owns CANONICAL_STATES/ALLOWED_TRANSITIONS and
    the two checks ControlPlane.transition() previously ran inline: is `to_state` even a
    recognized state, and is the (current_state, to_state) edge legal per the DAG."""

    def validate_known_state(self, to_state: str) -> None:
        """Raises InvalidStateTransition if `to_state` is not one of CANONICAL_STATES."""
        if to_state not in CANONICAL_STATES:
            raise InvalidStateTransition(f"Unknown state: {to_state}")

    def validate_adjacency(self, task_id: str, current_state: str, to_state: str) -> None:
        """Raises InvalidStateTransition if (current_state, to_state) is not a legal edge."""
        allowed = ALLOWED_TRANSITIONS.get(current_state, [])
        if to_state not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition task '{task_id}' from '{current_state}' to '{to_state}'. Allowed: {allowed}"
            )

    def validate_recovery_target(self, task_id: str, current_state: str, to_state: str) -> None:
        """Validate a human-authorized recovery target without changing the normal DAG."""
        self.validate_known_state(current_state)
        self.validate_known_state(to_state)
        if current_state == to_state:
            raise InvalidStateTransition(
                f"Recovery target for task '{task_id}' must differ from '{current_state}'."
            )
