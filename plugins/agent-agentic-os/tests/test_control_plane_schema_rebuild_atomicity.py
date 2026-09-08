"""
test_control_plane_schema_rebuild_atomicity.py — atomicity fix for _rebuild_schema_transactional() (issue-552)
================================================================================================================

Purpose:
    Proves _rebuild_schema_transactional()'s BEGIN IMMEDIATE/COMMIT transaction is actually
    atomic — a mid-rebuild failure leaves the DB in its exact pre-rebuild state (true rollback),
    not the half-migrated state the pre-fix code produced (conn.executescript(SCHEMA_SQL)
    silently commits any open transaction, per documented CPython sqlite3 behavior). Also covers
    the fix's necessary side effects: correct statement-splitting of SCHEMA_SQL (which embeds
    two CREATE TRIGGER ... BEGIN ... END; blocks with internal semicolons), no PRAGMA
    journal_mode/foreign_keys/busy_timeout drift, and map-debt.md write ordering (must not write
    on a rolled-back rebuild).

Key Input Dependencies:
    - Temporary SQLite databases via pytest's tmp_path fixture
    - control_plane.adapters.SqlitePersistenceAdapter, SCHEMA_SQL, _split_schema_sql_statements

Key Functions:
    - test_splitter_produces_expected_statement_breakdown()
    - test_splitter_preserves_trigger_bodies_intact()
    - test_rebuild_with_nonempty_data_survives_intact()
    - test_rebuild_failure_mid_copy_loop_rolls_back_completely()
    - test_rebuild_preserves_journal_mode_and_busy_timeout()
    - test_map_debt_not_written_on_rolled_back_rebuild()
"""

import sqlite3
import re
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter, SCHEMA_SQL


def _make_adapter(tmp_path):
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    return adapter, db_path


def _seed_realistic_data(conn):
    """Seeds tasks + child rows across multiple states, mirroring real control-plane usage.
    enforce_valid_initial_state only permits NULL->INTAKE inserts (LEGAL_INITIAL_STATES), so
    task-b is inserted at INTAKE and legally transitioned to RETROSPECTIVE via UPDATE because
    the trivial completion path now requires the retrospective gate."""
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
        ("task-a", "Task A", "INTAKE", "claude"),
    )
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
        ("task-b", "Task B", "INTAKE", "claude"),
    )
    conn.execute("UPDATE tasks SET state = 'INTERVIEW' WHERE task_id = 'task-b';")
    conn.execute(
        "INSERT INTO task_transitions (task_id, from_state, to_state, actor) VALUES (?, ?, ?, ?)",
        ("task-b", "INTAKE", "INTERVIEW", "test"),
    )
    interview_answers = {
        "interview_classification": "TRIVIAL",
        "interview_summary": "A small verified pipeline change.",
        "interview_scope": "The control-plane test fixture.",
        "interview_verification": "The schema rebuild test passes.",
        "interview_trivial_evidence": "The focused diff and test prove the change.",
        "confirm_interview_complete": "Yes [Recommended]",
    }
    for question_id, answer in interview_answers.items():
        conn.execute(
            """
            INSERT INTO transition_decisions (
                task_id, source_occupancy_transition_id, from_state, to_state,
                question_id, answer, decision_type, actor, recorded_at
            ) VALUES ('task-b', 1, 'INTERVIEW', 'RETROSPECTIVE', ?, ?, 'ANSWER', 'human', 12345.0)
            """,
            (question_id, answer),
        )
    conn.execute("UPDATE tasks SET state = 'RETROSPECTIVE' WHERE task_id = 'task-b';")
    conn.execute(
        "INSERT INTO task_transitions (task_id, from_state, to_state, actor) VALUES (?, ?, ?, ?)",
        ("task-b", "INTERVIEW", "RETROSPECTIVE", "test"),
    )
    conn.execute(
        "INSERT INTO critic_reviews (task_id, iteration, model_used, verdict, critique_findings) VALUES (?, ?, ?, ?, ?)",
        ("task-b", 1, "test-model", "PASS", "all good"),
    )
    conn.execute(
        "INSERT INTO verification_receipts (task_id, gate_name, command_executed, exit_code, receipt_token) VALUES (?, ?, ?, ?, ?)",
        ("task-b", "test-gate", "echo test", 0, "token-123"),
    )
    conn.commit()


