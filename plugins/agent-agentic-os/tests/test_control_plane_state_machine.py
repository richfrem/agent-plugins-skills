"""
test_control_plane_state_machine.py — State-Machine Domain Extraction (issue-524)
=====================================================================================

Purpose:
    Unit tests for control_plane/state_machine.py's StateMachine in complete isolation — no
    SQLite, no ControlPlane — proving state-machine validation (known-state check + adjacency
    legality) is genuinely independently testable domain logic. Added after external
    post-implementation review (round 2) found this validation still embedded directly in
    ControlPlane.transition(), contradicting the plan's declared "state-machine validation"
    separation. Also includes an integration test proving ControlPlane.transition() actually
    delegates to self._state_machine rather than reimplementing the checks inline.

Key Input Dependencies:
    None — pure in-memory StateMachine instance.

Key Functions:
    - test_validate_known_state_rejects_unknown_state()
    - test_validate_known_state_accepts_every_canonical_state()
    - test_validate_adjacency_rejects_illegal_edge()
    - test_validate_adjacency_accepts_every_legal_edge()
    - test_control_plane_transition_delegates_to_state_machine()
"""

import io
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.state_machine import StateMachine, CANONICAL_STATES, ALLOWED_TRANSITIONS, InvalidStateTransition
from control_plane.registry import TransitionRegistry
from control_plane.constants import (
    STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE, STATE_ROLLED_BACK, STATE_ESCALATED,
)


def test_validate_known_state_rejects_unknown_state():
    sm = StateMachine()
    with pytest.raises(InvalidStateTransition, match="Unknown state: NOT_A_REAL_STATE"):
        sm.validate_known_state("NOT_A_REAL_STATE")


def test_validate_known_state_accepts_every_canonical_state():
    sm = StateMachine()
    for state in CANONICAL_STATES:
        sm.validate_known_state(state)  # must not raise


def test_validate_adjacency_rejects_illegal_edge():
    # DONE -> INTAKE is now the deliberate reset_to_intake recovery edge (added
    # for control-plane-reset-transition) — no longer illegal, so it can't be
    # used as the illegal-edge example here. DONE -> WORKTREE_REVIEW remains
    # illegal (DONE is still terminal except for the one explicit reset edge).
    sm = StateMachine()
    with pytest.raises(InvalidStateTransition, match="Cannot transition task 't1' from 'DONE' to 'WORKTREE_REVIEW'"):
        sm.validate_adjacency("t1", STATE_DONE, STATE_WORKTREE_REVIEW)


def test_validate_adjacency_accepts_every_legal_edge():
    sm = StateMachine()
    for from_state, to_states in ALLOWED_TRANSITIONS.items():
        for to_state in to_states:
            sm.validate_adjacency("t1", from_state, to_state)  # must not raise


def test_human_recovery_target_is_not_limited_by_normal_dag():
    sm = StateMachine()
    sm.validate_recovery_target("t1", STATE_DONE, STATE_IN_WORKTREE)
    with pytest.raises(InvalidStateTransition, match="must differ"):
        sm.validate_recovery_target("t1", STATE_DONE, STATE_DONE)


def test_human_recovery_from_done_to_worktree_requires_and_consumes_approval(tmp_path):
    from agent_control import ControlPlane

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="recovery-done-1", title="Reopen", runtime_tool="claude")
    cp.coordinate_transition("recovery-done-1", STATE_DONE, "human", "Close fixture", interactive=True)  # signed close

    token = cp.record_recovery_approval(
        "recovery-done-1", STATE_IN_WORKTREE, "human", actor="human",
        reason="Missed implementation fix requires rework",
    )
    record = cp.apply_recovery_transition(
        "recovery-done-1", STATE_IN_WORKTREE, token, "human", "Reopen for bounded rework"
    )

    assert record.from_state == STATE_DONE
    assert record.to_state == STATE_IN_WORKTREE
    assert cp.get_task("recovery-done-1")["state"] == STATE_IN_WORKTREE

def test_every_non_done_state_has_a_signed_closure_edge():
    for state in CANONICAL_STATES:
        if state != STATE_DONE:
            assert STATE_DONE in ALLOWED_TRANSITIONS[state]


@pytest.mark.no_auto_signer
def test_direct_agent_close_is_refused_without_an_openssh_signature(tmp_path):
    """auth-ciba-increment-b: closing a task is a cryptographic gate. An agent (or anyone) calling the facade
    without a signed transition_request fails closed: the state does not move."""
    from agent_control import ControlPlane
    from control_plane.coordinator import HumanProofRequired

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="force-1", title="Close", runtime_tool="claude")
    with pytest.raises((HumanProofRequired, Exception)) as excinfo:
        cp.transition("force-1", STATE_DONE, "agent", "close now")
    assert "signature" in str(excinfo.value).lower() or "HUMAN_PROOF_REQUIRED" in str(excinfo.value)
    assert cp.get_task("force-1")["state"] == STATE_INTAKE


