"""
test_control_plane_sqlite_persistence_adapter.py — Persistence Extraction (issue-524, Step 5)
==================================================================================================

Purpose:
    Unit tests for control_plane/adapters.py's SqlitePersistenceAdapter in isolation — proving
    connection management, schema initialization, and the self-healing legacy-schema migration
    all work correctly when exercised directly against the adapter, not only indirectly through
    ControlPlane. Complements (does not replace) test_agent_control.py's existing self-heal
    tests, which already cover this logic end-to-end through the ControlPlane facade — these
    tests confirm the same behavior survives being addressed as its own component.

Key Input Dependencies:
    - Temporary SQLite databases via pytest's tmp_path fixture

Key Functions:
    - test_adapter_get_connection_returns_configured_connection()
    - test_adapter_ensure_schema_creates_all_tables()
    - test_adapter_ensure_schema_idempotent()
    - test_adapter_resolves_db_path_when_none_given()
    - test_control_plane_composes_persistence_adapter()
"""

import sqlite3
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter, CURRENT_SCHEMA_VERSION
from agent_control import ControlPlane


def test_adapter_get_connection_returns_configured_connection(tmp_path):
    """get_connection() returns a sqlite3.Connection with row_factory, foreign_keys, and
    busy_timeout configured — matching the original _get_connection() behavior exactly."""
    adapter = SqlitePersistenceAdapter(tmp_path / "control_plane.db", FilesystemAdapter())
    conn = adapter.get_connection()
    try:
        assert conn.row_factory is sqlite3.Row
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_status == 1
    finally:
        conn.close()


def test_adapter_ensure_schema_creates_all_tables(tmp_path):
    """ensure_schema() creates every expected table and seeds schema_version."""
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()

    conn = sqlite3.connect(str(db_path))
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()}
    for expected in ("tasks", "task_transitions", "locked_verifier_baselines",
                     "critic_reviews", "verification_receipts", "asymmetric_persistence_log",
                     "schema_version"):
        assert expected in tables

    version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION
    conn.close()


def test_adapter_ensure_schema_idempotent(tmp_path):
    """Calling ensure_schema() twice on an already-current schema is a no-op — no orphaned
    migration artifacts, no duplicate schema_version rows."""
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    adapter.ensure_schema()

    conn = sqlite3.connect(str(db_path))
    version_rows = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
    assert version_rows == 1
    leftover = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_migrating' OR name = '_tasks_old')"
    ).fetchall()
    assert leftover == []
    conn.close()


def test_adapter_resolves_db_path_when_none_given(tmp_path, monkeypatch):
    """When db_path=None, the adapter resolves a path itself via _discover_shared_db_path()
    rather than raising — mirrors ControlPlane's original db_path=None constructor behavior."""
    monkeypatch.chdir(tmp_path)
    adapter = SqlitePersistenceAdapter(None, FilesystemAdapter())
    assert adapter.db_path is not None
    assert adapter.db_path.name == "control_plane.db"


def test_control_plane_composes_persistence_adapter(tmp_path):
    """ControlPlane wires a SqlitePersistenceAdapter internally and exposes db_path as a
    convenience mirror of the adapter's resolved path (backward-compatible facade)."""
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    assert isinstance(cp._persistence, SqlitePersistenceAdapter)
    assert cp.db_path == cp._persistence.db_path == db_path


def test_update_worktree_on_fresh_db_preserves_auto_initialization(tmp_path):
    """Regression test (external review round 2): the pre-refactor update_worktree() began
    with self.init_db(), so calling it against a brand-new db_path self-healed the schema
    before querying. After the persistence extraction, update_worktree() calls
    self._persistence.read_current_state() first — which must still self-heal the schema
    (ensure_schema()) rather than raising sqlite3.OperationalError: no such table: tasks.
    This must fail with the expected domain error ("Task not found"), never a raw SQLite
    schema error, proving the auto-initialization behavior was preserved end-to-end."""
    import pytest
    from agent_control import ControlPlane

    cp = ControlPlane(db_path=tmp_path / "brand-new.db")
    with pytest.raises(ValueError, match="Task not found"):
        cp.update_worktree(
            task_id="missing-task",
            worktree_path="/tmp/wt",
            worktree_branch="branch",
            worktree_state="pushed_to_origin",
        )
