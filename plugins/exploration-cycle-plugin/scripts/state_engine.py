# plugins/exploration-cycle-plugin/scripts/state_engine.py
"""
state_engine.py — SQLite Control Plane for Exploration Cycle Plugin
DB path: ${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite
"""
import json, random, re, sqlite3, sys, time, uuid
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
    requires_premium BOOLEAN DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS phase_metrics (
    session_id TEXT NOT NULL,
    phase_ordinal INTEGER NOT NULL,
    premium_calls_used INTEGER DEFAULT 0,
    PRIMARY KEY (session_id, phase_ordinal),
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

CREATE TABLE IF NOT EXISTS nonces (
    nonce TEXT PRIMARY KEY,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    # Migration: add requires_premium column if upgrading from v1.3
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN requires_premium BOOLEAN DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise
    return conn


@contextmanager
def _immediate_transaction(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE with exponential backoff retry (up to MAX_RETRIES).

    ROLLBACK failures are logged to stderr but do not mask the original exception.
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
                except Exception as rollback_exc:
                    sys.stderr.write(f"[state_engine] ROLLBACK failed: {rollback_exc}\n")
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


def record_nonce(conn: sqlite3.Connection, nonce: str) -> bool:
    """Persist nonce to prevent cross-invocation replay. Returns False if already used (SEC-001)."""
    try:
        with _immediate_transaction(conn) as c:
            c.execute("INSERT INTO nonces (nonce) VALUES (?)", (nonce,))
        return True
    except sqlite3.IntegrityError:
        return False


def create_session(conn: sqlite3.Connection, session_id: str, session_name: str) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO sessions (id, session_name) VALUES (?, ?)",
            (session_id, session_name),
        )


def add_task(conn: sqlite3.Connection, task_id: str, session_id: str,
             phase_ordinal: int, phase_name: str, component_name: str,
             requires_premium: bool = False) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, "
            "component_name, requires_premium) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, session_id, phase_ordinal, phase_name,
             component_name, int(requires_premium)),
        )


def lease_task(conn: sqlite3.Connection, task_id: str, subagent_id: str,
               ttl_seconds: int = 300) -> bool:
    """Atomically lease a pending task. Increments parallel_agents_running on success."""
    with _immediate_transaction(conn) as c:
        row = c.execute(
            "SELECT s.parallel_agents_running, t.requires_premium, "
            "t.phase_ordinal, t.session_id "
            "FROM sessions s JOIN tasks t ON t.session_id = s.id WHERE t.id = ?",
            (task_id,)
        ).fetchone()
        if row and row["parallel_agents_running"] >= MAX_PARALLEL_AGENTS:
            raise RuntimeError(
                f"parallel_agents_running limit ({MAX_PARALLEL_AGENTS}) exceeded"
            )
        if row and row["requires_premium"]:
            phase_row = c.execute(
                "SELECT premium_calls_used FROM phase_metrics "
                "WHERE session_id = ? AND phase_ordinal = ?",
                (row["session_id"], row["phase_ordinal"])
            ).fetchone()
            phase_premium = phase_row["premium_calls_used"] if phase_row else 0
            if phase_premium >= MAX_PREMIUM_CALLS_PER_PHASE:
                raise RuntimeError(
                    f"premium_calls_used per phase limit ({MAX_PREMIUM_CALLS_PER_PHASE}) exceeded"
                )
        result = c.execute(
            "UPDATE tasks SET status='leased', assigned_subagent_id=?, "
            "lease_expires_at=datetime('now', ?), leased_at=CURRENT_TIMESTAMP, "
            "version=version+1, updated_at=CURRENT_TIMESTAMP "
            "WHERE id=? AND status='pending'",
            (subagent_id, f"+{ttl_seconds} seconds", task_id),
        )
        if result.rowcount == 1:
            c.execute(
                "UPDATE sessions SET parallel_agents_running = parallel_agents_running + 1, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = (SELECT session_id FROM tasks WHERE id = ?)",
                (task_id,)
            )
            return True
        return False


