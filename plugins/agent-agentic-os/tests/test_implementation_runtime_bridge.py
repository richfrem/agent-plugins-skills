import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from agent_control import ControlPlane
from control_plane.ports import TransitionCommitRequest, TransitionRecord


class FakePersistence:
    def __init__(self):
        self.receipts = []

    def apply_transition_with_receipts(self, request):
        return TransitionRecord(1, request.task_id, request.expected_from_state, request.to_state, request.actor, request.reason, "now")

    def has_receipt(self, task_id, gate_name):
        return any(r[0] == task_id and r[1] == gate_name for r in self.receipts)

    def insert_verification_receipt(self, task_id, gate_name, command, exit_code, token):
        self.receipts.append((task_id, gate_name, command, exit_code, token))


def _request(to_state="IN_WORKTREE"):
    return TransitionCommitRequest("task-1", "APPROVED", to_state, 1, "edge", "controller", "ready", [], [])


def test_approved_to_worktree_persists_kickoff_and_invokes_controller_once():
    persistence = FakePersistence()
    calls = []
    cp = ControlPlane(persistence_adapter=persistence, implementation_controller=lambda task_id, record: calls.append((task_id, record)))

    record = cp.commit_authorized_transition(_request())

    assert calls == [("task-1", record)]
    assert [r[1] for r in persistence.receipts] == ["implementation_kickoff"]


def test_other_transition_does_not_kickoff():
    persistence = FakePersistence()
    calls = []
    cp = ControlPlane(persistence_adapter=persistence, implementation_controller=lambda *args: calls.append(args))

    cp.commit_authorized_transition(_request("WORKTREE_REVIEW"))

    assert calls == []
    assert persistence.receipts == []


def test_replayed_worktree_entry_does_not_duplicate_kickoff():
    persistence = FakePersistence()
    calls = []
    cp = ControlPlane(persistence_adapter=persistence, implementation_controller=lambda *args: calls.append(args))
    cp.commit_authorized_transition(_request())
    cp.commit_authorized_transition(_request())

    assert len(calls) == 1
    assert len(persistence.receipts) == 1


def test_kickoff_error_is_visible():
    persistence = FakePersistence()

    def fail(*args):
        raise RuntimeError("controller unavailable")

    cp = ControlPlane(persistence_adapter=persistence, implementation_controller=fail)

    with pytest.raises(RuntimeError, match="controller unavailable"):
        cp.commit_authorized_transition(_request())
