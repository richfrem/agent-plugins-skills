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
from control_plane.ports import (
    FilesystemPort,
    CryptoPort,
    ModelCatalogPort,
    PersistencePort,
    ClockPort,
    TransitionRecord,
    TransitionDecision,
    TransitionCommitRequest,
    PhaseCapability,
)
from control_plane.state_machine import ALLOWED_TRANSITIONS



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

CREATE TABLE IF NOT EXISTS transition_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    source_occupancy_transition_id INTEGER NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    question_id TEXT NOT NULL,
    answer TEXT NOT NULL,
    decision_type TEXT NOT NULL CHECK(decision_type IN ('ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION')),
    actor TEXT NOT NULL,
    recorded_at REAL NOT NULL,
    consumed_at REAL,
    bound_transition_id INTEGER REFERENCES task_transitions(transition_id)
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS valid_transitions (
    from_state TEXT,
    to_state TEXT NOT NULL,
    PRIMARY KEY (from_state, to_state)
);

CREATE TABLE IF NOT EXISTS transition_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    attempted_from_state TEXT,
    attempted_to_state TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_transitions_task ON task_transitions(task_id);
CREATE INDEX IF NOT EXISTS idx_decisions_lookup ON transition_decisions(task_id, source_occupancy_transition_id);

-- issue-523: DB-level backstop enforcing legal state transitions on raw SQL writes that
-- bypass ControlPlane/PersistencePort entirely. Adjacency-legality only (see
-- docs/plans/issue-523-trigger-enforcement-spec.md guardrail table) — not a reimplementation
-- of policy.py's dynamic gate checks. Reverts silently (no SQL error), logs to
-- transition_violations. Both state and updated_at are restored (finding #7).
CREATE TRIGGER IF NOT EXISTS enforce_valid_transition
AFTER UPDATE ON tasks
WHEN NEW.state != OLD.state
 AND NOT EXISTS (
    SELECT 1 FROM valid_transitions WHERE from_state = OLD.state AND to_state = NEW.state
 )
BEGIN
    INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
    VALUES (OLD.task_id, OLD.state, NEW.state);
    UPDATE tasks SET state = OLD.state, updated_at = OLD.updated_at WHERE task_id = NEW.task_id;
END;

-- issue-523: closes the cheaper INSERT/DELETE+INSERT bypass identified by external security
-- review (finding #5) — deletes an illegally-seeded initial-state row. Revised from an
-- original coerce-to-INTAKE design: coercing via a corrective UPDATE fired
-- enforce_valid_transition (e.g. DONE -> INTAKE isn't a legal edge), which reverted the
-- coercion right back, silently defeating the fix. Delete avoids the UPDATE trigger
-- entirely. This does NOT reverse the UPDATE trigger's own coerce-not-delete decision — a
-- freshly-inserted illegal row has no accumulated transitions/receipts/decisions to protect,
-- unlike an existing task record (see spec guardrail table).
CREATE TRIGGER IF NOT EXISTS enforce_valid_initial_state
AFTER INSERT ON tasks
WHEN NOT EXISTS (
    SELECT 1 FROM valid_transitions WHERE from_state IS NULL AND to_state = NEW.state
)
BEGIN
    INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
    VALUES (NEW.task_id, NULL, NEW.state);
    DELETE FROM tasks WHERE task_id = NEW.task_id;
END;
"""

CURRENT_SCHEMA_VERSION = 5

# issue-523: the only state ControlPlane.create_task() ever seeds a new task at. Not derived
# from TransitionRegistry (which only declares state-to-state edges among existing states, not
# initial states) — this is the closest available source of truth for the INSERT-side trigger.
LEGAL_INITIAL_STATES = ["INTAKE"]

CHILD_TABLES = [
    "task_transitions",
    "locked_verifier_baselines",
    "critic_reviews",
    "verification_receipts",
    "asymmetric_persistence_log",
    "transition_decisions",
]
ALL_REBUILD_TABLES = ["tasks"] + CHILD_TABLES

SCHEMA_MIGRATIONS = [
    # Migration: add task_type column if not present (for existing DBs)
    "ALTER TABLE tasks ADD COLUMN task_type TEXT NOT NULL DEFAULT 'GENERAL' CHECK (task_type IN ('GENERAL', 'EVOLUTION'));",
    # Migration: add transition_decisions table if not present (v4)
    """CREATE TABLE IF NOT EXISTS transition_decisions (
        decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
        source_occupancy_transition_id INTEGER NOT NULL,
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        question_id TEXT NOT NULL,
        answer TEXT NOT NULL,
        decision_type TEXT NOT NULL CHECK(decision_type IN ('ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION')),
        actor TEXT NOT NULL,
        recorded_at REAL NOT NULL,
        consumed_at REAL,
        bound_transition_id INTEGER REFERENCES task_transitions(transition_id)
    );""",
    "CREATE INDEX IF NOT EXISTS idx_decisions_lookup ON transition_decisions(task_id, source_occupancy_transition_id);",
    # Migration: add valid_transitions/transition_violations tables + enforcement triggers (v5)
    """CREATE TABLE IF NOT EXISTS valid_transitions (
        from_state TEXT,
        to_state TEXT NOT NULL,
        PRIMARY KEY (from_state, to_state)
    );""",
    """CREATE TABLE IF NOT EXISTS transition_violations (
        violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        attempted_from_state TEXT,
        attempted_to_state TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""",
    """CREATE TRIGGER IF NOT EXISTS enforce_valid_transition
    AFTER UPDATE ON tasks
    WHEN NEW.state != OLD.state
     AND NOT EXISTS (
        SELECT 1 FROM valid_transitions WHERE from_state = OLD.state AND to_state = NEW.state
     )
    BEGIN
        INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
        VALUES (OLD.task_id, OLD.state, NEW.state);
        UPDATE tasks SET state = OLD.state, updated_at = OLD.updated_at WHERE task_id = NEW.task_id;
    END;""",
    """CREATE TRIGGER IF NOT EXISTS enforce_valid_initial_state
    AFTER INSERT ON tasks
    WHEN NOT EXISTS (
        SELECT 1 FROM valid_transitions WHERE from_state IS NULL AND to_state = NEW.state
    )
    BEGIN
        INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
        VALUES (NEW.task_id, NULL, NEW.state);
        DELETE FROM tasks WHERE task_id = NEW.task_id;
    END;""",
]


class SqlitePersistenceAdapter(PersistencePort):
    """SQLite-backed implementation of PersistencePort — connection management, schema
    migration, and every task/transition/receipt/review/verifier/log/worktree CRUD
    operation ControlPlane needs. Revised after external post-implementation review found
    the original version only covered connection/migration, leaving CRUD SQL embedded in
    ControlPlane — this version closes that gap: ControlPlane never calls sqlite3 directly."""

    def __init__(self, db_path: Optional[Path], fs_adapter: FilesystemPort,
                 clock_adapter: Optional[ClockPort] = None,
                 crypto_adapter: Optional[CryptoPort] = None):
        self.db_path = db_path if db_path is not None else self._discover_shared_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._fs = fs_adapter
        self._clock = clock_adapter if clock_adapter is not None else ClockAdapter()
        self._crypto = crypto_adapter if crypto_adapter is not None else CryptoAdapter()

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

            self._sync_valid_transitions(conn)
        finally:
            conn.close()

    def _sync_valid_transitions(self, conn: sqlite3.Connection) -> None:
        """issue-523: resyncs valid_transitions from TransitionRegistry.get_all_edges() plus
        LEGAL_INITIAL_STATES (as from_state IS NULL rows) on every ensure_schema() call —
        self-maintaining, zero manual migration step per DAG change (spec guardrail table).
        Uses parameterized INSERTs, not string-formatted SQL (finding #1)."""
        from control_plane.registry import TransitionRegistry
        registry = TransitionRegistry.load_default()
        edges = registry.get_all_edges()

        conn.execute("DELETE FROM valid_transitions;")
        conn.executemany(
            "INSERT INTO valid_transitions (from_state, to_state) VALUES (?, ?)",
            list(edges) + [(None, s) for s in LEGAL_INITIAL_STATES]
        )
        conn.commit()

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

            # issue-523: ALTER TABLE RENAME re-points existing triggers on `tasks` to follow
            # the rename (to `_tasks_migrating`) rather than dropping them — so both
            # enforcement triggers are now silently bound to the migrating table, not the
            # fresh `tasks` just created by SCHEMA_SQL above. Left alone, this causes two
            # distinct failures found empirically: (a) enforce_valid_initial_state would fire
            # on every bulk row-copy INSERT below, wrongly DELETING every already-progressed
            # task; (b) enforce_valid_transition silently vanishes entirely once
            # `_tasks_migrating` is dropped at the end of the copy loop, since SQLite drops a
            # table's triggers along with it — leaving UPDATE-side enforcement permanently
            # disabled after every rebuild. Drop both explicitly here, recreate both together
            # once real rows are back in place under the correct table.
            conn.execute("DROP TRIGGER IF EXISTS enforce_valid_initial_state;")
            conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition;")

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

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS enforce_valid_transition
                AFTER UPDATE ON tasks
                WHEN NEW.state != OLD.state
                 AND NOT EXISTS (
                    SELECT 1 FROM valid_transitions WHERE from_state = OLD.state AND to_state = NEW.state
                 )
                BEGIN
                    INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
                    VALUES (OLD.task_id, OLD.state, NEW.state);
                    UPDATE tasks SET state = OLD.state, updated_at = OLD.updated_at WHERE task_id = NEW.task_id;
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS enforce_valid_initial_state
                AFTER INSERT ON tasks
                WHEN NOT EXISTS (
                    SELECT 1 FROM valid_transitions WHERE from_state IS NULL AND to_state = NEW.state
                )
                BEGIN
                    INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state)
                    VALUES (NEW.task_id, NULL, NEW.state);
                    DELETE FROM tasks WHERE task_id = NEW.task_id;
                END;
            """)

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
                # Invalidate stale discretionary skip receipts on leaving occupancy
                conn.execute(
                    "DELETE FROM verification_receipts WHERE task_id = ? AND gate_name IN ('multi_agent_review_skipped', 'multi_agent_code_review_skipped')",
                    (task_id,)
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

    def get_last_transition(

        self,
        task_id: str,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
    ) -> Optional[TransitionRecord]:
        """Returns the latest TransitionRecord for task_id matching optional from_state/to_state filters."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            query = "SELECT transition_id, task_id, from_state, to_state, actor, reason, timestamp FROM task_transitions WHERE task_id = ?"
            params: List[Any] = [task_id]
            if from_state is not None:
                query += " AND from_state = ?"
                params.append(from_state)
            if to_state is not None:
                query += " AND to_state = ?"
                params.append(to_state)
            query += " ORDER BY transition_id DESC LIMIT 1"

            row = conn.execute(query, params).fetchone()
            if not row:
                return None
            return TransitionRecord(
                transition_id=row["transition_id"],
                task_id=row["task_id"],
                from_state=row["from_state"],
                to_state=row["to_state"],
                actor=row["actor"],
                reason=row["reason"],
                timestamp=str(row["timestamp"]),
            )
        finally:
            conn.close()

    def apply_transition_with_receipts(
        self,
        request: TransitionCommitRequest,
    ) -> TransitionRecord:
        """Atomically revalidates authoritative persistable facts in SQLite and applies transition.
        Enforces transactional invariants and structural consistency only:
        1. Task exists and current state == request.expected_from_state.
        2. Latest transition_id == request.source_occupancy_transition_id.
        3. Edge (expected_from_state -> to_state) is legal per ALLOWED_TRANSITIONS.
        4. Staged decisions structurally match (task_id, source_occupancy_transition_id, expected_from_state, to_state).
        5. No duplicate question_ids exist across staged decisions.
        6. Valid decision_type in ('ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION').
        7. Atomically updates task state, inserts task_transitions row, inserts transition_decisions
           bound to the new transition_id, and inserts verification_receipts.
        """
        self.ensure_schema()
        conn = self.get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            # 1. Task exists and state check
            task_row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (request.task_id,)).fetchone()
            if not task_row:
                raise ValueError(f"Task '{request.task_id}' not found in tasks table.")
            current_state = task_row["state"]
            if current_state != request.expected_from_state:
                raise ValueError(
                    f"Structural state mismatch: task state is '{current_state}', "
                    f"expected '{request.expected_from_state}'."
                )

            # 2. Source occupancy transition check
            last_trans_row = conn.execute(
                "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
                (request.task_id,)
            ).fetchone()
            latest_trans_id = last_trans_row["transition_id"] if last_trans_row else None
            if latest_trans_id != request.source_occupancy_transition_id:
                raise ValueError(
                    f"Stale occupancy transition ID: latest is {latest_trans_id}, "
                    f"request provided {request.source_occupancy_transition_id}."
                )

            # 3. Legal DAG edge check
            allowed_next = ALLOWED_TRANSITIONS.get(request.expected_from_state, [])
            if request.to_state not in allowed_next:
                raise ValueError(
                    f"Illegal transition edge: '{request.expected_from_state}' -> '{request.to_state}'. "
                    f"Allowed: {allowed_next}."
                )

            # 4. Structural validation of staged decisions
            valid_types = {'ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION'}
            seen_questions = set()
            for d in request.staged_decisions:
                if d.task_id != request.task_id:
                    raise ValueError(f"Structural mismatch: decision task_id '{d.task_id}' != '{request.task_id}'.")
                if d.source_occupancy_transition_id != request.source_occupancy_transition_id:
                    raise ValueError(f"Structural mismatch: decision occupancy ID '{d.source_occupancy_transition_id}' != '{request.source_occupancy_transition_id}'.")
                if d.from_state != request.expected_from_state or d.to_state != request.to_state:
                    raise ValueError(f"Structural mismatch: decision edge ({d.from_state} -> {d.to_state}) != ({request.expected_from_state} -> {request.to_state}).")
                if d.decision_type not in valid_types:
                    raise ValueError(f"Invalid decision_type '{d.decision_type}'. Must be one of {valid_types}.")
                if d.question_id in seen_questions:
                    raise ValueError(f"Duplicate question_id '{d.question_id}' in staged decisions.")
                seen_questions.add(d.question_id)

            # 5. Apply state change
            conn.execute(
                "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
                (request.to_state, request.task_id)
            )

            # 6. Insert task_transitions row
            cursor = conn.execute(
                "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, ?, ?, ?, ?)",
                (request.task_id, request.expected_from_state, request.to_state, request.actor, request.reason)
            )
            new_trans_id = cursor.lastrowid

            # 7. Insert staged decisions bound to new_trans_id
            for d in request.staged_decisions:
                conn.execute(
                    """
                    INSERT INTO transition_decisions (
                        task_id, source_occupancy_transition_id, from_state, to_state,
                        question_id, answer, decision_type, actor, recorded_at, bound_transition_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        d.task_id, d.source_occupancy_transition_id, d.from_state, d.to_state,
                        d.question_id, d.answer, d.decision_type, d.actor, d.recorded_at, new_trans_id
                    )
                )

            # Clear prior discretionary review skip receipts so stale skips don't persist.
            # NOTE (Ordering Dependency): Gate policy evaluation runs upstream before commit,
            # so any skip receipt relevant to the immediate transition being committed has already
            # been evaluated. Staged receipts inserted in Step 8 immediately restore valid skips
            # for the new transition if applicable.
            conn.execute(
                "DELETE FROM verification_receipts WHERE task_id = ? AND gate_name IN ('multi_agent_review_skipped', 'multi_agent_code_review_skipped')",
                (request.task_id,)
            )

            # 8. Insert staged receipts
            for r in request.staged_receipts:
                conn.execute(
                    """
                    INSERT INTO verification_receipts (task_id, gate_name, command_executed, exit_code, receipt_token)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (request.task_id, r["gate_name"], r["command_executed"], r["exit_code"], r["receipt_token"])
                )

            row = conn.execute(
                "SELECT transition_id, task_id, from_state, to_state, actor, reason, timestamp FROM task_transitions WHERE transition_id = ?",
                (new_trans_id,)
            ).fetchone()
            conn.commit()

            return TransitionRecord(
                transition_id=row["transition_id"],
                task_id=row["task_id"],
                from_state=row["from_state"],
                to_state=row["to_state"],
                actor=row["actor"],
                reason=row["reason"],
                timestamp=str(row["timestamp"]),
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_recovery_approval(
        self,
        task_id: str,
        expected_source_state: str,
        destination_state: str,
        source_occupancy_transition_id: int,
        approver: str,
        decision: str,
        reason: str,
    ) -> str:
        """Issues and persists an unconsumed recovery approval decision record bound to the current source occupancy ID."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            with conn:
                task_row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
                if not task_row or task_row["state"] != expected_source_state:
                    raise ValueError(f"Task state is '{task_row['state'] if task_row else None}', expected '{expected_source_state}'.")

                last_trans_row = conn.execute(
                    "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
                    (task_id,)
                ).fetchone()
                if not last_trans_row or last_trans_row["transition_id"] != source_occupancy_transition_id:
                    raise ValueError(f"Stale occupancy ID {source_occupancy_transition_id}.")

                recorded_at = self._clock.current_time()
                existing_count = conn.execute(
                    "SELECT COUNT(*) FROM transition_decisions WHERE task_id = ? AND source_occupancy_transition_id = ?",
                    (task_id, source_occupancy_transition_id)
                ).fetchone()[0]
                token_material = f"RECOVERY-{task_id}-{source_occupancy_transition_id}-{destination_state}-{recorded_at}-{existing_count + 1}"
                token = self._crypto.sha256_hex(token_material)

                conn.execute(
                    """
                    INSERT INTO transition_decisions (
                        task_id, source_occupancy_transition_id, from_state, to_state,
                        question_id, answer, decision_type, actor, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id, source_occupancy_transition_id, expected_source_state, destination_state,
                        f"recovery_approval_{token[:16]}", token, decision, approver, recorded_at
                    )
                )
                return token
        finally:
            conn.close()

    def apply_recovery_transition(
        self,
        task_id: str,
        expected_source_state: str,
        destination_state: str,
        source_occupancy_transition_id: int,
        approval_receipt_token: str,
        actor: str,
        reason: str,
    ) -> TransitionRecord:
        """Atomically executes recovery transition using a verified, unconsumed approval record."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            # 1. State check
            task_row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not task_row or task_row["state"] != expected_source_state:
                raise ValueError(f"State mismatch: task is '{task_row['state'] if task_row else None}', expected '{expected_source_state}'.")

            # 2. Occupancy check
            last_trans_row = conn.execute(
                "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
                (task_id,)
            ).fetchone()
            if not last_trans_row or last_trans_row["transition_id"] != source_occupancy_transition_id:
                raise ValueError(f"Stale occupancy ID: latest is {last_trans_row['transition_id'] if last_trans_row else None}, expected {source_occupancy_transition_id}.")

            # 3. Verify unconsumed approval record matching token & current occupancy directly at SQL level
            decision_row = conn.execute(
                """
                SELECT decision_id FROM transition_decisions
                WHERE task_id = ? AND source_occupancy_transition_id = ?
                  AND from_state = ? AND to_state = ?
                  AND answer = ? AND decision_type = 'APPROVAL'
                  AND consumed_at IS NULL
                """,
                (task_id, source_occupancy_transition_id, expected_source_state, destination_state, approval_receipt_token)
            ).fetchone()

            if not decision_row:
                # Check if it was already consumed to provide a distinct, clear error
                consumed_row = conn.execute(
                    """
                    SELECT decision_id FROM transition_decisions
                    WHERE task_id = ? AND source_occupancy_transition_id = ?
                      AND from_state = ? AND to_state = ?
                      AND answer = ? AND decision_type = 'APPROVAL'
                      AND consumed_at IS NOT NULL
                    """,
                    (task_id, source_occupancy_transition_id, expected_source_state, destination_state, approval_receipt_token)
                ).fetchone()
                if consumed_row:
                    raise ValueError(f"Recovery approval token {approval_receipt_token} has already been consumed.")
                raise ValueError(f"No matching recovery approval record found for token {approval_receipt_token} in current occupancy.")

            # 4. Mark approval consumed
            now = self._clock.current_time()
            conn.execute(
                "UPDATE transition_decisions SET consumed_at = ? WHERE decision_id = ?",
                (now, decision_row["decision_id"])
            )

            # 5. Apply state change & record transition
            conn.execute(
                "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
                (destination_state, task_id)
            )
            cursor = conn.execute(
                "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, ?, ?, ?, ?)",
                (task_id, expected_source_state, destination_state, actor, reason)
            )
            new_trans_id = cursor.lastrowid

            # Bind decision to new transition
            conn.execute(
                "UPDATE transition_decisions SET bound_transition_id = ? WHERE decision_id = ?",
                (new_trans_id, decision_row["decision_id"])
            )

            # Record verification receipt
            conn.execute(
                """
                INSERT INTO verification_receipts (task_id, gate_name, command_executed, exit_code, receipt_token)
                VALUES (?, 'recovery_approval', ?, 0, ?)
                """,
                (task_id, f"apply_recovery_transition({expected_source_state}->{destination_state})", approval_receipt_token)
            )

            row = conn.execute(
                "SELECT transition_id, task_id, from_state, to_state, actor, reason, timestamp FROM task_transitions WHERE transition_id = ?",
                (new_trans_id,)
            ).fetchone()
            conn.commit()

            return TransitionRecord(
                transition_id=row["transition_id"],
                task_id=row["task_id"],
                from_state=row["from_state"],
                to_state=row["to_state"],
                actor=row["actor"],
                reason=row["reason"],
                timestamp=str(row["timestamp"]),
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_decision(self, decision: TransitionDecision) -> int:
        """Records an occupancy-bound TransitionDecision. Rejects duplicates within same occupancy."""
        self.ensure_schema()
        conn = self.get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            existing = conn.execute(
                """
                SELECT COUNT(*) FROM transition_decisions
                WHERE task_id = ? AND source_occupancy_transition_id = ? AND question_id = ?
                """,
                (decision.task_id, decision.source_occupancy_transition_id, decision.question_id),
            ).fetchone()[0]
            if existing > 0:
                raise ValueError(
                    f"Duplicate decision for question '{decision.question_id}' already recorded "
                    f"in occupancy {decision.source_occupancy_transition_id} for task '{decision.task_id}'."
                )

            cursor = conn.execute(
                """
                INSERT INTO transition_decisions (
                    task_id, source_occupancy_transition_id, from_state, to_state,
                    question_id, answer, decision_type, actor, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.task_id,
                    decision.source_occupancy_transition_id,
                    decision.from_state,
                    decision.to_state,
                    decision.question_id,
                    decision.answer,
                    decision.decision_type,
                    decision.actor,
                    decision.recorded_at,
                ),
            )
            decision_id = cursor.lastrowid
            conn.commit()
            return decision_id
        except Exception:
            conn.rollback()
            raise
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
