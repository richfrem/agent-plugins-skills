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
from control_plane.constants import STATE_PLAN_REVIEW
from agent_control import ControlPlane


@pytest.fixture
def registry():
    return TransitionRegistry.load_default()


def test_authorized_actor_derived_human_only_for_awaiting_approval(registry):
    tmpl = registry.get_template("PLAN_REVIEW", "APPROVED")
    assert tmpl is not None
    assert tmpl.authorized_actor == "human_only"


def test_authorized_actor_derived_agent_or_human_for_routine_edge(registry):
    tmpl = registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")
    assert tmpl is not None
    assert tmpl.authorized_actor == "agent_or_human"


def test_authorized_actor_derived_human_only_for_force_close_family(registry):
    """The '* -> INTAKE' wildcard fans out into one literal template per active non-INTAKE state."""
    tmpl = registry.get_template("DRAFT_PLAN", "INTAKE")
    assert tmpl is not None
    assert tmpl.approval.get("required") is True
    assert tmpl.approval.get("approver_role") == "human"
    assert tmpl.authorized_actor == "human_only"


def test_authorized_actor_derived_human_only_and_proof_gated_for_closure_edges(registry):
    """Every edge into DONE is human_only AND requires_cryptographic_proof."""
    tmpl = registry.get_template("DRAFT_PLAN", "DONE")
    assert tmpl is not None
    assert tmpl.authorized_actor == "human_only"
    assert ("DRAFT_PLAN", "DONE") in registry.proof_required_edges()
    assert not any(
        {"FORCE_DONE", "FORCE_CLOSE"} & set(q.get("accepted_answers", [])) for q in tmpl.human_questions
    )


def test_valid_transitions_table_has_authorized_actor_column(tmp_path):
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    conn = sqlite3.connect(db_path)
    cols = [row[1] for row in conn.execute("PRAGMA table_info(valid_transitions)")]
    assert "authorized_actor" in cols

    row = conn.execute(
        "SELECT authorized_actor FROM valid_transitions WHERE from_state = ? AND to_state = ? AND retired = 0",
        ("PLAN_REVIEW", "APPROVED"),
    ).fetchone()
    assert row is not None
    assert row[0] == "human_only"

    row2 = conn.execute(
        "SELECT authorized_actor FROM valid_transitions WHERE from_state = ? AND to_state = ? AND retired = 0",
        ("DRAFT_PLAN", "PLAN_REVIEW"),
    ).fetchone()
    assert row2 is not None
    assert row2[0] == "agent_or_human"


def test_guidance_confirmation_agent_answerable_on_routine_edge(tmp_path, registry):
    """Case 10: DRAFT_PLAN -> PLAN_REVIEW is agent_or_human and commits non-interactively
    as actor='agent' without human ceremony (S5 removed guidance_compliance_confirmation)."""
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.repo_root = tmp_path / "repo"
    cp.repo_root.mkdir(parents=True, exist_ok=True)
    task_id = "case10-routine-edge"
    cp.create_task(task_id=task_id, title="Case 10", runtime_tool="test")
    TransitionCoordinator(cp, registry=registry, input_fn=lambda _p: "1", output_stream=io.StringIO()).coordinate_transition(
        task_id=task_id, to_state="DRAFT_PLAN", actor="human", reason="intake", interactive=True,
    )
    cp.record_plan_mode_entry(task_id, "agent")
    plans = cp.repo_root / "docs" / "plans" / "work-tasks" / task_id
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{task_id}-spec.md").write_text("# spec\n", encoding="utf-8")
    (plans / f"{task_id}-implementation-plan.md").write_text("# plan\n\n- Strategy: direct\n", encoding="utf-8")

    coord = TransitionCoordinator(cp, registry=registry, output_stream=io.StringIO())
    rec = coord.coordinate_transition(
        task_id=task_id,
        to_state="PLAN_REVIEW",
        actor="agent",
        reason="case 10: agent routine edge",
        interactive=False,
    )
    assert rec.to_state == "PLAN_REVIEW"