def commit_task_complete(conn: sqlite3.Connection, task_id: str, subagent_id: str,
                         version: int, payload_hash: str) -> bool:
    """CAS completion. Decrements parallel_agents_running on success."""
    completed = False
    with _immediate_transaction(conn) as c:
        result = c.execute(
            "UPDATE tasks "
            "SET status='complete', payload_hash=?, version=version+1, "
            "completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP "
            "WHERE id=? AND status='leased' AND assigned_subagent_id=? AND version=?",
            (payload_hash, task_id, subagent_id, version),
        )
        if result.rowcount == 1:
            c.execute(
                "UPDATE sessions SET "
                "parallel_agents_running = MAX(parallel_agents_running - 1, 0), "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = (SELECT session_id FROM tasks WHERE id = ?)",
                (task_id,)
            )
            completed = True
    # checkpoint AFTER the transaction closes — not inside it
    if completed:
        checkpoint_wal(conn)
    return completed


def record_premium_call(conn: sqlite3.Connection, session_id: str,
                        phase_ordinal: int | None = None) -> None:
    """Increment premium call counter. Per-phase when phase_ordinal provided."""
    with _immediate_transaction(conn) as c:
        if phase_ordinal is not None:
            c.execute(
                "INSERT INTO phase_metrics (session_id, phase_ordinal, premium_calls_used) "
                "VALUES (?, ?, 1) "
                "ON CONFLICT(session_id, phase_ordinal) DO UPDATE SET "
                "premium_calls_used = premium_calls_used + 1",
                (session_id, phase_ordinal),
            )
        else:
            c.execute(
                "UPDATE sessions SET premium_calls_used = premium_calls_used + 1, "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )


def checkpoint_wal(conn: sqlite3.Connection) -> None:
    """Flush WAL pages to main DB. Call outside any active transaction."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def verify_review_current(conn: sqlite3.Connection, artifact_id: str) -> bool:
    """Returns True if the artifact's sanitized_sha256 matches the most recent review's hash."""
    row = conn.execute("""
        SELECT a.sanitized_sha256, r.artifact_sha256
        FROM artifacts a
        JOIN reviews r ON r.artifact_id = a.id
        WHERE a.id = ?
        ORDER BY r.created_at DESC LIMIT 1
    """, (artifact_id,)).fetchone()
    if not row:
        return False
    return row[0] == row[1]


def reclaim_expired_leases(conn: sqlite3.Connection, max_retries: int = 3) -> int:
    """Move expired leases back to pending, or to failed if retry limit exceeded.

    Also decrements parallel_agents_running for the owning session.
    Returns total number of tasks transitioned.
    """
    with _immediate_transaction(conn) as c:
        expired = c.execute(
            "SELECT id, session_id, retry_count FROM tasks "
            "WHERE status='leased' AND lease_expires_at < datetime('now')"
        ).fetchall()
        count = 0
        for row in expired:
            task_id, session_id, retries = row["id"], row["session_id"], row["retry_count"]
            if retries < max_retries:
                c.execute("""
                    UPDATE tasks SET status='pending', assigned_subagent_id=NULL,
                        lease_expires_at=NULL, leased_at=NULL,
                        retry_count=retry_count+1, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (task_id,))
            else:
                c.execute("""
                    UPDATE tasks SET status='failed',
                        last_error='Max retries exceeded after lease expiry',
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (task_id,))
            c.execute(
                "UPDATE sessions SET "
                "parallel_agents_running = MAX(parallel_agents_running - 1, 0), "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
            count += 1
    return count


def project_dashboard(conn: sqlite3.Connection, session_id: str) -> str:
    """Render a read-only markdown dashboard from SQLite state."""
    sess = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not sess:
        return f"# Session Not Found\n\nNo session with id `{session_id}`.\n"
    status_icon = {"pending": "[ ]", "leased": "[~]", "complete": "[x]", "failed": "[!]"}
    lines = [
        f"# Exploration Session: {sess['session_name']}",
        f"",
        f"**Status:** {sess['status']}  ",
        f"**Premium calls used:** {sess['premium_calls_used']}  ",
        f"**Parallel agents:** {sess['parallel_agents_running']}  ",
        f"",
    ]
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE session_id=? ORDER BY phase_ordinal, id",
        (session_id,)
    ).fetchall()
    current_phase = None
    for task in tasks:
        if task["phase_name"] != current_phase:
            current_phase = task["phase_name"]
            lines.append(f"## Phase {task['phase_ordinal']}: {current_phase}")
        icon = status_icon.get(task["status"], "[ ]")
        lines.append(f"- {icon} {task['component_name']}")
    lines.append("")
    lines.append(
        f"*Generated from SQLite at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}*"
    )
    return "\n".join(lines) + "\n"


def validate_dashboard_checkboxes(dashboard_md: str, conn: sqlite3.Connection,
                                   session_id: str) -> bool:
    """Regex-based validator: True if checkboxes match DB task status.

    Intended for dashboards generated by project_dashboard (SQLite-backed).
    Pre-migration markdown files with [↩] lines are not supported.
    """
    checkbox_pattern = re.compile(r"- \[( |x|~|!)\] (.+)")
    db_tasks = conn.execute(
        "SELECT component_name, status FROM tasks WHERE session_id=? ORDER BY phase_ordinal, id",
        (session_id,)
    ).fetchall()
    md_checks = checkbox_pattern.findall(dashboard_md)
    icon_to_status = {" ": "pending", "x": "complete", "~": "leased", "!": "failed"}
    if len(md_checks) != len(db_tasks):
        return False
    for (icon, name), db_task in zip(md_checks, db_tasks):
        if icon_to_status.get(icon, "pending") != db_task["status"]:
            return False
        if name.strip() != db_task["component_name"]:
            return False
    return True


def migrate_dashboard(dashboard_path: Path, conn: sqlite3.Connection) -> bool:
    """Parse exploration-dashboard.md into SQLite, rename file to .migrated.

    Checkbox states: [ ]=pending  [x]=complete  [!]=failed  [~]/[↩]=skip (not migrated).
    """
    content = dashboard_path.read_text(encoding="utf-8")
    m = re.search(r"# Exploration Session:\s*(.+)", content)
    session_name = m.group(1).strip() if m else dashboard_path.stem
    session_id = str(uuid.uuid4())
    create_session(conn, session_id, session_name)

    phase_ordinal = 0
    phase_name = "Uncategorized"
    phase_pat = re.compile(r"## Phase\s+(\d+):\s*(.+)")
    # Expanded regex covers [ ] [x] [~] [↩] [!] — EXEC-3 fix
    task_pat = re.compile(r"- \[( |x|~|↩|!)\] (.+)")

    for line in content.splitlines():
        ph = phase_pat.match(line)
        if ph:
            phase_ordinal, phase_name = int(ph.group(1)), ph.group(2).strip()
            continue
        tm = task_pat.match(line)
        if tm:
            checked, component = tm.group(1), tm.group(2).strip()
            if checked in ("~", "↩"):
                continue  # Skip skipped/revised phases — no valid tasks table status
            task_id = str(uuid.uuid4())
            add_task(conn, task_id, session_id, phase_ordinal, phase_name, component)
            if checked in ("x", "!"):
                new_status = "complete" if checked == "x" else "failed"
                with _immediate_transaction(conn) as c:
                    c.execute(
                        "UPDATE tasks SET status=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                        (new_status, task_id),
                    )

    dashboard_path.rename(dashboard_path.with_suffix(".md.migrated"))
    return True


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
        conn = init_db(args.db_path)
        ok = lease_task(conn, args.task_id, args.subagent_id, args.ttl)
        print(json.dumps({"ok": ok}))
    elif args.command == "commit-complete":
        conn = init_db(args.db_path)
        ok = commit_task_complete(conn, args.task_id, args.subagent_id,
                                  args.version, args.payload_hash)
        print(json.dumps({"ok": ok}))
    elif args.command == "project-dashboard":
        conn = init_db(args.db_path)
        print(project_dashboard(conn, args.session_id))
    elif args.command == "reclaim-expired":
        conn = init_db(args.db_path)
        count = reclaim_expired_leases(conn)
        print(json.dumps({"reclaimed": count}))