def test_splitter_produces_expected_statement_breakdown():
    """Splitter must filter out all 3 leading PRAGMAs and produce exactly the DDL statements
    SCHEMA_SQL actually contains: 13 CREATE TABLE, 4 CREATE INDEX, 2 CREATE TRIGGER."""
    from control_plane.adapters import _split_schema_sql_statements

    statements = _split_schema_sql_statements(SCHEMA_SQL)

    assert not any(s.strip().upper().startswith("PRAGMA") for s in statements), (
        "PRAGMA statements must be filtered out of the split — they must not be individually "
        "executed inside the rebuild transaction (finding #2)."
    )

    upper_starts = [s.strip().upper() for s in statements]
    create_table = [s for s in upper_starts if s.startswith("CREATE TABLE")]
    create_index = [s for s in upper_starts if s.startswith("CREATE INDEX")]
    create_trigger = [s for s in upper_starts if s.startswith("CREATE TRIGGER") or "CREATE TRIGGER" in s]

    expected_table = len(re.findall(r"CREATE TABLE IF NOT EXISTS", SCHEMA_SQL, flags=re.IGNORECASE))
    expected_index = len(re.findall(r"CREATE INDEX IF NOT EXISTS", SCHEMA_SQL, flags=re.IGNORECASE))
    expected_trigger = len(re.findall(r"CREATE TRIGGER IF NOT EXISTS", SCHEMA_SQL, flags=re.IGNORECASE))
    assert len(create_table) == expected_table, f"expected {expected_table} CREATE TABLE statements, got {len(create_table)}"
    assert len(create_index) == expected_index, f"expected {expected_index} CREATE INDEX statements, got {len(create_index)}"
    assert len(create_trigger) == expected_trigger, f"expected {expected_trigger} CREATE TRIGGER statements, got {len(create_trigger)}"


def test_splitter_preserves_trigger_bodies_intact():
    """The two CREATE TRIGGER ... BEGIN ... END; blocks must survive as single statements, not
    be fragmented on their embedded semicolons (each trigger body has 2 inner semicolons)."""
    from control_plane.adapters import _split_schema_sql_statements

    statements = _split_schema_sql_statements(SCHEMA_SQL)
    trigger_statements = [s for s in statements if "CREATE TRIGGER" in s.upper()]

    assert len(trigger_statements) == 2
    for stmt in trigger_statements:
        assert "BEGIN" in stmt.upper() and stmt.rstrip().endswith(";") and stmt.rstrip().upper().endswith("END;")
        # Each trigger body has an INSERT + one more statement (UPDATE or DELETE) before END.
        assert stmt.upper().count("INSERT INTO TRANSITION_VIOLATIONS") == 1

    # Verify each is independently valid, executable SQL against a fresh connection with the
    # tables it depends on already present.
    conn = sqlite3.connect(":memory:")
    for stmt in [s for s in statements if s.strip().upper().startswith("CREATE TABLE")]:
        conn.execute(stmt)
    for stmt in trigger_statements:
        conn.execute(stmt)  # must not raise
    conn.close()


def test_rebuild_with_nonempty_data_survives_intact(tmp_path):
    """Happy-path rebuild against realistic non-empty data — the missing test-category gap
    identified during intake. All rows must survive the rebuild unchanged."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = adapter.get_connection()
    try:
        _seed_realistic_data(conn)
        adapter._rebuild_schema_transactional(conn)
    finally:
        conn.close()

    conn = sqlite3.connect(str(db_path))
    try:
        tasks = {r[0]: r[1] for r in conn.execute("SELECT task_id, state FROM tasks")}
        assert tasks == {"task-a": "INTAKE", "task-b": "RETROSPECTIVE"}
        transitions = conn.execute("SELECT COUNT(*) FROM task_transitions").fetchone()[0]
        assert transitions == 2
        orphans = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE '\\_%\\_migrating' ESCAPE '\\'"
        ).fetchone()[0]
        assert orphans == 0
    finally:
        conn.close()


def test_rebuild_failure_mid_copy_loop_rolls_back_completely(tmp_path, monkeypatch):
    """RED->GREEN: forces an exception partway through the copy loop against a non-empty DB.
    After the fix, the DB must be restored to its exact pre-rebuild state — no orphan
    _*_migrating tables, no data loss, schema_version unchanged. This is the core atomicity
    contract issue #552 exists to establish."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = adapter.get_connection()
    try:
        _seed_realistic_data(conn)
        pre_version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
    finally:
        conn.close()

    call_count = {"n": 0}
    real_copy = SqlitePersistenceAdapter._copy_common_columns

    def failing_copy(self, conn, source_table, dest_table):
        call_count["n"] += 1
        if call_count["n"] == 3:  # fail partway through the 7-table copy loop
            raise sqlite3.OperationalError("simulated mid-rebuild failure")
        return real_copy(self, conn, source_table, dest_table)

    monkeypatch.setattr(SqlitePersistenceAdapter, "_copy_common_columns", failing_copy)

    conn = adapter.get_connection()
    try:
        with pytest.raises(sqlite3.OperationalError):
            adapter._rebuild_schema_transactional(conn)
    finally:
        conn.close()

    # Verify true rollback: no orphan tables, data intact, schema_version unchanged.
    conn = sqlite3.connect(str(db_path))
    try:
        orphans = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE '\\_%\\_migrating' ESCAPE '\\'"
        ).fetchone()[0]
        assert orphans == 0, "orphan _*_migrating tables must not survive a rolled-back rebuild"

        tasks = {r[0]: r[1] for r in conn.execute("SELECT task_id, state FROM tasks")}
        assert tasks == {"task-a": "INTAKE", "task-b": "RETROSPECTIVE"}, "data must be unchanged after rollback"

        post_version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
        assert post_version == pre_version, "schema_version must be unchanged after rollback"
    finally:
        conn.close()


