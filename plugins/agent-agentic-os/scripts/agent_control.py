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

GATE_REQUIREMENTS (per-edge verification, enforced by transition()):
    Some transitions require a recorded receipt or passing critic review before they're
    accepted — e.g. INTERVIEW->DRAFT_PLAN needs proof Plan Mode/Socratic intake ran,
    APPROVED->IN_WORKTREE needs a human_approval receipt (never skippable). Discretionary
    review phases (multi_agent_review, multi_agent_code_review) accept an explicit recorded
    skip (record_review_skip) as an alternative to a real critic review — skips are never
    silent. See the GATE_REQUIREMENTS dict for the full per-edge registry.
"""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
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
            'APPROVED', 'IN_WORKTREE', 'WORKTREE_REVIEW', 'MULTI_AGENT_CODE_REVIEW', 'VERIFY_EXIT', 'DONE',
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

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_transitions_task ON task_transitions(task_id);
"""

CURRENT_SCHEMA_VERSION = 2

CHILD_TABLES = [
    "task_transitions",
    "locked_verifier_baselines",
    "critic_reviews",
    "verification_receipts",
    "asymmetric_persistence_log",
]
ALL_REBUILD_TABLES = ["tasks"] + CHILD_TABLES

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


class ConcurrentModificationError(Exception):
    """Raised when a transition's expected prior state no longer matches the stored row,
    indicating a concurrent writer changed it — never silently overwritten (no last-writer-wins)."""
    pass


