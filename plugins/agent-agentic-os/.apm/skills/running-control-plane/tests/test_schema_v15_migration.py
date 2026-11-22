"""S4 tests: schema v14 -> v15 migration (DoD row 4, G2, G2b, G3, arch-2-1/2-2)."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest

from control_plane.adapters import CURRENT_SCHEMA_VERSION, FilesystemAdapter, SqlitePersistenceAdapter
from control_plane.constants import (
    RETIRED_STATES,
    RETIRED_V14_EDGES,
    STATE_ABSORBED_BY,
    SchemaMigrationRequired,
)
from control_plane.migration import migrate_schema


def _make_v14_db(db_path: Path, *, with_retired_tasks: bool = True) -> Path:
    """Create a realistic schema v14 SQLite database with one open task per retired state,
    one PENDING request, and one DONE task whose history uses retired v14 edges."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE tasks (
            task_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            state TEXT NOT NULL,
            task_type TEXT NOT NULL DEFAULT 'GENERAL',
            runtime_tool TEXT NOT NULL,
            worktree_path TEXT,
            worktree_branch TEXT,
            worktree_state TEXT,
            spec_path TEXT,
            model_tier TEXT,
            model_id TEXT,
            guidance_block_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE task_transitions (
            transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            actor TEXT NOT NULL,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE valid_transitions (
            from_state TEXT,
            to_state TEXT NOT NULL,
            authorized_actor TEXT NOT NULL DEFAULT 'agent_or_human',
            requires_proof INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (from_state, to_state)
        );
        CREATE TABLE required_transition_questions (
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            question_id TEXT NOT NULL,
            PRIMARY KEY (from_state, to_state, question_id)
        );
        CREATE TABLE transition_decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            source_occupancy_transition_id INTEGER NOT NULL,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            question_id TEXT NOT NULL,
            answer TEXT NOT NULL,
            decision_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            recorded_at REAL NOT NULL,
            consumed_at REAL,
            bound_transition_id INTEGER REFERENCES task_transitions(transition_id)
        );
        CREATE TABLE transition_request (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            occupancy_id INTEGER NOT NULL,
            nonce TEXT NOT NULL UNIQUE,
            expiration REAL NOT NULL,
            revision_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            jti TEXT,
            consumed_at REAL,
            created_at REAL NOT NULL,
            challenge_version TEXT,
            content_snapshot TEXT
        );
        CREATE TABLE transition_violations (
            violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            attempted_from_state TEXT,
            attempted_to_state TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actor TEXT,
            reason TEXT,
            detail TEXT,
            kind TEXT NOT NULL DEFAULT 'ILLEGAL_TRANSITION'
        );
        CREATE TABLE schema_version (version INTEGER NOT NULL);
        INSERT INTO schema_version (version) VALUES (14);
        """
    )

    if with_retired_tasks:
        for idx, state in enumerate(RETIRED_STATES, start=1):
            tid = f"t-retired-{idx}"
            conn.execute(
                "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, 'claude')",
                (tid, f"Open in {state}", state),
            )
            conn.execute(
                "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'NONE', 'INTAKE', 'human', 'init')",
                (tid,),
            )
            conn.execute(
                "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'INTAKE', ?, 'human', 'setup')",
                (tid, state),
            )
            if state == "AWAITING_APPROVAL":
                conn.execute(
                    "INSERT INTO transition_request (task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash, status, created_at) "
                    "VALUES (?, 'AWAITING_APPROVAL', 'APPROVED', 2, 'nonce-pending-1', ?, 'rev1', 'PENDING', ?)",
                    (tid, time.time() + 3600, time.time()),
                )

    conn.commit()
    conn.close()
    return db_path


def test_ensure_schema_refuses_v14_with_open_retired_tasks_byte_identical(tmp_path):
    db_path = _make_v14_db(tmp_path / "control_plane.db")
    before_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()

    adapter = SqlitePersistenceAdapter(db_path=db_path, fs_adapter=FilesystemAdapter())
    with pytest.raises(SchemaMigrationRequired) as exc_info:
        adapter.ensure_schema()

    assert "migrate-schema" in str(exc_info.value)
    after_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
    assert after_sha == before_sha, "ensure_schema modified a v14 DB before refusing!"


def test_migrate_schema_dry_run_then_yes_maps_all_five_retired_states_and_is_idempotent(tmp_path):
    db_path = _make_v14_db(tmp_path / "control_plane.db")
    before_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()

    dry = migrate_schema(db_path, dry_run=True)
    assert dry["exit_code"] == 0
    assert dry["status"] == "dry_run"
    assert len(dry["tasks_to_map"]) == 5
    assert hashlib.sha256(db_path.read_bytes()).hexdigest() == before_sha

    res = migrate_schema(db_path, yes=True)
    assert res["exit_code"] == 0, res
    assert res["status"] == "migrated"
    assert Path(res["backup_path"]).is_file()
    assert hashlib.sha256(Path(res["backup_path"]).read_bytes()).hexdigest() == before_sha
    assert res["expired_requests"] == 1

    conn = sqlite3.connect(str(db_path))
    try:
        assert conn.execute("SELECT version FROM schema_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
        for idx, retired_state in enumerate(RETIRED_STATES, start=1):
            tid = f"t-retired-{idx}"
            actual = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (tid,)).fetchone()[0]
            assert actual == STATE_ABSORBED_BY[retired_state], f"{tid}: {retired_state} -> {actual}"
            mig_row = conn.execute(
                "SELECT from_state, to_state, actor, migration_run_id FROM task_transitions "
                "WHERE task_id = ? AND actor = 'migration'",
                (tid,),
            ).fetchone()
            assert mig_row == (retired_state, STATE_ABSORBED_BY[retired_state], "migration", res["run_id"])
        run_row = conn.execute("SELECT from_version, to_version, finished_at FROM schema_migration_runs WHERE id = ?", (res["run_id"],)).fetchone()
        assert run_row[0] == 14 and run_row[1] == 15 and run_row[2] is not None
        assert conn.execute("SELECT status FROM transition_request WHERE nonce = 'nonce-pending-1'").fetchone()[0] == "EXPIRED"
    finally:
        conn.close()

    # Idempotent: running again returns exit code 3 (already v15)
    again = migrate_schema(db_path, yes=True)
    assert again["exit_code"] == 3
    assert again["status"] == "already_v15"

    # Running ensure_schema twice after migration preserves retired and migration rows
    adapter = SqlitePersistenceAdapter(db_path=db_path, fs_adapter=FilesystemAdapter())
    adapter.ensure_schema()
    adapter.ensure_schema()
    conn = sqlite3.connect(str(db_path))
    try:
        retired_count = conn.execute("SELECT COUNT(*) FROM valid_transitions WHERE retired = 1").fetchone()[0]
        mig_edge_count = conn.execute("SELECT COUNT(*) FROM migration_edges").fetchone()[0]
        assert retired_count == len(RETIRED_V14_EDGES)
        assert mig_edge_count == len(STATE_ABSORBED_BY)
    finally:
        conn.close()


def test_migrate_schema_mid_transaction_crash_rolls_back_to_v14(tmp_path):
    db_path = _make_v14_db(tmp_path / "control_plane.db")

    def boom(stage, _conn):
        if stage == "after_first_task":
            raise RuntimeError("simulated power loss")

    res = migrate_schema(db_path, yes=True, fault_hook=boom)
    assert res["exit_code"] == 1
    assert res["status"] == "failed"
    assert Path(res["backup_path"]).is_file()

    conn = sqlite3.connect(str(db_path))
    try:
        assert conn.execute("SELECT version FROM schema_version").fetchone()[0] == 14
        # Every retired task is still in its original state
        for idx, retired_state in enumerate(RETIRED_STATES, start=1):
            actual = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (f"t-retired-{idx}",)).fetchone()[0]
            assert actual == retired_state
        # No open migration run row exists
        has_runs = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migration_runs'").fetchone()
        if has_runs:
            assert conn.execute("SELECT COUNT(*) FROM schema_migration_runs WHERE finished_at IS NULL").fetchone()[0] == 0
    finally:
        conn.close()
