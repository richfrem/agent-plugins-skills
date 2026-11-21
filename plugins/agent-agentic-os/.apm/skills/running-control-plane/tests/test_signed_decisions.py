"""S3 tests (DoD row 14, Q1, sec-2-6, arch-2-5): signed human decisions in `signed_decisions` table."""

from __future__ import annotations

import sqlite3
import subprocess
import time
from pathlib import Path

import pytest

from agent_control import ControlPlane
from control_plane.signed_decisions import (
    SignedDecisionError,
    build_decision_challenge,
    get_latest_signed_decision,
    new_decision_nonce,
    record_signed_decision,
)
from control_plane.simulation_identity import ensure_identity_at
from control_plane.ssh_signing import SIGN_NAMESPACE


def _sign_bytes(private_key: Path, data: bytes, tmp_path: Path) -> bytes:
    f = tmp_path / f"chal-{time.time_ns()}"
    f.write_bytes(data)
    subprocess.run(
        ["ssh-keygen", "-Y", "sign", "-f", str(private_key), "-n", SIGN_NAMESPACE, str(f)],
        check=True,
        capture_output=True,
    )
    return (f.with_suffix(".sig")).read_bytes()


def test_signed_decision_verifies_persists_and_rejects_tampering_or_stale_occupancy(tmp_path):
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.init_db()
    cp.create_task("t-sd-1", "Signed decision test", "claude")

    ident = ensure_identity_at(tmp_path / "sim-id")
    key = Path(ident["key"])
    anchor = Path(ident["layout"].allowed_signers)

    conn = sqlite3.connect(str(cp.db_path))
    try:
        occ = conn.execute("SELECT MAX(transition_id) FROM task_transitions WHERE task_id = 't-sd-1'").fetchone()[0]
        nonce = new_decision_nonce()
        exp = time.time() + 600
        decision_text = "internal-subagents: host-subagents / inherit / medium"
        chal = build_decision_challenge(
            task_id="t-sd-1",
            request_id=1,
            from_state="PLAN_REVIEW",
            to_state="APPROVED",
            occupancy_id=occ,
            question_id="plan_review_preset",
            decision_text=decision_text,
            nonce=nonce,
            expiration=exp,
        )
        sig = _sign_bytes(key, chal, tmp_path)

        # 1. Valid signature succeeds and stamps decided_at
        rec = record_signed_decision(
            conn,
            task_id="t-sd-1",
            from_state="PLAN_REVIEW",
            to_state="APPROVED",
            occupancy_id=occ,
            question_id="plan_review_preset",
            decision_text=decision_text,
            request_id=1,
            nonce=nonce,
            expiration=exp,
            signature=sig,
            allowed_signers=anchor,
        )
        assert rec.decision_text == decision_text
        assert rec.decided_at.endswith("Z")
        fetched = get_latest_signed_decision(conn, task_id="t-sd-1", occupancy_id=occ, question_id="plan_review_preset")
        assert fetched is not None and fetched["decision_text"] == decision_text

        # 2. Edited decision text with the same signature is REFUSED
        with pytest.raises(SignedDecisionError):
            record_signed_decision(
                conn,
                task_id="t-sd-1",
                from_state="PLAN_REVIEW",
                to_state="APPROVED",
                occupancy_id=occ,
                question_id="plan_review_preset",
                decision_text="skip",
                request_id=1,
                nonce=nonce,
                expiration=exp,
                signature=sig,
                allowed_signers=anchor,
            )

        # 3. Stale occupancy is REFUSED
        with pytest.raises(SignedDecisionError):
            record_signed_decision(
                conn,
                task_id="t-sd-1",
                from_state="PLAN_REVIEW",
                to_state="APPROVED",
                occupancy_id=occ + 99,
                question_id="plan_review_preset",
                decision_text=decision_text,
                request_id=1,
                nonce=nonce,
                expiration=exp,
                signature=sig,
                allowed_signers=anchor,
            )

        # 4. Unsigned / garbage bytes refused
        with pytest.raises(SignedDecisionError):
            record_signed_decision(
                conn,
                task_id="t-sd-1",
                from_state="PLAN_REVIEW",
                to_state="APPROVED",
                occupancy_id=occ,
                question_id="plan_review_preset",
                decision_text=decision_text,
                request_id=1,
                nonce=nonce,
                expiration=exp,
                signature=b"not-a-signature",
                allowed_signers=anchor,
            )
    finally:
        conn.close()
