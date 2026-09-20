"""
control_plane/constants.py -- Single Shared Source for Cross-File Domain Constants
====================================================================================

Purpose:
    One shared module for every named constant that means something specific to the
    control-plane's domain and is referenced from more than one file (production or
    test). Every consumer imports from here rather than retyping the literal or
    defining a second, independent copy of the same value elsewhere. Replaces an
    earlier per-module-colocation convention after review found that split ownership
    (state names in state_machine.py, decision types in adapters.py, etc.) still left
    consumers guessing which file to import from -- one shared file removes that
    ambiguity (per config-driven-constants-over-hardcoding.md).

Layer:
    OS Kernel / Execution Control Plane Substrate -- Domain constants (no logic).

Key Input Dependencies:
    None -- pure constant definitions, no I/O, no imports from sibling control_plane
    modules (this file must stay a leaf so anything can import it without a cycle).

Key Contents (grouped by domain; see each section for what enforces/consumes it):
    - STATE_* / CANONICAL_STATE_NAMES -- the 15 task lifecycle state names. The
      adjacency DAG (ALLOWED_TRANSITIONS) and CANONICAL_STATES list built from these
      still live in state_machine.py, since that IS domain logic, not just a constant.
    - DECISION_TYPE_* / DECISION_TYPES -- transition_decisions.decision_type values.
    - ACTOR_* -- the three recognized actor values (human/agent/system).
    - COST_TIER_* / COST_TIERS -- model capability cost tiers.
    - CONFIRMATION_STATUS_* -- source_assisted_answer_candidates confirmation states.
    - GATE_* / SKIPPED_REVIEW_GATE_NAMES_SQL -- verification_receipts gate names for
      the multi-agent review skip path.
    - ERROR_CODE_* -- record_interview_question.py's denial-envelope error codes.
    - GUIDANCE_COMPLIANCE_CONFIRM_ANSWER -- the one accepted answer to the mandatory
      guidance-compliance confirmation question (see coordinator.py).
    - REASON_* -- free-text, non-enforced reason/label strings reused across test call
      sites (e.g. "interview complete", "Worktree created"). Not constrained by any
      production CHECK/comparison, but still defined once here rather than in a
      separate test-only file, per the "one shared file for everything reused across
      files" direction -- tests/interview_helpers.py re-exports them for backward
      compatibility with existing `from interview_helpers import REASON_*` call sites.
    - sql_in_list() -- helper used to render a constants tuple as a SQL `IN (...)`
      literal list for SCHEMA_SQL in adapters.py.
"""

from typing import Iterable

# --- Task lifecycle state names -------------------------------------------------
# The adjacency DAG (ALLOWED_TRANSITIONS) and the ordered CANONICAL_STATES list built
# from these constants live in state_machine.py (domain logic owns the DAG shape);
# state_machine.py imports the names below rather than redefining them.
STATE_INTAKE = "INTAKE"
STATE_INTERVIEW = "INTERVIEW"
STATE_DRAFT_PLAN = "DRAFT_PLAN"
STATE_MULTI_AGENT_REVIEW = "MULTI_AGENT_REVIEW"
STATE_PLAN_REVIEW = "PLAN_REVIEW"
STATE_AWAITING_APPROVAL = "AWAITING_APPROVAL"
STATE_APPROVED = "APPROVED"
STATE_IN_WORKTREE = "IN_WORKTREE"
STATE_WORKTREE_REVIEW = "WORKTREE_REVIEW"
STATE_MULTI_AGENT_CODE_REVIEW = "MULTI_AGENT_CODE_REVIEW"
STATE_VERIFY_EXIT = "VERIFY_EXIT"
STATE_RETROSPECTIVE = "RETROSPECTIVE"
STATE_DONE = "DONE"
STATE_ROLLED_BACK = "ROLLED_BACK"
STATE_ESCALATED = "ESCALATED"

CANONICAL_STATE_NAMES = (
    STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW,
    STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE,
    STATE_WORKTREE_REVIEW, STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT,
    STATE_RETROSPECTIVE, STATE_DONE, STATE_ROLLED_BACK, STATE_ESCALATED,
)

# --- transition_decisions.decision_type ------------------------------------------
DECISION_TYPE_ANSWER = "ANSWER"
DECISION_TYPE_APPROVAL = "APPROVAL"
DECISION_TYPE_REJECTION = "REJECTION"
DECISION_TYPE_SKIP = "SKIP"
DECISION_TYPE_CONFIRMATION = "CONFIRMATION"
DECISION_TYPE_RESET = "RESET"
DECISION_TYPES = (
    DECISION_TYPE_ANSWER, DECISION_TYPE_APPROVAL, DECISION_TYPE_REJECTION,
    DECISION_TYPE_SKIP, DECISION_TYPE_CONFIRMATION, DECISION_TYPE_RESET,
)

# --- Actors -----------------------------------------------------------------------
ACTOR_HUMAN = "human"
ACTOR_AGENT = "agent"
ACTOR_SYSTEM = "system"

