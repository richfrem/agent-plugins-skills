"""Production-boundary contracts for the deterministic control-plane simulator."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.coordinator import TransitionCoordinatorError
from control_plane.state_machine import ALLOWED_TRANSITIONS, InvalidStateTransition


def test_simulator_runs_trivial_interview_fast_track_against_temporary_sqlite(tmp_path):
    simulator = PipelineSimulator(tmp_path / "simulator.db")
    task_id = simulator.create_task("trivial-001", "Trivial simulator path")

    report = simulator.run_trivial_interview_fast_track(task_id)

    assert report["states"] == ["INTAKE", "INTERVIEW", "RETROSPECTIVE"]
    assert report["db_path"] == str((tmp_path / "simulator.db").resolve())
    assert not (Path.cwd() / "context" / "control_plane.db").exists() or simulator.db_path != Path.cwd() / "context" / "control_plane.db"


def test_simulator_exercises_standard_interview_enforcement(tmp_path):
    simulator = PipelineSimulator(tmp_path / "standard.db")
    task_id = simulator.create_task("standard-001", "Standard simulator path")
    simulator.enter_interview(task_id)

    with pytest.raises(TransitionCoordinatorError, match="interview_classification"):
        simulator.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD")

    simulator.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
    record = simulator.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD")
    assert record.to_state == "DRAFT_PLAN"


def test_simulator_coverage_is_derived_from_live_registry(tmp_path):
    simulator = PipelineSimulator(tmp_path / "coverage.db")

    coverage = simulator.edge_scenario_coverage()
    expected = {
        (from_state, to_state)
        for from_state, to_states in ALLOWED_TRANSITIONS.items()
        for to_state in to_states
    }

    assert set(coverage) == expected
    assert all(coverage[edge]["transition_id"] for edge in expected)
    assert all("human_questions" in coverage[edge] for edge in expected)


def test_simulator_rejects_illegal_edge_through_production_control_plane(tmp_path):
    simulator = PipelineSimulator(tmp_path / "illegal.db")
    task_id = simulator.create_task("illegal-001", "Illegal simulator path")

    with pytest.raises(InvalidStateTransition):
        simulator.control_plane.transition(task_id, "VERIFY_EXIT", "simulator", "illegal edge")


def test_simulator_exercises_reset_wildcard_with_interactive_approval(tmp_path):
    simulator = PipelineSimulator(tmp_path / "reset.db")
    task_id = simulator.create_task("reset-001", "Reset simulator path")
    simulator.enter_interview(task_id)

    record = simulator.reset_to_intake(task_id)

    assert record.from_state == "INTERVIEW"
    assert record.to_state == "INTAKE"
    assert simulator.control_plane._persistence.read_current_state(task_id) == "INTAKE"


def test_simulator_reports_isolation_contract(tmp_path):
    simulator = PipelineSimulator(tmp_path / "isolation.db")
    report = simulator.isolation_report()

    assert report["database"] == str((tmp_path / "isolation.db").resolve())
    assert report["uses_repository_database"] is False
    assert report["uses_git_or_subprocess"] is False
    assert report["uses_worktree"] is False


def test_simulator_can_play_reproducible_adversarial_rounds(tmp_path):
    simulator = PipelineSimulator(tmp_path / "game.db")

    rounds = simulator.play_adversarial_rounds("game")

    assert [round_["name"] for round_ in rounds] == [
        "incomplete_interview",
        "wrong_trivial_route",
        "illegal_edge",
        "trivial_fast_track",
        "reset_recovery",
    ]
    assert all(round_["state_preserved"] for round_ in rounds[:3])
    assert rounds[3]["after_state"] == "RETROSPECTIVE"
    assert rounds[4]["after_state"] == "INTAKE"
    assert all(round_["no_orphan_transition"] for round_ in rounds)


def test_simulator_can_play_one_named_round(tmp_path):
    simulator = PipelineSimulator(tmp_path / "one-round.db")

    round_ = simulator.play_round("incomplete_interview", "one")

    assert round_["result"] == "DENIED_AS_EXPECTED"
    assert "interview_classification" in round_["error"]
    assert round_["state_preserved"] is True
    assert round_["no_orphan_transition"] is True
    assert round_["no_orphan_decision"] is True
    assert round_["no_orphan_receipt"] is True


def test_simulator_replays_standard_happy_path_to_done(tmp_path):
    simulator = PipelineSimulator(tmp_path / "standard-happy.db")
    task_id = simulator.create_task("standard-happy-001", "Standard happy path")

    report = simulator.run_standard_happy_path(task_id)

    assert report["states"][0] == "INTAKE"
    assert report["states"][-1] == "DONE"
    assert simulator.control_plane._persistence.read_current_state(task_id) == "DONE"


def test_standard_happy_path_routes_lifecycle_edges_through_coordinator(tmp_path, monkeypatch):
    simulator = PipelineSimulator(tmp_path / "coordinator-boundary.db")
    task_id = simulator.create_task("coordinator-boundary-001", "Coordinator boundary")

    def forbidden_raw_transition(*_args, **_kwargs):
        raise AssertionError("standard simulator must use TransitionCoordinator for lifecycle edges")

    monkeypatch.setattr(simulator.control_plane, "transition", forbidden_raw_transition)

    report = simulator.run_standard_happy_path(task_id)

    assert report["states"][-1] == "DONE"
