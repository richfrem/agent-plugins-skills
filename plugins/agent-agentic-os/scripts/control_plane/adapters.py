"""
control_plane/adapters.py — Concrete Port Implementations (issue-524)
========================================================================

Purpose:
    Concrete adapters implementing the port interfaces declared in control_plane/ports.py
    against real infrastructure. Populated incrementally as agent_control.py's ControlPlane
    responsibilities are extracted (docs/plans/issue-524-spec.md, Section 5). Step 3 added
    FilesystemAdapter. Step 6 added CryptoAdapter. Step 7 added ModelCatalogAdapter. Step 5 was
    revised after external post-implementation review (round 2) found the original
    SqlitePersistenceAdapter only covered connection management and schema migration, leaving
    all task/transition/receipt CRUD SQL still directly embedded in ControlPlane — contradicting
    the plan's stated goal of a real persistence boundary. SqlitePersistenceAdapter now fully
    implements PersistencePort: every CRUD operation ControlPlane needs has a concrete method
    here, and ControlPlane composes this port instead of ever calling sqlite3 itself. This
    revision also adds ClockAdapter (ClockPort was declared in Step 2 but never wired to
    anything — flagged by the same review as dead architecture).

Layer:
    OS Kernel / Execution Control Plane Substrate — Adapters (hexagonal boundary)

Key Input Dependencies:
    - Local filesystem (FilesystemAdapter, CryptoAdapter.sha256_file, ModelCatalogAdapter)
    - SQLite database file (SqlitePersistenceAdapter)
    - Wall clock (ClockAdapter)

Key Functions:
    - FilesystemAdapter.append_text() — appends text to a file, no-op if the file doesn't exist
    - FilesystemAdapter.read_text() — reads a file's full text content
    - FilesystemAdapter.exists() — checks file existence
    - ClockAdapter.current_time() / strftime() — real wall-clock time, real strftime formatting
    - SqlitePersistenceAdapter — full PersistencePort implementation: connection management,
      schema migration (self-healing, verbatim from the original init_db()/_schema_needs_rebuild()/
      _rebuild_schema_transactional()/_copy_common_columns()/_merge_orphaned_tasks_old()), plus
      every task/transition/receipt/review/verifier/log/worktree CRUD operation formerly issued
      directly by ControlPlane
    - CryptoAdapter.sha256_file() — SHA256 hex digest of a file, verbatim from the former
      module-level _sha256_file()
    - CryptoAdapter.sha256_hex() — SHA256 hex digest of a string (receipt token generation)
    - ModelCatalogAdapter.load_catalog() — reads/parses a model-catalog JSON file, or None
    - ModelCatalogAdapter.load_cheapest() — reads cheapest_models.json for a tool_key, or None
"""

import hashlib
import json
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from control_plane.ports import FilesystemPort, CryptoPort, ModelCatalogPort, PersistencePort, ClockPort


class FilesystemAdapter(FilesystemPort):
    """Real-filesystem implementation of FilesystemPort. Mirrors the exact current behavior
    of agent_control.py's _log_orphan_merge_conflicts(): silently does nothing if the target
    file does not already exist (never creates it), matching the original guard
    `if not map_debt_path.exists(): return`."""

    def append_text(self, path: Path, content: str) -> None:
        """Appends `content` to the file at `path`. No-op if the file does not already exist —
        preserves the original _log_orphan_merge_conflicts() behavior exactly."""
        if not path.exists():
            return
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    def read_text(self, path: Path) -> str:
        """Reads and returns the full text content of the file at `path`."""
        return path.read_text(encoding="utf-8")

    def exists(self, path: Path) -> bool:
        """Returns whether a file exists at `path`."""
        return path.exists()


class ClockAdapter(ClockPort):
    """Real wall-clock implementation of ClockPort, backed by the stdlib `time` module."""

    def current_time(self) -> float:
        """Returns the current time as a float (seconds since epoch)."""
        return time.time()

    def strftime(self, fmt: str) -> str:
        """Returns the current local time formatted per `fmt`."""
        return time.strftime(fmt)


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
    iteration INTEGER NOT NULL CHECK(iteration >= 1),
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

CURRENT_SCHEMA_VERSION = 3

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


