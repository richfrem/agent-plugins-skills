"""
Purpose:
    Unit test verifying that premium-call budget tracking in state_engine is
    scoped per-phase, so a later phase's premium tasks aren't blocked by an
    earlier phase's counter.

Key Input Dependencies:
    - state_engine.py module (init_db, create_session, add_task, lease_task,
      record_premium_call)
    - pytest tmp_path fixture
"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from state_engine import init_db, create_session, add_task, lease_task, record_premium_call

def test_premium_calls_are_tracked_per_phase(tmp_path):
    """Phase 2 premium tasks must not be blocked by phase 1's counter."""
    db = tmp_path / "test.sqlite"
    conn = init_db(str(db))
    sid = "session-1"
    create_session(conn, sid, "test")

    # Phase 1: add a premium task, lease it, record the premium call
    add_task(conn, "t1", sid, 1, "phase-1", "comp-a", requires_premium=True)
    assert lease_task(conn, "t1", "agent-a") is True
    record_premium_call(conn, sid, phase_ordinal=1)

    # Phase 2: should have a fresh budget — not blocked by phase 1
    add_task(conn, "t2", sid, 2, "phase-2", "comp-b", requires_premium=True)
    assert lease_task(conn, "t2", "agent-b") is True, \
        "Phase 2 premium task blocked by phase 1 counter — per-phase tracking broken"

def test_non_premium_task_not_gated(tmp_path):
    """Tasks without requires_premium=True must ignore the premium call counter."""
    db = tmp_path / "test.sqlite"
    conn = init_db(str(db))
    sid = "session-2"
    create_session(conn, sid, "test")

    # Saturate phase 1 premium counter
    add_task(conn, "tp1", sid, 1, "phase-1", "premium-comp", requires_premium=True)
    assert lease_task(conn, "tp1", "agent-x") is True
    record_premium_call(conn, sid, phase_ordinal=1)

    # A normal task in phase 1 should still lease fine
    add_task(conn, "tn1", sid, 1, "phase-1", "normal-comp", requires_premium=False)
    assert lease_task(conn, "tn1", "agent-y") is True
