"""
tests/test_actionable_rollback.py
=================================

Purpose:
    Failing-first tests for U2 (auth-ciba-increment-b, issue #639): a transition that the database
    trigger rejects for missing human decisions must say so and name the missing question ids, not
    report a misleading "changed concurrently ... Retry." (which sends the agent into a retry loop).
    A genuine concurrent state change still raises ConcurrentModificationError.

Key Input Dependencies:
    - agent_control.py (ControlPlane.transition), control_plane/adapters.py (required_transition_questions)
    - tests/test_review_selection.py helper (_plan_review_task)

Key Functions (test cases):
    - test_missing_human_decisions_are_named_not_reported_as_concurrency
    - test_a_real_concurrent_change_is_still_retryable
"""

import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ConcurrentModificationError, PersistenceInvariantViolation
from test_review_selection import TASK, _plan_review_task


def test_missing_human_decisions_are_named_not_reported_as_concurrency(tmp_path):
    sim = _plan_review_task(tmp_path)
    with pytest.raises(PersistenceInvariantViolation) as excinfo:
        sim.control_plane.transition(TASK, "MULTI_AGENT_REVIEW", "tester", "no decisions recorded")
    message = str(excinfo.value)
    assert "plan_review_agent_review_decision" in message
    assert "coordinate-transition" in message and "--interactive" in message
    assert "Retry" not in message


def test_a_real_concurrent_change_is_still_retryable(tmp_path):
    sim = _plan_review_task(tmp_path)
    cp = sim.control_plane

    def stale_read(task_id):
        conn = sqlite3.connect(cp.db_path)
        conn.execute("UPDATE tasks SET state = 'ESCALATED' WHERE task_id = ?", (task_id,))  # a competing writer
        conn.commit()
        return "PLAN_REVIEW"

    cp._read_current_state_for_update = stale_read
    with pytest.raises(ConcurrentModificationError) as excinfo:
        cp.transition(TASK, "MULTI_AGENT_REVIEW", "tester", "race")
    assert "Retry" in str(excinfo.value)