def _reach_awaiting_approval(tmp_path, registry, task_id: str) -> PipelineSimulator:
    """Shared setup for case 9 and case 8: walks a fresh task to PLAN_REVIEW (Gate 1 source state in v15)."""
    db_path = tmp_path / "control_plane.db"
    sim = PipelineSimulator(db_path, registry=registry)
    sim.create_task(task_id, "shared setup")
    sim.control_plane.repo_root = tmp_path / "simulated-repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)
    sim.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
    sim.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD", expect_success=True)
    sim.control_plane.record_plan_mode_entry(task_id, "simulator")

    plan_dir = sim.control_plane.repo_root / "docs" / "plans" / "work-tasks" / task_id
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec\n", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan\n\n- Strategy: direct\n", encoding="utf-8")

    TransitionCoordinator(
        sim.control_plane, registry=sim.registry, output_stream=io.StringIO(),
    ).coordinate_transition(
        task_id=task_id, to_state="PLAN_REVIEW", actor="agent",
        reason="shared setup", interactive=False,
    )
    return sim


def test_guidance_confirmation_still_human_only_on_consequential_edge(tmp_path, registry):
    """Case 9: AWAITING_APPROVAL -> APPROVED is human_only. This scope
    extension must not weaken existing behavior here -- a non-interactive
    attempt, even with guidance_compliance_confirmation supplied via
    --answers, must still be denied exactly as before."""
    task_id = "case9-consequential-edge"
    sim = _reach_awaiting_approval(tmp_path, registry, task_id)

    from control_plane.snapshot import gate1_artifact_paths
    coord = TransitionCoordinator(sim.control_plane, registry=sim.registry, output_stream=io.StringIO())
    for _label, _path in gate1_artifact_paths(coord._resolve_repo_root(), task_id):  # reviewed content exists: the refusal is about authority
        _path.parent.mkdir(parents=True, exist_ok=True)
        _path.write_text("reviewed\n")
    # Programmatic answers on a human_only, proof-gated edge never authorize it: the coordinator halts for a signature.
    with pytest.raises(TransitionCoordinatorError, match="HUMAN_PROOF_REQUIRED"):
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
    assert state == STATE_PLAN_REVIEW, (
        "Task must remain in PLAN_REVIEW -- the spoofed-actor attempt must "
        "not have advanced state to APPROVED under any circumstance."
    )


def test_phase_capability_exposes_authorized_actor(tmp_path):
    """T5: verify_phase_capability's returned PhaseCapability carries the releasing
    edge's authorized_actor classification directly."""
    from control_plane.ports import PhaseCapability

    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    task_id = "phase-cap-actor"
    cp.create_task(task_id=task_id, title="Phase capability actor", runtime_tool="test")

    cap = cp.verify_phase_capability(task_id, "interview_question")
    assert isinstance(cap, PhaseCapability)
    assert cap.releasing_edge == ("NONE", "INTAKE")
    assert cap.authorized_actor == "agent_or_human"


def test_transition_decision_supports_optional_token_provenance_fields():
    """T5: TransitionDecision gains optional token_jti/token_consumed_at fields so a
    decision recorded via the transition_request stub-JWT mechanics can carry the
    consumed token's identity for audit, without forcing every other call site
    (which has no token at all) to supply them."""
    from control_plane.ports import TransitionDecision

    plain = TransitionDecision(
        task_id="t1", source_occupancy_transition_id=1, from_state="A", to_state="B",
        question_id="q1", answer="YES", decision_type="ANSWER", actor="human",
        recorded_at=0.0,
    )
    assert plain.token_jti is None
    assert plain.token_consumed_at is None

    with_token = TransitionDecision(
        task_id="t1", source_occupancy_transition_id=1, from_state="A", to_state="B",
        question_id="q1", answer="YES", decision_type="ANSWER", actor="human",
        recorded_at=0.0, token_jti="jti-123", token_consumed_at=1758000000.0,
    )
    assert with_token.token_jti == "jti-123"
    assert with_token.token_consumed_at == 1758000000.0


