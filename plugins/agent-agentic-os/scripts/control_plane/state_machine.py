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

CANONICAL_STATES = [
    "INTAKE",
    "INTERVIEW",
    "DRAFT_PLAN",
    "MULTI_AGENT_REVIEW",
    "PLAN_REVIEW",
    "AWAITING_APPROVAL",
    "APPROVED",
    "IN_WORKTREE",
    "WORKTREE_REVIEW",
    "MULTI_AGENT_CODE_REVIEW",
    "VERIFY_EXIT",
    "RETROSPECTIVE",
    "DONE",
    "ROLLED_BACK",
    "ESCALATED"
]

ALLOWED_TRANSITIONS = {
    "INTAKE": ["INTERVIEW", "DRAFT_PLAN", "PLAN_REVIEW", "ESCALATED", "DONE"],
    "INTERVIEW": ["DRAFT_PLAN", "PLAN_REVIEW", "RETROSPECTIVE", "ESCALATED", "INTAKE", "DONE"],
    "DRAFT_PLAN": ["PLAN_REVIEW", "INTERVIEW", "ESCALATED", "INTAKE", "DONE"],
    "MULTI_AGENT_REVIEW": ["DRAFT_PLAN", "PLAN_REVIEW", "ESCALATED", "INTAKE", "DONE"],
    "PLAN_REVIEW": ["MULTI_AGENT_REVIEW", "AWAITING_APPROVAL", "DRAFT_PLAN", "INTERVIEW", "ESCALATED", "INTAKE", "DONE"],
    "AWAITING_APPROVAL": ["APPROVED", "PLAN_REVIEW", "DRAFT_PLAN", "ESCALATED", "INTAKE", "DONE"],
    "APPROVED": ["IN_WORKTREE", "ESCALATED", "INTAKE", "DONE"],
    "IN_WORKTREE": ["WORKTREE_REVIEW", "VERIFY_EXIT", "ROLLED_BACK", "ESCALATED", "INTAKE", "DONE"],
    "WORKTREE_REVIEW": ["MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT", "IN_WORKTREE", "ROLLED_BACK", "ESCALATED", "INTAKE", "DONE"],
    "MULTI_AGENT_CODE_REVIEW": ["WORKTREE_REVIEW", "VERIFY_EXIT", "IN_WORKTREE", "ROLLED_BACK", "ESCALATED", "INTAKE", "DONE"],
    "VERIFY_EXIT": ["RETROSPECTIVE", "IN_WORKTREE", "WORKTREE_REVIEW", "ROLLED_BACK", "ESCALATED", "INTAKE", "DONE"],
    "RETROSPECTIVE": ["DONE", "ESCALATED", "INTAKE"],
    "DONE": ["INTAKE"],
    "ROLLED_BACK": ["ESCALATED", "PLAN_REVIEW", "INTAKE", "DONE"],
    "ESCALATED": ["INTAKE", "PLAN_REVIEW", "DONE"]
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
