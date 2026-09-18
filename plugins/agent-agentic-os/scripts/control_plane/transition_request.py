#!/usr/bin/env python3
"""
control_plane/transition_request.py
====================================

Purpose:
    Local, vendor-independent proof-of-concept mechanics for auth-ciba-poc-
    transition-mechanics (issues #621, #626, #634): a transition_request
    record plus a self-signed stub token standing in for a real IdP's signed
    proof (e.g. a real CIBA+RAR token), so the Policy-side verification logic
    can be built and adversarially tested before any real IdP integration
    (Increment B, out of scope here). No external IdP call happens anywhere
    in this module.

Key Input Dependencies:
    - agent_control.ControlPlane (task_id existence, db_path)
    - Python stdlib only (hmac, hashlib, secrets, json, base64) -- no new
      third-party dependency for this stub signer, per this repo's
      dependency-management rules.

Key Functions:
    - create_transition_request() -- Policy-side creation; the agent proposes,
      Policy generates the nonce/revision_hash and persists PENDING (spec
      guardrail: no agent DB writes for transition_request creation).
    - issue_stub_token() -- stand-in for a real IdP's signed-proof issuance.
    - verify_and_consume() -- independent Policy-side verification: signature,
      expiration, payload-match against the stored request (not the token's
      own claims), single-use (jti + nonce), atomic consume-and-commit.

Exceptions:
    - TransitionRequestError (base)
    - TokenExpired, TokenReplayed, PayloadMismatch, RequestNotFound
"""

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from typing import Any, Dict, Optional


class TransitionRequestError(Exception):
    """Base exception for this module's verification failures."""


class TokenExpired(TransitionRequestError):
    pass


class TokenReplayed(TransitionRequestError):
    pass


class PayloadMismatch(TransitionRequestError):
    pass


class RequestNotFound(TransitionRequestError):
    pass


@dataclass(frozen=True)
class TransitionRequestRecord:
    request_id: int
    task_id: str
    from_state: str
    to_state: str
    occupancy_id: int
    nonce: str
    expiration: float
    revision_hash: str
    status: str