# --- Per-edge authorized-actor classification (auth-ciba-poc-transition-mechanics,
# issues #621/#626/#634) -- derived from each edge's approval block at registry-load
# time (TransitionTemplate.authorized_actor), not a hand-maintained parallel field.
AUTHORIZED_ACTOR_HUMAN_ONLY = "human_only"
AUTHORIZED_ACTOR_AGENT_OR_HUMAN = "agent_or_human"

# --- Model capability cost tiers ---------------------------------------------------
COST_TIER_LOW = "low"
COST_TIER_MEDIUM = "medium"
COST_TIER_HIGH = "high"
COST_TIERS = (COST_TIER_LOW, COST_TIER_MEDIUM, COST_TIER_HIGH)

# --- source_assisted_answer_candidates.confirmation_status -------------------------
CONFIRMATION_STATUS_PENDING = "pending"
CONFIRMATION_STATUS_CONFIRMED = "confirmed"

# --- tasks.task_type -----------------------------------------------------------------
TASK_TYPE_GENERAL = "GENERAL"
TASK_TYPE_EVOLUTION = "EVOLUTION"
TASK_TYPES = (TASK_TYPE_GENERAL, TASK_TYPE_EVOLUTION)

# --- tasks.worktree_state -- the exact 6-state vocabulary from
# worktree-lifecycle-management.md's "Six States" section; keep in sync with that doc.
WORKTREE_STATE_WRITTEN_IN_WORKTREE = "written_in_worktree"
WORKTREE_STATE_COMMITTED_IN_WORKTREE = "committed_in_worktree"
WORKTREE_STATE_PUSHED_TO_ORIGIN = "pushed_to_origin"
WORKTREE_STATE_MERGED_INTO_ORIGIN_MAIN = "merged_into_origin_main"
WORKTREE_STATE_LOCAL_BRANCH_REF_UPDATED = "local_branch_ref_updated"
WORKTREE_STATE_CHECKED_OUT_ON_DISK = "checked_out_on_disk"
WORKTREE_STATES = (
    WORKTREE_STATE_WRITTEN_IN_WORKTREE, WORKTREE_STATE_COMMITTED_IN_WORKTREE,
    WORKTREE_STATE_PUSHED_TO_ORIGIN, WORKTREE_STATE_MERGED_INTO_ORIGIN_MAIN,
    WORKTREE_STATE_LOCAL_BRANCH_REF_UPDATED, WORKTREE_STATE_CHECKED_OUT_ON_DISK,
)

# --- proof-required edges (auth-ciba-increment-b T4, issue #639) -------------------------

# --- verification_receipts gate names (multi-agent review skip path) ---------------
GATE_MULTI_AGENT_REVIEW_SKIPPED = "multi_agent_review_skipped"
GATE_MULTI_AGENT_CODE_REVIEW_SKIPPED = "multi_agent_code_review_skipped"
SKIPPED_REVIEW_GATE_NAMES = (GATE_MULTI_AGENT_REVIEW_SKIPPED, GATE_MULTI_AGENT_CODE_REVIEW_SKIPPED)

# --- critic_reviews.verdict ---------------------------------------------------------
CRITIC_VERDICT_PASS = "PASS"
CRITIC_VERDICT_REVISE = "REVISE"
CRITIC_VERDICT_REJECT = "REJECT"
CRITIC_VERDICTS = (CRITIC_VERDICT_PASS, CRITIC_VERDICT_REVISE, CRITIC_VERDICT_REJECT)

# --- asymmetric_persistence_log.status -----------------------------------------------
PERSISTENCE_LOG_STATUS_OBSERVED = "OBSERVED"
PERSISTENCE_LOG_STATUS_HYPOTHESIS = "HYPOTHESIS"
PERSISTENCE_LOG_STATUS_CONFIRMED = "CONFIRMED"
PERSISTENCE_LOG_STATUS_RESOLVED = "RESOLVED"
PERSISTENCE_LOG_STATUSES = (
    PERSISTENCE_LOG_STATUS_OBSERVED, PERSISTENCE_LOG_STATUS_HYPOTHESIS,
    PERSISTENCE_LOG_STATUS_CONFIRMED, PERSISTENCE_LOG_STATUS_RESOLVED,
)

# --- retrospective_entries.decision / .completion_mode -------------------------------
RETROSPECTIVE_DECISION_OPT_IN = "opt_in"
RETROSPECTIVE_DECISION_SKIP = "skip"
RETROSPECTIVE_DECISIONS = (RETROSPECTIVE_DECISION_OPT_IN, RETROSPECTIVE_DECISION_SKIP)

RETROSPECTIVE_COMPLETION_MODE_DRAFT = "draft"
RETROSPECTIVE_COMPLETION_MODE_COMPLETED = "completed"
RETROSPECTIVE_COMPLETION_MODE_SKIPPED = "skipped"
RETROSPECTIVE_COMPLETION_MODES = (
    RETROSPECTIVE_COMPLETION_MODE_DRAFT, RETROSPECTIVE_COMPLETION_MODE_COMPLETED,
    RETROSPECTIVE_COMPLETION_MODE_SKIPPED,
)