def test_rebuild_preserves_journal_mode_and_busy_timeout(tmp_path):
    """The 3 leading PRAGMA statements in SCHEMA_SQL must be skipped during the split
    (finding #2) without causing journal_mode/busy_timeout drift — they're already set on the
    connection by ensure_schema() before this method ever runs."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = adapter.get_connection()
    try:
        adapter._rebuild_schema_transactional(conn)
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        busy_timeout = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
    finally:
        conn.close()

    assert journal_mode.lower() == "wal"
    assert busy_timeout == 5000


class _RecordingFilesystemAdapter(FilesystemAdapter):
    """Wraps the real FilesystemAdapter but records every append_text() call, so the test can
    assert on write occurrence without touching the real repo's references/map-debt.md."""

    def __init__(self):
        self.appended: list = []

    def append_text(self, path, text):  # type: ignore[override]
        self.appended.append((path, text))

    def exists(self, path):  # type: ignore[override]
        # _log_orphan_merge_conflicts() no-ops if the map-debt file doesn't "exist" — report
        # True unconditionally so the write path (or its absence) is what the test observes.
        return True


def test_map_debt_not_written_on_rolled_back_rebuild(tmp_path, monkeypatch):
    """Finding #1 (HIGH): _log_orphan_merge_conflicts()'s map-debt.md write must not happen
    until after COMMIT succeeds. Forces a post-merge-but-pre-commit failure with an active
    orphan-merge path (a dangling _tasks_old from a previously-interrupted migration) and
    asserts zero map-debt writes occurred when the transaction rolls back."""
    db_path = tmp_path / "control_plane.db"
    recording_fs = _RecordingFilesystemAdapter()
    adapter = SqlitePersistenceAdapter(db_path, recording_fs)
    adapter.ensure_schema()

    conn = adapter.get_connection()
    try:
        # Seed a real tasks row, then create a dangling "_tasks_old" with a conflicting
        # task_id/different data, simulating a prior interrupted migration's leftover.
        _seed_realistic_data(conn)
        conn.execute('CREATE TABLE "_tasks_old" AS SELECT * FROM tasks WHERE task_id = "task-a";')
        conn.execute('UPDATE "_tasks_old" SET title = "Stale conflicting title";')
        conn.commit()
    finally:
        conn.close()

    # Let the entire copy loop AND the orphan merge (which calls _log_orphan_merge_conflicts,
    # the write under test) run to completion, then fail on the final schema_version INSERT —
    # i.e. after the write this test cares about has already happened, but before COMMIT. This
    # is the failure window finding #1 identifies: a write with real, observable effect that
    # occurs inside the "atomic" block but isn't covered by the SQL transaction.
    real_merge = SqlitePersistenceAdapter._merge_orphaned_tasks_old

    def failing_merge(self, conn):
        real_merge(self, conn)
        raise sqlite3.OperationalError("simulated post-merge pre-commit failure")

    monkeypatch.setattr(SqlitePersistenceAdapter, "_merge_orphaned_tasks_old", failing_merge)

    conn = adapter.get_connection()
    try:
        with pytest.raises(sqlite3.OperationalError):
            adapter._rebuild_schema_transactional(conn)
    finally:
        conn.close()

    assert recording_fs.appended == [], (
        "map-debt.md must receive no writes when the rebuild transaction rolls back "
        "(finding #1) — the write must be deferred until after a successful COMMIT"
    )