def test_cli_agent_attempt_denied(tmp_path, registry, monkeypatch):
    """Case 7 (T1, T2, T4): a non-interactive agent-driven attempt on a
    human_only edge (AWAITING_APPROVAL -> APPROVED), invoked through the real
    agent_control.py CLI entrypoint -- its actual argparse parser and main()
    dispatch, not direct Python instantiation (that's case 8, already covered
    by test_direct_instantiation_spoofed_actor_denied) -- must be denied
    structurally, and the task must remain in AWAITING_APPROVAL afterward.

    Deliberately NOT a subprocess test. A live subprocess reproduction during
    this task's own review revealed that SqlitePersistenceAdapter's db-path
    discovery (_discover_shared_db_path) resolves via `git rev-parse
    --git-common-dir` anchored to adapters.py's own file location -- entirely
    independent of the subprocess's cwd -- meaning a real subprocess CLI
    invocation with no override would target the actual shared
    context/control_plane.db for this whole repo, not an isolated test
    database. No CLI flag or environment variable exists to redirect it. To
    exercise the real CLI entrypoint (argparse parsing, --human-confirmed
    requirement, main()'s dispatch) without that live-database risk, main()
    is invoked in-process with sys.argv patched, and only the DB-path
    *discovery* method is monkeypatched to the test's isolated tmp_path --
    the actual authorized_actor/trigger enforcement logic this case tests
    runs completely unmocked. See map-debt.md for the discovery risk itself.

    This closes a real evidence-integrity gap found during the internal
    multi-agent code review of this task's own diff: the implementation plan's
    case-to-task mapping table claimed a CLI-level test named
    test_cli_agent_attempt_denied existed, but no such test -- and no test
    exercising agent_control.py's actual CLI entrypoint for this scenario at
    all -- previously existed anywhere in the suite."""
    import sys
    import agent_control as agent_control_module
    from control_plane.adapters import SqlitePersistenceAdapter

    task_id = "case7-cli-agent-attempt"
    sim = _reach_awaiting_approval(tmp_path, registry, task_id)

    isolated_db_path = sim.db_path
    monkeypatch.setattr(
        SqlitePersistenceAdapter, "_discover_shared_db_path",
        lambda self: isolated_db_path,
    )

    # main_clean_before_approval inspects the REAL git working tree's dirty
    # status (unrelated to this test's isolated tmp_path), so without this
    # exception receipt the test's pass/fail would depend on whatever
    # uncommitted state happens to exist in the actual repo at run time --
    # confirmed live: this test initially "passed" for the wrong reason
    # (real repo dirty-state denial) before this receipt was added. The
    # receipt is the check's own documented, supported exception mechanism
    # (see policy.py's _main_clean_before_approval_check), not a workaround.
    sim.control_plane.record_verification_receipt(
        task_id=task_id, gate_name="main_dirty_before_approval_exception",
        command_executed="test isolation: this case tests authorized_actor enforcement, not main-checkout cleanliness",
        exit_code=0,
    )

    argv = [
        "agent_control.py", "coordinate-transition",
        "--task-id", task_id,
        "--to", "APPROVED",
        "--actor", "agent",
        "--reason", "case 7: agent-driven CLI attempt on human_only edge",
        "--approval", "APPROVAL",
        "--answers", '{"human_implementation_approval": "Yes, approve implementation [Recommended]", "guidance_compliance_confirmation": "YES"}',
        "--human-confirmed", "HUMAN-CONFIRMED: case 7 fabricated claim -- an agent asserting human confirmation with no real human present",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as exc_info:
        agent_control_module.main()
    assert exc_info.value.code != 0, "CLI must exit non-zero on denial."

    conn = sqlite3.connect(isolated_db_path)
    state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]
    conn.close()
    assert state == STATE_PLAN_REVIEW, (
        "Task must remain in PLAN_REVIEW -- the CLI-driven agent attempt "
        "must not have advanced state to APPROVED under any circumstance."
    )


