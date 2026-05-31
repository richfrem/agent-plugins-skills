# plugins/exploration-cycle-plugin/tests/test_integration.py
import sys, uuid, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import state_engine as SE
import sandbox_runner as SR


@pytest.fixture
def db_conn(tmp_path):
    conn = SE.init_db(str(tmp_path / "test.sqlite"))
    yield conn
    conn.close()


def test_concurrent_task_completions(tmp_path):
    """5 concurrent threads completing distinct tasks must all succeed within 30s."""
    db_path = tmp_path / "concurrent.sqlite"
    conn = SE.init_db(str(db_path))
    SE.create_session(conn, "sess-c", "Concurrent Session")

    task_ids = [str(uuid.uuid4()) for _ in range(5)]
    # Insert tasks directly as 'leased' to bypass MAX_PARALLEL_AGENTS=2 limit.
    # The test exercises concurrent commit_task_complete calls, not the lease gate.
    for i, tid in enumerate(task_ids):
        conn.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, component_name, "
            "status, assigned_subagent_id, lease_expires_at, version) "
            "VALUES (?, 'sess-c', ?, ?, ?, 'leased', ?, datetime('now', '+300 seconds'), 1)",
            (tid, i + 1, f"Phase {i + 1}", f"Comp {i}", f"subagent-{i}"),
        )
    conn.execute(
        "UPDATE sessions SET parallel_agents_running = 5 WHERE id = 'sess-c'"
    )
    conn.commit()

    versions = {}
    for tid in task_ids:
        row = conn.execute("SELECT version FROM tasks WHERE id=?", (tid,)).fetchone()
        versions[tid] = row["version"]

    results, errors = [], []

    def complete_task(tid, agent_id, version):
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
