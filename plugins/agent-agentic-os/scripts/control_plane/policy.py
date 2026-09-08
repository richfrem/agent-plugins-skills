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
    - CHECK_REGISTRY — closed registry of deterministic check callables keyed by check_id
    - OPERATION_RULES — declarative registry keyed by operation name
    - evaluate_check() — evaluates a deterministic check by check_id
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


def _interview_route_check(ctx: Dict[str, Any], expected_classification: str, adaptive_question_id: str) -> Optional[str]:
    """Require the short-form interview baseline and its classification-driven follow-up."""
    answers = ctx.get("stage_answers", {})
    if answers.get("interview_classification", "").strip() != expected_classification:
        return (
            f"Interview classification must be {expected_classification} before this route; "
            f"received '{answers.get('interview_classification', '')}'."
        )
    required_ids = (
        "interview_classification",
        "interview_summary",
        "interview_scope",
        "interview_verification",
        adaptive_question_id,
    )
    missing = [qid for qid in required_ids if not str(answers.get(qid, "")).strip()]
    if missing:
        return "Interview answers missing: " + ", ".join(missing)
    return None


def _interview_trivial_check(ctx: Dict[str, Any]) -> Optional[str]:
    return _interview_route_check(ctx, "TRIVIAL", "interview_trivial_evidence")


def _interview_standard_check(ctx: Dict[str, Any]) -> Optional[str]:
    return _interview_route_check(ctx, "STANDARD", "interview_acceptance_criteria")


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