class _RaisingFilesystemAdapter(FilesystemAdapter):
    """Simulates a map-debt.md filesystem write failure (disk full, permissions) on
    append_text(), to prove it doesn't get reported as a schema-rebuild failure."""

    def append_text(self, path, text):  # type: ignore[override]
        raise OSError("simulated disk-full failure writing map-debt.md")

    def exists(self, path):  # type: ignore[override]
        return True


def test_map_debt_write_failure_after_successful_commit_does_not_raise(tmp_path, monkeypatch):
    """Implementation-review finding (MODERATE): if the deferred map-debt.md write itself
    fails after COMMIT has already succeeded, that failure must not propagate as an exception
    out of _rebuild_schema_transactional()/ensure_schema() — the schema rebuild genuinely
    succeeded; only a low-severity logging side effect failed. Every CRUD method calls
    ensure_schema() first, so an unhandled exception here would make a fully successful
    rebuild look like a fatal schema failure to every caller."""
    db_path = tmp_path / "control_plane.db"
    raising_fs = _RaisingFilesystemAdapter()
    adapter = SqlitePersistenceAdapter(db_path, raising_fs)
    adapter.ensure_schema()

    conn = adapter.get_connection()
    try:
        _seed_realistic_data(conn)
        conn.execute('CREATE TABLE "_tasks_old" AS SELECT * FROM tasks WHERE task_id = "task-a";')
        conn.execute('UPDATE "_tasks_old" SET title = "Stale conflicting title";')
        conn.commit()
    finally:
        conn.close()

    conn = adapter.get_connection()
    try:
        with pytest.warns(UserWarning, match="map-debt logging failed"):
            adapter._rebuild_schema_transactional(conn)  # must not raise
    finally:
        conn.close()

    # The rebuild itself must have genuinely succeeded despite the logging failure.
    conn = sqlite3.connect(str(db_path))
    try:
        tasks = {r[0] for r in conn.execute("SELECT task_id FROM tasks")}
        assert "task-a" in tasks and "task-b" in tasks
    finally:
        conn.close()


def test_health_check_fails_loudly_on_orphaned_migration_table(tmp_path):
    """Finding #4: ensure_schema() must detect an orphaned _<table>_migrating table as its
    literal first operation and fail with a clear, actionable error — not a cryptic
    FOREIGN KEY constraint failed surfaced deep inside a retried rebuild."""
    adapter, db_path = _make_adapter(tmp_path)
    conn = adapter.get_connection()
    try:
        conn.execute('CREATE TABLE "_tasks_migrating" (task_id TEXT PRIMARY KEY);')
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(RuntimeError, match="orphaned migration tables"):
        adapter.ensure_schema()


def test_health_check_does_not_misfire_on_concurrent_legitimate_rebuild(tmp_path):
    """Finding #5 (MODERATE): a second connection's health check specifically must not
    false-fire against a first connection's legitimate, uncommitted, in-progress rebuild. WAL
    snapshot isolation should make connection B's read of sqlite_master see the pre-rebuild
    state cleanly while A's BEGIN IMMEDIATE (which has renamed tasks -> _tasks_migrating) is
    still open and uncommitted. Scoped to the health-check read itself, not the rest of
    ensure_schema()'s later writes — those legitimately contend for A's write lock, a separate,
    already-tracked lock-hold-time concern (see spec §6 Out of Scope), not a health-check bug."""
    adapter, db_path = _make_adapter(tmp_path)

    conn_a = sqlite3.connect(str(db_path), timeout=1.0)
    conn_a.execute("PRAGMA foreign_keys = OFF;")
    conn_a.execute("BEGIN IMMEDIATE;")
    conn_a.execute('ALTER TABLE "tasks" RENAME TO "_tasks_migrating";')
    # Deliberately left open and uncommitted — simulates a legitimate in-progress rebuild.

    try:
        adapter_b = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
        conn_b = adapter_b.get_connection()
        try:
            # Must not raise: connection B's read of sqlite_master must see the pre-rebuild
            # snapshot (tasks present, no orphan _tasks_migrating), not A's uncommitted rename.
            adapter_b._check_no_orphaned_migration_tables(conn_b)
        finally:
            conn_b.close()
    finally:
        conn_a.execute("ROLLBACK;")
        conn_a.close()