# --- retrospective_follow_ups.kind / .status ------------------------------------------
FOLLOW_UP_KIND_DIRECT = "direct"
FOLLOW_UP_KIND_ISSUE = "issue"
FOLLOW_UP_KINDS = (FOLLOW_UP_KIND_DIRECT, FOLLOW_UP_KIND_ISSUE)

FOLLOW_UP_STATUS_PROPOSED = "proposed"
FOLLOW_UP_STATUS_CONFIRMED = "confirmed"
FOLLOW_UP_STATUS_REJECTED = "rejected"
FOLLOW_UP_STATUS_CREATED = "created"
FOLLOW_UP_STATUSES = (
    FOLLOW_UP_STATUS_PROPOSED, FOLLOW_UP_STATUS_CONFIRMED,
    FOLLOW_UP_STATUS_REJECTED, FOLLOW_UP_STATUS_CREATED,
)

# --- delegation_contracts.status -----------------------------------------------------
DELEGATION_STATUS_PENDING_APPROVAL = "PENDING_APPROVAL"
DELEGATION_STATUS_APPROVED = "APPROVED"
DELEGATION_STATUS_EXECUTING = "EXECUTING"
DELEGATION_STATUS_ACCEPTED = "ACCEPTED"
DELEGATION_STATUS_REJECTED = "REJECTED"
DELEGATION_STATUSES = (
    DELEGATION_STATUS_PENDING_APPROVAL, DELEGATION_STATUS_APPROVED,
    DELEGATION_STATUS_EXECUTING, DELEGATION_STATUS_ACCEPTED, DELEGATION_STATUS_REJECTED,
)

# --- ModelCatalogAdapter heuristics --------------------------------------------------
DISALLOWED_MODEL_STATUSES = frozenset({"withdrawn", "deprecated", "unavailable"})
STRATEGY_FALLBACK_KEYS = ("complex_reasoning", "architecture", "default")

# Tool key -> (canonical cli_id, catalog filename). Aliases map many recognized spellings
# of the same runtime tool onto one canonical id; unrecognized/missing tool_key falls back
# to "copilot" (ModelCatalogAdapter._resolve_tool_catalog's own default, not encoded here).
TOOL_CATALOG_ALIASES = {
    "claude": ("claude", "claude-models.json"),
    "claude-code": ("claude", "claude-models.json"),
    "copilot": ("copilot", "copilot-models.json"),
    "github-copilot": ("copilot", "copilot-models.json"),
    "antigravity": ("agy", "agy-models.json"),
    "agy": ("agy", "agy-models.json"),
    "gemini": ("agy", "agy-models.json"),
    "codex": ("codex", "codex-models.json"),
    "openai": ("codex", "codex-models.json"),
}

# --- Special transition_decisions question IDs referenced from
# the enforce_valid_transition trigger (defined twice in adapters.py: once in the
# fresh-create SCHEMA_SQL, once in _rebuild_schema_transactional()'s trigger
# recreation) -- both derive from these so they can never drift apart from each other.
QUESTION_ID_RETROSPECTIVE_DECISION = "retrospective_decision"
# (Removed 2026-09-20: QUESTION_ID_FORCE_CLOSE_AUTHORIZATION, QUESTION_ID_HUMAN_FORCE_DONE_CONFIRMATION,
# ANSWER_FORCE_CLOSE, ANSWER_FORCE_DONE -- every edge into DONE now takes a cryptographic signature.)

# --- record_interview_question.py denial-envelope error codes ----------------------
ERROR_CODE_CAPABILITY_DENIED = "CAPABILITY_DENIED"
ERROR_CODE_CONTRACT_DENIED = "CONTRACT_DENIED"
ERROR_CODE_PERSISTENCE_DENIED = "PERSISTENCE_DENIED"

# --- coordinator.py mandatory guidance-compliance confirmation ---------------------
GUIDANCE_COMPLIANCE_CONFIRM_ANSWER = "YES"


# --- Test-only free-text reason/label strings ---------------------------------------
# Not enforced by any production CHECK constraint -- these exist purely so test call
# sites read as intent ("why is this transition happening") instead of retyping the
# same literal per test file. Kept in this same shared file (not a separate one) per
# explicit direction: one shared constants module for everything reused across files,
# production or test, rather than splitting by production/test boundary.
REASON_INTERVIEW_COMPLETE = "interview complete"
REASON_WORKTREE_CREATED = "Worktree created"
REASON_WORKTREE_ISOLATED = "Worktree isolated"
REASON_NOT_NEEDED_FOR_TEST = "Not needed for this test"
REASON_PLAN_DISPOSITION = "plan disposition"
REASON_ENTER_DRAFT_PLAN = "Enter draft plan"
REASON_ATTEMPT_COMPLETE = "Attempt complete"


def sql_in_list(values: Iterable[str]) -> str:
    """Renders a tuple of plain string constants as a SQL `IN (...)` literal list,
    e.g. ('a', 'b') -> "'a', 'b'". Used to build SCHEMA_SQL (the current fresh-create
    schema in adapters.py) from these constants -- never used on SCHEMA_MIGRATIONS,
    which is an immutable historical record and must keep its own literal strings."""
    return ", ".join(f"'{v}'" for v in values)
