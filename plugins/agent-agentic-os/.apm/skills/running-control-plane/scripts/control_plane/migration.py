#!/usr/bin/env python3
"""
control_plane/migration.py — Sole Owner of the Schema v14 -> v15 Data Migration (G3, arch-2-1/2-2)
==================================================================================================

Purpose:
    Performs the atomic v14 -> v15 control-plane database migration:
      1. Backs up the DB file to `<db>.bak-v14-<UTC>`.
      2. In ONE BEGIN IMMEDIATE transaction:
         - applies the v15 DDL (columns, migration_edges, schema_migration_runs, signed_decisions, trigger rebuild);
         - writes derived rows via SqlitePersistenceAdapter._write_derived_rows(conn) (no nested BEGIN);
         - opens a schema_migration_runs row (from_version=14, to_version=15, started_at=UTC ISO-8601, finished_at=NULL);
         - maps every open task in RETIRED_STATES to STATE_ABSORBED_BY[state], re-reading tasks.state after
           each UPDATE (the trigger reverts silently on refusal) and aborting/rolling back with exit 1 if unchanged;
         - inserts a task_transitions row (actor='migration', migration_run_id=run_id) for each migrated task;
         - expires PENDING transition_request rows of migrated tasks;
         - bumps schema_version to 15 and updates registry_sync_state;
         - closes schema_migration_runs (sets finished_at);
         - COMMITs.
      3. Any error rolls back cleanly, leaving the DB at v14 and preserving the backup.

Exit codes:
    0 = migrated (or dry-run succeeded)
    1 = migration failed and rolled back
    2 = usage error (neither --dry-run nor --yes, or missing DB)
    3 = already at v15 (idempotent no-op)
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from control_plane.adapters import (
    CURRENT_SCHEMA_VERSION,
    ENFORCE_VALID_TRANSITION_TRIGGER_SQL,
    FilesystemAdapter,
    SqlitePersistenceAdapter,
)
from control_plane.constants import (
    RETIRED_STATES,
    RETIRED_V14_EDGES,
    STATE_ABSORBED_BY,
)


_V15_DDL_STATEMENTS: tuple[str, ...] = (
    "ALTER TABLE valid_transitions ADD COLUMN retired INTEGER NOT NULL DEFAULT 0;",
    "ALTER TABLE valid_transitions ADD COLUMN kind TEXT NOT NULL DEFAULT 'normal';",
    "CREATE TABLE IF NOT EXISTS migration_edges (from_state TEXT NOT NULL, to_state TEXT NOT NULL, PRIMARY KEY (from_state, to_state));",
    "CREATE TABLE IF NOT EXISTS schema_migration_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, from_version INTEGER NOT NULL, to_version INTEGER NOT NULL, started_at TEXT NOT NULL, finished_at TEXT);",
    "ALTER TABLE task_transitions ADD COLUMN migration_run_id INTEGER REFERENCES schema_migration_runs(id);",
    "ALTER TABLE tasks ADD COLUMN rollback_base_sha TEXT;",
    """CREATE TABLE IF NOT EXISTS signed_decisions (
        decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
        occupancy_id INTEGER NOT NULL,
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        question_id TEXT NOT NULL,
        decision_text TEXT NOT NULL,
        request_id INTEGER,
        nonce TEXT NOT NULL,
        challenge BLOB NOT NULL,
        signature BLOB NOT NULL,
        principal TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        decided_at TEXT NOT NULL
    );""",
    "CREATE INDEX IF NOT EXISTS idx_signed_decisions_task ON signed_decisions(task_id, occupancy_id);",
    "DROP TRIGGER IF EXISTS enforce_valid_transition;",
    ENFORCE_VALID_TRANSITION_TRIGGER_SQL,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _backup_path_for(db_path: Path, utc_stamp: Optional[str] = None) -> Path:
    stamp = utc_stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return db_path.parent / f"{db_path.name}.bak-v14-{stamp}"


def _read_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.OperationalError:
        return 0


def _read_retired_tasks(conn: sqlite3.Connection) -> List[Dict[str, str]]:
    placeholders = ", ".join("?" for _ in RETIRED_STATES)
    rows = conn.execute(
        f"SELECT task_id, state FROM tasks WHERE state IN ({placeholders}) ORDER BY task_id",
        RETIRED_STATES,
    ).fetchall()
    return [
        {"task_id": r[0], "from_state": r[1], "to_state": STATE_ABSORBED_BY[r[1]]}
        for r in rows
    ]


def migrate_schema(
    db_path: Path,
    *,
    dry_run: bool = False,
    yes: bool = False,
    fault_hook: Optional[Callable[[str, sqlite3.Connection], None]] = None,
) -> Dict[str, Any]:
    """Run or preview the v14 -> v15 migration.

    `fault_hook` is a test-only seam invoked at named checkpoints ('after_ddl', 'after_first_task',
    'before_commit') so crash/rollback tests can inject an exception mid-transaction.
    """
    db_path = Path(db_path)
    if dry_run == yes:
        return {
            "status": "usage_error",
            "exit_code": 2,
            "message": "Specify exactly one of --dry-run or --yes.",
        }
    if not db_path.is_file():
        return {
            "status": "missing_db",
            "exit_code": 2,
            "message": f"Database not found: {db_path}",
        }

    ro_conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        current_version = _read_version(ro_conn)
        if current_version >= CURRENT_SCHEMA_VERSION:
            return {
                "status": "already_v15",
                "exit_code": 3,
                "from_version": current_version,
                "to_version": CURRENT_SCHEMA_VERSION,
                "message": f"Database {db_path} is already at schema v{current_version}; nothing to migrate.",
            }
        tasks_to_map = _read_retired_tasks(ro_conn)
    finally:
        ro_conn.close()

    backup_path = _backup_path_for(db_path)
    if dry_run:
        return {
            "status": "dry_run",
            "exit_code": 0,
            "from_version": current_version,
            "to_version": CURRENT_SCHEMA_VERSION,
            "backup_path": str(backup_path),
            "tasks_to_map": tasks_to_map,
            "retired_edges_count": len(RETIRED_V14_EDGES),
        }

    # --yes: back up first, then migrate in one BEGIN IMMEDIATE transaction.
    shutil.copy2(db_path, backup_path)
    adapter = SqlitePersistenceAdapter(db_path=db_path, fs_adapter=FilesystemAdapter())

    conn = sqlite3.connect(str(db_path), timeout=10.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    try:
        conn.execute("BEGIN IMMEDIATE;")

        # 1. Apply v15 DDL (including trigger rebuild)
        for stmt in _V15_DDL_STATEMENTS:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as exc:
                if "duplicate column" not in str(exc).lower():
                    raise

        # Add kind column to signed_gate_evidence if that table already exists
        has_sge = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='signed_gate_evidence'"
        ).fetchone()
        if has_sge:
            try:
                conn.execute("ALTER TABLE signed_gate_evidence ADD COLUMN kind TEXT NOT NULL DEFAULT 'gate';")
            except sqlite3.OperationalError as exc:
                if "duplicate column" not in str(exc).lower():
                    raise

        if fault_hook:
            fault_hook("after_ddl", conn)

        # 2. Write derived rows (valid_transitions + retired + migration_edges) with no nested BEGIN
        adapter._write_derived_rows(conn)

        # 3. Open schema_migration_runs row
        started_at = _utc_now_iso()
        cur = conn.execute(
            "INSERT INTO schema_migration_runs (from_version, to_version, started_at, finished_at) "
            "VALUES (?, ?, ?, NULL)",
            (current_version, CURRENT_SCHEMA_VERSION, started_at),
        )
        run_id = cur.lastrowid

        # 4. Map every open retired-state task, verify post-UPDATE state, log transition, expire PENDING requests
        migrated_tasks: List[Dict[str, str]] = []
        expired_requests = 0
        for idx, item in enumerate(tasks_to_map):
            task_id = item["task_id"]
            from_state = item["from_state"]
            to_state = item["to_state"]

            conn.execute(
                "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ? AND state = ?",
                (to_state, task_id, from_state),
            )
            # Trigger reverts silently on refusal; always re-read tasks.state (arch-2-1)
            actual = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if actual is None or actual[0] != to_state:
                raise RuntimeError(
                    f"Migration UPDATE for task '{task_id}' ({from_state} -> {to_state}) was reverted "
                    f"(actual state: {actual[0] if actual else None}). Rolling back."
                )

            conn.execute(
                "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason, migration_run_id) "
                "VALUES (?, ?, ?, 'migration', ?, ?)",
                (
                    task_id,
                    from_state,
                    to_state,
                    f"schema v{current_version}->v{CURRENT_SCHEMA_VERSION} state absorption",
                    run_id,
                ),
            )

            exp = conn.execute(
                "UPDATE transition_request SET status = 'EXPIRED' WHERE task_id = ? AND status = 'PENDING'",
                (task_id,),
            )
            expired_requests += exp.rowcount
            migrated_tasks.append(item)

            if idx == 0 and fault_hook:
                fault_hook("after_first_task", conn)

        # 5. Bump schema_version and refresh registry_sync_state digest
        conn.execute("DELETE FROM schema_version;")
        conn.execute("INSERT INTO schema_version (version) VALUES (?);", (CURRENT_SCHEMA_VERSION,))
        conn.execute(
            "INSERT OR REPLACE INTO registry_sync_state (id, inputs_fingerprint, tables_digest) VALUES (1, ?, ?)",
            (adapter._sync_inputs_fingerprint(), adapter._derived_state_digest(conn)),
        )

        # 6. Close the migration run row
        finished_at = _utc_now_iso()
        conn.execute(
            "UPDATE schema_migration_runs SET finished_at = ? WHERE id = ?",
            (finished_at, run_id),
        )

        if fault_hook:
            fault_hook("before_commit", conn)

        conn.execute("COMMIT;")
        return {
            "status": "migrated",
            "exit_code": 0,
            "run_id": run_id,
            "from_version": current_version,
            "to_version": CURRENT_SCHEMA_VERSION,
            "started_at": started_at,
            "finished_at": finished_at,
            "backup_path": str(backup_path),
            "migrated_tasks": migrated_tasks,
            "expired_requests": expired_requests,
        }
    except Exception as exc:
        try:
            conn.execute("ROLLBACK;")
        except sqlite3.Error:
            pass
        return {
            "status": "failed",
            "exit_code": 1,
            "backup_path": str(backup_path),
            "error": str(exc),
        }
    finally:
        conn.close()
