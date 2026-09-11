import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.implementation_loop import (
    ImplementationController,
    PersistentTaskQueue,
    run_implementation_session,
)


def test_revise_automatically_dispatches_fix_and_next_review():
    calls = []

    def dispatch(round_number):
        calls.append(("dispatch", round_number))
        return f"artifact-{round_number}"

    def review(round_number, artifact):
        calls.append(("review", round_number, artifact))
        return ("REVISE", "missing evidence") if round_number == 1 else ("PASS", "clean")

    def fix(round_number, artifact, findings):
        calls.append(("fix", round_number, artifact, findings))
        return "fix-1"

    events = run_implementation_session(dispatch, review, fix)
    assert [event.kind for event in events] == [
        "DISPATCHED", "REVIEWED", "FIX_DISPATCHED", "DISPATCHED", "REVIEWED", "COMPLETE"
    ]
    assert calls[4] == ("review", 2, "artifact-2")


def test_loop_stops_with_visible_blocker_at_round_bound():
    events = run_implementation_session(
        lambda round_number: "artifact",
        lambda round_number, artifact: ("REVISE", "still incomplete"),
        lambda round_number, artifact, findings: "fix",
        max_rounds=2,
    )
    assert events[-1].kind == "BLOCKED"
    assert "exhausted" in events[-1].detail


def test_loop_never_calls_pipeline_transition_callback():
    transitions = []
    events = run_implementation_session(
        lambda round_number: "artifact",
        lambda round_number, artifact: ("PASS", "clean"),
        lambda round_number, artifact, findings: "unused",
    )
    transitions.extend(event.kind for event in events if "TRANSITION" in event.kind)
    assert transitions == []


def test_controller_persists_queue_and_progresses_without_prompt(tmp_path):
    queue_path = tmp_path / "implementation-queue.json"
    queue = PersistentTaskQueue(queue_path)
    queue.enqueue("one", {"scope": "slice"})
    calls = []

    def dispatch(round_number, task):
        calls.append(("dispatch", task["id"], round_number))
        return "artifact"

    def review(round_number, task, artifact):
        calls.append(("review", task["id"], round_number))
        return ("PASS", "clean")

    controller = ImplementationController(queue, dispatch, review, heartbeat_path=tmp_path / "heartbeat.json")
    events = controller.run()

    assert [event.kind for event in events][-2:] == ["COMPLETE", "EXIT_VERIFICATION"]
    assert json.loads(queue_path.read_text())[0]["status"] == "complete"
    assert json.loads((tmp_path / "heartbeat.json").read_text())["event"] == "EXIT_VERIFICATION"
    assert calls == [("dispatch", "one", 1), ("review", "one", 1)]


def test_controller_requeues_fix_round_without_prompt(tmp_path):
    queue = PersistentTaskQueue(tmp_path / "queue.json")
    queue.enqueue("one")
    calls = []
    controller = ImplementationController(
        queue,
        lambda round_number, task: calls.append(("dispatch", round_number)) or f"artifact-{round_number}",
        lambda round_number, task, artifact: calls.append(("review", round_number))
        or (("REVISE", "evidence") if round_number == 1 else ("PASS", "clean")),
        lambda round_number, task, artifact, findings: calls.append(("fix", round_number)) or "fixed",
    )
    controller.run()
    assert calls == [("dispatch", 1), ("review", 1), ("fix", 1), ("dispatch", 2), ("review", 2)]


def test_controller_watchdog_blocks_stale_runner(tmp_path):
    now = [100.0]
    queue = PersistentTaskQueue(tmp_path / "queue.json")
    queue.enqueue("one")
    controller = ImplementationController(
        queue, lambda round_number, task: "artifact", lambda round_number, task, artifact: ("PASS", ""),
        heartbeat_path=tmp_path / "heartbeat.json", clock=lambda: now[0], watchdog_timeout=5,
    )
    controller.heartbeat()
    now[0] = 106.0
    events = controller.run()
    assert events[-1].kind == "BLOCKED"
    assert "heartbeat" in events[-1].detail


def test_controller_stops_at_exit_gate_and_never_transitions(tmp_path):
    queue = PersistentTaskQueue(tmp_path / "queue.json")
    queue.enqueue("one")
    transitions = []
    controller = ImplementationController(
        queue, lambda round_number, task: "artifact", lambda round_number, task, artifact: ("PASS", ""),
        exit_verification=lambda: transitions.append("exit") or True,
    )
    events = controller.run()
    assert transitions == ["exit"]
    assert [event.kind for event in events].count("EXIT_VERIFICATION") == 1
    assert all("TRANSITION" not in event.kind for event in events)
