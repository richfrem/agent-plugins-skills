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
    - consume_with_signature() -- T4: verify a human's SSHSIG and consume the request
      inside the CALLER's open transaction (the adapter's BEGIN IMMEDIATE).
    - verify_and_consume() -- independent Policy-side verification: signature,
      expiration, payload-match against the stored request (not the token's
      own claims), content binding (T2: a request created with a content snapshot
      can only be consumed against the same live content), single-use (jti +
      nonce), atomic consume-and-commit.

Exceptions:
    - TransitionRequestError (base)
    - TokenExpired, TokenReplayed, PayloadMismatch, RequestNotFound
    - ContentChanged, ContentBindingRequired (T2, auth-ciba-increment-b)
    - StaleOccupancy (T4)
"""

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

from control_plane.ssh_signing import VerifiedSignature, derive_challenge_from_row, verify_signature
from control_plane.snapshot import (
    CHALLENGE_VERSION,
    SnapshotEntry,
    compute_revision_hash,
    diff_snapshot,
    snapshot_matches,
    snapshot_to_json,
)


# Default lifetime of a Gate 1 request: a human must read the challenge, sign it (passphrase or
# hardware touch) and run approve-transition, which needs more than the Increment A 300 s.
DEFAULT_GATE1_TTL_SECONDS = 900.0


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


class StaleOccupancy(TransitionRequestError):
    """The request was created for an earlier occupancy of the task."""


class ContentChanged(TransitionRequestError):
    """The reviewed content differs from the snapshot bound to the request."""


class ContentBindingRequired(TransitionRequestError):
    """A content-bound request cannot be consumed without a live snapshot to compare."""


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
    challenge_version: Optional[str] = None
    content_snapshot: Optional[str] = None


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
    content_snapshot: Optional[Sequence[SnapshotEntry]] = None,
) -> TransitionRequestRecord:
    """Policy-side creation. The caller (Policy, never the agent directly --
    see spec guardrail 'No agent DB writes for transition_request creation')
    generates the nonce and revision_hash and persists PENDING here."""
    nonce = secrets.token_hex(16)
    now = now if now is not None else time.time()
    expiration = now + ttl_seconds
    # T2: with a content snapshot the hash binds the reviewed files; without one it is
    # exactly the Increment A metadata-only hash.
    revision_hash = compute_revision_hash(
        task_id, from_state, to_state, occupancy_id, nonce, content_snapshot
    )
    challenge_version = CHALLENGE_VERSION if content_snapshot else None
    snapshot_json = snapshot_to_json(content_snapshot) if content_snapshot else None

    conn.execute("BEGIN IMMEDIATE;")
    try:
        cursor = conn.execute(
            """
            INSERT INTO transition_request
                (task_id, from_state, to_state, occupancy_id, nonce, expiration,
                 revision_hash, status, created_at, challenge_version, content_snapshot)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?, ?)
            """,
            (task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash, now,
             challenge_version, snapshot_json),
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
        challenge_version=challenge_version, content_snapshot=snapshot_json,
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
    live_snapshot: Optional[Sequence[SnapshotEntry]] = None,
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
                   nonce, expiration, revision_hash, status, jti,
                   challenge_version, content_snapshot
            FROM transition_request WHERE nonce = ?
            """,
            (payload.get("nonce"),),
        ).fetchone()

        if row is None:
            raise RequestNotFound(f"No transition_request found for nonce {payload.get('nonce')!r}.")

        (request_id, stored_task_id, stored_from, stored_to, stored_occ,
         stored_nonce, stored_exp, stored_rev_hash, status, stored_jti,
         stored_version, stored_snapshot) = row

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

        # T2 content binding: a request created with a content snapshot may only be
        # consumed against the same live content. Fail closed when the caller supplies
        # no live snapshot; leave the request PENDING (nothing is mutated on refusal).
        if stored_snapshot is not None:
            if live_snapshot is None:
                raise ContentBindingRequired(
                    f"transition_request {request_id} is bound to reviewed content; "
                    "pass live_snapshot so it can be re-checked before consumption."
                )
            if not snapshot_matches(stored_snapshot, live_snapshot):
                changed = ", ".join(diff_snapshot(stored_snapshot, live_snapshot))
                raise ContentChanged(
                    f"transition_request {request_id}: reviewed content changed since the "
                    f"request was created ({changed}); the approval no longer applies."
                )

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
        challenge_version=stored_version, content_snapshot=stored_snapshot,
    )


@dataclass(frozen=True)
class PreVerified:
    """Result of preverify_signature(): the live snapshot read, the challenge rebuilt from it, and the
    signature verified over that challenge -- all computed with NO write lock held. The commit transaction
    trusts none of it blindly: consume_with_signature() rebuilds the challenge from the row inside the
    transaction and refuses unless it is byte-identical to the one that was verified here."""

    request_id: int
    live: Sequence[Any]
    challenge: Any
    verified: VerifiedSignature


