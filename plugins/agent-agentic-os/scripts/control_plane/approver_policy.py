"""
control_plane/approver_policy.py
================================

Purpose:
    One approver per pipeline, with real work and simulations in SEPARATE databases.

    Two signing identities coexist in allowed_signers: the human operator's key(s) and the
    agent's simulation key (any key enrolled under AGENT_SIMULATION_PRINCIPAL). Which one may
    approve is decided by the DATABASE, never by a row inside it:
      - real work   : every control-plane database EXCEPT one named SIMULATION_DB_NAME. This is
                      the repository's <repo>/context/control_plane.db that work-intake and the
                      push/merge gates use. Only human keys approve; the agent key is refused on
                      every gate.
      - simulation  : a database file named SIMULATION_DB_NAME (for example
                      <repo>/context/simulation/simulation_control_plane.db, or a temp file).
                      Only the agent key approves; human keys are refused. Nothing in it can
                      satisfy a real-work gate, because real gates never read it.
    Unknown or unexpected database names are treated as real work (fail safe: human only).

    Roles are decided by KEY FINGERPRINT, never by the principal a signature reports: any key
    enrolled under AGENT_SIMULATION_PRINCIPAL is the agent's, whatever aliases it also has; a
    key enrolled as both fails closed, and wildcard/negated principal patterns fail closed.

    Within either database every signed gate of a task must use the same key. The first signed
    gate records it in task_approver_binding. For tasks signed before this policy existed, the
    first approver is recovered from the task's consumed transition_request history.

    In the repository's own <repo>/context/control_plane.db, proofs must also be verified
    against <repo>/context/identity/allowed_signers; any other trust file is refused.

Key Input Dependencies:
    - task_approver_binding table (created here with CREATE TABLE IF NOT EXISTS; additive, no
      schema-version bump or rebuild)
    - transition_request.jti ('sshsig:<fingerprint>' on consumed requests) for rollout
    - the database path and the proof's allowed_signers

Key Functions:
    - classify_path() -- 'real', 'simulation' or 'ambiguous' (always refused) for a database path (alias: pipeline_context)
    - database_identity() / stamp_database_identity() -- the context recorded inside the database itself
    - record_gate_evidence() -- store a committed gate's challenge and signature for the push guard
    - registered_simulation_keys() -- simulation keys a repository registered; refused on real work even if relabelled
    - is_repository_db() -- whether a path is spelled <repo>/context/control_plane.db (a symlink there is refused)
    - canonical_anchor() -- the allowed_signers a repository database's proofs must use
    - key_fingerprint() -- OpenSSH SHA256 fingerprint of a base64 public key blob
    - enrolled_keys() -- (principals, fingerprint) per enrolled key; refuses principal patterns
    - key_role() -- 'agent' or 'human' for an enrolled key fingerprint (fails closed on ambiguity)
    - ensure_binding_table() / get_binding() -- the per-task approver binding
    - historical_approver() -- first approver key from consumed signed-gate history (rollout)
    - enforce_pipeline_approver() -- the gate check run inside the commit transaction, built from
      _checked_context(), _check_role(), _check_existing_binding() and _bind_first_approver()

Usage:
    Called by SqlitePersistenceAdapter._apply_transition_with_receipts after a gate signature verifies.
    Simulations: PipelineSimulator(<dir>/simulation_control_plane.db).
"""

import base64
import hashlib
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from control_plane.ports import PersistenceInvariantViolation

AGENT_SIMULATION_PRINCIPAL = "test-human@local"
SIMULATION_DB_NAME = "simulation_control_plane.db"
REPOSITORY_DB_NAME = "control_plane.db"
CONTEXT_REAL = "real"
CONTEXT_SIMULATION = "simulation"
CONTEXT_AMBIGUOUS = "ambiguous"
_KEY_TYPE_PREFIXES = ("ssh-", "ecdsa-", "sk-")
_PATTERN_CHARS = ("*", "?")

BINDING_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task_approver_binding (
    task_id TEXT PRIMARY KEY,
    task_created_at TEXT NOT NULL,
    context TEXT NOT NULL CHECK (context IN ('real', 'simulation')),
    approver_fingerprint TEXT NOT NULL,
    approver_principal TEXT,
    source TEXT NOT NULL CHECK (source IN ('first_gate', 'history')),
    bound_at REAL NOT NULL
)
"""


IDENTITY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS control_plane_identity (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    context TEXT NOT NULL CHECK (context IN ('real', 'simulation')),
    db_uuid TEXT NOT NULL,
    stamped_at REAL NOT NULL
)
"""

EVIDENCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS signed_gate_evidence (
    request_id INTEGER PRIMARY KEY,
    task_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    challenge BLOB NOT NULL,
    signature BLOB NOT NULL,
    fingerprint TEXT NOT NULL,
    principal TEXT,
    context TEXT NOT NULL,
    recorded_at REAL NOT NULL
)
"""


class ApproverPolicyError(PersistenceInvariantViolation):
    """Every refusal from the one-approver-per-pipeline policy."""


@dataclass(frozen=True)
class EnrolledKey:
    principals: Tuple[str, ...]
    fingerprint: str


# Real work vs simulation is a property of the database file, never of a row inside it
def classify_path(db_path: Any) -> str:
    """Return 'simulation', 'real' or 'ambiguous' for a database path.

    'simulation' only when the name it is opened as and the name it resolves to are both exactly
    SIMULATION_DB_NAME and the file has a single hard link. Any other spelling that looks like a
    simulation database (a case variant, a symlink or hard link reaching another file, or a
    simulation file with extra hard links) is 'ambiguous' and is refused for every key, so it can
    never be reassigned to the other role. Every other name is 'real' (fail safe: human only)."""
    given = Path(db_path)
    resolved = given.resolve()
    folded = SIMULATION_DB_NAME.casefold()
    if given.name.casefold() != folded and resolved.name.casefold() != folded:
        return CONTEXT_REAL
    if given.name == SIMULATION_DB_NAME and resolved.name == SIMULATION_DB_NAME:
        if not resolved.exists() or resolved.stat().st_nlink == 1:
            return CONTEXT_SIMULATION
    return CONTEXT_AMBIGUOUS


pipeline_context = classify_path


# The repository's own work database, judged by the path it is opened as
def is_repository_db(db_path: Any) -> bool:
    """Return True for a path spelled <repo>/context/control_plane.db (not following symlinks)."""
    given = Path(db_path)
    return given.name == REPOSITORY_DB_NAME and given.parent.name == "context"


# The only trust file a repository database's proofs may use
def canonical_anchor(db_path: Any) -> Path:
    """Return <repo>/context/identity/allowed_signers for <repo>/context/control_plane.db."""
    return Path(db_path).parent.resolve() / "identity" / "allowed_signers"


# Keys the repository registered as simulation keys (<repo>/context/simulation/identity/allowed_signers)
def registered_simulation_keys(db_path: Any) -> set:
    """Return simulation-key fingerprints registered for the repository owning a repository database."""
    if not is_repository_db(db_path):
        return set()
    anchor = Path(db_path).parent.resolve() / "simulation" / "identity" / "allowed_signers"
    return {k.fingerprint for k in enrolled_keys(anchor)} if anchor.exists() else set()


# The context a database was created for, recorded inside the database itself
def database_identity(conn: sqlite3.Connection) -> Optional[str]:
    """Return the context stamped in this database ('real' or 'simulation'), or None if unstamped."""
    exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'control_plane_identity'").fetchone()
    if not exists:
        return None
    row = conn.execute("SELECT context FROM control_plane_identity WHERE singleton = 1").fetchone()
    return row[0] if row else None


# Stamp a database's context the first time it is used; never restamps
def stamp_database_identity(conn: sqlite3.Connection, db_path: Any) -> Optional[str]:
    """Record the database's context from its path if not yet stamped; return the stamped context.
    An ambiguous path is never stamped."""
    current = database_identity(conn)
    if current is not None:
        return current
    context = classify_path(db_path)
    if context == CONTEXT_AMBIGUOUS:
        return None
    conn.execute(IDENTITY_TABLE_SQL)
    conn.execute(
        "INSERT OR IGNORE INTO control_plane_identity (singleton, context, db_uuid, stamped_at) VALUES (1, ?, ?, ?)",
        (context, secrets.token_hex(16), time.time()),
    )
    return database_identity(conn)


# Signed gate evidence, re-verified by the push guard against the human trust anchor
def record_gate_evidence(
    conn: sqlite3.Connection, request_id: int, task_id: str, from_state: str, to_state: str,
    challenge: bytes, signature: bytes, fingerprint: str, principal: str, context: str,
) -> None:
    """Store the exact challenge and signature of a committed signed gate."""
    conn.execute(EVIDENCE_TABLE_SQL)
    conn.execute(
        "INSERT OR REPLACE INTO signed_gate_evidence (request_id, task_id, from_state, to_state, challenge, signature, "
        "fingerprint, principal, context, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (request_id, task_id, from_state, to_state, challenge, signature, fingerprint, principal, context, time.time()),
    )


# OpenSSH SHA256 fingerprint, computed without a subprocess
def key_fingerprint(key_b64: str) -> str:
    """Return 'SHA256:<base64>' for a base64 public key blob, as ssh-keygen prints it."""
    digest = hashlib.sha256(base64.b64decode(key_b64)).digest()
    return "SHA256:" + base64.b64encode(digest).decode("ascii").rstrip("=")


def _split_line(line: str) -> List[str]:
    """Split an allowed_signers line on whitespace outside double quotes."""
    tokens, current, quoted = [], [], False
    for char in line:
        if char == '"':
            quoted = not quoted
            current.append(char)
        elif char.isspace() and not quoted:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        tokens.append("".join(current))
    return tokens


# Parse allowed_signers into (principals, fingerprint) per enrolled key
def enrolled_keys(allowed_signers: Any) -> List[EnrolledKey]:
    """Return every key enrolled in an allowed_signers file with its principal list.

    Refuses principal patterns (wildcards or negations): with them, which keys can verify as
    the agent principal can no longer be decided from the literal list."""
    keys = []
    for raw in Path(allowed_signers).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        tokens = _split_line(line)
        principals = tuple(p for p in tokens[0].split(",") if p)
        if any(p.startswith("!") or any(c in p for c in _PATTERN_CHARS) for p in principals):
            raise ApproverPolicyError(
                f"{allowed_signers} uses a principal pattern ({tokens[0]}); enroll each key under literal principals only."
            )
        for i, token in enumerate(tokens[1:], start=1):
            if token.startswith(_KEY_TYPE_PREFIXES) and i + 1 < len(tokens):
                keys.append(EnrolledKey(principals, key_fingerprint(tokens[i + 1])))
                break
    return keys


# Role of a key: any enrollment under the agent principal makes it the agent's key
def key_role(fingerprint: str, allowed_signers: Any) -> str:
    """Return 'agent' or 'human' for an enrolled key; refuse unknown or ambiguous enrollments."""
    entries = [k for k in enrolled_keys(allowed_signers) if k.fingerprint == fingerprint]
    if not entries:
        raise ApproverPolicyError(f"Key {fingerprint} is not enrolled in {allowed_signers}.")
    agent = [k for k in entries if AGENT_SIMULATION_PRINCIPAL in k.principals]
    if agent and len(agent) != len(entries):
        raise ApproverPolicyError(
            f"Key {fingerprint} is enrolled both as the agent's simulation identity and as a human in "
            f"{allowed_signers}. Enroll the agent key only under {AGENT_SIMULATION_PRINCIPAL} and the human key only under the human's principal."
        )
    return "agent" if agent else "human"


# Create the binding table on demand; additive, so no schema rebuild of existing databases
def ensure_binding_table(conn: sqlite3.Connection) -> None:
    """Create task_approver_binding if it does not exist."""
    conn.execute(BINDING_TABLE_SQL)


# The task's binding row, if any (read-only: never creates the table)
def get_binding(conn: sqlite3.Connection, task_id: str) -> Optional[Dict[str, Any]]:
    """Return the task's binding as a dict, or None if the task is not bound yet."""
    exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'task_approver_binding'").fetchone()
    if not exists:
        return None
    cur = conn.execute("SELECT * FROM task_approver_binding WHERE task_id = ?", (task_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return dict(zip([c[0] for c in cur.description], row))


# Rollout: the first approver key of a task signed before this policy existed
def historical_approver(conn: sqlite3.Connection, task_id: str, exclude_request_id: Optional[int] = None) -> Optional[str]:
    """Return the fingerprint of the task's earliest consumed signed gate (other than the one
    being committed now), or None."""
    row = conn.execute(
        "SELECT jti FROM transition_request WHERE task_id = ? AND status = 'CONSUMED' AND jti LIKE 'sshsig:%' "
        "AND request_id != ? ORDER BY request_id ASC LIMIT 1",
        (task_id, -1 if exclude_request_id is None else exclude_request_id),
    ).fetchone()
    return row[0][len("sshsig:"):] if row else None


def _task_created_at(conn: sqlite3.Connection, task_id: str) -> str:
    """Return the task's created_at as text, or raise if the task does not exist."""
    row = conn.execute("SELECT created_at FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if row is None:
        raise ApproverPolicyError(f"Unknown task {task_id}.")
    return str(row[0])


# Which database is being committed: its path, its trust file, and the stamp inside it must agree
def _checked_context(conn: sqlite3.Connection, db_path: Any, allowed_signers: Any) -> str:
    """Return the database's context ('real' or 'simulation') or raise if it cannot be trusted."""
    context = classify_path(db_path)
    if context == CONTEXT_AMBIGUOUS:
        raise ApproverPolicyError(
            f"{db_path} is an ambiguous alias of a simulation database (case variant, symlink or extra hard link); "
            "refusing every key. Open simulations only as <dir>/simulation_control_plane.db."
        )
    if is_repository_db(db_path):
        if Path(db_path).is_symlink():
            raise ApproverPolicyError(f"The repository database {db_path} is a symlink; a production control plane must be a regular file.")
        if allowed_signers is None or Path(allowed_signers).resolve() != canonical_anchor(db_path):
            raise ApproverPolicyError(f"Proofs for this repository must be verified against {canonical_anchor(db_path)}.")
    identity = stamp_database_identity(conn, db_path)
    if identity != context:
        raise ApproverPolicyError(
            f"Database identity mismatch: the database being committed is stamped '{identity}' but is opened as a "
            f"'{context}' database ({db_path}); refusing (a copied, swapped or aliased database)."
        )
    return context


# Real work accepts only human keys; a simulation only the agent key
def _check_role(task_id: str, fingerprint: str, allowed_signers: Any, db_path: Any, context: str) -> None:
    """Raise unless the signing key's role matches the database's context."""
    role = key_role(fingerprint, allowed_signers)
    if context == CONTEXT_REAL and fingerprint in registered_simulation_keys(db_path):
        raise ApproverPolicyError(
            f"Key {fingerprint} is a registered simulation key; it cannot approve real work (task {task_id}) even if "
            "the production trust file labels it as a human."
        )
    if context == CONTEXT_REAL and role != "human":
        raise ApproverPolicyError(
            f"The agent's simulation key cannot approve real work (task {task_id}). Real work is approved only by the "
            f"human operator; simulations run in a separate database named {SIMULATION_DB_NAME}."
        )
    if context == CONTEXT_SIMULATION and role != "agent":
        raise ApproverPolicyError(
            f"Task {task_id} is in a simulation database: only the agent's simulation key approves it; a human key cannot."
        )


# An existing binding must belong to this task, agree with signed history, and name this key
def _check_existing_binding(
    conn: sqlite3.Connection, task_id: str, fingerprint: str, context: str, created_at: str,
    binding: Dict[str, Any], request_id: Optional[int],
) -> None:
    """Raise unless the task's recorded approver key is `fingerprint` and the binding is consistent."""
    if binding["task_created_at"] != created_at or binding["context"] != context:
        raise ApproverPolicyError(f"Task {task_id}'s approver binding does not belong to this task; refusing.")
    first = historical_approver(conn, task_id, exclude_request_id=request_id)
    if first is not None and first != binding["approver_fingerprint"]:
        raise ApproverPolicyError(
            f"Task {task_id}'s approver binding ({binding['approver_fingerprint']}) disagrees with its signed-gate "
            f"history ({first}); refusing (edited binding)."
        )
    if binding["approver_fingerprint"] != fingerprint:
        raise ApproverPolicyError(
            f"One approver per pipeline: task {task_id} is approved by key {binding['approver_fingerprint']} "
            f"({binding['approver_principal']}); key {fingerprint} cannot approve it."
        )


# First signed gate (or first since rollout): bind the task to this key
def _bind_first_approver(
    conn: sqlite3.Connection, task_id: str, fingerprint: str, principal: str, context: str,
    created_at: str, request_id: Optional[int],
) -> None:
    """Record the task's approver key, refusing a key other than the one in its signed-gate history."""
    first = historical_approver(conn, task_id, exclude_request_id=request_id)
    if first is not None and first != fingerprint:
        raise ApproverPolicyError(
            f"One approver per pipeline: task {task_id}'s earlier signed gate was approved by key {first}; "
            f"key {fingerprint} cannot approve it."
        )
    ensure_binding_table(conn)
    conn.execute(
        "INSERT INTO task_approver_binding (task_id, task_created_at, context, approver_fingerprint, approver_principal, source, bound_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (task_id, created_at, context, fingerprint, principal, "history" if first is not None else "first_gate", time.time()),
    )


# Inside the commit transaction, after the gate signature verified
def enforce_pipeline_approver(
    conn: sqlite3.Connection,
    task_id: str,
    fingerprint: str,
    principal: str,
    allowed_signers: Any,
    db_path: Any,
    request_id: Optional[int] = None,
) -> None:
    """Raise ApproverPolicyError unless key `fingerprint` may approve this task's gate in this
    database; record the task's approver key on its first signed gate."""
    context = _checked_context(conn, db_path, allowed_signers)
    _check_role(task_id, fingerprint, allowed_signers, db_path, context)
    created_at = _task_created_at(conn, task_id)
    binding = get_binding(conn, task_id)
    if binding is not None:
        _check_existing_binding(conn, task_id, fingerprint, context, created_at, binding, request_id)
        return
    _bind_first_approver(conn, task_id, fingerprint, principal, context, created_at, request_id)
