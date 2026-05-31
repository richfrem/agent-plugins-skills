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


def test_create_session_and_add_task(mem_conn):
    SE.create_session(mem_conn, "sess-1", "Test Session")
    SE.add_task(mem_conn, "task-1", "sess-1", 1, "Phase 1", "Comp A")
    row = mem_conn.execute("SELECT * FROM tasks WHERE id='task-1'").fetchone()
    assert row is not None
    assert row["status"] == "pending"


def test_lease_task_increments_parallel_counter(mem_conn):
    """Successful lease must increment sessions.parallel_agents_running."""
    SE.create_session(mem_conn, "sess-2", "Session 2")
    SE.add_task(mem_conn, "task-2", "sess-2", 1, "Phase 1", "Comp B")
    before = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-2'"
    ).fetchone()["parallel_agents_running"]

    SE.lease_task(mem_conn, "task-2", "subagent-abc", ttl_seconds=300)

    after = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-2'"
    ).fetchone()["parallel_agents_running"]
    assert after == before + 1


def test_commit_task_complete_decrements_parallel_counter(mem_conn):
    """Completion must decrement sessions.parallel_agents_running."""
    SE.create_session(mem_conn, "sess-3", "Session 3")
    SE.add_task(mem_conn, "task-3", "sess-3", 1, "Phase 1", "Comp C")
    SE.lease_task(mem_conn, "task-3", "subagent-x", ttl_seconds=300)
    row = mem_conn.execute("SELECT version FROM tasks WHERE id='task-3'").fetchone()

    SE.commit_task_complete(mem_conn, "task-3", "subagent-x", row["version"], "hash1")

    after = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-3'"
    ).fetchone()["parallel_agents_running"]
    assert after == 0


def test_commit_task_complete_cas_guard(mem_conn):
    SE.create_session(mem_conn, "sess-4", "Session 4")
    SE.add_task(mem_conn, "task-4", "sess-4", 1, "Phase 1", "Comp D")
    SE.lease_task(mem_conn, "task-4", "subagent-x", ttl_seconds=300)
    row = mem_conn.execute("SELECT version FROM tasks WHERE id='task-4'").fetchone()
    version = row["version"]

    assert SE.commit_task_complete(mem_conn, "task-4", "wrong-agent", version, "h") is False
    assert SE.commit_task_complete(mem_conn, "task-4", "subagent-x", version + 99, "h") is False
    assert SE.commit_task_complete(mem_conn, "task-4", "subagent-x", version, "h") is True


def test_budget_gate_blocks_over_parallel_limit(mem_conn):
    SE.create_session(mem_conn, "sess-5", "Session 5")
    mem_conn.execute(
        "UPDATE sessions SET parallel_agents_running=? WHERE id='sess-5'",
        (SE.MAX_PARALLEL_AGENTS,)
    )
    mem_conn.commit()
    SE.add_task(mem_conn, "task-5", "sess-5", 1, "Phase 1", "Comp E")
    with pytest.raises(RuntimeError, match="parallel_agents_running"):
        SE.lease_task(mem_conn, "task-5", "subagent-over-limit", ttl_seconds=300)


def test_record_premium_call_increments_counter(mem_conn):
    SE.create_session(mem_conn, "sess-6", "Session 6")
    SE.record_premium_call(mem_conn, "sess-6")
    used = mem_conn.execute(
        "SELECT premium_calls_used FROM sessions WHERE id='sess-6'"
    ).fetchone()["premium_calls_used"]
    assert used == 1