def test_the_force_close_bypass_parameters_no_longer_exist(tmp_path):
    """The force_close / human_authorization keyword bypass was removed; passing it is a TypeError, not a
    quiet fallback, on both the coordinator and the ControlPlane facade."""
    from agent_control import ControlPlane
    from control_plane.coordinator import TransitionCoordinator

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task("force-kw", "Close", "claude")
    with pytest.raises(TypeError, match="force_close"):
        TransitionCoordinator(cp).coordinate_transition(
            "force-kw", STATE_DONE, "human", "close", force_close=True, human_authorization="FORCE_CLOSE", interactive=True,
        )
    with pytest.raises(TypeError, match="force_close"):
        cp.coordinate_transition(
            "force-kw", STATE_DONE, "human", "close", force_close=True, human_authorization="FORCE_CLOSE", interactive=True,
        )
    assert cp.get_task("force-kw")["state"] == STATE_INTAKE


@pytest.mark.no_auto_signer
@pytest.mark.parametrize("typed", ["FORCE_CLOSE", "FORCE_DONE", "YES", "1"])
def test_a_typed_word_at_an_interactive_prompt_cannot_close_a_task(tmp_path, typed):
    """Even a real interactive terminal and the old magic words do nothing without a signature: the coordinator
    halts with HUMAN_PROOF_REQUIRED and the task does not move."""
    from agent_control import ControlPlane
    from control_plane.coordinator import HumanProofRequired, TransitionCoordinator

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task("force-typed", "Close", "claude")
    prompts = []
    coord = TransitionCoordinator(cp, input_fn=lambda p: prompts.append(p) or typed, output_stream=io.StringIO())
    with pytest.raises(HumanProofRequired):
        coord.coordinate_transition("force-typed", STATE_DONE, "human", "close", interactive=True)
    assert cp.get_task("force-typed")["state"] == STATE_INTAKE
    assert prompts == []  # nothing was offered as an authorizing prompt


@pytest.mark.no_auto_signer
def test_a_noninteractive_human_actor_string_cannot_close_a_task(tmp_path):
    from agent_control import ControlPlane
    from control_plane.coordinator import HumanProofRequired

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task("force-spoof", "Close", "claude")
    with pytest.raises(HumanProofRequired):
        cp.coordinate_transition("force-spoof", STATE_DONE, "human", "close", interactive=False)
    assert cp.get_task("force-spoof")["state"] == STATE_INTAKE


def test_a_signed_close_persists_from_any_state(tmp_path):
    """The positive path: with the (test) human signing the real request, closure commits."""
    from agent_control import ControlPlane

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="force-2", title="Close", runtime_tool="claude")
    record = cp.coordinate_transition("force-2", STATE_DONE, "human", "Emergency close", interactive=True)
    assert record.from_state == STATE_INTAKE
    assert cp.get_task("force-2")["state"] == STATE_DONE
    assert cp._persistence.get_last_transition("force-2").to_state == STATE_DONE


def test_every_non_done_state_exposes_a_proof_gated_closure_edge():
    """Closure is legal from every non-terminal state, and every such edge is cryptographic: it declares
    requires_cryptographic_proof, authority type cryptographic_proof, and no FORCE_* accepted-answer question."""
    registry = TransitionRegistry.load_default()
    proof_edges = registry.proof_required_edges()
    for state in CANONICAL_STATES:
        if state == STATE_DONE:
            continue
        assert STATE_DONE in ALLOWED_TRANSITIONS[state]
        template = registry.get_template(state, STATE_DONE)
        assert template is not None
        assert (state, STATE_DONE) in proof_edges
        assert template.authority.get("type") == "cryptographic_proof"
        for question in template.human_questions:
            assert not {"FORCE_DONE", "FORCE_CLOSE"} & set(question.get("accepted_answers", []))