class SqlitePersistenceAdapter(PersistencePort):
    """SQLite-backed implementation of PersistencePort — connection management, schema
    migration, and every task/transition/receipt/review/verifier/log/worktree CRUD
    operation ControlPlane needs. Revised after external post-implementation review found
    the original version only covered connection/migration, leaving CRUD SQL embedded in
    ControlPlane — this version closes that gap: ControlPlane never calls sqlite3 directly."""

    def __init__(self, db_path: Optional[Path], fs_adapter: FilesystemPort,
                 clock_adapter: Optional[ClockPort] = None):
        self.db_path = db_path if db_path is not None else self._discover_shared_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._fs = fs_adapter
        self._clock = clock_adapter if clock_adapter is not None else ClockAdapter()

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

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured sqlite3 connection with WAL mode and foreign keys."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def ensure_schema(self) -> None:
        """Initializes SQLite tables and WAL mode. Self-heals FK-corrupted or legacy schemas."""
        conn = self.get_connection()
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.executescript(SCHEMA_SQL)
            # Apply idempotent migrations for existing databases
            for migration in SCHEMA_MIGRATIONS:
                try:
                    conn.execute(migration)
                    conn.commit()
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e).lower():
                        raise
                    # Column already exists — expected on a previously-migrated DB, ignore.

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
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        map_debt_path = repo_root / "references" / "map-debt.md"
        if not self._fs.exists(map_debt_path):
            return
        entry = (
            f"\n| DEBT-{self._clock.strftime('%Y%m%d')}-AUTO | Orphaned _tasks_old merge conflict "
            f"discarded rows for task_ids: {', '.join(conflicting_task_ids)} | OPEN | Tier 1 | 1 | "
            f"{self._clock.strftime('%Y-%m-%d')} | Self-heal migration in init_db() found these task_ids "
            f"in both the fresh tasks table and a dangling _tasks_old, with differing data. "
            f"The tasks table's version was kept; _tasks_old's version was discarded. | "
            f"Review discarded data manually if needed; _tasks_old is already dropped. |\n"
        )
        self._fs.append_text(map_debt_path, entry)

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

    # --- PersistencePort CRUD implementation (moved verbatim from ControlPlane) ---

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a task dictionary by task_id."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def insert_task(self, task_id: str, title: str, task_type: str, runtime_tool: str,
                     spec_path: Optional[str], model_tier: Optional[str], model_id: Optional[str]) -> None:
        """Inserts a new task row in INTAKE state and its creation transition, atomically."""
        self.ensure_schema()
        conn = self.get_connection()
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

    def read_current_state(self, task_id: str) -> Optional[str]:
        """Reads a task's current state value directly, for use immediately before a guarded
        write. Calls ensure_schema() first (issue-524, post-round-2-review correction: this
        method previously could hit "no such table: tasks" against a fresh DB — every public
        PersistencePort operation now self-heals the schema before querying, closing that gap)."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def apply_transition(self, task_id: str, from_state: str, to_state: str, actor: str, reason: str) -> bool:
        """Atomically updates task state (guarded by expected from_state) and records the
        transition row. Returns False if the guard predicate did not match (concurrent write) —
        the caller (ControlPlane.transition()) raises ConcurrentModificationError in that case."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ? AND state = ?",
                    (to_state, task_id, from_state)
                )
                if cursor.rowcount == 0:
                    return False
                conn.execute(
                    "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, ?, ?, ?, ?)",
                    (task_id, from_state, to_state, actor, reason)
                )
                return True
        finally:
            conn.close()

    def count_asymmetric_persistence(self, task_id: str, details_like: Optional[str] = None,
                                      destination_like_any: Optional[List[str]] = None) -> int:
        """Counts asymmetric_persistence_log rows for task_id, filtered per details_like
        (single LIKE pattern on `details`) or destination_like_any (OR'd LIKE patterns on
        `destination`) — at most one filter kind is expected per call."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
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
        finally:
            conn.close()

    def count_receipts(self, task_id: str, gate_name: str, exit_code: Optional[int] = None) -> int:
        """Counts verification_receipts rows for task_id matching gate_name (and exit_code if given)."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            if exit_code is None:
                return conn.execute(
                    "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ?",
                    (task_id, gate_name)
                ).fetchone()[0]
            return conn.execute(
                "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ? AND exit_code = ?",
                (task_id, gate_name, exit_code)
            ).fetchone()[0]
        finally:
            conn.close()

    def count_locked_verifiers(self, task_id: str) -> int:
        """Counts locked_verifier_baselines rows for task_id."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM locked_verifier_baselines WHERE task_id = ?", (task_id,)
            ).fetchone()[0]
        finally:
            conn.close()

    def get_locked_verifiers(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns locked_verifier_baselines rows (file_path, expected_sha256) for task_id."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            rows = conn.execute(
                "SELECT file_path, expected_sha256 FROM locked_verifier_baselines WHERE task_id = ?",
                (task_id,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def has_passing_critic_review(self, task_id: str) -> bool:
        """Returns whether any critic_reviews row for task_id has verdict='PASS'."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM critic_reviews WHERE task_id = ? AND verdict = 'PASS'",
                (task_id,)
            ).fetchone()[0] > 0
        finally:
            conn.close()

    def has_receipt(self, task_id: str, gate_name: str) -> bool:
        """Returns whether any verification_receipts row exists for task_id with the given gate_name."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM verification_receipts WHERE task_id = ? AND gate_name = ?",
                (task_id, gate_name)
            ).fetchone()[0] > 0
        finally:
            conn.close()

    def insert_verification_receipt(self, task_id: str, gate_name: str, command_executed: str,
                                     exit_code: int, receipt_token: str) -> None:
        """Inserts a verification_receipts row."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO verification_receipts (task_id, gate_name, command_executed, exit_code, receipt_token)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, gate_name, command_executed, exit_code, receipt_token)
                )
        finally:
            conn.close()

    def insert_critic_review(self, task_id: str, iteration: int, model: str, verdict: str, findings: str) -> None:
        """Inserts a critic_reviews row."""
        self.ensure_schema()
        conn = self.get_connection()
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

    def insert_locked_verifier(self, task_id: str, file_path: str, expected_sha256: str) -> None:
        """Inserts a locked_verifier_baselines row."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO locked_verifier_baselines (task_id, file_path, expected_sha256) VALUES (?, ?, ?)",
                    (task_id, file_path, expected_sha256)
                )
        finally:
            conn.close()

    def insert_asymmetric_persistence(self, task_id: str, destination: str, status: str, details: str) -> None:
        """Inserts an asymmetric_persistence_log row."""
        self.ensure_schema()
        conn = self.get_connection()
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

    def get_verification_receipts(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns all verification_receipts rows for task_id."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            rows = conn.execute("SELECT * FROM verification_receipts WHERE task_id = ?", (task_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_worktree_fields(self, task_id: str, worktree_path: str, worktree_branch: str, worktree_state: str) -> None:
        """Updates a task's worktree_path/worktree_branch/worktree_state columns."""
        self.ensure_schema()
        conn = self.get_connection()
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


