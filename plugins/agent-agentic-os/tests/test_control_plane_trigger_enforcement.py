"""
test_control_plane_trigger_enforcement.py — SQLite trigger-based transition enforcement (issue-523)
=====================================================================================================

Purpose:
    Proves that context/control_plane.db enforces legal state transitions at the SQLite engine
    level, independent of the Python application layer — closing the raw-sqlite3-bypass gap
    described in GitHub Issue #523. Exercises the AFTER UPDATE and AFTER INSERT triggers, the
    valid_transitions registry-sync table, and the transition_violations audit log directly via
    raw sqlite3 connections (not through ControlPlane/SqlitePersistenceAdapter), since the whole
    point of this feature is protecting against callers that skip the Python layer entirely.

    The UPDATE trigger reverts (coerces state+updated_at back to OLD.*, never destroys). The
    INSERT trigger deletes the illegally-inserted row instead — a deliberate asymmetry (see
    docs/plans/issue-523-trigger-enforcement-spec.md guardrail table): a fresh illegal INSERT
    has no accumulated transitions/receipts/decisions to protect, so delete loses nothing a
    legitimate caller would have accrued, and it avoids a cross-trigger cascade where a
    corrective UPDATE would itself fire enforce_valid_transition (e.g. DONE -> INTAKE isn't a
    legal edge) and revert the fix right back.

Key Input Dependencies:
    - Temporary SQLite databases via pytest's tmp_path fixture
    - control_plane.registry.TransitionRegistry.load_default() (for the parity assertion)

Key Functions:
    - test_valid_transitions_table_matches_registry()
    - test_illegal_update_transition_via_raw_sql_is_reverted_and_logged()
    - test_legal_transition_via_raw_sql_is_unaffected_and_unlogged()
    - test_illegal_insert_initial_state_via_raw_sql_is_deleted_and_logged()
    - test_delete_then_reinsert_bypass_is_caught_by_insert_trigger()
    - test_insert_trigger_cascade_does_not_fire_update_trigger()
    - test_trigger_survives_schema_rebuild()
    - test_recursive_triggers_on_hits_recursion_limit_but_no_illegal_write_persists()
"""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter
from control_plane.registry import TransitionRegistry

# INTAKE -> IN_WORKTREE is not a legal edge in ALLOWED_TRANSITIONS (unlike INTAKE -> DONE,
# which IS a legal short-circuit edge) — this is the illegal-UPDATE example used throughout
# issue-523's design discussion. Using DONE here would silently test nothing.
ILLEGAL_UPDATE_TARGET = "IN_WORKTREE"


def _make_adapter(tmp_path):
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    return adapter, db_path


def _insert_legal_task(conn, task_id, state):
    """Inserts a task row bypassing Python (raw SQL), at a state legal as an initial state."""
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
        (task_id, "Test Task", state, "claude"),
    )
    conn.commit()


