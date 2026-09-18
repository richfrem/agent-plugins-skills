"""
tests/test_authorized_actor_enforcement.py
===========================================

Purpose:
    Adversarial acceptance matrix for auth-ciba-poc-transition-mechanics
    (issues #621, #626, #634). Verifies the authorized_actor structural
    classification is correctly derived and enforced, per
    docs/plans/work-tasks/auth-ciba-poc-transition-mechanics/
    auth-ciba-poc-transition-mechanics-spec.md's DoD table and
    ...implementation-plan.md's case-to-task mapping.

Key Input Dependencies:
    - control_plane/transition_templates.yaml (approval blocks per edge)
    - A temporary, isolated SQLite database per test (never the real
      context/control_plane.db)

Key Functions (test cases, matrix numbering matches the spec):
    - test_authorized_actor_derived_human_only_for_awaiting_approval (T1)
    - test_authorized_actor_derived_agent_or_human_for_routine_edge (T1)
    - test_authorized_actor_derived_human_only_for_force_close_family (T1)
    - test_authorized_actor_derived_agent_or_human_for_force_done (T1, negative case)
    - test_valid_transitions_table_has_authorized_actor_column (T1)
    - test_guidance_confirmation_agent_answerable_on_routine_edge (T7, case 10)
    - test_guidance_confirmation_still_human_only_on_consequential_edge (T7, case 9)
    - test_direct_instantiation_spoofed_actor_denied (T2, case 8)
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
from control_plane.constants import STATE_AWAITING_APPROVAL
from agent_control import ControlPlane


@pytest.fixture
def registry():
    return TransitionRegistry.load_default()


def test_authorized_actor_derived_human_only_for_awaiting_approval(registry):
    tmpl = registry.get_template("AWAITING_APPROVAL", "APPROVED")
    assert tmpl is not None
    assert tmpl.authorized_actor == "human_only"


def test_authorized_actor_derived_agent_or_human_for_routine_edge(registry):
    tmpl = registry.get_template("INTAKE", "INTERVIEW")
    assert tmpl is not None
    assert tmpl.authorized_actor == "agent_or_human"


def test_authorized_actor_derived_human_only_for_force_close_family(registry):
    """The '* -> INTAKE' wildcard fans out into one literal template per
    canonical state at load time (registry.py's wildcard-expansion logic) --
    there is no literal ('*', 'INTAKE') key. INTERVIEW -> INTAKE is the exact
    edge exercised live this session (the real reset used to fix the
    actor='agent' interview-answer mistake)."""
    tmpl = registry.get_template("INTERVIEW", "INTAKE")
    assert tmpl is not None
    assert tmpl.approval.get("required") is True
    assert tmpl.approval.get("approver_role") == "human"
    assert tmpl.authorized_actor == "human_only"


def test_authorized_actor_derived_agent_or_human_for_force_done(registry):
    """Negative case: '* -> DONE' (force-done) has approval.required=False even
    though approver_role='human' -- its real gate is the separate
    FORCE_CLOSE/FORCE_DONE literal-value check in coordinator.py, not the
    generic approval block this derivation reads. Confirms the derivation
    does not accidentally over-classify this edge. Same wildcard-expansion
    note as above applies: INTERVIEW -> DONE is one of the expanded edges."""
    tmpl = registry.get_template("INTERVIEW", "DONE")
    assert tmpl is not None
    assert tmpl.approval.get("required") is False
    assert tmpl.authorized_actor == "agent_or_human"


def test_valid_transitions_table_has_authorized_actor_column(tmp_path):
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    conn = sqlite3.connect(db_path)
    cols = [row[1] for row in conn.execute("PRAGMA table_info(valid_transitions)")]
    assert "authorized_actor" in cols

    row = conn.execute(
        "SELECT authorized_actor FROM valid_transitions WHERE from_state = ? AND to_state = ?",
        ("AWAITING_APPROVAL", "APPROVED"),
    ).fetchone()
    assert row is not None
    assert row[0] == "human_only"

    row2 = conn.execute(
        "SELECT authorized_actor FROM valid_transitions WHERE from_state = ? AND to_state = ?",
        ("INTAKE", "INTERVIEW"),
    ).fetchone()
    assert row2 is not None
    assert row2[0] == "agent_or_human"


def test_guidance_confirmation_agent_answerable_on_routine_edge(tmp_path, registry):
    """Case 10: INTAKE -> INTERVIEW is agent_or_human. A non-interactive call
    supplying guidance_compliance_confirmation via --answers must succeed, and
    the recorded decision's actor must be 'agent' (never falsely 'human')."""
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    task_id = "case10-routine-edge"
    cp.create_task(task_id=task_id, title="Case 10", runtime_tool="test")

    coord = TransitionCoordinator(cp, registry=registry, output_stream=io.StringIO())
    rec = coord.coordinate_transition(
        task_id=task_id,
        to_state="INTERVIEW",
        actor="agent",
        reason="case 10: agent-answerable guidance confirmation on routine edge",
        provided_answers={"guidance_compliance_confirmation": "YES"},
    )
    assert rec.to_state == "INTERVIEW"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT actor, answer FROM transition_decisions WHERE task_id = ? AND question_id = ?",
        (task_id, "guidance_compliance_confirmation"),
    ).fetchone()
    assert row is not None
    assert row[0] == "agent"
    assert row[1] == "YES"