class CryptoAdapter(CryptoPort):
    """Real hashlib-backed implementation of CryptoPort, extracted verbatim from
    agent_control.py's former module-level _sha256_file() and record_verification_receipt()'s
    inline token-hashing logic (issue-524 Step 6)."""

    def sha256_file(self, path: Path) -> str:
        """Computes the SHA256 hex digest of the file at `path`, streaming in 64KB chunks."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def sha256_hex(self, raw: str) -> str:
        """Computes the SHA256 hex digest of the given string."""
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ModelCatalogAdapter(ModelCatalogPort):
    """Real filesystem/JSON-backed implementation of ModelCatalogPort. Step 7 moved only the
    file-read methods (load_catalog/load_cheapest); after external post-implementation review
    (round 2) found ControlPlane still owned tool-alias resolution, tier-selection strategy,
    and fallback logic, this revision moves resolve_recommended_model() and its two former
    ControlPlane helpers (_resolve_tool_catalog/_pick_tier_model) here in full — verbatim
    behavior, just relocated. Any parse/read error is swallowed and treated as "unavailable"
    (returns None from the file-read methods), matching the original bare
    `except Exception: pass` behavior exactly."""

    def resolve_recommended_model(self, runtime_tool: str, tier: str = "low") -> Dict[str, str]:
        """Resolves a full model recommendation: tool-alias resolution, catalog file lookup,
        tier-strategy selection, and fallback. Moved verbatim from ControlPlane."""
        tier = tier.lower() if tier.lower() in ("low", "medium", "high") else "low"
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        cli_refs = repo_root / "plugins" / "cli-agents" / "references"
        tool_key, catalog_file = self._resolve_tool_catalog(runtime_tool, cli_refs)

        cheapest_file = cli_refs / "cheapest_models.json"
        cheapest_model = self.load_cheapest(cheapest_file, tool_key)

        selected_model = None
        cat_data = self.load_catalog(catalog_file)
        if cat_data is not None:
            selected_model = self._pick_tier_model(cat_data, tier, cheapest_model)

        return {
            "runtime_tool": runtime_tool,
            "tier": tier,
            "model_id": selected_model or cheapest_model or "gpt-5.4-nano"
        }

    def _resolve_tool_catalog(self, runtime_tool: str, cli_refs: Path):
        """Resolves tool alias and catalog file path. Moved verbatim from ControlPlane."""
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
        """Picks a model ID from catalog strategy and cost tiers. Moved verbatim from ControlPlane."""
        strategy = cat_data.get("strategy", {})
        cost_tiers = cat_data.get("cost_tiers", {})
        if tier == "low":
            return cheapest_model or strategy.get("heartbeat") or strategy.get("default")
        if tier == "medium":
            return strategy.get("default") or (cost_tiers.get("moderate", [None])[0] if "moderate" in cost_tiers else None)
        return strategy.get("complex_reasoning") or strategy.get("architecture") or strategy.get("default")

    def load_catalog(self, catalog_path: Path) -> Optional[Dict[str, Any]]:
        """Loads and returns a parsed model-catalog JSON file, or None if missing/unparsable."""
        if not catalog_path.exists():
            return None
        try:
            return json.loads(catalog_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def load_cheapest(self, cheapest_path: Path, tool_key: str) -> Optional[str]:
        """Loads cheapest_models.json and returns the cheapest model id for `tool_key`, or None."""
        if not cheapest_path.exists():
            return None
        try:
            c_data = json.loads(cheapest_path.read_text(encoding="utf-8"))
            return c_data.get(tool_key, {}).get("model")
        except Exception:
            return None
