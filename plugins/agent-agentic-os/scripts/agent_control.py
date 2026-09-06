#!/usr/bin/env python3
"""
agent_control.py — Lightweight SQLite Control Plane for Agent Lifecycle
========================================================================

Purpose:
    ACID state machine and audit log for task execution, verifier sovereignty,
    pre-execution review gating, worktree 6-state tracking, and cryptographic
    receipt generation across multi-tool agent environments.

Architecture (issue-524, hexagonal decomposition):
    ControlPlane is a backward-compatible facade over 4 composed ports/adapters, so external
    callers (CLI, init_agentic_os.py, tests) see no change in the public constructor, method
    names, or CLI behavior — only the internals moved. ControlPlane's own remaining code is
    task/transition/receipt CRUD orchestration and tier-selection logic; every direct
    infrastructure concretion (SQLite connection/migration, filesystem writes, SHA256 hashing,
    model-catalog JSON reads) now lives behind a port, and all gate/policy logic lives in
    control_plane/policy.py (a pure domain module — see the Gate Policy section below):
      - self._fs            -> control_plane.adapters.FilesystemAdapter   (FilesystemPort)
      - self._crypto         -> control_plane.adapters.CryptoAdapter       (CryptoPort)
      - self._model_catalog -> control_plane.adapters.ModelCatalogAdapter (ModelCatalogPort)
      - self._persistence   -> control_plane.adapters.SqlitePersistenceAdapter (connection +
                                 schema migration only; task/transition/receipt CRUD queries
                                 remain here in ControlPlane, a deliberate, plan-documented
                                 scope boundary — see docs/plans/issue-524-spec.md Section 5)
    Every adapter is constructor-injectable for testing (e.g. `ControlPlane(crypto_adapter=...)`)
    while defaulting to the real infrastructure implementation for all existing callers.

Layer:
    OS Kernel / Execution Control Plane Substrate

Key Input Dependencies:
    - SQLite database: context/control_plane.db (auto-initialized with WAL mode)
    - Optional model catalog references: plugins/cli-agents/references/*.json

Key Functions:
    - ControlPlane.init_db() — Initializes tables and WAL mode
    - ControlPlane.resolve_recommended_model() — Resolves model tier recommendations
    - ControlPlane.create_task() — Creates task in INTAKE
    - ControlPlane.get_task() — Retrieves task record
    - ControlPlane.transition() — Validates and transitions canonical DAG state
    - ControlPlane.lock_verifiers() — Locks SHA256 baseline hashes of verifier files
    - ControlPlane.verify_sovereignty() — Ensures verifier hashes have not been mutated
    - ControlPlane.record_critic_review() — Logs pre-execution review outcomes
    - ControlPlane.record_verification_receipt() — Stamps deterministic exit receipts
    - ControlPlane.get_verification_receipts() — Retrieves verification receipts
    - ControlPlane.update_worktree() — Updates worktree path, branch, and 6-state status
    - ControlPlane.log_asymmetric_persistence() — Logs Layer 2 wiki/map-debt persistence
    - ControlPlane.record_plan_mode_entry() — Records proof Plan Mode was entered (DRAFT_PLAN gate)
    - ControlPlane.record_socratic_intake_complete() — Records proof Socratic intake completed (DRAFT_PLAN gate)
    - ControlPlane.record_human_approval() — Records the human approval receipt (APPROVED->IN_WORKTREE gate, never skippable)
    - ControlPlane.record_review_skip() — Records an explicit, auditable decision to skip a discretionary review phase
    - main() — CLI dispatcher entry point

Usage Examples:
    python3 agent_control.py init --task-id <id> --title <title> --runtime <tool> [--task-type EVOLUTION]
    python3 agent_control.py transition --task-id <id> --to <state> --reason <text>
    python3 agent_control.py lock-verifiers --task-id <id> --paths <file1,file2>
    python3 agent_control.py verify-sovereignty --task-id <id>
    python3 agent_control.py record-receipt --task-id <id> --gate <g> --cmd "<c>" --exit-code <ec>
    python3 agent_control.py update-worktree --task-id <id> --path <p> --branch <b> --state <s>
    python3 agent_control.py status --task-id <id>
    python3 agent_control.py log-prior-art --task-id <id> --summary <text> [--repeat-yes-entries <csv>]
    python3 agent_control.py record-plan-mode-entry --task-id <id> --actor <a>
    python3 agent_control.py record-socratic-intake --task-id <id> --summary <text>
    python3 agent_control.py record-human-approval --task-id <id> --approver <a>
    python3 agent_control.py record-review-skip --task-id <id> --phase <p> --actor <a> --reason <text>

Gate Policy (unified, issue-524 Step 4):
    All gate/policy enforcement — per-edge transition requirements (formerly GATE_REQUIREMENTS),
    the prior-art/done/rolled-back guards (formerly 3 hardcoded _check_*_guard methods), and the
    worktree-push operation guard (formerly update_worktree()'s own independent barrier) — now
    resolves through ONE declarative policy-evaluation mechanism in control_plane/policy.py.
    See that module's TRANSITION_RULES/TO_STATE_RULES (lifecycle transitions) and
    OPERATION_RULES (controlled operations like the worktree push) for the full registry.
    Discretionary review phases (multi_agent_review, multi_agent_code_review) still accept an
    explicit recorded skip (record_review_skip) as an alternative to a real critic review —
    skips are never silent.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from control_plane.ports import FilesystemPort, CryptoPort, ModelCatalogPort
from control_plane.adapters import (
    FilesystemAdapter, SqlitePersistenceAdapter, CryptoAdapter, ModelCatalogAdapter,
    CURRENT_SCHEMA_VERSION,
)
from control_plane import policy as _policy

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
    "DONE",
    "ROLLED_BACK",
    "ESCALATED"
]

WORKTREE_STATES = [
    "written_in_worktree",
    "committed_in_worktree",
    "pushed_to_origin",
    "merged_into_origin_main",
    "local_branch_ref_updated",
    "checked_out_on_disk"
]

ALLOWED_TRANSITIONS = {
    "INTAKE": ["INTERVIEW", "DRAFT_PLAN", "PLAN_REVIEW", "ESCALATED"],
    "INTERVIEW": ["DRAFT_PLAN", "PLAN_REVIEW", "ESCALATED"],
    "DRAFT_PLAN": ["MULTI_AGENT_REVIEW", "PLAN_REVIEW", "AWAITING_APPROVAL", "INTERVIEW", "ESCALATED"],
    "MULTI_AGENT_REVIEW": ["DRAFT_PLAN", "PLAN_REVIEW", "AWAITING_APPROVAL", "ESCALATED"],
    "PLAN_REVIEW": ["MULTI_AGENT_REVIEW", "AWAITING_APPROVAL", "DRAFT_PLAN", "INTERVIEW", "ESCALATED"],
    "AWAITING_APPROVAL": ["APPROVED", "MULTI_AGENT_REVIEW", "PLAN_REVIEW", "DRAFT_PLAN", "ESCALATED"],
    "APPROVED": ["IN_WORKTREE", "ESCALATED"],
    "IN_WORKTREE": ["WORKTREE_REVIEW", "VERIFY_EXIT", "ROLLED_BACK", "ESCALATED"],
    "WORKTREE_REVIEW": ["MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT", "IN_WORKTREE", "ROLLED_BACK", "ESCALATED"],
    "MULTI_AGENT_CODE_REVIEW": ["WORKTREE_REVIEW", "VERIFY_EXIT", "IN_WORKTREE", "ROLLED_BACK", "ESCALATED"],
    "VERIFY_EXIT": ["DONE", "IN_WORKTREE", "WORKTREE_REVIEW", "ROLLED_BACK", "ESCALATED"],
    "DONE": [],
    "ROLLED_BACK": ["ESCALATED", "PLAN_REVIEW"],
    "ESCALATED": ["INTAKE", "PLAN_REVIEW"]
}

# SCHEMA_SQL, CURRENT_SCHEMA_VERSION, CHILD_TABLES, ALL_REBUILD_TABLES, and SCHEMA_MIGRATIONS
# moved to control_plane/adapters.py's SqlitePersistenceAdapter (issue-524 Step 5). This module
# re-imports CURRENT_SCHEMA_VERSION above for backward-compatible `from agent_control import
# CURRENT_SCHEMA_VERSION` (existing test/consumer import surface, unchanged).


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class VerifierSovereigntyViolation(Exception):
    """Raised when a protected verifier file has been tampered with."""
    pass


class PersistenceInvariantViolation(Exception):
    """Raised when evolution integrity or asymmetric persistence invariants are violated."""
    pass


class ConcurrentModificationError(Exception):
    """Raised when a transition's expected prior state no longer matches the stored row,
    indicating a concurrent writer changed it — never silently overwritten (no last-writer-wins)."""
    pass


# Gate/policy enforcement (per-edge transition requirements, prior-art/done/rolled-back
# guards, and the worktree-push operation guard) is unified in control_plane/policy.py's
# TRANSITION_RULES / TO_STATE_RULES / OPERATION_RULES (issue-524 Step 4). This module no
# longer declares its own gate registry.


class ControlPlane:
    """Controller and state machine manager for task lifecycles."""

    def __init__(self, db_path: Optional[Path] = None, fs_adapter: Optional["FilesystemPort"] = None,
                 crypto_adapter: Optional["CryptoPort"] = None,
                 model_catalog_adapter: Optional["ModelCatalogPort"] = None):
        """Initializes the ControlPlane instance. Connection management and schema migration
        are delegated to a SqlitePersistenceAdapter (issue-524 Step 5); SHA256/receipt-token
        hashing is delegated to a CryptoAdapter (issue-524 Step 6); model-catalog JSON file
        reads are delegated to a ModelCatalogAdapter (issue-524 Step 7). `self.db_path` is kept
        as a convenience property mirroring the persistence adapter's resolved path, for any
        code that introspects it directly. All optional parameters default to real
        infrastructure adapters; tests/callers can substitute different Port implementations
        without touching disk/hashing — public callers relying on the default constructor
        signature are unaffected (backward-compatible facade, per
        docs/plans/issue-524-spec.md Section 3)."""
        self._fs = fs_adapter if fs_adapter is not None else FilesystemAdapter()
        self._crypto = crypto_adapter if crypto_adapter is not None else CryptoAdapter()
        self._model_catalog = model_catalog_adapter if model_catalog_adapter is not None else ModelCatalogAdapter()
        self._persistence = SqlitePersistenceAdapter(
            db_path if db_path is None else Path(db_path), self._fs
        )
        self.db_path = self._persistence.db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured sqlite3 connection. Delegates to the SqlitePersistenceAdapter."""
        return self._persistence.get_connection()

    def init_db(self):
        """Initializes SQLite tables and WAL mode. Delegates to the SqlitePersistenceAdapter,
        which self-heals FK-corrupted or legacy schemas."""
        self._persistence.ensure_schema()

    def _resolve_tool_catalog(self, runtime_tool: str, cli_refs: Path) -> tuple:
        """Resolves tool alias and catalog file path."""
        tool_key = runtime_tool.lower()
        if tool_key in ("claude", "claude-code"):
            return "claude", cli_refs / "claude-models.json"
        if tool_key in ("copilot", "github-copilot"):
            return "copilot", cli_refs / "copilot-models.json"
        if tool_key in ("antigravity", "agy", "gemini"):
            return "agy", cli_refs / "agy-models.json"
        if tool_key in ("codex", "openai"):
            return "codex", cli_refs / "codex-models.json"
        return "copilot", cli_refs / "copilot-models.json"

    def _pick_tier_model(self, cat_data: Dict[str, Any], tier: str, cheapest_model: Optional[str]) -> Optional[str]:
        """Picks a model ID from catalog strategy and cost tiers."""
        strategy = cat_data.get("strategy", {})
        cost_tiers = cat_data.get("cost_tiers", {})
        if tier == "low":
            return cheapest_model or strategy.get("heartbeat") or strategy.get("default")
        if tier == "medium":
            return strategy.get("default") or (cost_tiers.get("moderate", [None])[0] if "moderate" in cost_tiers else None)
        return strategy.get("complex_reasoning") or strategy.get("architecture") or strategy.get("default")

    def resolve_recommended_model(self, runtime_tool: str, tier: str = "low") -> Dict[str, str]:
        """Resolves model recommendation and model_id from plugins/cli-agents/references/."""
        tier = tier.lower() if tier.lower() in ("low", "medium", "high") else "low"
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        cli_refs = repo_root / "plugins" / "cli-agents" / "references"
        tool_key, catalog_file = self._resolve_tool_catalog(runtime_tool, cli_refs)

        cheapest_file = cli_refs / "cheapest_models.json"
        cheapest_model = self._model_catalog.load_cheapest(cheapest_file, tool_key)

        selected_model = None
        cat_data = self._model_catalog.load_catalog(catalog_file)
        if cat_data is not None:
            selected_model = self._pick_tier_model(cat_data, tier, cheapest_model)

        return {
            "runtime_tool": runtime_tool,
            "tier": tier,
            "model_id": selected_model or cheapest_model or "gpt-5.4-nano"
        }

    def create_task(
        self,
        task_id: str,
        title: str,
        runtime_tool: str,
        spec_path: Optional[str] = None,
        model_tier: Optional[str] = None,
        model_id: Optional[str] = None,
        task_type: str = "GENERAL"
    ):
        """Creates a new task in INTAKE state and records creation transition."""
        self.init_db()
        if task_type not in ("GENERAL", "EVOLUTION"):
            raise ValueError(f"Invalid task_type '{task_type}'. Must be 'GENERAL' or 'EVOLUTION'.")
        if model_tier and not model_id:
            rec = self.resolve_recommended_model(runtime_tool=runtime_tool, tier=model_tier)
            model_id = rec["model_id"]

        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO tasks (task_id, title, state, task_type, runtime_tool, spec_path, model_tier, model_id)
                    VALUES (?, ?, 'INTAKE', ?, ?, ?, ?, ?)
                    """,
                    (task_id, title, task_type, runtime_tool, spec_path, model_tier, model_id)
                )
                conn.execute(
                    """
                    INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason)
                    VALUES (?, 'NONE', 'INTAKE', 'system', 'Task created')
                    """,
                    (task_id,)
                )
        finally:
            conn.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a task dictionary by task_id."""
        self.init_db()
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def _build_transition_policy_ctx(self, conn: sqlite3.Connection, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Builds the ctx dict consumed by control_plane.policy's transition/to-state rules.
        Every SQL query here is behavior-identical to what the pre-Step-4 hardcoded guards
        and GATE_REQUIREMENTS registry issued directly — this method is the sole remaining
        place that translates policy needs into SQL, until persistence is extracted (Step 5)."""

        def has_receipt(gate_name: str) -> bool:
            return conn.execute(
                "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ?",
                (task_id, gate_name)
            ).fetchone()[0] > 0

        def has_passing_critic_review() -> bool:
            return conn.execute(
                "SELECT COUNT(*) FROM critic_reviews WHERE task_id = ? AND verdict = 'PASS'",
                (task_id,)
            ).fetchone()[0] > 0

        def count_receipts(gate_name: str, exit_code: Optional[int] = None) -> int:
            if exit_code is None:
                return conn.execute(
                    "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ?",
                    (task_id, gate_name)
                ).fetchone()[0]
            return conn.execute(
                "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ? AND exit_code = ?",
                (task_id, gate_name, exit_code)
            ).fetchone()[0]

        def count_locked_verifiers() -> int:
            return conn.execute(
                "SELECT COUNT(*) FROM locked_verifier_baselines WHERE task_id = ?", (task_id,)
            ).fetchone()[0]

        def count_asymmetric_persistence(details_like: Optional[str] = None,
                                          destination_like_any: Optional[List[str]] = None) -> int:
            if details_like is not None:
                return conn.execute(
                    "SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ? AND details LIKE ?",
                    (task_id, details_like)
                ).fetchone()[0]
            if destination_like_any is not None:
                clause = " OR ".join(["destination LIKE ?"] * len(destination_like_any))
                return conn.execute(
                    f"SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ? AND ({clause})",
                    (task_id, *destination_like_any)
                ).fetchone()[0]
            return conn.execute(
                "SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ?", (task_id,)
            ).fetchone()[0]

        return {
            "task_id": task_id,
            "task": task,
            "has_receipt": has_receipt,
            "has_passing_critic_review": has_passing_critic_review,
            "count_receipts": count_receipts,
            "count_locked_verifiers": count_locked_verifiers,
            "count_asymmetric_persistence": count_asymmetric_persistence,
            "verify_sovereignty": lambda: self.verify_sovereignty(task_id),
        }

    def transition(self, task_id: str, to_state: str, actor: str, reason: str):
        """Validates and applies a state transition according to the canonical DAG."""
        if to_state not in CANONICAL_STATES:
            raise InvalidStateTransition(f"Unknown state: {to_state}")

        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        conn = self._get_connection()
        try:
            # Authoritative state read, done once via conn — both the adjacency check and
            # the final guarded UPDATE use this same value, closing the race window between
            # them (a concurrent writer changing the row after this point is caught by the
            # UPDATE's WHERE predicate rather than silently overwritten).
            current_state = self._read_current_state_for_update(conn, task_id)
            if current_state is None:
                raise ValueError(f"Task not found: {task_id}")

            allowed = ALLOWED_TRANSITIONS.get(current_state, [])
            if to_state not in allowed:
                raise InvalidStateTransition(
                    f"Cannot transition task '{task_id}' from '{current_state}' to '{to_state}'. Allowed: {allowed}"
                )

            # --- Unified gate policy: lifecycle transition rules + to-state-wide guards ---
            ctx = self._build_transition_policy_ctx(conn, task_id, task)
            try:
                _policy.evaluate_transition(ctx, current_state, to_state)
            except _policy.PolicyViolation as e:
                raise PersistenceInvariantViolation(str(e)) from e

            with conn:
                cursor = conn.execute(
                    "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ? AND state = ?",
                    (to_state, task_id, current_state)
                )
                if cursor.rowcount == 0:
                    raise ConcurrentModificationError(
                        f"Task '{task_id}' state changed concurrently (expected '{current_state}'). Retry."
                    )
                conn.execute(
                    "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, ?, ?, ?, ?)",
                    (task_id, current_state, to_state, actor, reason)
                )
        finally:
            conn.close()


    def lock_verifiers(self, task_id: str, file_paths: List[Path]):
        """Calculates and locks baseline SHA256 hashes of verifier files."""
        self.init_db()
        conn = self._get_connection()
        try:
            with conn:
                for fp in file_paths:
                    p = Path(fp).resolve()
                    if not p.exists():
                        raise FileNotFoundError(f"Verifier file to lock does not exist: {p}")
                    file_sha = self._crypto.sha256_file(p)
                    conn.execute(
                        "INSERT INTO locked_verifier_baselines (task_id, file_path, expected_sha256) VALUES (?, ?, ?)",
                        (task_id, str(p), file_sha)
                    )
        finally:
            conn.close()

    def verify_sovereignty(self, task_id: str) -> bool:
        """Verifies that locked baseline verifiers have not been modified."""
        self.init_db()
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT file_path, expected_sha256 FROM locked_verifier_baselines WHERE task_id = ?",
                (task_id,)
            ).fetchall()
            for r in rows:
                p = Path(r["file_path"])
                if not p.exists():
                    raise VerifierSovereigntyViolation(f"Verifier file missing: {p}")
                curr_sha = self._crypto.sha256_file(p)
                if curr_sha != r["expected_sha256"]:
                    raise VerifierSovereigntyViolation(
                        f"Verifier sovereignty violated! {p} has been mutated. Expected {r['expected_sha256']}, got {curr_sha}"
                    )
            return True
        finally:
            conn.close()

    def record_critic_review(self, task_id: str, iteration: int, model: str, verdict: str, findings: str):
        """Records a clean-context peer critic review iteration and verdict."""
        if verdict not in ("PASS", "REVISE", "REJECT"):
            raise ValueError(f"Invalid verdict: {verdict}")
        self.init_db()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO critic_reviews (task_id, iteration, model_used, verdict, critique_findings)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, iteration, model, verdict, findings)
                )
        finally:
            conn.close()

    def record_verification_receipt(self, task_id: str, gate_name: str, command_executed: str, exit_code: int) -> str:
        """Records a deterministic exit receipt and returns an immutable receipt token."""
        self.init_db()
        raw = f"{task_id}:{gate_name}:{command_executed}:{exit_code}:{time.time()}"
        h = self._crypto.sha256_hex(raw)[:12]
        token = f"EVO-INTEGRITY-{task_id}-{h}"

        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO verification_receipts (task_id, gate_name, command_executed, exit_code, receipt_token)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, gate_name, command_executed, exit_code, token)
                )
            return token
        finally:
            conn.close()

    def record_plan_mode_entry(self, task_id: str, actor: str) -> str:
        """Records proof that native Plan Mode was entered, satisfying the DRAFT_PLAN gate."""
        return self.record_verification_receipt(
            task_id, gate_name="plan_mode_entry", command_executed=f"plan-mode-entered:{actor}", exit_code=0
        )

    def record_socratic_intake_complete(self, task_id: str, summary: str) -> str:
        """Records proof that Socratic Defaulting intake completed, satisfying the DRAFT_PLAN gate."""
        return self.record_verification_receipt(
            task_id, gate_name="socratic_intake_complete", command_executed=f"socratic-intake:{summary}", exit_code=0
        )

    def record_human_approval(self, task_id: str, approver: str) -> str:
        """Records the human approval receipt required for APPROVED -> IN_WORKTREE (never skippable)."""
        return self.record_verification_receipt(
            task_id, gate_name="human_approval", command_executed=f"approved-by:{approver}", exit_code=0
        )

    def record_review_skip(self, task_id: str, phase: str, actor: str, reason: str) -> str:
        """Records an explicit, auditable decision to skip a user-discretionary review phase
        (e.g. multi_agent_review, multi_agent_code_review) — makes the skip visible, never silent."""
        return self.record_verification_receipt(
            task_id, gate_name=f"{phase}_skipped", command_executed=f"user-skip:{actor}:{reason}", exit_code=0
        )

    def _read_current_state_for_update(self, conn: sqlite3.Connection, task_id: str) -> Optional[str]:
        """Reads the task's current state within the active connection, immediately before
        the guarded write — the value used as the WHERE predicate closing the race window."""
        row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return row[0] if row else None

    def get_verification_receipts(self, task_id: str) -> List[Dict[str, Any]]:
        """Retrieves all verification receipts stamped for a given task."""
        self.init_db()
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM verification_receipts WHERE task_id = ?", (task_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_worktree(self, task_id: str, worktree_path: str, worktree_branch: str, worktree_state: str):
        """Updates worktree path, branch, and status using the strict 6-state vocabulary."""
        if worktree_state not in WORKTREE_STATES:
            raise ValueError(f"Invalid worktree state '{worktree_state}'. Must be one of {WORKTREE_STATES}")
        self.init_db()
        conn = self._get_connection()
        try:
            # Unified gate policy: worktree_push is a controlled operation, not a lifecycle
            # transition — evaluated via the same policy engine as transition() (issue-524 Step 4).
            if worktree_state == "pushed_to_origin":
                row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
                if not row:
                    raise ValueError(f"Task not found: {task_id}")
                task_state = row[0]
                op_ctx = {"task_id": task_id, "task_state": task_state}
                try:
                    _policy.evaluate_operation(op_ctx, "worktree_push")
                except _policy.PolicyViolation as e:
                    raise PersistenceInvariantViolation(str(e)) from e

            with conn:
                conn.execute(
                    """
                    UPDATE tasks
                    SET worktree_path = ?, worktree_branch = ?, worktree_state = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                    """,
                    (worktree_path, worktree_branch, worktree_state, task_id)
                )
        finally:
            conn.close()

    def log_asymmetric_persistence(self, task_id: str, destination: str, status: str, details: str):
        """Logs asymmetric Layer 2 persistence entries into the SQLite audit table."""
        self.init_db()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO asymmetric_persistence_log (task_id, destination, status, details)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, destination, status, details)
                )
        finally:
            conn.close()


def _build_parser() -> argparse.ArgumentParser:
    """Constructs and returns CLI argument parser."""
    parser = argparse.ArgumentParser(description="SQLite Control Plane CLI for Agent Lifecycle")
    sub = parser.add_subparsers(dest="subcommand")

    p_init = sub.add_parser("init")
    p_init.add_argument("--task-id", required=True)
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--runtime", default="cli")
    p_init.add_argument("--spec-path", default=None)
    p_init.add_argument("--model-tier", choices=["low", "medium", "high"], default=None)
    p_init.add_argument("--model-id", default=None)
    p_init.add_argument("--task-type", choices=["GENERAL", "EVOLUTION"], default="GENERAL")

    p_rec = sub.add_parser("recommend-model")
    p_rec.add_argument("--runtime", required=True)
    p_rec.add_argument("--tier", choices=["low", "medium", "high"], default="low")

    p_tr = sub.add_parser("transition")
    p_tr.add_argument("--task-id", required=True)
    p_tr.add_argument("--to", required=True)
    p_tr.add_argument("--actor", default="controller")
    p_tr.add_argument("--reason", default="State transition")

    p_lock = sub.add_parser("lock-verifiers")
    p_lock.add_argument("--task-id", required=True)
    p_lock.add_argument("--paths", required=True, help="Comma-separated file paths")

    p_vsov = sub.add_parser("verify-sovereignty")
    p_vsov.add_argument("--task-id", required=True)

    p_rc = sub.add_parser("record-receipt")
    p_rc.add_argument("--task-id", required=True)
    p_rc.add_argument("--gate", required=True)
    p_rc.add_argument("--cmd", required=True)
    p_rc.add_argument("--exit-code", type=int, required=True)

    p_wt = sub.add_parser("update-worktree")
    p_wt.add_argument("--task-id", required=True)
    p_wt.add_argument("--path", required=True)
    p_wt.add_argument("--branch", required=True)
    p_wt.add_argument("--state", required=True)

    p_st = sub.add_parser("status")
    p_st.add_argument("--task-id", required=True)

    p_lap = sub.add_parser("log-prior-art")
    p_lap.add_argument("--task-id", required=True)
    p_lap.add_argument("--summary", required=True, help="Summary of prior art scan findings")
    p_lap.add_argument("--repeat-yes-entries", default="", help="Comma-separated Repeat:YES map-debt entries found")

    p_pme = sub.add_parser("record-plan-mode-entry")
    p_pme.add_argument("--task-id", required=True)
    p_pme.add_argument("--actor", required=True)

    p_sic = sub.add_parser("record-socratic-intake")
    p_sic.add_argument("--task-id", required=True)
    p_sic.add_argument("--summary", required=True)

    p_ha = sub.add_parser("record-human-approval")
    p_ha.add_argument("--task-id", required=True)
    p_ha.add_argument("--approver", required=True)

    p_rs = sub.add_parser("record-review-skip")
    p_rs.add_argument("--task-id", required=True)
    p_rs.add_argument("--phase", required=True, help="e.g. multi_agent_review, multi_agent_code_review")
    p_rs.add_argument("--actor", required=True)
    p_rs.add_argument("--reason", required=True)

    return parser


def _dispatch_command(cp: ControlPlane, args: argparse.Namespace):
    """Executes the dispatched CLI command."""
    if args.subcommand == "init":
        cp.create_task(args.task_id, args.title, args.runtime, args.spec_path, args.model_tier, args.model_id, args.task_type)
        print(f"Task {args.task_id} initialized in INTAKE (type={args.task_type}).")
    elif args.subcommand == "recommend-model":
        print(json.dumps(cp.resolve_recommended_model(args.runtime, args.tier), indent=2))
    elif args.subcommand == "transition":
        cp.transition(args.task_id, args.to, args.actor, args.reason)
        print(f"Task {args.task_id} transitioned to {args.to}.")
    elif args.subcommand == "lock-verifiers":
        paths = [Path(p.strip()) for p in args.paths.split(",")]
        cp.lock_verifiers(args.task_id, paths)
        print(f"Locked {len(paths)} verifiers for {args.task_id}.")
    elif args.subcommand == "verify-sovereignty":
        cp.verify_sovereignty(args.task_id)
        print(f"Verifier sovereignty verified for {args.task_id}.")
    elif args.subcommand == "record-receipt":
        token = cp.record_verification_receipt(args.task_id, args.gate, args.cmd, args.exit_code)
        print(f"Receipt stamped: {token}")
    elif args.subcommand == "update-worktree":
        cp.update_worktree(args.task_id, args.path, args.branch, args.state)
        print(f"Task {args.task_id} worktree state set to {args.state}.")
    elif args.subcommand == "status":
        print(json.dumps(cp.get_task(args.task_id), indent=2, default=str))
    elif args.subcommand == "log-prior-art":
        repeat_entries = args.repeat_yes_entries or "none"
        details = f"prior_art_scan: summary={args.summary}; repeat_yes_entries={repeat_entries}"
        cp.log_asymmetric_persistence(
            task_id=args.task_id,
            destination="references/map-debt.md",
            status="OBSERVED",
            details=details
        )
        print(f"Prior art scan logged for task {args.task_id}.")
    elif args.subcommand in (
        "record-plan-mode-entry", "record-socratic-intake", "record-human-approval", "record-review-skip"
    ):
        _dispatch_gate_record_command(cp, args)


def _dispatch_gate_record_command(cp: ControlPlane, args: argparse.Namespace):
    """Executes the gate-registry receipt-recording CLI subcommands."""
    if args.subcommand == "record-plan-mode-entry":
        token = cp.record_plan_mode_entry(args.task_id, args.actor)
        print(f"Plan Mode entry recorded: {token}")
    elif args.subcommand == "record-socratic-intake":
        token = cp.record_socratic_intake_complete(args.task_id, args.summary)
        print(f"Socratic intake completion recorded: {token}")
    elif args.subcommand == "record-human-approval":
        token = cp.record_human_approval(args.task_id, args.approver)
        print(f"Human approval recorded: {token}")
    elif args.subcommand == "record-review-skip":
        token = cp.record_review_skip(args.task_id, args.phase, args.actor, args.reason)
        print(f"Review skip recorded: {token}")


def main():
    """Main CLI entry point for SQLite Control Plane."""
    parser = _build_parser()
    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    cp = ControlPlane()
    try:
        _dispatch_command(cp, args)
    except Exception as e:
        print(f"{'CONTROL PLANE ERROR' if isinstance(e, (InvalidStateTransition, VerifierSovereigntyViolation, PersistenceInvariantViolation, ConcurrentModificationError)) else 'ERROR'}: {e}", file=sys.stderr)
        sys.exit(_map_exception_to_exit_code(e))


def _map_exception_to_exit_code(e: Exception) -> int:
    """Maps a caught exception to its CLI exit code. ConcurrentModificationError gets its own
    code (3) since it's the one error that's explicitly retryable — indistinguishable from a
    generic crash (exit 1) would prevent callers from retrying only on contention."""
    if isinstance(e, ConcurrentModificationError):
        return 3
    if isinstance(e, (InvalidStateTransition, VerifierSovereigntyViolation, PersistenceInvariantViolation)):
        return 2
    return 1


if __name__ == "__main__":
    main()
