"""
control_plane/policy.py — Unified Declarative Gate-Policy Engine (issue-524, Step 4)
========================================================================================

Purpose:
    Replaces agent_control.py's 4 scattered gate mechanisms — the GATE_REQUIREMENTS registry,
    the 3 hardcoded _check_prior_art_guard/_check_done_guard/_check_rolled_back_guard methods,
    and update_worktree()'s own independent pushed_to_origin barrier — with ONE declarative
    policy-evaluation mechanism that can evaluate both:
      (a) lifecycle transitions, keyed by (from_state, to_state); and
      (b) controlled operations (e.g. the worktree-push write), keyed by an operation name.
    Per docs/plans/issue-524-spec.md Section 5 Step 4 (generalized per external plan review
    round 1): one policy path, two rule kinds it can evaluate — not two independent engines.

    This module does not itself talk to SQLite, subprocess, hashlib, or the filesystem — every
    rule receives a `ctx` dict of plain data/callables (counts, a bound verify-sovereignty
    callback), so this file has zero infrastructure imports (dependency-direction invariant,
    DoD item 5). Since the persistence extraction revision, `ctx`'s callables are backed by
    control_plane.adapters.SqlitePersistenceAdapter (via ControlPlane) rather than a raw
    connection — this module never sees or imports sqlite3 either way.

Layer:
    OS Kernel / Execution Control Plane Substrate — Policy (domain layer)

Key Input Dependencies:
    None directly — all data arrives via the `ctx` dict passed to `evaluate()`.

Key Functions:
    - PolicyViolation — exception raised when a rule's check fails (caller-facing validation
      failure, e.g. missing receipt)
    - PolicyConfigurationError — exception raised when a rule itself is malformed (an unknown
      `check` type) — a bug in the policy registry, never silently treated as a pass
    - TRANSITION_RULES — declarative registry keyed by (from_state, to_state)
    - OPERATION_RULES — declarative registry keyed by operation name
    - evaluate_transition() — evaluates all rules registered for a given transition edge
    - evaluate_operation() — evaluates all rules registered for a given operation name
"""

from typing import Any, Dict, List, Optional, Tuple


class PolicyViolation(Exception):
    """Raised when a policy rule's check fails. agent_control.py's ControlPlane catches this
    and re-raises as PersistenceInvariantViolation to preserve the existing CLI exit-code
    contract (DoD item 6 of docs/plans/issue-524-spec.md) — external behavior is unchanged."""
    pass


class PolicyConfigurationError(Exception):
    """Raised when a rule declares an unrecognized `check` type — a bug in the policy registry
    itself, not a normal validation failure. Deliberately NOT a subclass of PolicyViolation:
    ControlPlane's `except PolicyViolation` clauses must not silently convert this into a
    PersistenceInvariantViolation (which would look like an ordinary, retryable gate failure)
    — it should propagate as an unhandled error (CLI exit code 1, a genuine crash), since it
    means a rule was misconfigured, not that a real precondition was unmet. Added after
    external post-implementation review flagged the prior `else: satisfied = True` fallback
    as an unsafe fail-open default for the single authoritative policy engine."""
    pass


def _gate_receipt_exists(ctx: Dict[str, Any], gate_name: str) -> bool:
    """Rule primitive: checks ctx['has_receipt'](gate_name)."""
    return ctx["has_receipt"](gate_name)


def _gate_critic_review_pass(ctx: Dict[str, Any]) -> bool:
    """Rule primitive: checks ctx['has_passing_critic_review']()."""
    return ctx["has_passing_critic_review"]()


def _gate_any_of(ctx: Dict[str, Any], options: List[Dict[str, Any]]) -> bool:
    """Rule primitive: passes if any nested option passes."""
    for opt in options:
        if opt["type"] == "receipt" and _gate_receipt_exists(ctx, opt["gate_name"]):
            return True
        if opt["type"] == "critic_review_pass" and _gate_critic_review_pass(ctx):
            return True
    return False