def _check_request_row(conn: sqlite3.Connection, *, task_id: str, from_state: str, to_state: str,
                       occupancy_id: int, proof: Any, now: float) -> str:
    """Row-level checks shared by both phases (no external work): request exists, matches task and edge,
    is PENDING, belongs to the live occupancy, is unexpired, and is content-bound. Returns the stored snapshot."""
    row = conn.execute(
        """
        SELECT task_id, from_state, to_state, occupancy_id, expiration, status, content_snapshot
        FROM transition_request WHERE request_id = ?
        """,
        (proof.request_id,),
    ).fetchone()
    if row is None:
        raise RequestNotFound(f"No transition_request {proof.request_id}.")
    stored_task, stored_from, stored_to, stored_occ, stored_exp, status, stored_snapshot = tuple(row)
    if (stored_task, stored_from, stored_to) != (task_id, from_state, to_state):
        raise PayloadMismatch(
            f"transition_request {proof.request_id} is for {stored_task} {stored_from}->{stored_to}, "
            f"not {task_id} {from_state}->{to_state}."
        )
    if status != "PENDING":
        raise TokenReplayed(f"transition_request {proof.request_id} is '{status}', not PENDING.")
    if stored_occ != occupancy_id:
        raise StaleOccupancy(
            f"transition_request {proof.request_id} was created for occupancy {stored_occ}; live occupancy is {occupancy_id}."
        )
    if now >= stored_exp:
        raise TokenExpired(f"transition_request {proof.request_id} expired at {stored_exp}, now {now}.")
    if stored_snapshot is None:
        raise ContentBindingRequired(f"transition_request {proof.request_id} is not bound to reviewed content.")
    return stored_snapshot


def _check_live_content(stored_snapshot: str, live: Any, proof: Any) -> None:
    if live is None:
        raise ContentBindingRequired("a live content snapshot is required to consume a content-bound request.")
    if not snapshot_matches(stored_snapshot, live):
        raise ContentChanged(
            f"transition_request {proof.request_id}: reviewed content changed since the request "
            f"({', '.join(diff_snapshot(stored_snapshot, live))}); the approval no longer applies."
        )


def preverify_signature(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    proof: Any,
    now: float,
) -> PreVerified:
    """The slow, external half of consumption, run BEFORE the commit's `BEGIN IMMEDIATE`: read the live
    snapshot (git/file hashing), rebuild the challenge and run `ssh-keygen -Y verify`. `conn` must be a
    read-only, non-transactional connection -- holding the write lock across a subprocess makes every
    concurrent writer fail with `database is locked` for the subprocess's duration. Nothing here mutates."""
    stored_snapshot = _check_request_row(
        conn, task_id=task_id, from_state=from_state, to_state=to_state,
        occupancy_id=occupancy_id, proof=proof, now=now,
    )
    live = proof.live_snapshot_fn() if proof.live_snapshot_fn is not None else None
    _check_live_content(stored_snapshot, live, proof)
    challenge = derive_challenge_from_row(conn, proof.request_id, live)
    if proof.allowed_signers is None:
        from control_plane.ssh_signing import SignatureInvalid

        raise SignatureInvalid("no allowed_signers file supplied with the proof")
    verified = verify_signature(
        challenge, proof.signature, allowed_signers=proof.allowed_signers, principal=proof.principal,
        require_uv=proof.require_uv, binary=proof.binary, timeout=proof.timeout,
    )
    return PreVerified(request_id=proof.request_id, live=live, challenge=challenge, verified=verified)


def consume_with_signature(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    proof: Any,
    now: float,
    preverified: Optional[PreVerified] = None,
) -> VerifiedSignature:
    """Consume a human's SSHSIG-verified request INSIDE the caller's transaction.

    Does not begin or commit: the persistence adapter calls this within its `BEGIN IMMEDIATE` so
    consumption, decision rows and the state advance are one atomic unit (a failure anywhere rolls all of
    it back and leaves the request PENDING). `proof` is a control_plane.ports.AuthorizationProof.

    With `preverified` (the adapter path), the subprocess and git work already happened outside the write
    lock; this re-runs every row check against the transaction's own view, requires the stored snapshot to
    still match the snapshot that was verified, and requires the challenge rebuilt from the row here to be
    identical to the verified one -- so a request mutated between the two phases cannot ride the earlier
    verification -- then flips PENDING -> CONSUMED. Without it (direct callers), it performs the whole
    verification inline, exactly as before."""
    stored_snapshot = _check_request_row(
        conn, task_id=task_id, from_state=from_state, to_state=to_state,
        occupancy_id=occupancy_id, proof=proof, now=now,
    )
    if preverified is None:
        preverified = preverify_signature(
            conn, task_id=task_id, from_state=from_state, to_state=to_state,
            occupancy_id=occupancy_id, proof=proof, now=now,
        )
    else:
        if preverified.request_id != proof.request_id:
            raise PayloadMismatch("pre-verified signature belongs to a different transition_request.")
        _check_live_content(stored_snapshot, preverified.live, proof)
        if derive_challenge_from_row(conn, proof.request_id, preverified.live) != preverified.challenge:
            raise ContentChanged(
                f"transition_request {proof.request_id} changed between signature verification and commit; "
                "the verified challenge no longer matches the stored request."
            )
    verified = preverified.verified
    cursor = conn.execute(
        "UPDATE transition_request SET status = 'CONSUMED', consumed_at = ?, jti = ? WHERE request_id = ? AND status = 'PENDING'",
        (now, f"sshsig:{verified.fingerprint}", proof.request_id),
    )
    if cursor.rowcount == 0:
        raise TokenReplayed(f"transition_request {proof.request_id} was consumed concurrently.")
    return verified