def _b64url(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return urlsafe_b64decode(data + padding)


def create_transition_request(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    ttl_seconds: float = 300.0,
    now: Optional[float] = None,
) -> TransitionRequestRecord:
    """Policy-side creation. The caller (Policy, never the agent directly --
    see spec guardrail 'No agent DB writes for transition_request creation')
    generates the nonce and revision_hash and persists PENDING here."""
    nonce = secrets.token_hex(16)
    now = now if now is not None else time.time()
    expiration = now + ttl_seconds
    revision_hash = hashlib.sha256(
        f"{task_id}:{from_state}:{to_state}:{occupancy_id}:{nonce}".encode("utf-8")
    ).hexdigest()

    conn.execute("BEGIN IMMEDIATE;")
    try:
        cursor = conn.execute(
            """
            INSERT INTO transition_request
                (task_id, from_state, to_state, occupancy_id, nonce, expiration,
                 revision_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
            """,
            (task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash, now),
        )
        conn.commit()
        request_id = cursor.lastrowid
    except Exception:
        conn.rollback()
        raise

    return TransitionRequestRecord(
        request_id=request_id, task_id=task_id, from_state=from_state, to_state=to_state,
        occupancy_id=occupancy_id, nonce=nonce, expiration=expiration,
        revision_hash=revision_hash, status="PENDING",
    )


def issue_stub_token(
    record: TransitionRequestRecord,
    secret: bytes,
    *,
    jti: Optional[str] = None,
    now: Optional[float] = None,
) -> str:
    """Stub stand-in for a real IdP's signed proof (e.g. CIBA+RAR). Generated
    fresh per caller and never reused as a trusted key outside a test fixture
    or this local PoC -- a real deployment replaces this entirely with actual
    IdP-issued, IdP-signed tokens (Increment B, out of scope for this module).

    Compact format: base64url(payload_json).base64url(hmac_sha256_signature) --
    deliberately not claiming JWT/JWS standard compliance, just a stand-in
    with an equivalent signed-and-verifiable shape."""
    payload = {
        "task_id": record.task_id,
        "from_state": record.from_state,
        "to_state": record.to_state,
        "occupancy_id": record.occupancy_id,
        "nonce": record.nonce,
        "revision_hash": record.revision_hash,
        "exp": record.expiration,
        "jti": jti or secrets.token_hex(16),
        "iat": now if now is not None else time.time(),
    }
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(secret, payload_bytes, hashlib.sha256).digest()
    return f"{_b64url(payload_bytes)}.{_b64url(signature)}"


def _decode_stub_token(token: str, secret: bytes) -> Dict[str, Any]:
    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError:
        raise TransitionRequestError("Malformed token: expected 'payload.signature'.")
    payload_bytes = _b64url_decode(payload_part)
    signature = _b64url_decode(signature_part)
    expected_signature = hmac.new(secret, payload_bytes, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_signature):
        raise TransitionRequestError("Token signature verification failed.")
    return json.loads(payload_bytes)


def verify_and_consume(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    token: str,
    secret: bytes,
    now: Optional[float] = None,
) -> TransitionRequestRecord:
    """Independent Policy-side verification -- the actual mechanics this task
    exists to prove: signature (via _decode_stub_token), expiration, payload-
    match against the STORED request (not the token's own self-reported
    claims), single-use via nonce+jti, atomic consume-and-commit in one
    transaction (TOCTOU-safe). Adversarial matrix cases 1-4 map directly onto
    this function's checks."""
    now = now if now is not None else time.time()
    payload = _decode_stub_token(token, secret)  # raises on bad signature

    conn.execute("BEGIN IMMEDIATE;")
    try:
        row = conn.execute(
            """
            SELECT request_id, task_id, from_state, to_state, occupancy_id,
                   nonce, expiration, revision_hash, status, jti
            FROM transition_request WHERE nonce = ?
            """,
            (payload.get("nonce"),),
        ).fetchone()

        if row is None:
            raise RequestNotFound(f"No transition_request found for nonce {payload.get('nonce')!r}.")

        (request_id, stored_task_id, stored_from, stored_to, stored_occ,
         stored_nonce, stored_exp, stored_rev_hash, status, stored_jti) = row

        # Case 2: replay -- already consumed (or otherwise not PENDING).
        if status != "PENDING":
            raise TokenReplayed(
                f"transition_request {request_id} is '{status}', not PENDING -- "
                "token already consumed or request already resolved."
            )

        # Case 3: payload mismatch -- token's claims must match the STORED
        # request exactly, not just be internally self-consistent. A token
        # correctly signed for a *different* task/nonce must not validate here.
        if (
            payload.get("task_id") != stored_task_id
            or payload.get("from_state") != stored_from
            or payload.get("to_state") != stored_to
            or payload.get("occupancy_id") != stored_occ
            or payload.get("revision_hash") != stored_rev_hash
        ):
            raise PayloadMismatch(
                "Token payload does not match the stored transition_request -- "
                "possible cross-request token reuse."
            )
        if task_id != stored_task_id:
            raise PayloadMismatch(f"Token is for task '{stored_task_id}', not '{task_id}'.")

        # Case 4: expired.
        if now >= stored_exp:
            conn.execute(
                "UPDATE transition_request SET status = 'EXPIRED' WHERE request_id = ?",
                (request_id,),
            )
            conn.commit()
            raise TokenExpired(f"transition_request {request_id} expired at {stored_exp}, now {now}.")

        # All checks passed -- atomic consume-and-commit (case 1 success path).
        # WHERE ... AND status = 'PENDING' makes this the actual TOCTOU guard:
        # cursor.rowcount (not conn.total_changes, which is connection-wide and
        # not scoped to this statement) is 0 only if another writer consumed
        # this exact row between the SELECT above and this UPDATE.
        update_cursor = conn.execute(
            """
            UPDATE transition_request
            SET status = 'CONSUMED', consumed_at = ?, jti = ?
            WHERE request_id = ? AND status = 'PENDING'
            """,
            (now, payload.get("jti"), request_id),
        )
        if update_cursor.rowcount == 0:
            conn.rollback()
            raise TokenReplayed(f"transition_request {request_id} was consumed concurrently.")
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    return TransitionRequestRecord(
        request_id=request_id, task_id=stored_task_id, from_state=stored_from,
        to_state=stored_to, occupancy_id=stored_occ, nonce=stored_nonce,
        expiration=stored_exp, revision_hash=stored_rev_hash, status="CONSUMED",
    )