def _prior_art_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Predicate rule folding in the original _check_prior_art_guard: blocks EVOLUTION tasks
    from leaving INTAKE without a logged prior-art scan. Returns an error message string if
    the rule fails (with the exact original wording), or None if it passes/is not applicable."""
    task = ctx["task"]
    if task.get("task_type", "GENERAL") != "EVOLUTION":
        return None
    if ctx["count_asymmetric_persistence"](details_like="%prior_art_scan%") > 0:
        return None
    task_id = ctx["task_id"]
    return (
        f"Cannot advance EVOLUTION task '{task_id}' past INTAKE: "
        "Prior art scan required. Read references/map-debt.md (check Repeat: YES entries) "
        "and wiki/decisions/ before drafting hypotheses. "
        "Log result via log_asymmetric_persistence() with details containing 'prior_art_scan'."
    )


def _done_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Predicate rule folding in the original _check_done_guard: requires a passing test_suite
    receipt, an asymmetric persistence log entry, a clean leak check, and (if any verifiers
    were locked) intact verifier sovereignty. Returns an error message on failure, else None.
    Raises whatever ctx['verify_sovereignty']() raises (VerifierSovereigntyViolation) — that
    exception type and message are preserved exactly, unrelated to PolicyViolation."""
    task_id = ctx["task_id"]
    if ctx["count_receipts"](gate_name="test_suite", exit_code=0) == 0:
        return (
            f"Cannot complete task '{task_id}': No passing test_suite verification receipt "
            "(gate_name='test_suite', exit_code == 0) found."
        )

    if ctx["count_locked_verifiers"]() > 0:
        ctx["verify_sovereignty"]()  # raises VerifierSovereigntyViolation directly if tampered

    if ctx["count_asymmetric_persistence"](
        destination_like_any=["%wiki/decisions/%", "%references/map-debt.md%", "%map-debt%"]
    ) == 0:
        return (
            f"Cannot complete task '{task_id}': Asymmetric persistence required before DONE. "
            "Log an entry to wiki/decisions/ or references/map-debt.md."
        )

    if ctx["count_receipts"](gate_name="leak_check", exit_code=0) == 0:
        return f"Cannot complete task '{task_id}': Missing clean leak check receipt (gate_name='leak_check', exit_code=0)."

    return None


def _rolled_back_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Predicate rule folding in the original _check_rolled_back_guard: requires at least one
    asymmetric_persistence_log entry documenting the failure before rollback."""
    task_id = ctx["task_id"]
    if ctx["count_asymmetric_persistence"]() > 0:
        return None
    return (
        f"Cannot roll back task '{task_id}': Asymmetric persistence required. "
        "Document failure mode/learning in asymmetric_persistence_log before rolling back code."
    )


def _worktree_push_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Predicate rule folding in the original update_worktree() pushed_to_origin barrier:
    the task must currently be in one of WORKTREE_REVIEW/MULTI_AGENT_CODE_REVIEW/VERIFY_EXIT."""
    task_state = ctx["task_state"]
    task_id = ctx["task_id"]
    valid_states_for_push = ("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")
    if task_state in valid_states_for_push:
        return None
    return (
        f"Cannot mark worktree 'pushed_to_origin' for task '{task_id}': Task state is '{task_state}'. "
        f"Post-implementation review stage gate required. Task must be in {valid_states_for_push} before pushing to origin."
    )


# --- Lifecycle transition rules, keyed by (from_state, to_state) ---
# Each entry is a list of rules; ALL rules in the list must pass. A rule is either:
#   {"check": "any_of", "options": [...]} / {"check": "receipt", "gate_name": ...} /
#   {"check": "critic_review_pass"}  — declarative registry checks (formerly GATE_REQUIREMENTS)
#   {"check": "predicate", "fn": <callable>, "applies_to": <optional edge filter>} — folded-in guards
TRANSITION_RULES: Dict[Tuple[str, str], List[Dict[str, Any]]] = {
    ("INTAKE", "INTERVIEW"): [
        {"check": "predicate", "fn": _prior_art_check},
    ],
    ("INTERVIEW", "DRAFT_PLAN"): [
        {
            "check": "any_of",
            "options": [
                {"type": "receipt", "gate_name": "plan_mode_entry"},
                {"type": "receipt", "gate_name": "socratic_intake_complete"},
            ],
            "error": "Cannot enter DRAFT_PLAN: no proof Plan Mode was entered or Socratic intake "
                     "completed. Call record_plan_mode_entry() or record_socratic_intake_complete() first.",
        },
    ],
    ("INTERVIEW", "PLAN_REVIEW"): [
        {
            "check": "any_of",
            "options": [
                {"type": "receipt", "gate_name": "plan_mode_entry"},
                {"type": "receipt", "gate_name": "socratic_intake_complete"},
            ],
            "error": "Cannot enter PLAN_REVIEW: no proof Plan Mode was entered or Socratic intake "
                     "completed. Call record_plan_mode_entry() or record_socratic_intake_complete() first.",
        },
    ],
    ("DRAFT_PLAN", "AWAITING_APPROVAL"): [
        {
            "check": "any_of",
            "options": [
                {"type": "critic_review_pass"},
                {"type": "receipt", "gate_name": "multi_agent_review_skipped"},
            ],
            "error": "Cannot enter AWAITING_APPROVAL: no passing critic review or explicit recorded "
                     "skip found. Call record_critic_review(verdict='PASS') or record_review_skip().",
        },
    ],
    ("PLAN_REVIEW", "AWAITING_APPROVAL"): [
        {
            "check": "any_of",
            "options": [
                {"type": "critic_review_pass"},
                {"type": "receipt", "gate_name": "multi_agent_review_skipped"},
            ],
            "error": "Cannot enter AWAITING_APPROVAL: no passing critic review or explicit recorded "
                     "skip found. Call record_critic_review(verdict='PASS') or record_review_skip().",
        },
    ],
    ("MULTI_AGENT_REVIEW", "AWAITING_APPROVAL"): [
        {
            "check": "critic_review_pass",
            "error": "Cannot enter AWAITING_APPROVAL: no passing critic review found after "
                     "MULTI_AGENT_REVIEW. Call record_critic_review(verdict='PASS').",
        },
    ],
    ("APPROVED", "IN_WORKTREE"): [
        {
            "check": "receipt",
            "gate_name": "human_approval",
            "error": "Cannot enter IN_WORKTREE: no recorded human_approval receipt found. "
                     "Call record_human_approval() — this gate can never be skipped.",
        },
    ],
    ("IN_WORKTREE", "WORKTREE_REVIEW"): [
        {
            "check": "receipt",
            "gate_name": "test_suite",
            "error": "Cannot enter WORKTREE_REVIEW: no recorded test_suite verification receipt found. "
                     "Call record_verification_receipt(gate_name='test_suite', ...).",
        },
    ],
    ("WORKTREE_REVIEW", "VERIFY_EXIT"): [
        {
            "check": "any_of",
            "options": [
                {"type": "critic_review_pass"},
                {"type": "receipt", "gate_name": "multi_agent_code_review_skipped"},
            ],
            "error": "Cannot enter VERIFY_EXIT: no passing critic review or explicit recorded skip "
                     "found. Call record_critic_review(verdict='PASS') or record_review_skip().",
        },
    ],
}

