#!/usr/bin/env python3
"""
control_plane/signed_decisions.py — Cryptographically Signed Human Decisions (S3, Q1, sec-2-6, arch-2-5)
=========================================================================================================

Purpose:
    Review presets (plan-review preset, code-review preset) and review skips decide which
    evidence counts, so they are high-risk decisions signed with the human's SSH key (same
    SSHSIG mechanism and trust anchor as Gates 1/3/DONE) and stored in the dedicated v15
    `signed_decisions` table.

    Challenge format includes:
      - challenge_version (`control-plane-decision/1`)
      - task, request, edge (from -> to), occupancy, question_id, decision_text, nonce, expires
    Verified against `allowed_signers` and bound to the current task occupancy.
    `decided_at` is always stamped by the control-plane UTC clock (ISO-8601 with microseconds)
    so `plan_audit.py check --not-before` reads it directly from SQLite (never passed by an agent).
"""

from __future__ import annotations

import secrets
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from control_plane.ssh_signing import SigningError, verify_signature


DECISION_CHALLENGE_VERSION = "control-plane-decision/1"


class SignedDecisionError(Exception):
    """Raised when a signed decision fails verification, binding, or persistence."""


@dataclass(frozen=True)
class SignedDecisionRecord:
    decision_id: int
    task_id: str
    occupancy_id: int
    from_state: str
    to_state: str
    question_id: str
    decision_text: str
    request_id: Optional[int]
    nonce: str
    principal: str
    fingerprint: str
    decided_at: str


def build_decision_challenge(
    *,
    task_id: str,
    request_id: int,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    question_id: str,
    decision_text: str,
    nonce: str,
    expiration: float,
) -> bytes:
    """Deterministic UTF-8 challenge bytes for a signed human decision (sec-2-6, arch-2-5)."""
    lines = [
        DECISION_CHALLENGE_VERSION,
        "kind: decision",
        f"task: {task_id}",
        f"request: {request_id}",
        f"transition: {from_state} -> {to_state}",
        f"occupancy: {occupancy_id}",
        f"question: {question_id}",
        f"decision: {decision_text}",
        f"nonce: {nonce}",
        f"expires: {int(expiration)}",
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def record_signed_decision(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    question_id: str,
    decision_text: str,
    request_id: int,
    nonce: str,
    expiration: float,
    signature: bytes,
    allowed_signers: Path,
    principal: Optional[str] = None,
    require_uv: bool = False,
    binary: str = "ssh-keygen",
) -> SignedDecisionRecord:
    """Verify the SSHSIG signature over the reconstructed decision challenge and persist it
    to `signed_decisions` with the control-plane DB clock timestamp."""
    if not decision_text or not decision_text.strip():
        raise SignedDecisionError("decision_text must be non-empty.")
    if time.time() >= expiration:
        raise SignedDecisionError("Signed decision challenge has expired.")

    # Verify occupancy is current for this task
    row = conn.execute(
        "SELECT MAX(transition_id) FROM task_transitions WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    live_occupancy = row[0] if row else None
    if live_occupancy != occupancy_id:
        raise SignedDecisionError(
            f"Stale occupancy for signed decision: expected {live_occupancy}, got {occupancy_id}."
        )

    challenge = build_decision_challenge(
        task_id=task_id,
        request_id=request_id,
        from_state=from_state,
        to_state=to_state,
        occupancy_id=occupancy_id,
        question_id=question_id,
        decision_text=decision_text.strip(),
        nonce=nonce,
        expiration=expiration,
    )

    try:
        verified = verify_signature(
            challenge,
            signature,
            allowed_signers=allowed_signers,
            principal=principal,
            require_uv=require_uv,
            binary=binary,
        )
    except SigningError as exc:
        raise SignedDecisionError(f"Decision signature verification failed: {exc}") from exc

    decided_at = _utc_now_iso()
    cur = conn.execute(
        """
        INSERT INTO signed_decisions (
            task_id, occupancy_id, from_state, to_state, question_id,
            decision_text, request_id, nonce, challenge, signature,
            principal, fingerprint, decided_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id, occupancy_id, from_state, to_state, question_id,
            decision_text.strip(), request_id, nonce, challenge, signature,
            verified.principal, verified.fingerprint, decided_at,
        ),
    )
    conn.commit()
    return SignedDecisionRecord(
        decision_id=cur.lastrowid,
        task_id=task_id,
        occupancy_id=occupancy_id,
        from_state=from_state,
        to_state=to_state,
        question_id=question_id,
        decision_text=decision_text.strip(),
        request_id=request_id,
        nonce=nonce,
        principal=verified.principal,
        fingerprint=verified.fingerprint,
        decided_at=decided_at,
    )


def get_latest_signed_decision(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    occupancy_id: int,
    question_id: str,
) -> Optional[Dict[str, Any]]:
    """Return the latest verified signed decision for (task_id, occupancy_id, question_id), or None."""
    row = conn.execute(
        """
        SELECT decision_id, task_id, occupancy_id, from_state, to_state, question_id,
               decision_text, request_id, nonce, principal, fingerprint, decided_at
        FROM signed_decisions
        WHERE task_id = ? AND occupancy_id = ? AND question_id = ?
        ORDER BY decision_id DESC LIMIT 1
        """,
        (task_id, occupancy_id, question_id),
    ).fetchone()
    if row is None:
        return None
    keys = (
        "decision_id", "task_id", "occupancy_id", "from_state", "to_state", "question_id",
        "decision_text", "request_id", "nonce", "principal", "fingerprint", "decided_at",
    )
    return dict(zip(keys, tuple(row)))


def new_decision_nonce() -> str:
    return secrets.token_hex(16)
