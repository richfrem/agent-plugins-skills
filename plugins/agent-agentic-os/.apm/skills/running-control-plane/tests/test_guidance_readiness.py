"""
tests/test_guidance_readiness.py
================================

Purpose:
    Failing-first test for U1 (auth-ciba-increment-b, issue #639): `transition-guidance --to X`
    separates DATA readiness (are the artifacts/checks for the edge in place) from EXECUTION readiness
    (can the transition commit now, i.e. are there still human-actor questions without an unconsumed
    human decision), and lists the pending human question ids. Read-only; never authorizes anything.

Key Input Dependencies:
    - agent_control.py (ControlPlane.get_transition_guidance), tests/test_review_selection.py helper

Key Functions (test cases):
    - test_guidance_lists_pending_human_questions_and_separates_readiness
    - test_readiness_is_absent_once_the_edge_is_no_longer_current
"""

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from test_review_selection import EXTERNAL, TASK, YES, _go, _plan_review_task


def test_guidance_lists_pending_human_questions_and_separates_readiness(tmp_path):
    sim = _plan_review_task(tmp_path)
    guidance = sim.control_plane.get_transition_guidance(TASK, "MULTI_AGENT_REVIEW")
    readiness = guidance["readiness"]
    assert set(readiness) == {"data_readiness", "execution_readiness"}
    assert "plan_review_agent_review_decision" in readiness["execution_readiness"]["pending_human_question_ids"]
    assert readiness["execution_readiness"]["ready"] is False
    assert readiness["data_readiness"]["required_artifacts"]
    assert "does not authorize" in readiness["execution_readiness"]["note"].lower()


def test_readiness_is_absent_once_the_edge_is_no_longer_current(tmp_path):
    sim = _plan_review_task(tmp_path)
    before = sim.control_plane.get_transition_guidance(TASK, "MULTI_AGENT_REVIEW")["readiness"]["execution_readiness"]["pending_human_question_ids"]
    _go(sim, [YES, EXTERNAL, "YES"])
    after = sim.control_plane.get_transition_guidance(TASK, "MULTI_AGENT_REVIEW")
    # the task has advanced, so the requested edge is no longer legal from here: readiness is absent
    assert before and "readiness" not in after
