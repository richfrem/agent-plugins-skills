"""
tests/test_review_selection.py
==============================

Purpose:
    Failing-first contract tests for T17 (auth-ciba-increment-b, issue #639): the review-selection-v1
    sequence on BOTH review edges (PLAN_REVIEW -> MULTI_AGENT_REVIEW and WORKTREE_REVIEW ->
    MULTI_AGENT_CODE_REVIEW): review needed -> method -> (internal only) runtime -> model -> effort.
    The three internal-review selections are conditional human questions declared in the YAML
    (`asked_when`), asked one at a time, human-typed only (never `provided_answers`), never defaulted,
    and a reviewer outcome cannot be recorded for an internal review without them.
    Real coordinator, real SQLite; expectations come from the live registry, not retyped literals.

Key Input Dependencies:
    - control_plane/transition_templates.yaml (asked_when questions), registry.py, coordinator.py
    - control_plane/review_selection.py (conditional_questions, review_selection_gaps)
    - agent_control.py (ControlPlane.record_critic_review)
    - tests/helpers/gate1_fixtures.py

Key Functions (test cases):
    - test_both_edges_declare_the_three_internal_selections_conditionally
    - test_conditional_questions_are_not_dbrequired
    - test_internal_method_asks_runtime_model_effort_in_order_and_records_human_decisions
    - test_external_method_asks_nothing_more
    - test_provided_answers_cannot_satisfy_an_internal_selection
    - test_empty_selection_is_rejected
    - test_critic_outcome_is_refused_without_the_selections
    - test_review_selection_gaps_reports_missing_ids
"""

import io
import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.registry import TransitionRegistry
from control_plane.review_selection import REVIEW_EDGES, conditional_questions, review_selection_gaps

TASK = "review-sel-001"
INTERNAL = "Multi-agent review — internal [Recommended]"
EXTERNAL = "Multi-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)"
YES = "Yes — continue to review method selection [Recommended]"


