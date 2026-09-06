#!/usr/bin/env python3
"""
agent_control.py — Lightweight SQLite Control Plane for Agent Lifecycle
========================================================================

Purpose:
    ACID state machine and audit log for task execution, verifier sovereignty,
    pre-execution review gating, worktree 6-state tracking, and cryptographic
    receipt generation across multi-tool agent environments.

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
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

CANONICAL_STATES = [
    "INTAKE",
    "INTERVIEW",
    "DRAFT_PLAN",
    "MULTI_AGENT_REVIEW",
    "PLAN_REVIEW",
    "AWAITING_APPROVAL",
    "APPROVED",
    "IN_WORKTREE",
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
    "IN_WORKTREE": ["VERIFY_EXIT", "ROLLED_BACK", "ESCALATED"],
    "VERIFY_EXIT": ["DONE", "IN_WORKTREE", "ROLLED_BACK", "ESCALATED"],
    "DONE": [],
    "ROLLED_BACK": ["ESCALATED", "PLAN_REVIEW"],
    "ESCALATED": ["INTAKE", "PLAN_REVIEW"]
}

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN (
            'INTAKE', 'INTERVIEW', 'DRAFT_PLAN', 'MULTI_AGENT_REVIEW', 'PLAN_REVIEW', 'AWAITING_APPROVAL',
            'APPROVED', 'IN_WORKTREE', 'VERIFY_EXIT', 'DONE',
            'ROLLED_BACK', 'ESCALATED'
        )
    ),
    task_type TEXT NOT NULL DEFAULT 'GENERAL' CHECK (task_type IN ('GENERAL', 'EVOLUTION')),
    runtime_tool TEXT NOT NULL,
    worktree_path TEXT,
    worktree_branch TEXT,
    worktree_state TEXT CHECK (
        worktree_state IS NULL OR worktree_state IN (
            'written_in_worktree', 'committed_in_worktree', 'pushed_to_origin',
            'merged_into_origin_main', 'local_branch_ref_updated', 'checked_out_on_disk'
        )
    ),
    spec_path TEXT,
    model_tier TEXT CHECK (model_tier IS NULL OR model_tier IN ('low', 'medium', 'high')),
    model_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_transitions (
    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    actor TEXT NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locked_verifier_baselines (
    baseline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    expected_sha256 TEXT NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS critic_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL CHECK(iteration BETWEEN 1 AND 3),
    model_used TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('PASS', 'REVISE', 'REJECT')),
    critique_findings TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_receipts (
    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    gate_name TEXT NOT NULL,
    command_executed TEXT NOT NULL,
    exit_code INTEGER NOT NULL,
    receipt_token TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asymmetric_persistence_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    destination TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OBSERVED', 'HYPOTHESIS', 'CONFIRMED', 'RESOLVED')),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_transitions_task ON task_transitions(task_id);
"""

SCHEMA_MIGRATIONS = [
    # Migration: add task_type column if not present (for existing DBs)
    "ALTER TABLE tasks ADD COLUMN task_type TEXT NOT NULL DEFAULT 'GENERAL' CHECK (task_type IN ('GENERAL', 'EVOLUTION'));",
]


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class VerifierSovereigntyViolation(Exception):
    """Raised when a protected verifier file has been tampered with."""
    pass


class PersistenceInvariantViolation(Exception):
    """Raised when evolution integrity or asymmetric persistence invariants are violated."""
    pass