# Per-edge verification requirements for transition(). A skippable gate accepts an
# explicit recorded skip receipt (record_review_skip) as an alternative to a real critic
# review — the user retains discretion to skip, but the skip itself is never silent.
GATE_REQUIREMENTS = {
    ("INTERVIEW", "DRAFT_PLAN"): {
        "check": "any_of",
        "options": [
            {"type": "receipt", "gate_name": "plan_mode_entry"},
            {"type": "receipt", "gate_name": "socratic_intake_complete"},
        ],
        "error": "Cannot enter DRAFT_PLAN: no proof Plan Mode was entered or Socratic intake "
                 "completed. Call record_plan_mode_entry() or record_socratic_intake_complete() first.",
    },
    ("INTERVIEW", "PLAN_REVIEW"): {
        "check": "any_of",
        "options": [
            {"type": "receipt", "gate_name": "plan_mode_entry"},
            {"type": "receipt", "gate_name": "socratic_intake_complete"},
        ],
        "error": "Cannot enter PLAN_REVIEW: no proof Plan Mode was entered or Socratic intake "
                 "completed. Call record_plan_mode_entry() or record_socratic_intake_complete() first.",
    },
    ("DRAFT_PLAN", "AWAITING_APPROVAL"): {
        "check": "any_of",
        "options": [
            {"type": "critic_review_pass"},
            {"type": "receipt", "gate_name": "multi_agent_review_skipped"},
        ],
        "error": "Cannot enter AWAITING_APPROVAL: no passing critic review or explicit recorded "
                 "skip found. Call record_critic_review(verdict='PASS') or record_review_skip().",
    },
    ("PLAN_REVIEW", "AWAITING_APPROVAL"): {
        "check": "any_of",
        "options": [
            {"type": "critic_review_pass"},
            {"type": "receipt", "gate_name": "multi_agent_review_skipped"},
        ],
        "error": "Cannot enter AWAITING_APPROVAL: no passing critic review or explicit recorded "
                 "skip found. Call record_critic_review(verdict='PASS') or record_review_skip().",
    },
    ("MULTI_AGENT_REVIEW", "AWAITING_APPROVAL"): {
        "check": "critic_review_pass",
        "error": "Cannot enter AWAITING_APPROVAL: no passing critic review found after "
                 "MULTI_AGENT_REVIEW. Call record_critic_review(verdict='PASS').",
    },
    ("APPROVED", "IN_WORKTREE"): {
        "check": "receipt",
        "gate_name": "human_approval",
        "error": "Cannot enter IN_WORKTREE: no recorded human_approval receipt found. "
                 "Call record_human_approval() — this gate can never be skipped.",
    },
    ("IN_WORKTREE", "WORKTREE_REVIEW"): {
        "check": "receipt",
        "gate_name": "test_suite",
        "error": "Cannot enter WORKTREE_REVIEW: no recorded test_suite verification receipt found. "
                 "Call record_verification_receipt(gate_name='test_suite', ...).",
    },
    ("WORKTREE_REVIEW", "VERIFY_EXIT"): {
        "check": "any_of",
        "options": [
            {"type": "critic_review_pass"},
            {"type": "receipt", "gate_name": "multi_agent_code_review_skipped"},
        ],
        "error": "Cannot enter VERIFY_EXIT: no passing critic review or explicit recorded skip "
                 "found. Call record_critic_review(verdict='PASS') or record_review_skip().",
    },
}


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
            self.db_path = self._discover_shared_db_path()
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _discover_shared_db_path(self) -> Path:
        """Resolves context/control_plane.db anchored at the repo root shared across
        ALL git worktrees of the same repo — via `git rev-parse --git-common-dir`,
        which (unlike a manual walk-up for the nearest `.git`) returns the same
        physical .git directory whether invoked from the main checkout or any
        worktree, so they all read/write one control plane instead of each worktree
        getting its own disconnected DB."""
        curr = Path(__file__).resolve().parent
        for p in [curr] + list(curr.parents):
            if p.name == ".agents":
                return p.parent / "context" / "control_plane.db"

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-common-dir"],
                cwd=str(curr), capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                common_dir = Path(result.stdout.strip())
                if not common_dir.is_absolute():
                    common_dir = (curr / common_dir).resolve()
                return common_dir.parent / "context" / "control_plane.db"
        except (subprocess.SubprocessError, OSError):
            pass

        for p in [curr] + list(curr.parents):
            if (p / "context").exists() and not (p / "skills").exists():
                return p / "context" / "control_plane.db"

        return Path.cwd() / "context" / "control_plane.db"

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured sqlite3 connection with WAL mode and foreign keys."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def init_db(self):
        """Initializes SQLite tables and WAL mode. Self-heals FK-corrupted or legacy schemas."""
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

            if self._schema_needs_rebuild(conn):
                self._rebuild_schema_transactional(conn)
            else:
                conn.execute(
                    "INSERT INTO schema_version (version) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM schema_version)",
                    (CURRENT_SCHEMA_VERSION,)
                )
                conn.commit()
        finally:
            conn.close()

    def _schema_needs_rebuild(self, conn: sqlite3.Connection) -> bool:
        """Detects a stale schema_version, a legacy tasks schema, or FK-corrupted/orphaned
        migration artifacts. schema_version is the primary migration trigger; the DDL-sniff
        and corruption checks below are defensive fallbacks for pre-schema_version databases
        and self-healing already-corrupted ones, not the source of truth for version bumps."""
        version_row = conn.execute("SELECT version FROM schema_version").fetchone()
        if version_row and version_row[0] < CURRENT_SCHEMA_VERSION:
            return True

        row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone()
        if row and "WORKTREE_REVIEW" not in (row[0] or ""):
            return True

        orphan = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='_tasks_old'"
        ).fetchone()[0]
        if orphan:
            return True

        for table in CHILD_TABLES:
            child_row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
            if child_row and child_row[0] and ("_tasks_old" in child_row[0] or "_migrating" in child_row[0]):
                return True
        return False

    def _copy_common_columns(self, conn: sqlite3.Connection, source_table: str, dest_table: str):
        """Copies rows between tables via the intersection of their columns."""
        source_cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{source_table}");').fetchall()]
        dest_cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{dest_table}");').fetchall()]
        common_cols = [c for c in source_cols if c in dest_cols]
        cols_str = ", ".join(f'"{c}"' for c in common_cols)
        conn.execute(f'INSERT INTO "{dest_table}" ({cols_str}) SELECT {cols_str} FROM "{source_table}";')

    def _merge_orphaned_tasks_old(self, conn: sqlite3.Connection):
        """Merges a dangling `_tasks_old` (from a previously-interrupted migration) into the
        fresh `tasks` table. Logs any conflicting task_id (present in both with different
        values) to map-debt instead of silently discarding it."""
        merge_cols = [r[1] for r in conn.execute('PRAGMA table_info("_tasks_old_merge");').fetchall()]
        target_cols = [r[1] for r in conn.execute('PRAGMA table_info("tasks");').fetchall()]
        common_cols = [c for c in merge_cols if c in target_cols]
        cols_str = ", ".join(f'"{c}"' for c in common_cols)

        existing_ids = {r[0] for r in conn.execute("SELECT task_id FROM tasks").fetchall()}
        conflicts = []
        for row in conn.execute(f'SELECT {cols_str} FROM "_tasks_old_merge"').fetchall():
            row_dict = dict(zip(common_cols, row))
            task_id = row_dict["task_id"]
            if task_id in existing_ids:
                conflicts.append(task_id)
                continue
            placeholders = ", ".join(["?"] * len(common_cols))
            conn.execute(f'INSERT INTO tasks ({cols_str}) VALUES ({placeholders})', row)

        if conflicts:
            self._log_orphan_merge_conflicts(conflicts)

    def _log_orphan_merge_conflicts(self, conflicting_task_ids: List[str]):
        """Appends a map-debt entry for task_ids dropped during an orphaned-table merge
        (present in both the fresh `tasks` table and a dangling `_tasks_old`)."""
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        map_debt_path = repo_root / "references" / "map-debt.md"
        if not map_debt_path.exists():
            return
        entry = (
            f"\n| DEBT-{time.strftime('%Y%m%d')}-AUTO | Orphaned _tasks_old merge conflict "
            f"discarded rows for task_ids: {', '.join(conflicting_task_ids)} | OPEN | Tier 1 | 1 | "
            f"{time.strftime('%Y-%m-%d')} | Self-heal migration in init_db() found these task_ids "
            f"in both the fresh tasks table and a dangling _tasks_old, with differing data. "
            f"The tasks table's version was kept; _tasks_old's version was discarded. | "
            f"Review discarded data manually if needed; _tasks_old is already dropped. |\n"
        )
        with open(map_debt_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def _rebuild_schema_transactional(self, conn: sqlite3.Connection):
        """Rebuilds tasks + all child tables together in one explicit transaction, so a
        mid-sequence failure rolls back cleanly instead of leaving a corrupted intermediate
        state. Renaming all six tables together (instead of `tasks` alone) prevents SQLite's
        FK-auto-repoint behavior from leaving child tables pointing at a stale name."""
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("BEGIN IMMEDIATE;")
        try:
            orphan_exists = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='_tasks_old'"
            ).fetchone()[0]
            if orphan_exists:
                conn.execute('ALTER TABLE "_tasks_old" RENAME TO "_tasks_old_merge";')

            for table in ALL_REBUILD_TABLES:
                exists = conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,)
                ).fetchone()[0]
                if exists:
                    conn.execute(f'ALTER TABLE "{table}" RENAME TO "_{table}_migrating";')

            conn.executescript(SCHEMA_SQL)

            for table in ALL_REBUILD_TABLES:
                migrating_name = f"_{table}_migrating"
                migrating_exists = conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (migrating_name,)
                ).fetchone()[0]
                if migrating_exists:
                    self._copy_common_columns(conn, migrating_name, table)
                    conn.execute(f'DROP TABLE "{migrating_name}";')

            if orphan_exists:
                self._merge_orphaned_tasks_old(conn)
                conn.execute('DROP TABLE "_tasks_old_merge";')

            conn.execute("DELETE FROM schema_version;")
            conn.execute("INSERT INTO schema_version (version) VALUES (?);", (CURRENT_SCHEMA_VERSION,))
            conn.execute("COMMIT;")
        except Exception:
            conn.execute("ROLLBACK;")
            raise
        finally:
            conn.execute("PRAGMA foreign_keys = ON;")

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

    def _check_prior_art_guard(self, conn: sqlite3.Connection, task_id: str, task: Dict[str, Any], current_state: str, to_state: str):
        """Blocks EVOLUTION tasks from leaving INTAKE without a logged prior-art scan."""
        if to_state != "INTERVIEW" or current_state != "INTAKE":
            return
        if task.get("task_type", "GENERAL") != "EVOLUTION":
            return
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

    def _check_done_guard(self, conn: sqlite3.Connection, task_id: str, to_state: str):
        """Blocks transition to DONE without a passing test_suite receipt, asymmetric
        persistence log, clean leak check, and (if any verifiers were locked) intact
        verifier sovereignty."""
        if to_state != "DONE":
            return
        rec = conn.execute(
            "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = 'test_suite' AND exit_code = 0",
            (task_id,)
        ).fetchone()[0]
        if rec == 0:
            raise PersistenceInvariantViolation(
                f"Cannot complete task '{task_id}': No passing test_suite verification receipt "
                "(gate_name='test_suite', exit_code == 0) found."
            )

        locked_count = conn.execute(
            "SELECT COUNT(*) FROM locked_verifier_baselines WHERE task_id = ?", (task_id,)
        ).fetchone()[0]
        if locked_count > 0:
            self.verify_sovereignty(task_id)

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

        leak_rec = conn.execute(
            "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = 'leak_check' AND exit_code = 0",
            (task_id,)
        ).fetchone()[0]
        if leak_rec == 0:
            raise PersistenceInvariantViolation(
                f"Cannot complete task '{task_id}': Missing clean leak check receipt (gate_name='leak_check', exit_code=0)."
            )

    def _check_rolled_back_guard(self, conn: sqlite3.Connection, task_id: str, to_state: str):
        """Blocks transition to ROLLED_BACK without a logged asymmetric persistence entry."""
        if to_state != "ROLLED_BACK":
            return
        failure_persist = conn.execute(
            "SELECT COUNT(*) FROM asymmetric_persistence_log WHERE task_id = ?",
            (task_id,)
        ).fetchone()[0]
        if failure_persist == 0:
            raise PersistenceInvariantViolation(
                f"Cannot roll back task '{task_id}': Asymmetric persistence required. "
                "Document failure mode/learning in asymmetric_persistence_log before rolling back code."
            )

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

            self._check_prior_art_guard(conn, task_id, task, current_state, to_state)
            self._check_done_guard(conn, task_id, to_state)
            self._check_rolled_back_guard(conn, task_id, to_state)

            # --- Gate-Requirement Registry: per-edge verification check ---
            self._check_gate_requirement(conn, task_id, current_state, to_state)

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

    def _gate_receipt_exists(self, conn: sqlite3.Connection, task_id: str, gate_name: str) -> bool:
        """Checks whether a verification receipt with the given gate_name exists for the task."""
        count = conn.execute(
            "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ?",
            (task_id, gate_name)
        ).fetchone()[0]
        return count > 0

    def _gate_critic_review_pass_exists(self, conn: sqlite3.Connection, task_id: str) -> bool:
        """Checks whether a passing critic review exists for the task."""
        count = conn.execute(
            "SELECT COUNT(*) FROM critic_reviews WHERE task_id = ? AND verdict = 'PASS'",
            (task_id,)
        ).fetchone()[0]
        return count > 0

    def _gate_any_of(self, conn: sqlite3.Connection, task_id: str, options: List[Dict[str, str]]) -> bool:
        """Checks whether any one of the given gate options is satisfied."""
        for opt in options:
            if opt["type"] == "receipt" and self._gate_receipt_exists(conn, task_id, opt["gate_name"]):
                return True
            if opt["type"] == "critic_review_pass" and self._gate_critic_review_pass_exists(conn, task_id):
                return True
        return False

    def _check_gate_requirement(self, conn: sqlite3.Connection, task_id: str, current_state: str, to_state: str):
        """Enforces GATE_REQUIREMENTS for the given transition edge, if one is registered."""
        spec = GATE_REQUIREMENTS.get((current_state, to_state))
        if spec is None:
            return
        check = spec["check"]
        if check == "receipt":
            satisfied = self._gate_receipt_exists(conn, task_id, spec["gate_name"])
        elif check == "critic_review_pass":
            satisfied = self._gate_critic_review_pass_exists(conn, task_id)
        elif check == "any_of":
            satisfied = self._gate_any_of(conn, task_id, spec["options"])
        else:
            satisfied = True
        if not satisfied:
            raise PersistenceInvariantViolation(spec["error"])

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
            # Enforce review gate before allowing worktree_state='pushed_to_origin'
            if worktree_state == "pushed_to_origin":
                row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
                if not row:
                    raise ValueError(f"Task not found: {task_id}")
                task_state = row[0]
                valid_states_for_push = ("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")
                if task_state not in valid_states_for_push:
                    raise PersistenceInvariantViolation(
                        f"Cannot mark worktree '{worktree_state}' for task '{task_id}': Task state is '{task_state}'. "
                        f"Post-implementation review stage gate required. Task must be in {valid_states_for_push} before pushing to origin."
                    )

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