def test_signed_close_reaches_done_from_every_nonterminal_state(tmp_path):
    """Exercise every closure source edge through the coordinator, real SQLite and the real (test) signer."""
    from agent_control import ControlPlane
    from control_plane.coordinator import TransitionCoordinator
    from helpers.gate1_fixtures import init_git_worktree

    paths = {
        STATE_INTAKE: [],
        STATE_INTERVIEW: [STATE_INTERVIEW],
        STATE_DRAFT_PLAN: [STATE_INTERVIEW, STATE_DRAFT_PLAN],
        STATE_PLAN_REVIEW: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW],
        STATE_MULTI_AGENT_REVIEW: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_MULTI_AGENT_REVIEW],
        STATE_AWAITING_APPROVAL: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL],
        STATE_APPROVED: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED],
        STATE_IN_WORKTREE: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE],
        STATE_WORKTREE_REVIEW: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW],
        STATE_MULTI_AGENT_CODE_REVIEW: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_MULTI_AGENT_CODE_REVIEW],
        STATE_VERIFY_EXIT: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT],
        # RETROSPECTIVE is closed by retrospective_to_done, which adds retrospective_done_guard and the full-suite
        # receipt on top of the signature; those guards are covered by test_transition_guidance / test_agent_control.
        STATE_ROLLED_BACK: [STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_ROLLED_BACK],
        STATE_ESCALATED: [STATE_ESCALATED],
    }
    registry = TransitionRegistry.load_default()

    for state, path in paths.items():
        # <repo>/context/control_plane.db makes tmp the repo root, so the dirty-main check does not inspect the real checkout
        (tmp_path / state.lower() / "context").mkdir(parents=True)
        control_plane = ControlPlane(db_path=tmp_path / state.lower() / "context" / "control_plane.db")
        control_plane.init_db()
        task_id = f"close-{state.lower()}"
        control_plane.create_task(task_id, "Closure simulation", "simulator")
        current = STATE_INTAKE
        for next_state in path:
            template = registry.get_template(current, next_state)
            assert template is not None
            source_transition = control_plane._persistence.get_last_transition(task_id)
            question_ids = list(template.stage_question_ids or [])
            question_ids += [question["question_id"] for question in template.human_questions]
            if template.approval.get("required") and template.approval.get("approver_role", "human") == "human":
                question_ids.append(f"approval_{template.transition_id}")
            for question_id in question_ids:
                control_plane.record_decision(
                    task_id, source_transition.transition_id, current, next_state,
                    question_id, "SIMULATED_HUMAN_CONFIRMATION", actor="human",
                )
            if (current, next_state) in registry.proof_required_edges():
                # a cryptographic gate: setup walks it through the real signed flow, never a direct persistence write
                if next_state == STATE_VERIFY_EXIT:
                    control_plane.update_worktree(task_id, str(init_git_worktree(tmp_path / f"wt-{task_id}")), f"sim/{task_id}", "written_in_worktree")
                control_plane.coordinate_transition(task_id, next_state, "human", f"legal setup for {state}", interactive=True)
            else:
                assert control_plane._persistence.apply_transition(
                    task_id, current, next_state, "simulator", f"legal setup for {state}"
                )
            current = next_state

        record = TransitionCoordinator(control_plane, registry=registry, output_stream=io.StringIO()).coordinate_transition(
            task_id, STATE_DONE, "human", f"Signed close from {state}", interactive=True,
        )
        assert (record.from_state, record.to_state) == (state, STATE_DONE)
        assert control_plane.get_task(task_id)["state"] == STATE_DONE


def test_control_plane_transition_delegates_to_state_machine(tmp_path, monkeypatch):
    """Integration: ControlPlane.transition() calls self._state_machine.validate_known_state()
    and validate_adjacency() rather than checking CANONICAL_STATES/ALLOWED_TRANSITIONS inline —
    proven by monkeypatching StateMachine to record calls and confirm they happened."""
    from agent_control import ControlPlane

    calls = []
    original_validate_known = StateMachine.validate_known_state
    original_validate_adjacency = StateMachine.validate_adjacency

    def recording_validate_known(self, to_state):
        calls.append(("validate_known_state", to_state))
        return original_validate_known(self, to_state)

    def recording_validate_adjacency(self, task_id, current_state, to_state):
        calls.append(("validate_adjacency", task_id, current_state, to_state))
        return original_validate_adjacency(self, task_id, current_state, to_state)

    monkeypatch.setattr(StateMachine, "validate_known_state", recording_validate_known)
    monkeypatch.setattr(StateMachine, "validate_adjacency", recording_validate_adjacency)

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task(task_id="t1", title="State Machine Delegation Task", runtime_tool="claude")
    cp.transition(task_id="t1", to_state=STATE_INTERVIEW, actor="user", reason="test")

    assert ("validate_known_state", STATE_INTERVIEW) in calls
    assert ("validate_adjacency", "t1", STATE_INTAKE, STATE_INTERVIEW) in calls
