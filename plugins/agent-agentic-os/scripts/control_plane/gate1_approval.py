#!/usr/bin/env python3
"""
control_plane/gate1_approval.py
===============================

Purpose:
    The human-uid half of Gate 1 (AWAITING_APPROVAL -> APPROVED) for auth-ciba-increment-b
    (issue #639, task T6). The agent-run request phase (coordinator.py) creates a content-bound
    `transition_request` and returns the remediation error; the human then runs, in their own
    session:
      1. `agent_control.py show-challenge --request-id N`  -> renders the challenge from the DB row into
         the human-owned 0700 directory, prints the exact bytes and the exact `ssh-keygen -Y sign`
         command for their key;
      2. `ssh-keygen -Y sign ...` (passphrase prompt or hardware touch) -> `<stem>.sig` beside it;
      3. `agent_control.py approve-transition --request-id N` -> isolation preflight, the coordinator's
         edge policy re-run (guidance block, required artifacts, deterministic checks), the signature
         read once by descriptor, then ONE transaction in the persistence adapter verifies it, consumes
         the request, writes the decision rows and advances the state.
    There is deliberately no `--signature` argument: the signature path is derived from the request row.
    Every refusal leaves the request PENDING and the task unchanged.

Key Input Dependencies:
    - control_plane/coordinator.py (authorization_preflight), ssh_signing.py, snapshot.py,
      isolation_check.py, identity_layout.py, transition_request.py, ports.py
    - `context/identity/` files created by setup_ciba_identity.py (T11)
    - `ssh-keygen` on PATH

Key Functions:
    - show_challenge() -- write and print the challenge and the sign command.
    - approve_transition() -- verify and commit; returns the TransitionRecord.
    - GateApprovalError -- every refusal, with `.reasons`.
"""

import shlex
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from control_plane.identity_layout import DEFAULT_KEY_HINT, IdentityLayout, default_layout
from control_plane.isolation_check import IsolationError, check_isolation
from control_plane.ports import AuthorizationProof, PersistenceInvariantViolation, TransitionCommitRequest
from control_plane.proof_edges import prefetch_for_edge, snapshot_for_edge
from control_plane.snapshot import SnapshotError, diff_snapshot, snapshot_matches
from control_plane.ssh_signing import (
    SigningError,
    derive_challenge_from_row,
    read_signature,
    request_file_stem,
    sign_command,
    write_challenge,
)
from control_plane.transition_request import TransitionRequestError


class GateApprovalError(Exception):
    """A refusal by show-challenge or approve-transition; nothing was changed."""

    def __init__(self, message: str, reasons: Optional[List[str]] = None):
        self.reasons = list(reasons or [])
        super().__init__(message if not self.reasons else message + "\n  - " + "\n  - ".join(self.reasons))


def _coordinator(cp: Any):
    from control_plane.coordinator import TransitionCoordinator

    return TransitionCoordinator(cp)