# External comment: Compute the SHA256 hex digest of a local file
def _sha256_file(filepath: Path) -> str:
    """Computes SHA256 hex digest of a given file path."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ControlPlane:
    """Controller and state machine manager for task lifecycles."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initializes the ControlPlane instance with database path."""
        if db_path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            self.db_path = repo_root / "context" / "control_plane.db"
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured sqlite3 connection with WAL mode and foreign keys."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def init_db(self):
        """Initializes SQLite tables and WAL mode."""
        conn = self._get_connection()
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.executescript(SCHEMA_SQL)
            # Apply idempotent migrations for existing databases
            for migration in SCHEMA_MIGRATIONS:
                try:
                    conn.execute(migration)
                    conn.commit()
                except Exception:
                    pass  # Column already exists — ignore
        finally:
            conn.close()

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
        cheapest_model = None
        if cheapest_file.exists():
            try:
                c_data = json.loads(cheapest_file.read_text(encoding="utf-8"))
                cheapest_model = c_data.get(tool_key, {}).get("model")
            except Exception:
                pass

        selected_model = None
        if catalog_file.exists():
            try:
                cat_data = json.loads(catalog_file.read_text(encoding="utf-8"))
                selected_model = self._pick_tier_model(cat_data, tier, cheapest_model)
            except Exception:
                pass

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

    def transition(self, task_id: str, to_state: str, actor: str, reason: str):
        """Validates and applies a state transition according to the canonical DAG."""
        if to_state not in CANONICAL_STATES:
            raise InvalidStateTransition(f"Unknown state: {to_state}")

        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        current_state = task["state"]
        allowed = ALLOWED_TRANSITIONS.get(current_state, [])
        if to_state not in allowed:
            raise InvalidStateTransition(
                f"Cannot transition task '{task_id}' from '{current_state}' to '{to_state}'. Allowed: {allowed}"
            )

        conn = self._get_connection()
        try:
            # --- Invariant Guard: INTAKE -> INTERVIEW for EVOLUTION tasks ---
            if to_state == "INTERVIEW" and current_state == "INTAKE":
                task_type = task.get("task_type", "GENERAL")
                if task_type == "EVOLUTION":
                    prior_art_count = conn.execute(
                        """
                        SELECT COUNT(*) FROM asymmetric_persistence_log
                        WHERE task_id = ? AND details LIKE '%prior_art_scan%'
                        """,
                        (task_id,)
                    ).fetchone()[0]
                    if prior_art_count == 0:
                        raise PersistenceInvariantViolation(
                            f"Cannot advance EVOLUTION task '{task_id}' past INTAKE: "
                            "Prior art scan required. Read references/map-debt.md (check Repeat: YES entries) "
                            "and wiki/decisions/ before drafting hypotheses. "
                            "Log result via log_asymmetric_persistence() with details containing 'prior_art_scan'."
                        )

            # --- Invariant Guard: VERIFY_EXIT -> DONE ---
            if to_state == "DONE":
                # 1. Deterministic Verification Receipt Exists (exit_code == 0)
                rec = conn.execute(
                    "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND exit_code = 0",
                    (task_id,)
                ).fetchone()[0]
                if rec == 0:
                    raise PersistenceInvariantViolation(
                        f"Cannot complete task '{task_id}': No passing verification receipt (exit_code == 0) found."
                    )

                # 2. Asymmetric Persistence Logged (decision / debt sync)
                persist_count = conn.execute(
                    """
                    SELECT COUNT(*) FROM asymmetric_persistence_log 
                    WHERE task_id = ? 
                      AND (destination LIKE '%wiki/decisions/%' OR destination LIKE '%references/map-debt.md%' OR destination LIKE '%map-debt%')
                    """,
                    (task_id,)
                ).fetchone()[0]
                if persist_count == 0:
                    raise PersistenceInvariantViolation(
                        f"Cannot complete task '{task_id}': Asymmetric persistence required before DONE. "
                        "Log an entry to wiki/decisions/ or references/map-debt.md."
                    )

                # 3. Clean Leak Check
                leak_rec = conn.execute(
                    "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = 'leak_check' AND exit_code = 0",
                    (task_id,)
                ).fetchone()[0]
                if leak_rec == 0:
                    raise PersistenceInvariantViolation(
                        f"Cannot complete task '{task_id}': Missing clean leak check receipt (gate_name='leak_check', exit_code=0)."
                    )

            # --- Invariant Guard: Failure -> ROLLED_BACK ---
            if to_state == "ROLLED_BACK":
                failure_persist = conn.execute(
                    "SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ?",
                    (task_id,)
                ).fetchone()[0]
                if failure_persist == 0:
                    raise PersistenceInvariantViolation(
                        f"Cannot roll back task '{task_id}': Asymmetric persistence required. "
                        "Document failure mode/learning in asymmetric_persistence_log before rolling back code."
                    )

            with conn:
                conn.execute(
                    "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
                    (to_state, task_id)
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
                    file_sha = _sha256_file(p)
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
                curr_sha = _sha256_file(p)
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
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
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
    except (InvalidStateTransition, VerifierSovereigntyViolation, PersistenceInvariantViolation) as e:
        print(f"CONTROL PLANE ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