def test_valid_transitions_table_matches_registry(tmp_path):
    """valid_transitions (as materialized in a live DB) matches TransitionRegistry.get_all_edges()
    exactly — the automated drift-detection test requested during interview-spec."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        db_edges = {
            (row[0], row[1])
            for row in conn.execute("SELECT from_state, to_state FROM valid_transitions WHERE from_state IS NOT NULL")
        }
    finally:
        conn.close()
    registry_edges = TransitionRegistry.load_default().get_all_edges()
    assert db_edges == registry_edges


def test_illegal_update_transition_via_raw_sql_is_reverted_and_logged(tmp_path):
    """A raw sqlite3 UPDATE attempting an illegal (OLD.state, NEW.state) transition is reverted
    (both state and updated_at restored — finding #7) and logged to transition_violations."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        _insert_legal_task(conn, "task-1", "INTAKE")
        before = conn.execute("SELECT state, updated_at FROM tasks WHERE task_id='task-1'").fetchone()

        conn.execute(f"UPDATE tasks SET state='{ILLEGAL_UPDATE_TARGET}' WHERE task_id='task-1'")
        conn.commit()

        after = conn.execute("SELECT state, updated_at FROM tasks WHERE task_id='task-1'").fetchone()
        assert after[0] == "INTAKE"
        assert after[1] == before[1]

        violations = conn.execute(
            "SELECT task_id, attempted_from_state, attempted_to_state FROM transition_violations WHERE task_id='task-1'"
        ).fetchall()
        assert violations == [("task-1", "INTAKE", ILLEGAL_UPDATE_TARGET)]
    finally:
        conn.close()


def test_legal_transition_via_raw_sql_is_unaffected_and_unlogged(tmp_path):
    """A raw sqlite3 UPDATE performing a legal transition is unaffected by the trigger and
    produces no transition_violations row."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        _insert_legal_task(conn, "task-2", "INTAKE")

        conn.execute("UPDATE tasks SET state='INTERVIEW' WHERE task_id='task-2'")
        conn.commit()

        after = conn.execute("SELECT state FROM tasks WHERE task_id='task-2'").fetchone()
        assert after[0] == "INTERVIEW"

        count = conn.execute(
            "SELECT COUNT(*) FROM transition_violations WHERE task_id='task-2'"
        ).fetchone()[0]
        assert count == 0
    finally:
        conn.close()


def test_illegal_insert_initial_state_via_raw_sql_is_deleted_and_logged(tmp_path):
    """A raw sqlite3 INSERT creating a new task already in an illegal initial state (e.g. DONE)
    is deleted (revised: not coerced — see module docstring) and logged to
    transition_violations with attempted_from_state=NULL (finding #5)."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
            ("task-3", "Test Task", "DONE", "claude"),
        )
        conn.commit()

        after = conn.execute("SELECT * FROM tasks WHERE task_id='task-3'").fetchone()
        assert after is None

        violations = conn.execute(
            "SELECT task_id, attempted_from_state, attempted_to_state FROM transition_violations WHERE task_id='task-3'"
        ).fetchall()
        assert violations == [("task-3", None, "DONE")]
    finally:
        conn.close()


def test_delete_then_reinsert_bypass_is_caught_by_insert_trigger(tmp_path):
    """DELETE + re-INSERT (an UPDATE-trigger bypass, finding #5) is caught by the INSERT-side
    trigger on the re-INSERT half, since the re-INSERT is itself checked against legal initial
    states — the re-inserted row is deleted, leaving the task nonexistent."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        _insert_legal_task(conn, "task-4", "INTAKE")

        conn.execute("DELETE FROM tasks WHERE task_id='task-4'")
        conn.execute(
            "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
            ("task-4", "Test Task", "DONE", "claude"),
        )
        conn.commit()

        after = conn.execute("SELECT * FROM tasks WHERE task_id='task-4'").fetchone()
        assert after is None

        violations = conn.execute(
            "SELECT task_id, attempted_from_state, attempted_to_state FROM transition_violations WHERE task_id='task-4'"
        ).fetchall()
        assert violations == [("task-4", None, "DONE")]
    finally:
        conn.close()


def test_insert_trigger_cascade_does_not_fire_update_trigger(tmp_path):
    """Regression test for the cross-trigger cascade bug found during implementation: the
    INSERT trigger's original coerce-to-INTAKE corrective UPDATE fired enforce_valid_transition
    as a side effect (since e.g. DONE -> INTAKE isn't a legal edge), which reverted the
    coercion right back and logged a spurious second violation. Deleting instead of coercing
    fixes this — proves exactly one violation row is logged, not two, and the row is gone."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
            ("task-7", "Test Task", "DONE", "claude"),
        )
        conn.commit()

        count = conn.execute(
            "SELECT COUNT(*) FROM transition_violations WHERE task_id='task-7'"
        ).fetchone()[0]
        assert count == 1

        after = conn.execute("SELECT * FROM tasks WHERE task_id='task-7'").fetchone()
        assert after is None
    finally:
        conn.close()


def test_trigger_survives_schema_rebuild(tmp_path):
    """The enforcement triggers are re-declared as part of SCHEMA_SQL, so they survive
    _rebuild_schema_transactional()'s rename->recreate->copy path, not just a fresh
    ensure_schema() call."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = adapter.get_connection()
    try:
        adapter._rebuild_schema_transactional(conn)
    finally:
        conn.close()

    conn = sqlite3.connect(str(db_path))
    try:
        _insert_legal_task(conn, "task-5", "INTAKE")
        conn.execute(f"UPDATE tasks SET state='{ILLEGAL_UPDATE_TARGET}' WHERE task_id='task-5'")
        conn.commit()
        after = conn.execute("SELECT state FROM tasks WHERE task_id='task-5'").fetchone()
        assert after[0] == "INTAKE"
    finally:
        conn.close()


def test_recursive_triggers_on_hits_recursion_limit_but_no_illegal_write_persists(tmp_path):
    """With PRAGMA recursive_triggers = ON explicitly set (finding #2), the corrective UPDATE
    inside the UPDATE trigger's body re-fires the same trigger (the correction itself looks
    like a fresh, non-adjacent transition), oscillating until SQLite's built-in recursion-depth
    cap aborts the entire statement — rolling back the illegal write AND the violation-log
    INSERT together, the same way RAISE(ABORT) does (see spec guardrail table).

    Documented, accepted residual risk (decided 2026-09-07, not a security regression): the
    illegal write never persists — this asserts state is unaffected — but the violation goes
    unlogged in this non-default pragma mode, and the caller gets an unhandled
    sqlite3.OperationalError instead of a clean revert. recursive_triggers is OFF by default in
    SQLite; this only matters if something else touching this DB explicitly turns it on."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA recursive_triggers = ON;")
        _insert_legal_task(conn, "task-6", "INTAKE")

        with pytest.raises(sqlite3.OperationalError, match="too many levels of trigger recursion"):
            conn.execute(f"UPDATE tasks SET state='{ILLEGAL_UPDATE_TARGET}' WHERE task_id='task-6'")
            conn.commit()

        after = conn.execute("SELECT state FROM tasks WHERE task_id='task-6'").fetchone()
        assert after[0] == "INTAKE"

        count = conn.execute(
            "SELECT COUNT(*) FROM transition_violations WHERE task_id='task-6'"
        ).fetchone()[0]
        assert count == 0
    finally:
        conn.close()
