# plugins/exploration-cycle-plugin/scripts/state_engine.py
"""
state_engine.py — SQLite Control Plane for Exploration Cycle Plugin
DB path: ${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite
"""
import json, os, random, re, sqlite3, time, uuid
from contextlib import contextmanager
from pathlib import Path

MAX_RETRIES = 5
MAX_PARALLEL_AGENTS = 2
MAX_PREMIUM_CALLS_PER_PHASE = 1

# PRAGMA foreign_keys must be set on the connection object, not inside executescript.
# executescript does not persist PRAGMAs across its implicit transaction.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    session_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('in_progress', 'complete', 'suspended')) DEFAULT 'in_progress',
    awaiting_human_validation BOOLEAN DEFAULT 0,
    premium_calls_used INTEGER DEFAULT 0,
    parallel_agents_running INTEGER DEFAULT 0,
    review_passes_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    phase_ordinal INTEGER NOT NULL,
    phase_name TEXT NOT NULL,
    component_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'leased', 'complete', 'failed')) DEFAULT 'pending',
    assigned_subagent_id TEXT DEFAULT NULL,
    version INTEGER DEFAULT 1,
    payload_hash TEXT DEFAULT NULL,
    lease_expires_at TIMESTAMP DEFAULT NULL,
    leased_at TIMESTAMP DEFAULT NULL,
    completed_at TIMESTAMP DEFAULT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    phase TEXT NOT NULL,
    approved_actions TEXT NOT NULL,
    allowed_paths TEXT NOT NULL,
    spec_hash TEXT NOT NULL,
    spec_source_path TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP DEFAULT NULL,
    revoked_at TIMESTAMP DEFAULT NULL,
    revocation_reason TEXT DEFAULT NULL,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id),
    CHECK(expires_at <= datetime(created_at, '+1 hour'))
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    path TEXT NOT NULL,
    original_sha256 TEXT NOT NULL,
    sanitized_sha256 TEXT NOT NULL,
    sanitizer_version TEXT NOT NULL,
    sanitization_report TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    review_type TEXT CHECK(review_type IN (
        'spec_alignment', 'code_quality', 'runtime_observer',
        'semantic_drift', 'domain_purity')) NOT NULL,
    verdict TEXT CHECK(verdict IN ('pass', 'fail', 'warning')) NOT NULL,
    artifact_sha256 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
);

CREATE TABLE IF NOT EXISTS dispatches (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    approval_id TEXT,
    envelope_hash TEXT NOT NULL,
    status TEXT CHECK(status IN ('queued', 'running', 'complete', 'failed', 'rejected')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(approval_id) REFERENCES approvals(id)
);

CREATE TABLE IF NOT EXISTS policy_decisions (
    id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL,
    decision TEXT CHECK(decision IN ('allow', 'deny', 'defer')) NOT NULL,
    reason_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dispatch_id) REFERENCES dispatches(id)
);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    """Open DB, verify WAL mode (fail closed if unavailable), apply schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    result = conn.execute("PRAGMA journal_mode;").fetchone()
    if result[0].lower() != "wal":
        conn.close()
        raise RuntimeError(
            f"WAL mode unavailable at {db_path!r}. "
            "Check filesystem (network mounts do not support WAL). Aborting."
        )
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")  # Must be set on connection, not in executescript
    conn.executescript(SCHEMA_SQL)
    return conn


@contextmanager
def _immediate_transaction(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE with exponential backoff retry (up to MAX_RETRIES).

    ROLLBACK failures are suppressed to avoid masking the original exception (FIX-2).
    A safety raise after loop exhaustion makes the error explicit if MAX_RETRIES is 0.
    """
    for attempt in range(MAX_RETRIES):
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
                conn.execute("COMMIT")
                return
            except Exception:
                try:
                    conn.execute("ROLLBACK")
                except Exception:
                    pass  # Don't mask the original exception
                raise
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < MAX_RETRIES - 1:
                delay = (2 ** attempt) * 0.05 + random.uniform(0, 0.01)
                time.sleep(delay)
                continue
            raise
    raise sqlite3.OperationalError(
        f"Failed to acquire IMMEDIATE transaction after {MAX_RETRIES} retries"
    )


def create_session(conn: sqlite3.Connection, session_id: str, session_name: str) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO sessions (id, session_name) VALUES (?, ?)",
            (session_id, session_name),
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="State Engine CLI")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize database")
    p_init.add_argument("--db-path", required=True)

    p_lease = sub.add_parser("lease-task")
    p_lease.add_argument("--db-path", required=True)
    p_lease.add_argument("--task-id", required=True)
    p_lease.add_argument("--subagent-id", required=True)
    p_lease.add_argument("--ttl", type=int, default=300)

    p_complete = sub.add_parser("commit-complete")
    p_complete.add_argument("--db-path", required=True)
    p_complete.add_argument("--task-id", required=True)
    p_complete.add_argument("--subagent-id", required=True)
    p_complete.add_argument("--version", type=int, required=True)
    p_complete.add_argument("--payload-hash", required=True)

    p_dash = sub.add_parser("project-dashboard")
    p_dash.add_argument("--db-path", required=True)
    p_dash.add_argument("--session-id", required=True)

    p_reclaim = sub.add_parser("reclaim-expired")
    p_reclaim.add_argument("--db-path", required=True)

    args = parser.parse_args()

    if args.command == "init":
        init_db(args.db_path)
        print(f"Database initialized at {args.db_path}")
    elif args.command == "lease-task":
        raise NotImplementedError("lease-task: added in Task 6")
    elif args.command == "commit-complete":
        raise NotImplementedError("commit-complete: added in Task 6")
    elif args.command == "project-dashboard":
        raise NotImplementedError("project-dashboard: added in Task 7")
    elif args.command == "reclaim-expired":
        raise NotImplementedError("reclaim-expired: added in Task 6")