def _reach_awaiting_approval(tmp_path, registry, task_id: str) -> PipelineSimulator:
    """Shared setup for case 9 and case 8: walks a fresh task to AWAITING_APPROVAL,
    faithfully mirroring PipelineSimulator.run_standard_happy_path's own sequence
    (DRAFT_PLAN -> PLAN_REVIEW only accepts "Proceed with review"; the skip-review
    disposition lives at PLAN_REVIEW's own outgoing edges, not there)."""
    db_path = tmp_path / "control_plane.db"
    sim = PipelineSimulator(db_path, registry=registry)
    sim.create_task(task_id, "shared setup")
    sim.control_plane.repo_root = tmp_path / "simulated-repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)
    sim.enter_interview(task_id)
    sim.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
    sim.control_plane.record_plan_mode_entry(task_id, "simulator")
    sim.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD", expect_success=True)

    plan_dir = sim.control_plane.repo_root / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan", encoding="utf-8")

    plan_review_answers = iter(["1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(plan_review_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state="PLAN_REVIEW", actor="human",
        reason="shared setup", interactive=True,
    )
    review_answers = iter(["1", "3", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(review_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state="MULTI_AGENT_REVIEW", actor="human",
        reason="shared setup", interactive=True,
    )
    sim.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: "YES", output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state="PLAN_REVIEW", actor="simulator",
        reason="shared setup", interactive=True,
    )
    accept_answers = iter(["1", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry,
        input_fn=lambda _p: next(accept_answers), output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state=STATE_AWAITING_APPROVAL, actor="human",
        reason="shared setup", interactive=True,
    )
    return sim


def test_guidance_confirmation_still_human_only_on_consequential_edge(tmp_path, registry):
    """Case 9: AWAITING_APPROVAL -> APPROVED is human_only. This scope
    extension must not weaken existing behavior here -- a non-interactive
    attempt, even with guidance_compliance_confirmation supplied via
    --answers, must still be denied exactly as before."""
    task_id = "case9-consequential-edge"
    sim = _reach_awaiting_approval(tmp_path, registry, task_id)

    coord = TransitionCoordinator(sim.control_plane, registry=sim.registry, output_stream=io.StringIO())
    with pytest.raises(TransitionCoordinatorError, match="requires a real human answer"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="agent",
            reason="case 9: agent attempts guidance confirmation on human_only edge",
            approval_decision="APPROVAL",
            provided_answers={
                "human_implementation_approval": "Yes, approve implementation [Recommended]",
                "guidance_compliance_confirmation": "YES",
            },
        )


def test_direct_instantiation_spoofed_actor_denied(tmp_path, registry):
    """Case 8 (T2, round-1 security review finding): direct Python instantiation
    of TransitionCoordinator, bypassing agent_control.py's CLI entrypoint and its
    --human-confirmed requirement entirely, with a spoofed top-level actor="human"
    argument and a non-interactive approval_decision="APPROVAL", must still be
    denied on a human_only edge. This closes the gap at the API boundary, not
    just the CLI -- the CLI is not the trust boundary.

    Verifies existing behavior (approval_actor is derived internally from
    interactive/approval_decision, never trusted from the caller-supplied top-
    level `actor` string) plus the SQLite trigger's own actor='human' requirement
    for approval_{transition_id} on human_only edges -- both already close this
    specific bypass without needing new enforcement code, but this case was
    previously untested."""
    task_id = "case8-spoofed-actor"
    sim = _reach_awaiting_approval(tmp_path, registry, task_id)

    coord = TransitionCoordinator(sim.control_plane, registry=sim.registry, output_stream=io.StringIO())
    with pytest.raises(TransitionCoordinatorError):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="human",  # spoofed -- no real human present, no --interactive
            reason="case 8: spoofed actor, bypassing the CLI's --human-confirmed gate",
            approval_decision="APPROVAL",
            provided_answers={
                "human_implementation_approval": "Yes, approve implementation [Recommended]",
                "guidance_compliance_confirmation": "YES",
            },
        )

    conn = sqlite3.connect(sim.db_path)
    state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]
    assert state == STATE_AWAITING_APPROVAL, (
        "Task must remain in AWAITING_APPROVAL -- the spoofed-actor attempt must "
        "not have advanced state to APPROVED under any circumstance."
    )