def _load_request(cp: Any, request_id: int) -> Dict[str, Any]:
    conn = cp._persistence.get_connection()
    try:
        row = conn.execute(
            """
            SELECT task_id, from_state, to_state, occupancy_id, nonce, expiration, status, content_snapshot
            FROM transition_request WHERE request_id = ?
            """,
            (request_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise GateApprovalError(f"No transition_request {request_id}.")
    keys = ("task_id", "from_state", "to_state", "occupancy_id", "nonce", "expiration", "status", "content_snapshot")
    data = dict(zip(keys, tuple(row)))
    data["request_id"] = request_id
    if (data["from_state"], data["to_state"]) not in _coordinator(cp)._registry.proof_required_edges():
        raise GateApprovalError(f"transition_request {request_id} is for {data['from_state']} -> {data['to_state']}, which takes no signed approval.")
    if data["status"] != "PENDING":
        raise GateApprovalError(f"transition_request {request_id} is '{data['status']}', not PENDING; run the request again.")
    if time.time() >= data["expiration"]:
        raise GateApprovalError(f"transition_request {request_id} expired; run `coordinate-transition --to {data['to_state']}` again for a new request.")
    return data


def _isolation(layout: IdentityLayout, agent_identity: Optional[Dict[str, Any]]) -> None:
    """Fail closed unless the trust anchors are human-owned and agent-inaccessible.

    The human's own process is not the agent: SSH_AUTH_SOCK is not checked here (verification never
    uses an agent). The socket check concerns the agent's environment and is reported at request time."""
    result = check_isolation(
        allowed_signers=layout.allowed_signers, allowed_signers_selftest=layout.allowed_signers_selftest,
        challenge_dir=layout.challenge_dir, environ={}, **(agent_identity or {}),
    )
    if not result.ok:
        raise GateApprovalError(
            "The signing trust anchors are not safely set up (see plugins/agent-agentic-os/references/isolation-setup.md).",
            [f"{f.code}: {f.message}" + (f" ({f.path})" if f.path else "") for f in result.failures],
        )


def _live_snapshot(cp: Any, data: Dict[str, Any]):
    """The live content bound by this request's edge: plan artifacts (Gate 1) or the git worktree (Gate 3)."""
    repo_root = _coordinator(cp)._resolve_repo_root()
    try:
        return snapshot_for_edge(cp, repo_root, data["task_id"], data["from_state"], data["to_state"]), repo_root
    except SnapshotError as exc:
        raise GateApprovalError(f"The content this request binds is not readable: {exc}") from exc


def show_challenge(
    cp: Any,
    request_id: int,
    *,
    layout: Optional[IdentityLayout] = None,
    key_hint: str = DEFAULT_KEY_HINT,
    agent_identity: Optional[Dict[str, Any]] = None,
    out: Optional[TextIO] = None,
) -> Path:
    """Render the challenge for a request into the human-owned directory and print how to sign it."""
    out = out or sys.stdout
    data = _load_request(cp, request_id)
    live, repo_root = _live_snapshot(cp, data)
    layout = layout or default_layout(repo_root)
    _isolation(layout, agent_identity)
    if not snapshot_matches(data["content_snapshot"], live):
        raise GateApprovalError(
            "The reviewed content changed since this request was created "
            f"({', '.join(diff_snapshot(data['content_snapshot'], live))}); the request no longer applies. "
            f"Run `coordinate-transition --to {data['to_state']}` again."
        )
    conn = cp._persistence.get_connection()
    try:
        try:
            challenge = derive_challenge_from_row(conn, request_id, live)
        except SigningError as exc:
            raise GateApprovalError(str(exc)) from exc
    finally:
        conn.close()
    stem = request_file_stem(request_id, data["nonce"])
    path = layout.challenge_dir / stem
    if path.exists():
        if path.is_symlink() or path.read_bytes() != challenge:
            raise GateApprovalError(f"{path} already exists with different content; refusing to overwrite it.")
    else:
        path = write_challenge(layout.challenge_dir, stem, challenge)
    out.write("\nYou are about to sign this exact text (it is the approval):\n\n")
    out.write(challenge.decode("utf-8"))
    out.write("\nSign it in your own terminal (you will be asked for your passphrase or to touch your key):\n\n")
    out.write("  " + shlex.join(sign_command(key_hint, path)) + "\n\n")
    out.write(f"Then approve:  python3 plugins/agent-agentic-os/scripts/agent_control.py approve-transition --request-id {request_id}\n")
    return path


def approve_transition(
    cp: Any,
    request_id: int,
    *,
    layout: Optional[IdentityLayout] = None,
    principal: Optional[str] = None,
    agent_identity: Optional[Dict[str, Any]] = None,
    out: Optional[TextIO] = None,
    require_uv: bool = True,
    binary: str = "ssh-keygen",
):
    """Verify the human's signature and commit Gate 1 in one transaction. Raises GateApprovalError."""
    out = out or sys.stdout
    data = _load_request(cp, request_id)
    _, repo_root = _live_snapshot(cp, data)
    layout = layout or default_layout(repo_root)
    _isolation(layout, agent_identity)
    reasons = _coordinator(cp).authorization_preflight(data["task_id"], data["to_state"])
    if reasons:
        raise GateApprovalError("The edge's policy checks no longer pass; nothing was approved.", reasons)
    stem = request_file_stem(request_id, data["nonce"])
    try:
        signature = read_signature(layout.challenge_dir, stem)
    except IsolationError as exc:
        raise GateApprovalError(f"No usable signature at {layout.challenge_dir / (stem + '.sig')}: {exc}. Run show-challenge and sign it first.") from exc
    task_id = data["task_id"]
    # database-backed inputs are read BEFORE the commit transaction: the live snapshot runs inside it and must
    # not open another connection
    try:
        prefetched = prefetch_for_edge(cp, repo_root, task_id, data["from_state"], data["to_state"])
    except SnapshotError as exc:
        raise GateApprovalError(f"The content this request binds is not readable: {exc}") from exc
    last = cp._persistence.get_last_transition(task_id)
    template = _coordinator(cp)._registry.get_template(data["from_state"], data["to_state"])
    proof = AuthorizationProof(
        kind="sshsig", request_id=request_id, signature=signature, allowed_signers=layout.allowed_signers,
        principal=principal, require_uv=require_uv, binary=binary,
        live_snapshot_fn=lambda: snapshot_for_edge(cp, repo_root, task_id, data["from_state"], data["to_state"], prefetched=prefetched),
    )
    commit = TransitionCommitRequest(
        task_id=task_id, expected_from_state=data["from_state"], to_state=data["to_state"],
        source_occupancy_transition_id=last.transition_id, template_id=template.transition_id, actor="human",
        reason="Gate 1 approved with a verified SSHSIG signature", staged_decisions=[], staged_receipts=[], proof=proof,
    )
    try:
        record = cp.commit_authorized_transition(commit)
    except (SigningError, TransitionRequestError, PersistenceInvariantViolation, SnapshotError, ValueError) as exc:
        retry = ""
        if isinstance(exc, SigningError):
            retry = (
                f" If you signed with the wrong key or passphrase, delete {layout.challenge_dir / (stem + '.sig')} first "
                "(ssh-keygen will not overwrite it), then sign the challenge again and re-run approve-transition."
            )
        raise GateApprovalError(f"Approval refused: {exc}.{retry}") from exc
    out.write(f"Approved: {record.from_state} -> {record.to_state} (transition {record.transition_id}), signature verified.\n")
    return record