# _done_check and _rolled_back_check apply to ANY edge landing on DONE / ROLLED_BACK
# respectively, not one specific (from_state, to_state) pair — registered separately since
# the original guards fired on `to_state` alone, independent of `from_state`.
TO_STATE_RULES: Dict[str, List[Dict[str, Any]]] = {
    "DONE": [{"check": "predicate", "fn": _done_check}],
    "ROLLED_BACK": [{"check": "predicate", "fn": _rolled_back_check}],
}

# --- Controlled-operation rules, keyed by operation name (not a lifecycle transition) ---
OPERATION_RULES: Dict[str, List[Dict[str, Any]]] = {
    "worktree_push": [{"check": "predicate", "fn": _worktree_push_check}],
}


def _run_rule(ctx: Dict[str, Any], rule: Dict[str, Any]) -> None:
    """Evaluates a single rule against ctx; raises PolicyViolation with the rule's configured
    error message (or the predicate's returned message) if the rule fails. An unrecognized
    `check` type fails CLOSED — raises PolicyConfigurationError — rather than silently passing;
    this is the single authoritative policy engine, so a misconfigured/misspelled rule type
    must never be mistaken for "no rule to enforce"."""
    check = rule["check"]
    if check == "receipt":
        satisfied = _gate_receipt_exists(ctx, rule["gate_name"])
    elif check == "critic_review_pass":
        satisfied = _gate_critic_review_pass(ctx)
    elif check == "any_of":
        satisfied = _gate_any_of(ctx, rule["options"])
    elif check == "predicate":
        error = rule["fn"](ctx)
        if error is not None:
            raise PolicyViolation(error)
        return
    else:
        raise PolicyConfigurationError(f"Unknown policy check type: {check!r} in rule {rule!r}")
    if not satisfied:
        raise PolicyViolation(rule["error"])


def evaluate_transition(ctx: Dict[str, Any], from_state: str, to_state: str) -> None:
    """Evaluates every rule registered for the (from_state, to_state) edge, plus any
    to_state-wide rule (DONE/ROLLED_BACK guards). Raises PolicyViolation on the first
    failing rule; does nothing if all applicable rules pass or none are registered."""
    for rule in TRANSITION_RULES.get((from_state, to_state), []):
        _run_rule(ctx, rule)
    for rule in TO_STATE_RULES.get(to_state, []):
        _run_rule(ctx, rule)


def evaluate_operation(ctx: Dict[str, Any], operation_name: str) -> None:
    """Evaluates every rule registered for the given controlled operation (e.g.
    'worktree_push'). Raises PolicyViolation on the first failing rule."""
    for rule in OPERATION_RULES.get(operation_name, []):
        _run_rule(ctx, rule)
