"""
tests/test_done_closure_proof.py
================================

Purpose:
    Failing-first acceptance tests for the third human-authority gate (auth-ciba-increment-b, human decision
    2026-09-20): ONLY A HUMAN CAN TRANSITION TO DONE, by the same cryptographic mechanism as APPROVED and
    VERIFY_EXIT. Every edge into DONE -- the force-close/force-done edges from any state and the normal
    RETROSPECTIVE -> DONE completion -- halts with HUMAN_PROOF_REQUIRED and a request_id in strict mode; a
    prompt, `--force-close`/FORCE_DONE flags or an interactive session cannot authorize it. The challenge
    binds task, edge, occupancy, nonce, expiry and the closing content (worktree commit/diff/untracked hashes,
    plus the recorded retrospective decision and digest for normal completion); only a verified
    `ssh-keygen -Y sign` signature consumed in the commit transaction reaches DONE. Real git, SQLite and
    ssh-keygen; nothing mocked.

Key Input Dependencies:
    - control_plane/proof_edges.py (DONE snapshot), ssh_signing.py (assertions_for_edge), coordinator.py,
      adapters.py (get_retrospective_summary), gate1_approval.py
    - tests/test_gate3_code_acceptance.py (CodeGate fixture)

Key Functions (test cases):
    - test_force_done_edges_halt_for_a_signature_even_for_an_interactive_human
    - test_a_signature_closes_the_task_from_a_force_done_edge
    - test_a_changed_worktree_refuses_a_closure_and_audits
    - test_retrospective_completion_needs_a_signature
    - test_every_edge_into_done_approved_and_verify_exit_is_proof_required
"""

import io
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.coordinator import HumanProofRequired, TransitionCoordinator
from control_plane.gate1_approval import GateApprovalError
from control_plane.registry import TransitionRegistry
from test_gate3_code_acceptance import DIRECT, POST_REVIEW, TASK, CodeGate


pytestmark = pytest.mark.no_auto_signer


@pytest.fixture(params=[DIRECT, POST_REVIEW], ids=["from-worktree-review", "from-code-review"])
def gate(request, tmp_path):
    return CodeGate(tmp_path, request.param)


def _request_done(gate, **kwargs):
    with pytest.raises(HumanProofRequired) as excinfo:
        gate.coordinator().coordinate_transition(task_id=TASK, to_state="DONE", reason="close", **kwargs)
    gate.request_id = excinfo.value.remediation["request_id"]


def test_force_done_edges_halt_for_a_signature_even_for_an_interactive_human(gate):
    _request_done(gate, actor="agent", interactive=False)
    assert gate.state() == gate.edge[0]
    with pytest.raises(HumanProofRequired):  # an interactive human WITHOUT a signer still cannot close by prompt alone
        gate.coordinator().coordinate_transition(task_id=TASK, to_state="DONE", actor="human", reason="close", interactive=True)
    assert gate.state() == gate.edge[0]
    # the force-close entry points are gone
    import inspect
    assert "force_close" not in inspect.signature(TransitionCoordinator.coordinate_transition).parameters


def test_a_signature_closes_the_task_from_a_force_done_edge(gate):
    _request_done(gate, actor="agent", interactive=False)
    path, printed = gate.show()
    assert "approves: " in printed and "head:" in printed and "FORCE" not in printed
    gate.sign(path)
    record = gate.approve()
    assert record.to_state == "DONE" and gate.state() == "DONE"
    assert gate.db().execute("SELECT COUNT(*) FROM transition_decisions WHERE task_id = ? AND to_state = 'DONE'", (TASK,)).fetchone()[0] == 0


def test_a_changed_worktree_refuses_a_closure_and_audits(gate):
    _request_done(gate, actor="agent", interactive=False)
    path, _ = gate.show()
    gate.sign(path)
    (gate.worktree / "module.py").write_text("VALUE = 42\n")
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == gate.edge[0] and gate.violations()


def test_retrospective_completion_needs_a_signature(tmp_path):
    """Normal completion (RETROSPECTIVE -> DONE) is signed too: an agent cannot complete a task, and the challenge binds
    the recorded retrospective decision and digest."""
    from control_plane.gate1_approval import show_challenge
    from control_plane.pipeline_simulator import PipelineSimulator
    from helpers.human_signer import get_test_human

    task = "retro-done-001"
    sim = PipelineSimulator(tmp_path / "control_plane.db", registry=TransitionRegistry.load_default())
    sim.create_task(task, "retrospective closure")
    sim.control_plane.repo_root = (tmp_path / "repo").resolve()
    sim.control_plane.repo_root.mkdir()
    sim.run_trivial_interview_fast_track(task)
    cp = sim.control_plane
    cp.save_retrospective(task, {"decision": "opt_in", "completion_mode": "completed", "actor": "human", "outcome": "ok"}, [])
    for gate_name in ("test_suite", "full_test_suite"):
        cp.record_verification_receipt(task, gate_name, "pytest", 0)
    strict = TransitionCoordinator(cp, registry=sim.registry, output_stream=io.StringIO())
    with pytest.raises(HumanProofRequired) as excinfo:
        strict.coordinate_transition(task_id=task, to_state="DONE", actor="agent", reason="complete", interactive=False)
    request_id = excinfo.value.remediation["request_id"]
    assert cp._persistence.read_current_state(task) == "RETROSPECTIVE"
    human = get_test_human()
    layout = human.ensure_identity(cp.repo_root)
    out = io.StringIO()
    show_challenge(cp, request_id, layout=layout, key_hint=str(human.key), agent_identity=human.agent_identity, out=out)
    assert "retrospective_decision: complete" in out.getvalue() and "retrospective: " in out.getvalue()
    record = human.sign_request(cp, request_id)
    assert record.to_state == "DONE" and cp._persistence.read_current_state(task) == "DONE"


def test_every_edge_into_done_approved_and_verify_exit_is_proof_required():
    """The YAML is the single source of truth: every edge into DONE, every edge from AWAITING_APPROVAL into APPROVED
    and both review edges into VERIFY_EXIT declare requires_cryptographic_proof, with no soft question, approval prompt,
    skip or actor-string surrogate on them."""
    registry = TransitionRegistry.load_default()
    proof_edges = registry.proof_required_edges()
    expected = {
        edge for edge in registry._templates_by_edge
        if edge[1] == "DONE"
        or edge == ("AWAITING_APPROVAL", "APPROVED")
        or edge in (("WORKTREE_REVIEW", "VERIFY_EXIT"), ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"))
    }
    assert expected and expected == set(proof_edges) & expected and proof_edges == expected
    for edge in proof_edges:
        template = registry.get_template(*edge)
        assert template.human_questions == [] and not template.stage_question_ids, edge
        assert template.approval.get("required") is False and template.skip.get("allowed") is False, edge
        assert template.authorized_actor == "human_only", edge
