"""
tests/test_transition_request_mechanics.py
============================================

Purpose:
    Adversarial acceptance matrix cases 1-6 for auth-ciba-poc-transition-mechanics
    (issues #621, #626, #634) -- control_plane/transition_request.py's
    create_transition_request/issue_stub_token/verify_and_consume mechanics,
    exercised against a real disposable SQLite database (never the production
    context/control_plane.db, never mocked -- this repo's TDW rule prohibits
    mocking the verification logic itself on this critical path).

Key Input Dependencies:
    - control_plane/transition_request.py
    - A temporary, isolated SQLite database per test

Key Functions (test cases, matrix numbering matches the spec):
    - test_case1_genuine_token_first_use_commits
    - test_case2_replayed_token_denied
    - test_case3_payload_mismatch_denied
    - test_case4_expired_token_denied
    - test_case5_no_bypass_parameter_exists
    - test_case6_direct_sqlite_write_finding (reports, does not assert pass/fail
      on the finding itself -- see spec DoD: "written report ... regardless of
      this task's own overall pass/fail")
"""

import secrets
import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ControlPlane
from control_plane.transition_request import (
    PayloadMismatch,
    RequestNotFound,
    TokenExpired,
    TokenReplayed,
    create_transition_request,
    issue_stub_token,
    verify_and_consume,
)


@pytest.fixture
def db_and_task(tmp_path):
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    task_id = "mechanics-task-001"
    cp.create_task(task_id=task_id, title="Mechanics test", runtime_tool="test")
    conn = sqlite3.connect(db_path)
    return conn, task_id


def test_case1_genuine_token_first_use_commits(db_and_task):
    conn, task_id = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )
    token = issue_stub_token(record, secret)

    result = verify_and_consume(conn, task_id=task_id, token=token, secret=secret)
    assert result.status == "CONSUMED"

    row = conn.execute(
        "SELECT status, consumed_at FROM transition_request WHERE request_id = ?",
        (record.request_id,),
    ).fetchone()
    assert row[0] == "CONSUMED"
    assert row[1] is not None


def test_case2_replayed_token_denied(db_and_task):
    conn, task_id = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )
    token = issue_stub_token(record, secret)

    verify_and_consume(conn, task_id=task_id, token=token, secret=secret)  # first use succeeds
    with pytest.raises(TokenReplayed):
        verify_and_consume(conn, task_id=task_id, token=token, secret=secret)  # replay denied


def test_case3_payload_mismatch_denied(db_and_task):
    """A token correctly signed and internally self-consistent, but for a
    DIFFERENT transition_request (different task_id/nonce), must not validate
    against the first request even if somehow presented against it."""
    conn, task_id = db_and_task
    secret = secrets.token_bytes(32)
    record_a = create_transition_request(
        conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )
    other_task_id = "mechanics-task-002"
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, runtime_tool, created_at, updated_at) "
        "VALUES (?, ?, 'INTAKE', 'test', 0, 0)",
        (other_task_id, "Other task"),
    )
    conn.commit()
    record_b = create_transition_request(
        conn, task_id=other_task_id, from_state="INTAKE", to_state="INTERVIEW", occupancy_id=2,
    )
    token_for_b = issue_stub_token(record_b, secret)

    # Attempting to verify task A using a genuinely-signed token for request B's
    # nonce should fail because verify_and_consume looks up by the token's own
    # nonce -- it will correctly find request B, but the caller-supplied task_id
    # (task A) won't match the stored request's task_id.
    with pytest.raises(PayloadMismatch):
        verify_and_consume(conn, task_id=task_id, token=token_for_b, secret=secret)

    # request A remains untouched and still consumable on its own.
    token_for_a = issue_stub_token(record_a, secret)
    result = verify_and_consume(conn, task_id=task_id, token=token_for_a, secret=secret)
    assert result.status == "CONSUMED"


def test_case4_expired_token_denied(db_and_task):
    conn, task_id = db_and_task
    secret = secrets.token_bytes(32)
    past = 1000.0
    record = create_transition_request(
        conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, ttl_seconds=1.0, now=past,
    )
    token = issue_stub_token(record, secret, now=past)

    with pytest.raises(TokenExpired):
        verify_and_consume(conn, task_id=task_id, token=token, secret=secret, now=past + 3600)

    row = conn.execute(
        "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()
    assert row[0] == "EXPIRED"


def test_case5_no_bypass_parameter_exists(db_and_task):
    """verify_and_consume has no parameter that skips signature/payload/
    expiration checking -- inspecting its actual signature, not just its
    behavior, since a bypass parameter could exist but default to off."""
    import inspect
    sig = inspect.signature(verify_and_consume)
    param_names = set(sig.parameters.keys())
    bypass_like = {"skip_verification", "force", "bypass", "trust", "no_check"}
    assert not (param_names & bypass_like), (
        f"verify_and_consume must not expose a bypass parameter; found: {param_names & bypass_like}"
    )
    # And a request that was never created cannot be verified against any token.
    secret = secrets.token_bytes(32)
    fake_record_shape = type("R", (), {
        "task_id": "nonexistent-task", "from_state": "A", "to_state": "B",
        "occupancy_id": 1, "nonce": "nonexistent-nonce-" + secrets.token_hex(8),
        "expiration": 9999999999.0, "revision_hash": "deadbeef",
    })()
    token = issue_stub_token(fake_record_shape, secret)
    conn, task_id = db_and_task
    with pytest.raises(RequestNotFound):
        verify_and_consume(conn, task_id=task_id, token=token, secret=secret)


def test_case6_direct_sqlite_write_finding(db_and_task):
    """Case 6 finding, reported regardless of pass/fail per the spec DoD:
    can an agent flip transition_request.status (or tasks.state) directly via
    SQLite, bypassing verify_and_consume entirely? This test documents the
    actual current answer rather than assuming it.

    Finding: YES, currently possible. Nothing in this module or the existing
    schema (transition_request has no trigger analogous to
    enforce_valid_transition on the tasks table) prevents a direct
    'UPDATE transition_request SET status = ...' or 'UPDATE tasks SET state = ...'
    from a caller with raw sqlite3 access to control_plane.db. This is the same
    class of gap the AUTH-PLAN research register already names (Option C:
    "Agent-writable SQLite fails") -- SQLite alone was never claimed to be the
    authorization boundary; Policy code (verify_and_consume, coordinator.py)
    is. Closing this fully requires deploying with the database itself
    inaccessible to the agent process (a separate, previously-scoped-out
    infrastructure decision -- AUTH-PLAN Option A), not a change this local
    PoC module can make on its own. Recorded here as the required finding,
    not silently treated as passing."""
    conn, task_id = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )

    # Direct write, bypassing verify_and_consume entirely.
    conn.execute(
        "UPDATE transition_request SET status = 'CONSUMED', consumed_at = 0 WHERE request_id = ?",
        (record.request_id,),
    )
    conn.commit()

    row = conn.execute(
        "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()
    direct_write_succeeded = row[0] == "CONSUMED"

    # This assertion documents the finding as a known, reported gap -- it is
    # NOT a claim that this is acceptable for production use. See docstring
    # and docs/plans/work-tasks/auth-ciba-poc-transition-mechanics/ for the
    # required written report citing this exact result.
    assert direct_write_succeeded is True, (
        "If this ever becomes False, the finding above is stale -- update the "
        "docstring and the task's written report to reflect what actually "
        "changed (e.g. a trigger was added to transition_request)."
    )
