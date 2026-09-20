"""
tests/test_ensure_schema_fastpath.py
====================================

Purpose:
    Failing-first contract for the ensure_schema() fast path (auth-ciba-increment-b, Problem 1): every
    persistence call runs ensure_schema(), which used to re-parse the 158KB transition_templates.yaml
    (pure-Python YAML, ~0.13s) and take BEGIN IMMEDIATE to DELETE/re-INSERT valid_transitions on EVERY
    call -- including plain reads -- so read operations contended for the write lock and each test setup
    burned ~20s. Contract: an up-to-date database costs a read-only check (no write lock, no YAML parse);
    the registry-derived tables still self-heal when they drift or when the registry inputs change.
    Real SQLite, real YAML, real files; nothing mocked.

Key Input Dependencies:
    - control_plane/adapters.py (SqlitePersistenceAdapter.ensure_schema), registry.py, transition_templates.yaml

Key Functions (test cases):
    - test_registry_load_default_parses_yaml_once_per_content
    - test_up_to_date_ensure_schema_takes_no_write_lock
    - test_up_to_date_ensure_schema_does_not_reparse_yaml
    - test_drifted_valid_transitions_self_heal
    - test_changed_registry_inputs_force_a_resync
    - test_orphaned_migration_table_still_fails_loudly_on_the_fast_path
"""

import sqlite3
import sys
from pathlib import Path

import pytest
import yaml

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.adapters import FilesystemAdapter, SqlitePersistenceAdapter
from control_plane.registry import TransitionRegistry


@pytest.fixture
def adapter(tmp_path):
    a = SqlitePersistenceAdapter(tmp_path / "control_plane.db", FilesystemAdapter())
    a.ensure_schema()
    return a


def _count_yaml_parses(monkeypatch):
    calls = []
    real = yaml.safe_load
    monkeypatch.setattr(yaml, "safe_load", lambda *a, **k: (calls.append(1), real(*a, **k))[1])
    return calls


def test_registry_load_default_parses_yaml_once_per_content(monkeypatch):
    TransitionRegistry.load_default()  # warm
    calls = _count_yaml_parses(monkeypatch)
    for _ in range(5):
        TransitionRegistry.load_default()
    assert calls == []


def test_up_to_date_ensure_schema_takes_no_write_lock(adapter):
    holder = sqlite3.connect(adapter.db_path, isolation_level=None)
    holder.execute("BEGIN IMMEDIATE;")  # another writer is mid-transaction
    try:
        adapter.get_connection = lambda: _short_timeout(adapter.db_path)
        adapter.ensure_schema()  # must not need the write lock
        adapter.get_last_transition("no-such-task")  # a plain read must not either
    finally:
        holder.execute("ROLLBACK;")
        holder.close()


def _short_timeout(db_path):
    conn = sqlite3.connect(str(db_path), timeout=0.3)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 300;")
    return conn


def test_up_to_date_ensure_schema_does_not_reparse_yaml(adapter, monkeypatch):
    calls = _count_yaml_parses(monkeypatch)
    for _ in range(5):
        adapter.ensure_schema()
    assert calls == []


def test_drifted_valid_transitions_self_heal(adapter):
    conn = sqlite3.connect(adapter.db_path)
    before = conn.execute("SELECT COUNT(*) FROM valid_transitions").fetchone()[0]
    conn.execute("DELETE FROM valid_transitions WHERE rowid IN (SELECT rowid FROM valid_transitions LIMIT 3)")
    conn.commit()
    adapter.ensure_schema()
    assert conn.execute("SELECT COUNT(*) FROM valid_transitions").fetchone()[0] == before
    conn.close()


def test_changed_registry_inputs_force_a_resync(adapter):
    conn = sqlite3.connect(adapter.db_path)
    conn.execute("DELETE FROM required_transition_questions")
    conn.execute("UPDATE registry_sync_state SET inputs_fingerprint = 'stale'")
    conn.commit()
    adapter.ensure_schema()
    assert conn.execute("SELECT COUNT(*) FROM required_transition_questions").fetchone()[0] > 0
    assert conn.execute("SELECT inputs_fingerprint FROM registry_sync_state").fetchone()[0] != "stale"
    conn.close()


def test_orphaned_migration_table_still_fails_loudly_on_the_fast_path(adapter):
    conn = sqlite3.connect(adapter.db_path)
    conn.execute("CREATE TABLE _tasks_migrating (x)")
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="orphaned migration tables"):
        adapter.ensure_schema()