def test_verify_review_current_detects_mismatch(mem_conn):
    """verify_review_current must return False when artifact hash doesn't match review hash."""
    SE.create_session(mem_conn, "sess-7", "Session 7")
    SE.add_task(mem_conn, "task-7", "sess-7", 1, "Phase 1", "Comp F")
    artifact_id = str(uuid.uuid4())
    mem_conn.execute(
        "INSERT INTO artifacts (id, task_id, path, original_sha256, sanitized_sha256, "
        "sanitization_report, artifact_type, created_by, sanitizer_version) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (artifact_id, "task-7", "/tmp/file.py", "aaa", "bbb", "{}", "code", "agent-1", "1.0")
    )
    review_id = str(uuid.uuid4())
    mem_conn.execute(
        "INSERT INTO reviews (id, artifact_id, reviewer, review_type, verdict, artifact_sha256) "
        "VALUES (?,?,?,?,?,?)",
        (review_id, artifact_id, "reviewer-1", "code_quality", "pass", "DIFFERENT_HASH")
    )
    mem_conn.commit()
    assert SE.verify_review_current(mem_conn, artifact_id) is False


def test_reclaim_expired_leases_returns_tasks_to_pending(mem_conn):
    SE.create_session(mem_conn, "sess-8", "Session 8")
    SE.add_task(mem_conn, "task-8", "sess-8", 1, "Phase 1", "Comp G")
    SE.lease_task(mem_conn, "task-8", "subagent-crash", ttl_seconds=300)
    # Manually expire the lease
    mem_conn.execute(
        "UPDATE tasks SET lease_expires_at=datetime('now', '-1 second') WHERE id='task-8'"
    )
    mem_conn.commit()
    count = SE.reclaim_expired_leases(mem_conn)
    assert count >= 1
    row = mem_conn.execute("SELECT status FROM tasks WHERE id='task-8'").fetchone()
    assert row["status"] == "pending"


def test_state_engine_cli_lease_task(tmp_path):
    """CLI lease-task command must work end-to-end (dual-runtime invariant, ADR-002)."""
    import subprocess
    import json
    db_path = str(tmp_path / "cli.sqlite")
    conn = SE.init_db(db_path)
    SE.create_session(conn, "cli-sess", "CLI Test")
    SE.add_task(conn, "cli-task", "cli-sess", 1, "Phase 1", "Comp A")
    conn.close()
    result = subprocess.run(
        [sys.executable, str(Path(SE.__file__)), "lease-task",
         "--db-path", db_path, "--task-id", "cli-task", "--subagent-id", "gemini-1"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"CLI lease-task failed: {result.stderr}"
    assert json.loads(result.stdout)["ok"] is True


def test_project_dashboard_round_trips(mem_conn):
    SE.create_session(mem_conn, "sess-d1", "My Session")
    SE.add_task(mem_conn, "task-d1a", "sess-d1", 1, "Phase 1", "Component Alpha")
    SE.add_task(mem_conn, "task-d1b", "sess-d1", 1, "Phase 1", "Component Beta")
    md = SE.project_dashboard(mem_conn, "sess-d1")
    assert "My Session" in md
    assert "Component Alpha" in md
    assert "Component Beta" in md


def test_validate_dashboard_detects_drift(mem_conn):
    SE.create_session(mem_conn, "sess-d2", "Drift Session")
    SE.add_task(mem_conn, "task-d2", "sess-d2", 1, "Phase 1", "Comp X")
    fake_md = "- [x] Comp X\n"  # DB says pending, md says complete
    assert SE.validate_dashboard_checkboxes(fake_md, mem_conn, "sess-d2") is False


def test_migrate_dashboard_parses_tasks(mem_conn, tmp_path):
    dashboard = tmp_path / "exploration-dashboard.md"
    dashboard.write_text(
        "# Exploration Session: Test Migration\n"
        "## Phase 1: Discovery\n"
        "- [ ] Task Alpha\n"
        "- [x] Task Beta\n"
        "- [~] Task Gamma\n"  # skipped — must be ignored
    )
    SE.migrate_dashboard(dashboard, mem_conn)
    tasks = mem_conn.execute(
        "SELECT component_name, status FROM tasks ORDER BY phase_ordinal"
    ).fetchall()
    names = {t["component_name"] for t in tasks}
    assert "Task Alpha" in names
    assert "Task Beta" in names
    assert "Task Gamma" not in names  # [~] skipped lines not migrated
    beta = next(t for t in tasks if t["component_name"] == "Task Beta")
    assert beta["status"] == "complete"
    assert (tmp_path / "exploration-dashboard.md.migrated").exists()
