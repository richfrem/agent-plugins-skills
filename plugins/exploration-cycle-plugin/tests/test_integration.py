"""
Purpose:
    Integration tests for the exploration-cycle-plugin control plane spanning
    state_engine.py, sandbox_runner.py, and dispatch.py together: concurrent
    task-completion races, sandbox environment leak prevention, and approval
    expiry rejection.

Key Input Dependencies:
    - state_engine.py, sandbox_runner.py, dispatch.py modules (in ../scripts/)
    - pytest tmp_path and monkeypatch fixtures
"""
import sys, uuid, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import state_engine as SE
import sandbox_runner as SR


@pytest.fixture
def db_conn(tmp_path):
    """Yield a fresh file-backed SQLite connection, closed on teardown."""
    conn = SE.init_db(str(tmp_path / "test.sqlite"))
    yield conn
    conn.close()


def _seed_leased_tasks(conn, count: int = 5) -> tuple:
    """Insert `count` tasks directly as 'leased', bypassing MAX_PARALLEL_AGENTS.

    Exercises concurrent commit_task_complete calls, not the lease gate itself.
    Returns (task_ids, versions) for the caller to use in completion threads.
    """
    task_ids = [str(uuid.uuid4()) for _ in range(count)]
    for i, tid in enumerate(task_ids):
        conn.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, component_name, "
            "status, assigned_subagent_id, lease_expires_at, version) "
            "VALUES (?, 'sess-c', ?, ?, ?, 'leased', ?, datetime('now', '+300 seconds'), 1)",
            (tid, i + 1, f"Phase {i + 1}", f"Comp {i}", f"subagent-{i}"),
        )
    conn.execute(
        "UPDATE sessions SET parallel_agents_running = ? WHERE id = 'sess-c'", (count,)
    )
    conn.commit()

    versions = {}
    for tid in task_ids:
        row = conn.execute("SELECT version FROM tasks WHERE id=?", (tid,)).fetchone()
        versions[tid] = row["version"]
    return task_ids, versions


def test_concurrent_task_completions(tmp_path):
    """5 concurrent threads completing distinct tasks must all succeed within 30s."""
    db_path = tmp_path / "concurrent.sqlite"
    conn = SE.init_db(str(db_path))
    SE.create_session(conn, "sess-c", "Concurrent Session")

    task_ids, versions = _seed_leased_tasks(conn)

    results, errors = [], []

    def complete_task(tid, agent_id, version):
        """Complete one task on its own thread-local DB connection, recording result or error."""
        try:
            thread_conn = SE.init_db(str(db_path))
            ok = SE.commit_task_complete(thread_conn, tid, agent_id, version, f"hash-{tid[:8]}")
            results.append(ok)
            thread_conn.close()
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=complete_task, args=(tid, f"subagent-{i}", versions[tid]))
        for i, tid in enumerate(task_ids)
    ]
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    elapsed = time.time() - start

    assert not errors, f"Threads raised: {errors}"
    assert elapsed < 30
    assert sum(results) == 5
    final = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='complete'").fetchone()[0]
    assert final == 5
    conn.close()


def test_sandbox_env_vars_do_not_leak(monkeypatch):
    """ANTHROPIC_API_KEY and PYTHONPATH must not be visible inside sandboxed process."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-secret")
    monkeypatch.setenv("PYTHONPATH", "/injected")
    result = SR.run_hygienic(
        [sys.executable, "-c",
         "import os, sys; "
         "leaked = [k for k in ['ANTHROPIC_API_KEY', 'PYTHONPATH'] if k in os.environ]; "
         "sys.exit(len(leaked))"],
        timeout=10,
    )
    assert result.returncode == 0


def test_expired_approval_is_rejected(db_conn):
    """Verify check_approval rejects an approval whose expires_at is in the past."""
    import dispatch
    approval_id = str(uuid.uuid4())
    SE.create_session(db_conn, "sess", "Expiry Session")
    db_conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '[]', '[]', 'abc', '/spec.md', 1,
                datetime('now', '-1 second'))
    """, (approval_id,))
    db_conn.commit()
    is_valid, reason = dispatch.check_approval(db_conn, approval_id)
    assert is_valid is False
    assert "expired" in reason.lower()
