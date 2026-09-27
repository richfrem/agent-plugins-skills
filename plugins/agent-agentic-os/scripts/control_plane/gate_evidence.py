"""
control_plane/gate_evidence.py
==============================

Purpose:
    Authenticate a real-work task's DONE before git lets its branch leave the machine. The push
    guard must not trust stored task state alone: a completed simulation database copied or
    symlinked into <repo>/context/control_plane.db looks DONE. This re-verifies, with ssh-keygen,
    every signed gate the task committed, against the repository's own human trust anchor:
      - <repo>/context/control_plane.db is a regular file (not a symlink), with one hard link,
        classified as real work, and stamped 'real' inside the database;
      - the task is DONE and has stored evidence for its signed gates, including the gate into DONE;
      - each stored challenge names this task and that transition, its signature verifies against
        <repo>/context/identity/allowed_signers, and the signing key is a human key (never a key
        registered in <repo>/context/simulation/identity, whatever the production file calls it);
      - every signed gate used the same key (one approver per pipeline).
    Cross-platform (macOS, Linux, Windows): Python stdlib plus ssh-keygen (OpenSSH 8.1+).

Key Input Dependencies:
    - <repo>/context/control_plane.db (tasks, signed_gate_evidence, control_plane_identity)
    - <repo>/context/identity/allowed_signers (the human trust anchor)
    - control_plane.approver_policy (classification, key roles), control_plane.ssh_signing (verification)

Key Functions:
    - verify_branch_done() -- list every reason a branch's task may not be pushed (empty list: allowed)
    - _database_file_problems(), _load_task_evidence(), _check_evidence_row() -- its three steps

Usage:
    python3 plugins/agent-agentic-os/scripts/verify_gate_evidence.py --repo-root <repo> --branch <branch>
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from control_plane.approver_policy import (
    CONTEXT_REAL,
    ApproverPolicyError,
    classify_path,
    database_identity,
    key_role,
    registered_simulation_keys,
)


def _task_for_branch(conn: sqlite3.Connection, branch: str) -> Optional[tuple]:
    """Return (task_id, state) of the latest task registered for a branch, or None."""
    return conn.execute(
        "SELECT task_id, state FROM tasks WHERE worktree_branch = ? ORDER BY created_at DESC LIMIT 1", (branch,)
    ).fetchone()


def _challenge_names(challenge: bytes, task_id: str, from_state: str, to_state: str) -> bool:
    """Return True if a signed challenge names exactly this task and transition."""
    lines = challenge.decode("utf-8", "replace").splitlines()
    return f"task: {task_id}" in lines and f"transition: {from_state} -> {to_state}" in lines


# The production database file itself must be trustworthy before anything in it is read
def _database_file_problems(db: Path, anchor: Path) -> List[str]:
    """Return problems with the production database file and trust anchor (empty when sound)."""
    if db.is_symlink():
        return [f"{db} is a symlink; the production control plane must be a regular file."]
    if not db.is_file():
        return [f"{db} does not exist."]
    if db.stat().st_nlink != 1:
        return [f"{db} has {db.stat().st_nlink} hard links; the production control plane must have exactly one."]
    if classify_path(db) != CONTEXT_REAL:
        return [f"{db} is not classified as a real-work database."]
    if not anchor.is_file():
        return [f"The human trust anchor {anchor} is missing."]
    return []


# Read the branch's task and its stored signed-gate evidence (read-only)
def _evidence_history_problems(conn: sqlite3.Connection, task_id: str, evidence: list) -> List[str]:
    """Match every proof-bearing history edge to one consumed, content-bound request."""
    from control_plane.registry import TransitionRegistry
    from control_plane.ssh_signing import ChallengeError, derive_challenge_from_row

    registry = TransitionRegistry.load_default()
    problems = []
    expected_requests = set()
    by_request = {row[0]: row for row in evidence}
    history = conn.execute(
        "SELECT transition_id, from_state, to_state FROM task_transitions "
        "WHERE task_id = ? ORDER BY transition_id", (task_id,),
    ).fetchall()
    occupancy = None
    for transition_id, from_state, to_state in history:
        template = registry.get_template(from_state, to_state)
        if template and template.requires_cryptographic_proof:
            requests = conn.execute(
                "SELECT request_id, jti FROM transition_request WHERE task_id = ? "
                "AND from_state = ? AND to_state = ? AND occupancy_id = ? AND status = 'CONSUMED'",
                (task_id, from_state, to_state, occupancy),
            ).fetchall()
            if len(requests) != 1:
                problems.append(f"Transition {transition_id} lacks exactly one consumed signed evidence request.")
            else:
                request_id, jti = requests[0]
                expected_requests.add(request_id)
                row = by_request.get(request_id)
                if row is None:
                    problems.append(f"Transition {transition_id} ({from_state} -> {to_state}) lacks signed gate evidence.")
                elif row[1:3] != (from_state, to_state) or jti != f"sshsig:{row[5]}":
                    problems.append(f"Evidence {request_id} disagrees with its committed transition request.")
                else:
                    try:
                        expected = derive_challenge_from_row(conn, request_id)
                        if bytes(row[3]) != expected:
                            problems.append(f"Evidence {request_id} challenge disagrees with its original request.")
                    except ChallengeError as exc:
                        problems.append(f"Evidence {request_id}: {exc}")
        occupancy = transition_id
    if set(by_request) != expected_requests:
        problems.append(f"Task {task_id} has signed evidence unrelated to its proof-bearing transition history.")
    return problems


def _load_task_evidence(db: Path, branch: str) -> Tuple[List[str], Optional[str], list]:
    """Return (problems, task_id, evidence rows) for the task registered on `branch`."""
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        identity = database_identity(conn)
        if identity != CONTEXT_REAL:
            return [f"{db} is stamped '{identity}', not 'real': a simulation or unidentified database cannot unlock a push."], None, []
        row = _task_for_branch(conn, branch)
        if row is None:
            return [f"No task is registered for branch {branch}."], None, []
        task_id, state = row
        if state != "DONE":
            return [f"Task {task_id} is in state {state}, not DONE."], task_id, []
        has_table = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'signed_gate_evidence'").fetchone()
        evidence = conn.execute(
            "SELECT request_id, from_state, to_state, challenge, signature, fingerprint FROM signed_gate_evidence "
            "WHERE task_id = ? ORDER BY request_id", (task_id,),
        ).fetchall() if has_table else []
        return _evidence_history_problems(conn, task_id, evidence), task_id, evidence
    finally:
        conn.close()


# Re-verify one stored gate against the human trust anchor; return (problem or None, verified key)
def _check_evidence_row(row: tuple, task_id: str, anchor: Path, simulation_keys: set) -> Tuple[Optional[str], Optional[str]]:
    """Return (problem, fingerprint) for one evidence row; problem is None when it is a valid human signature."""
    from control_plane.ssh_signing import SigningError, verify_signature

    request_id, from_state, to_state, challenge, signature, fingerprint = row
    challenge, signature = bytes(challenge), bytes(signature)
    if not _challenge_names(challenge, task_id, from_state, to_state):
        return f"Evidence {request_id} does not name task {task_id} and {from_state} -> {to_state}.", None
    try:
        verified = verify_signature(challenge, signature, allowed_signers=anchor)
    except SigningError as exc:
        return f"Evidence {request_id} ({from_state} -> {to_state}) does not verify against {anchor}: {exc}", None
    if verified.fingerprint != fingerprint:
        return f"Evidence {request_id} was signed by {verified.fingerprint}, not the recorded {fingerprint}.", None
    try:
        role = key_role(verified.fingerprint, anchor)
    except ApproverPolicyError as exc:
        return f"Evidence {request_id}: {exc}", None
    if role != "human" or verified.fingerprint in simulation_keys:
        return f"Evidence {request_id} ({from_state} -> {to_state}) was signed by the agent's simulation key, not a human.", verified.fingerprint
    return None, verified.fingerprint


# Every reason this branch's task may not be pushed; an empty list means allowed
def verify_branch_done(repo_root: Path, branch: str) -> List[str]:
    """Return the problems that block pushing `branch`; [] when its task's DONE is authenticated."""
    repo_root = Path(repo_root)
    db = repo_root / "context" / "control_plane.db"
    anchor = repo_root / "context" / "identity" / "allowed_signers"
    problems = _database_file_problems(db, anchor)
    if problems:
        return problems
    problems, task_id, evidence = _load_task_evidence(db, branch)
    if problems:
        return problems
    if not evidence:
        return [f"Task {task_id} has no signed gate evidence; its DONE cannot be authenticated against the human trust anchor."]
    if not any(row[2] == "DONE" for row in evidence):
        return [f"Task {task_id} has no signed evidence for its transition into DONE."]
    simulation_keys = registered_simulation_keys(db)
    keys = set()
    for row in evidence:
        problem, key = _check_evidence_row(row, task_id, anchor, simulation_keys)
        if problem:
            problems.append(problem)
        if key:
            keys.add(key)
    if len(keys) > 1:
        problems.append(f"Task {task_id}'s gates were signed by {len(keys)} different keys; one approver per pipeline is required.")
    return problems
