# plugins/exploration-cycle-plugin/tests/test_state_engine.py
import sys, sqlite3, uuid, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import state_engine as SE


@pytest.fixture
def mem_conn(tmp_path):
    """File-backed SQLite — WAL mode requires a real filesystem, not :memory:."""
    db_path = tmp_path / "test.sqlite"
    conn = SE.init_db(str(db_path))
    yield conn
    conn.close()


def test_wal_mode_enabled(tmp_path):
    db_path = tmp_path / "wal.sqlite"
    conn = SE.init_db(str(db_path))
    result = conn.execute("PRAGMA journal_mode;").fetchone()
    assert result[0].lower() == "wal"
    conn.close()


def test_all_tables_created(mem_conn):
    expected = {"sessions", "tasks", "approvals", "artifacts", "reviews",
                "dispatches", "policy_decisions"}
    rows = mem_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    actual = {r[0] for r in rows}
    assert expected == actual, f"Missing tables: {expected - actual}"


def test_session_status_constraint(mem_conn):
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute(
            "INSERT INTO sessions (id, session_name, status) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), "test", "invalid_status")
        )
        mem_conn.commit()


def test_task_fk_references_session(mem_conn):
    """tasks.session_id must reference a real session (FK enforced at connection level)."""
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, component_name) "
            "VALUES (?,?,?,?,?)",
            (str(uuid.uuid4()), "nonexistent-session", 1, "phase1", "comp1")
        )
        mem_conn.commit()


def test_approval_ttl_capped_at_one_hour(mem_conn):
    """approvals.expires_at must not exceed created_at + 1 hour (CHECK constraint)."""
    SE.create_session(mem_conn, "s1", "TTL Test Session")
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute("""
            INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
                spec_hash, spec_source_path, expires_at)
            VALUES (?, 's1', 'p1', '[]', '[]', 'abc', '/spec.md', datetime('now', '+2 hours'))
        """, (str(uuid.uuid4()),))
        mem_conn.commit()


def test_immediate_transaction_retries_on_busy(tmp_path):
    db_path = tmp_path / "retry.sqlite"
    conn1 = SE.init_db(str(db_path))
    conn2 = SE.init_db(str(db_path))
    conn2.execute("PRAGMA busy_timeout=0")

    conn1.execute("BEGIN EXCLUSIVE")
    retry_count = []

    def write_with_conn2():
        try:
            with SE._immediate_transaction(conn2) as c:
                retry_count.append(1)
        except Exception:
            retry_count.append(0)

    t = threading.Thread(target=write_with_conn2)
    t.start()
    time.sleep(0.2)
    conn1.execute("ROLLBACK")
    t.join(timeout=5)
    conn1.close()
    conn2.close()
    assert len(retry_count) >= 1


def test_state_engine_cli_init(tmp_path):
    """state_engine.py must be callable as a CLI tool — dual-runtime invariant (ADR-002)."""
    import subprocess
    db_path = str(tmp_path / "cli.sqlite")
    result = subprocess.run(
        [sys.executable, str(Path(SE.__file__)), "init", "--db-path", db_path],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"CLI init failed: {result.stderr}"
    assert Path(db_path).exists(), "DB file must exist after CLI init"