def _retrospective_done_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Requires the optional survey to be completed or explicitly skipped before DONE."""
    if not ctx["has_complete_retrospective"]():
        return (
            f"Cannot complete task '{ctx['task_id']}': retrospective is incomplete. "
            "Complete the survey or explicitly skip it with a reason; confirmed issue follow-ups "
            "must be created or rejected first."
        )
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
    """Predicate rule enforcing push gate: pushing to origin is strictly forbidden unless
    the task has cleared all verification gates and is in final state DONE."""
    task_state = ctx["task_state"]
    task_id = ctx["task_id"]
    if task_state == "DONE":
        return None
    return (
        f"Cannot mark worktree 'pushed_to_origin' for task '{task_id}': Task state is '{task_state}'. "
        "Pushing to origin requires full pipeline completion. Task must be in final state 'DONE' before pushing."
    )


def _task_commit_check(ctx: Dict[str, Any]) -> Optional[str]:
    """Predicate rule enforcing pipeline execution and stage validity on git commits.
    
    Permits commit if:
    1. The task is in an authorized implementation state (IN_WORKTREE, WORKTREE_REVIEW,
       MULTI_AGENT_CODE_REVIEW, VERIFY_EXIT, DONE); OR
    2. The task is in a planning/proposal state (INTAKE, INTERVIEW, DRAFT_PLAN, PLAN_REVIEW,
       MULTI_AGENT_REVIEW, AWAITING_APPROVAL) AND all staged files are documentation under
       docs/plans/ or docs/superpowers/.
       
    Furthermore, if a session was initiated in the control plane:
    - Verifies all transitions recorded in task_transitions match valid_transitions.
    - Verifies no transition violations are recorded for the task.
    - Verifies transition chain continuity from INTAKE to current state.
    """
    task_state = ctx.get("task_state")
    task_id = ctx.get("task_id", "unknown")
    staged_files: List[str] = ctx.get("staged_files", [])

    implementation_states = ("IN_WORKTREE", "WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT", "DONE")
    planning_states = ("INTAKE", "INTERVIEW", "DRAFT_PLAN", "PLAN_REVIEW", "MULTI_AGENT_REVIEW", "AWAITING_APPROVAL")

    # If in planning states, permit only if ALL staged files are docs/plans/ or docs/superpowers/
    if task_state in planning_states:
        if staged_files:
            non_doc_files = [
                f for f in staged_files
                if not (f.startswith("docs/plans/") or f.startswith("docs/superpowers/"))
            ]
            if non_doc_files:
                return (
                    f"Cannot commit code for task '{task_id}': Task state is '{task_state}' (Proposal Mode). "
                    f"Production code modifications are prohibited during planning. Non-planning staged files: {non_doc_files}. "
                    f"Complete Socratic interview, spec generation, and human approval before implementing in worktree."
                )
        # If all staged files are planning docs (or no staged files provided), allow commit
        return None

    if task_state not in implementation_states:
        return (
            f"Cannot commit for task '{task_id}': Task state is '{task_state}'. "
            f"Commits are only permitted in implementation states {implementation_states} "
            f"or during planning with documentation files only."
        )

    # If the caller provided transition history and validation functions, verify execution integrity
    validate_history_fn = ctx.get("validate_transition_history")
    if validate_history_fn is not None:
        history_error = validate_history_fn()
        if history_error:
            return f"Cannot commit for task '{task_id}': Pipeline integrity check failed: {history_error}"

    return None


# --- Controlled-operation rules, keyed by operation name (not a lifecycle transition) ---
OPERATION_RULES: Dict[str, List[Dict[str, Any]]] = {
    "worktree_push": [{"check": "predicate", "fn": _worktree_push_check}],
    "commit": [{"check": "predicate", "fn": _task_commit_check}],
}


# --- Closed Check Registry: check_id -> callable predicate ---
CHECK_REGISTRY: Dict[str, Any] = {
    "prior_art_scan": _prior_art_check,
    "interview_trivial_complete": _interview_trivial_check,
    "interview_standard_complete": _interview_standard_check,
    "plan_mode_or_socratic": lambda ctx: (
        None if _gate_any_of(ctx, [
            {"type": "receipt", "gate_name": "plan_mode_entry"},
            {"type": "receipt", "gate_name": "socratic_intake_complete"},
        ]) else (
            "Cannot advance: no proof Plan Mode was entered or Socratic intake completed. "
            "Call record_plan_mode_entry() or record_socratic_intake_complete() first."
        )
    ),
    "critic_review_or_skip": lambda ctx: (
        None if _gate_any_of(ctx, [
            {"type": "critic_review_pass"},
            {"type": "receipt", "gate_name": "multi_agent_review_skipped"},
        ]) else (
            "Cannot advance: no passing critic review or explicit recorded skip found. "
            "Call record_critic_review(verdict='PASS') or record_review_skip()."
        )
    ),
    "critic_review_pass": lambda ctx: (
        None if _gate_critic_review_pass(ctx) else (
            "Cannot advance: no passing critic review found. Call record_critic_review(verdict='PASS')."
        )
    ),
    "human_approval": lambda ctx: (
        None if _gate_receipt_exists(ctx, "human_approval") else (
            "Cannot advance: no recorded human_approval receipt found. "
            "Call record_human_approval() — this gate can never be skipped."
        )
    ),
    "test_suite": lambda ctx: (
        None if _gate_receipt_exists(ctx, "test_suite") else (
            "Cannot advance: no recorded test_suite verification receipt found. "
            "Call record_verification_receipt(gate_name='test_suite', ...)."
        )
    ),
    "code_review_or_skip": lambda ctx: (
        None if _gate_any_of(ctx, [
            {"type": "critic_review_pass"},
            {"type": "receipt", "gate_name": "multi_agent_code_review_skipped"},
        ]) else (
            "Cannot advance: no passing critic review or explicit recorded skip found. "
            "Call record_critic_review(verdict='PASS') or record_review_skip()."
        )
    ),
    "done_guard": _done_check,
    "retrospective_done_guard": _retrospective_done_check,
    "rolled_back_guard": _rolled_back_check,
}


def get_registered_check_ids() -> List[str]:
    """Returns a list of all registered deterministic check IDs."""
    return list(CHECK_REGISTRY.keys())


def evaluate_check(check_id: str, ctx: Dict[str, Any]) -> None:
    """Evaluates a single check by its check_id. Raises PolicyViolation if check fails,
    or PolicyConfigurationError if check_id is unrecognized."""
    if check_id not in CHECK_REGISTRY:
        raise PolicyConfigurationError(f"Unknown check_id: '{check_id}'")
    fn = CHECK_REGISTRY[check_id]
    error = fn(ctx)
    if error is not None:
        raise PolicyViolation(error)


def evaluate_operation(ctx: Dict[str, Any], operation_name: str) -> None:
    """Evaluates every rule registered for the given controlled operation (e.g.
    'worktree_push'). Raises PolicyViolation on the first failing rule."""
    if operation_name not in OPERATION_RULES:
        raise PolicyConfigurationError(f"Unknown operation: '{operation_name}'")
    for rule in OPERATION_RULES.get(operation_name, []):
        error = rule["fn"](ctx)
        if error is not None:
            raise PolicyViolation(error)


def _run_rule(ctx: Dict[str, Any], rule: Dict[str, Any]) -> None:
    """Dispatches a single rule spec by its `check` type. Raises PolicyViolation if the
    rule's predicate fails, or PolicyConfigurationError if `check` is unrecognized — fails
    closed on a misconfigured rule rather than silently passing (see PolicyConfigurationError
    docstring)."""
    check_type = rule.get("check")
    if check_type == "predicate":
        error = rule["fn"](ctx)
        if error is not None:
            raise PolicyViolation(error)
        return
    raise PolicyConfigurationError(f"Unknown policy check type: '{check_type}'")


def evaluate_transition(ctx: Dict[str, Any], from_state: str, to_state: str) -> None:
    """Evaluates the small set of legacy lifecycle-edge rules that predate the
    template-driven deterministic_checks/CHECK_REGISTRY path in coordinator.py (prior art,
    done, rolled back guards). A no-op for any other edge — everything else is governed
    entirely by CHECK_REGISTRY via evaluate_check(), driven from transition_templates.yaml.

    Deliberately no module-level TRANSITION_RULES/TO_STATE_RULES table here (Architecture
    Review Finding 6, see test_policy_py_contains_no_transition_rules_or_to_state_rules) —
    this local mapping exists only inside this function, routing through the same
    CHECK_REGISTRY functions _prior_art_check/_done_check/_rolled_back_check already use."""
    edge_to_check_fn = {
        ("INTAKE", "INTERVIEW"): _prior_art_check,
        ("VERIFY_EXIT", "DONE"): _done_check,
        ("IN_WORKTREE", "ROLLED_BACK"): _rolled_back_check,
    }
    fn = edge_to_check_fn.get((from_state, to_state))
    if fn is not None:
        _run_rule(ctx, {"check": "predicate", "fn": fn})