def test_recovery_approval_cannot_reach_verify_exit_bypassing_worktree_review(tmp_path):
    """CRITICAL finding from live multi-agent code review (2026-09-18, external codex
    review + independent live reproduction): record_recovery_approval() previously
    hardcoded actor='human' into the inserted transition_decisions row regardless of
    the real caller, and enforce_valid_transition's recovery bypass clause permitted
    ANY transition once a matching row existed -- with no re-check of valid_transitions
    membership. Combined, an agent calling record_recovery_approval() then
    apply_recovery_transition() directly could reach VERIFY_EXIT from any state,
    completely recreating the IN_WORKTREE -> VERIFY_EXIT backdoor this task's own
    state_machine.py edge deletion was supposed to close.

    Live reproduction before the fix (recorded here for posterity, not re-run):
        token = cp.record_recovery_approval(task_id, "VERIFY_EXIT", "agent-self", ...)
        cp.apply_recovery_transition(task_id, "VERIFY_EXIT", token, actor="agent", ...)
        # -> task reached VERIFY_EXIT with zero real human authorization

    Fix: RECOVERY_FORBIDDEN_DESTINATIONS (adapters.py) blocks record_recovery_approval
    from ever creating an approval row targeting VERIFY_EXIT or APPROVED, and the
    trigger's own recovery_td clause independently excludes these destinations as
    defense-in-depth against a hand-crafted decision row bypassing the Python guard."""
    from control_plane.constants import STATE_IN_WORKTREE, STATE_VERIFY_EXIT

    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    task_id = "case-recovery-verify-exit-bypass"
    cp.create_task(task_id, "Recovery bypass regression", "agent")

    # Reach IN_WORKTREE via the real, legitimate recovery mechanism itself (INTAKE ->
    # IN_WORKTREE is not a RECOVERY_FORBIDDEN_DESTINATIONS entry, so this must still
    # work normally) rather than a raw SQL UPDATE -- the trigger correctly reverts any
    # untracked raw state change with no matching decision, so a raw UPDATE here would
    # silently no-op instead of actually reaching IN_WORKTREE.
    token = cp.record_recovery_approval(
        task_id=task_id, destination_state=STATE_IN_WORKTREE, approver="human-operator",
        actor="human", reason="test setup: legitimate reopen into IN_WORKTREE",
    )
    cp.apply_recovery_transition(
        task_id=task_id, destination_state=STATE_IN_WORKTREE, token=token,
        actor="human", reason="test setup",
    )
    assert cp.get_task(task_id)["state"] == STATE_IN_WORKTREE

    # Layer 1: record_recovery_approval itself must refuse to create the approval row.
    with pytest.raises(ValueError, match="not permitted"):
        cp.record_recovery_approval(
            task_id=task_id,
            destination_state=STATE_VERIFY_EXIT,
            approver="agent-self",
            actor="agent",
            reason="attempting to bypass WORKTREE_REVIEW",
            expected_source_state=STATE_IN_WORKTREE,
        )

    # Layer 2 (defense-in-depth): even a hand-crafted decision row bypassing the
    # Python-level guard entirely must not satisfy the trigger's recovery bypass for
    # this destination -- the trigger's own recovery_td clause independently excludes
    # RECOVERY_FORBIDDEN_DESTINATIONS.
    conn = sqlite3.connect(db_path)
    last_transition_id = conn.execute(
        "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
        (task_id,),
    ).fetchone()[0]
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at, consumed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (task_id, last_transition_id, STATE_IN_WORKTREE, STATE_VERIFY_EXIT,
         "forged_recovery_approval", "FORGED-TOKEN", "APPROVAL", "human", 0.0),
    )
    conn.commit()
    conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (STATE_VERIFY_EXIT, task_id))
    conn.commit()
    final_state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]
    violation_count = conn.execute(
        "SELECT COUNT(*) FROM transition_violations WHERE task_id = ? AND attempted_to_state = ?",
        (task_id, STATE_VERIFY_EXIT),
    ).fetchone()[0]
    conn.close()

    assert final_state == STATE_IN_WORKTREE, (
        f"Task must remain in IN_WORKTREE -- a forged recovery decision row must not "
        f"permit reaching VERIFY_EXIT, but final state was '{final_state}'."
    )
    assert violation_count >= 1, "The forged attempt must be logged as a trigger-reverted violation."
