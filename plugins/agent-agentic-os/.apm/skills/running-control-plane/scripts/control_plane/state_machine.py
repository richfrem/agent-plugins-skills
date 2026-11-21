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
    ACTIVE_STATES,
    RETIRED_STATES,
)

CANONICAL_STATES = list(CANONICAL_STATE_NAMES)
ACTIVE_STATE_LIST = list(ACTIVE_STATES)

ALLOWED_TRANSITIONS = {
    STATE_INTAKE: [STATE_DRAFT_PLAN, STATE_ESCALATED, STATE_DONE],
    STATE_DRAFT_PLAN: [STATE_PLAN_REVIEW, STATE_INTAKE, STATE_DONE],
    STATE_PLAN_REVIEW: [STATE_APPROVED, STATE_DRAFT_PLAN, STATE_INTAKE, STATE_DONE],
    STATE_APPROVED: [STATE_IN_WORKTREE, STATE_INTAKE, STATE_DONE],
    STATE_IN_WORKTREE: [STATE_WORKTREE_REVIEW, STATE_ROLLED_BACK, STATE_INTAKE, STATE_DONE],
    STATE_WORKTREE_REVIEW: [STATE_VERIFY_EXIT, STATE_IN_WORKTREE, STATE_ROLLED_BACK, STATE_INTAKE, STATE_DONE],
    STATE_VERIFY_EXIT: [STATE_DONE, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_ROLLED_BACK, STATE_INTAKE],
    STATE_DONE: [],
    STATE_ROLLED_BACK: [STATE_PLAN_REVIEW, STATE_ESCALATED, STATE_INTAKE, STATE_DONE],
    STATE_ESCALATED: [STATE_PLAN_REVIEW, STATE_INTAKE, STATE_DONE],
}


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachine:
    """Pure domain state-machine validation over the 10 active states (v15).
    Retired v14 states remain in CANONICAL_STATES for historical storage only and are
    refused as transition or recovery targets."""

    def validate_known_state(self, to_state: str) -> None:
        """Raises InvalidStateTransition if `to_state` is retired or unknown."""
        if to_state in RETIRED_STATES:
            raise InvalidStateTransition(f"State '{to_state}' is retired in schema v15 and cannot be targeted.")
        if to_state not in ACTIVE_STATES:
            raise InvalidStateTransition(f"Unknown state: {to_state}")

    def validate_adjacency(self, task_id: str, current_state: str, to_state: str) -> None:
        """Raises InvalidStateTransition if (current_state, to_state) is not a legal active edge."""
        allowed = ALLOWED_TRANSITIONS.get(current_state, [])
        if to_state not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition task '{task_id}' from '{current_state}' to '{to_state}'. Allowed: {allowed}"
            )

    def validate_recovery_target(self, task_id: str, current_state: str, to_state: str) -> None:
        """Validate a human-authorized recovery target without changing the normal DAG.
        Retired states are never valid recovery destinations."""
        if current_state not in CANONICAL_STATES:
            raise InvalidStateTransition(f"Unknown state: {current_state}")
        self.validate_known_state(to_state)
        if current_state == to_state:
            raise InvalidStateTransition(
                f"Recovery target for task '{task_id}' must differ from '{current_state}'."
            )