def _plan_review_task(tmp_path):
    registry = TransitionRegistry.load_default()
    sim = PipelineSimulator(tmp_path / "control_plane.db", registry=registry)
    sim.create_task(TASK, "review selection")
    sim.control_plane.repo_root = tmp_path / "repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)
    sim.enter_interview(TASK)
    sim.stage_interview_answers(TASK, classification="STANDARD", to_state="DRAFT_PLAN")
    sim.control_plane.record_plan_mode_entry(TASK, "simulator")
    sim.transition_from_interview(TASK, "DRAFT_PLAN", classification="STANDARD", expect_success=True)
    plans = sim.control_plane.repo_root / "docs" / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{TASK}-spec.md").write_text("# spec", encoding="utf-8")
    (plans / f"{TASK}-implementation-plan.md").write_text("# plan", encoding="utf-8")
    feed = iter(["1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
    ).coordinate_transition(task_id=TASK, to_state="PLAN_REVIEW", actor="human", reason="setup", interactive=True)
    return sim


def _go(sim, answers, **kw):
    feed = iter(answers)
    prompts = []

    def ask(p):
        prompts.append(p)
        return next(feed)

    coordinator = TransitionCoordinator(sim.control_plane, registry=sim.registry, input_fn=ask, output_stream=io.StringIO())
    kwargs = dict(task_id=TASK, to_state="MULTI_AGENT_REVIEW", actor="human", reason="review", interactive=True)
    kwargs.update(kw)
    return coordinator.coordinate_transition(**kwargs), prompts


def _decisions(sim):
    conn = sqlite3.connect(sim.control_plane.db_path)
    return conn.execute(
        "SELECT question_id, answer, actor FROM transition_decisions WHERE task_id = ? AND to_state = 'MULTI_AGENT_REVIEW' ORDER BY decision_id",
        (TASK,),
    ).fetchall()


def test_both_edges_declare_the_three_internal_selections_conditionally():
    registry = TransitionRegistry.load_default()
    for from_state, to_state in REVIEW_EDGES:
        questions = conditional_questions(registry.get_template(from_state, to_state))
        assert len(questions) == 3
        assert [q["asked_when"]["question_id"] for q in questions] == [questions[0]["asked_when"]["question_id"]] * 3


def test_conditional_questions_are_not_dbrequired(tmp_path):
    sim = _plan_review_task(tmp_path)
    conn = sqlite3.connect(sim.control_plane.db_path)
    required = {r[0] for r in conn.execute(
        "SELECT question_id FROM required_transition_questions WHERE from_state = 'PLAN_REVIEW' AND to_state = 'MULTI_AGENT_REVIEW'")}
    conditional = {q["question_id"] for q in conditional_questions(sim.registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW"))}
    assert conditional and not (required & conditional)


def test_internal_method_asks_runtime_model_effort_in_order_and_records_human_decisions(tmp_path):
    sim = _plan_review_task(tmp_path)
    _, prompts = _go(sim, [YES, INTERNAL, "claude-cli", "opus-5", "medium", "YES"])
    ids = [p.split(":")[0] for p in prompts]
    conditional = [q["question_id"] for q in conditional_questions(sim.registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW"))]
    assert ids[2:5] == conditional
    rows = {r[0]: (r[1], r[2]) for r in _decisions(sim)}
    assert [rows[c] for c in conditional] == [("claude-cli", "human"), ("opus-5", "human"), ("medium", "human")]


def test_external_method_asks_nothing_more(tmp_path):
    sim = _plan_review_task(tmp_path)
    _, prompts = _go(sim, [YES, EXTERNAL, "YES"])
    conditional = {q["question_id"] for q in conditional_questions(sim.registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW"))}
    assert not ({p.split(":")[0] for p in prompts} & conditional)
    assert not ({r[0] for r in _decisions(sim)} & conditional)


def test_provided_answers_cannot_satisfy_an_internal_selection(tmp_path):
    sim = _plan_review_task(tmp_path)
    conditional = conditional_questions(sim.registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW"))
    answers = {"plan_review_agent_review_decision": YES, "plan_review_method": INTERNAL}
    answers.update({q["question_id"]: "x" for q in conditional})
    with pytest.raises(TransitionCoordinatorError):
        _go(sim, [], interactive=False, provided_answers=answers)
    assert sim.control_plane._persistence.read_current_state(TASK) == "PLAN_REVIEW"


def test_empty_selection_is_rejected(tmp_path):
    sim = _plan_review_task(tmp_path)
    with pytest.raises(TransitionCoordinatorError):
        _go(sim, [YES, INTERNAL, "", "opus-5", "medium", "YES"])
    assert sim.control_plane._persistence.read_current_state(TASK) == "PLAN_REVIEW"


def test_critic_outcome_is_refused_without_the_selections(tmp_path):
    sim = _plan_review_task(tmp_path)
    _go(sim, [YES, INTERNAL, "claude-cli", "opus-5", "medium", "YES"])
    conn = sqlite3.connect(sim.control_plane.db_path)
    conn.execute("DELETE FROM transition_decisions WHERE task_id = ? AND question_id LIKE '%internal_model'", (TASK,))
    conn.commit()
    with pytest.raises(Exception) as excinfo:
        sim.control_plane.record_critic_review(TASK, 1, "opus-5", "PASS", "no selection recorded")
    assert "selection" in str(excinfo.value).lower()


def test_review_selection_gaps_reports_missing_ids(tmp_path):
    sim = _plan_review_task(tmp_path)
    conn = sqlite3.connect(sim.control_plane.db_path)
    assert review_selection_gaps(conn, sim.registry, TASK, "PLAN_REVIEW", "MULTI_AGENT_REVIEW") == []
    _go(sim, [YES, INTERNAL, "claude-cli", "opus-5", "medium", "YES"])
    assert review_selection_gaps(conn, sim.registry, TASK, "PLAN_REVIEW", "MULTI_AGENT_REVIEW") == []
    conn.execute("DELETE FROM transition_decisions WHERE task_id = ? AND question_id LIKE '%internal_effort'", (TASK,))
    conn.commit()
    gaps = review_selection_gaps(conn, sim.registry, TASK, "PLAN_REVIEW", "MULTI_AGENT_REVIEW")
    assert len(gaps) == 1 and gaps[0].endswith("internal_effort")
