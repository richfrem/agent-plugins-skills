"""
tests/test_inspect_verbs.py
===========================

Purpose:
    Failing-first acceptance tests for U3 (auth-ciba-increment-b, issue #639): the canonical
    read-only inspection verbs `agent_control.py inspect-decisions` and `inspect-candidates`
    (control_plane/inspection.py). They replace the ad-hoc raw SQL that agents kept running against
    internal table schemas (which even guessed column names wrong). Read-only is enforced by opening
    the database with SQLite's `mode=ro`. Real disposable SQLite databases; the decisions come from a
    real coordinator walk.

Key Input Dependencies:
    - control_plane/inspection.py (inspect_decisions, inspect_candidates, open_readonly)
    - agent_control.py (_build_parser), tests/helpers/gate1_fixtures.py

Key Functions (test cases):
    - test_inspect_decisions_lists_actor_and_answers_in_order
    - test_inspect_decisions_filters_by_edge
    - test_inspect_candidates_lists_confirmation_status
    - test_connection_is_read_only
    - test_cli_registers_both_verbs
"""

import sqlite3
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.inspection import inspect_candidates, inspect_decisions, open_readonly
from helpers.gate1_fixtures import reach_awaiting_approval

TASK = "inspect-task-001"


@pytest.fixture(scope="module")
def sim(tmp_path_factory):
    path = tmp_path_factory.mktemp("inspect")
    simulator = reach_awaiting_approval(path, TASK)
    simulator.control_plane.record_source_assisted_answer_candidate(
        TASK, "INTERVIEW", "round-1", "interview_summary", "a candidate answer", "docs/plans/backlog.md", True,
    )
    return simulator


def _conn(sim):
    return open_readonly(sim.control_plane.db_path)


def test_inspect_decisions_lists_actor_and_answers_in_order(sim):
    rows = inspect_decisions(_conn(sim), TASK)
    assert rows and [r["decision_id"] for r in rows] == sorted(r["decision_id"] for r in rows)
    first = rows[0]
    assert {"decision_id", "edge", "question_id", "actor", "answer", "decision_type", "consumed"} <= set(first)
    assert any(r["actor"] == "human" and r["question_id"] == "guidance_compliance_confirmation" for r in rows)


def test_inspect_decisions_filters_by_edge(sim):
    rows = inspect_decisions(_conn(sim), TASK, to_state="PLAN_REVIEW")
    assert rows and all(r["edge"].endswith("-> PLAN_REVIEW") for r in rows)
    assert inspect_decisions(_conn(sim), TASK, to_state="NO_SUCH_STATE") == []


def test_inspect_candidates_lists_confirmation_status(sim):
    rows = inspect_candidates(_conn(sim), TASK)
    assert len(rows) == 1
    assert rows[0]["question_id"] == "interview_summary" and rows[0]["confirmation_status"] == "pending"
    assert rows[0]["confirmed_by"] is None and rows[0]["source_path"] == "docs/plans/backlog.md"


def test_connection_is_read_only(sim):
    conn = _conn(sim)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("UPDATE tasks SET state = 'DONE' WHERE task_id = ?", (TASK,))


def test_unknown_task_returns_nothing(sim):
    assert inspect_decisions(_conn(sim), "no-such-task") == []
    assert inspect_candidates(_conn(sim), "no-such-task") == []


def test_cli_registers_both_verbs():
    parser = agent_control._build_parser()
    a = parser.parse_args(["inspect-decisions", "--task-id", "t", "--to-state", "APPROVED", "--json"])
    assert a.task_id == "t" and a.to_state == "APPROVED" and a.json is True
    b = parser.parse_args(["inspect-candidates", "--task-id", "t"])
    assert b.task_id == "t"
