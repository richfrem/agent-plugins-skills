"""Task 5 contract tests for advisory, registry-derived transition guidance."""

import io
import pytest
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.coordinator import TransitionCoordinator
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS
from agent_control import ControlPlane


EXECUTION_GUIDANCE_UNITS = {
    "work_package",
    "task",
    "slice",
    "transition",
    "execution_step",
}
EXECUTION_GUIDANCE_FIELDS = {
    "objective",
    "scope_boundary",
    "prerequisites",
    "authority",
    "expected_artifacts",
    "validation_command",
    "completion_evidence",
    "handoff_condition",
    "failure_recovery",
}


@pytest.fixture
def control_plane(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.init_db()
    return control_plane


def test_guidance_derives_legal_next_states_and_exposes_versioned_snapshot(control_plane):
    task_id = "guidance-derived-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id)

    assert guidance["advisory"] is True
    assert guidance["registry_version"]
    assert guidance["current_state"] == "INTAKE"
    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS["INTAKE"]
    assert {edge["to_state"] for edge in guidance["transitions"]} == set(ALLOWED_TRANSITIONS["INTAKE"])
    assert all(edge["command"].startswith("python3 ") for edge in guidance["transitions"])
    interview = next(edge for edge in guidance["transitions"] if edge["to_state"] == "INTERVIEW")
    assert any("log-prior-art" in helper for helper in interview["helper_commands"])


def test_guidance_cannot_authorize_illegal_requested_edge(control_plane):
    task_id = "guidance-denial-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id, requested_to_state="DONE")

    assert guidance["advisory"] is True
    assert guidance["legal"] is False
    assert guidance["command"] is None
    assert guidance["denial_guidance"]
    assert guidance["recovery_states"] == ALLOWED_TRANSITIONS["INTAKE"]


def test_done_guidance_names_retrospective_recording_protocol(control_plane):
    task_id = "guidance-retrospective-001"
    control_plane.create_task(task_id=task_id, title="Retrospective guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()
    template = registry.get_template("RETROSPECTIVE", "DONE")

    assert template is not None
    hint = template.next_steps_hint.lower()
    assert "record_retrospective" in hint
    assert "before" in hint and "done" in hint
    assert "defaults are not inferred" in hint


def test_standard_path_hints_name_each_operational_handoff(control_plane):
    registry = TransitionRegistry.load_default()
    expected = {
        ("INTERVIEW", "DRAFT_PLAN"): ("record-plan-mode-entry", "verify-interview-question"),
        ("DRAFT_PLAN", "MULTI_AGENT_REVIEW"): ("plan artifacts", "coordinate-transition"),
        ("DRAFT_PLAN", "AWAITING_APPROVAL"): ("record-critic-review", "record-review-skip"),
        ("APPROVED", "IN_WORKTREE"): ("record-human-approval", "worktree"),
        ("VERIFY_EXIT", "RETROSPECTIVE"): ("test_suite", "leak_check", "references/map-debt.md"),
    }
    for edge, markers in expected.items():
        template = registry.get_template(*edge)
        assert template is not None
        hint = template.next_steps_hint.lower()
        assert all(marker.lower() in hint for marker in markers), (edge, hint)


def test_worktree_review_exit_hint_explains_skip_branch_and_human_question_boundary():
    registry = TransitionRegistry.load_default()
    template = registry.get_template("WORKTREE_REVIEW", "VERIFY_EXIT")

    assert template is not None
    hint = template.next_steps_hint.lower()
    assert "no additional human question is required" in hint
    assert "--skip-review" in hint
    assert "--skip-reason" in hint
    assert "multi_agent_code_review" in hint


def test_stale_yaml_next_state_claim_is_ignored_for_guidance_legality(control_plane):
    task_id = "guidance-stale-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()
    control_plane._transition_registry = registry
    registry.get_template("INTAKE", "INTERVIEW").guidance["legal_next_states"] = ["DONE"]

    guidance = control_plane.get_transition_guidance(task_id)

    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS["INTAKE"]
    assert "DONE" not in guidance["legal_next_states"]


def test_coordinator_surfaces_advisory_guidance_before_and_after_transition(control_plane):
    task_id = "guidance-output-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    output = io.StringIO()
    coordinator = TransitionCoordinator(control_plane, output_stream=output)

    coordinator._write_transition_guidance("INTAKE", "INTERVIEW", phase="before")
    coordinator._write_next_steps_hint("INTAKE")

    rendered = output.getvalue()
    assert "Advisory transition guidance" in rendered
    assert "registry version" in rendered
    assert "INTAKE -> INTERVIEW" in rendered
    assert "advisory only" in rendered.lower()
    assert "Next possible transitions from INTAKE" in rendered


def test_coordinator_renders_execution_unit_guidance(control_plane):
    """The model-facing transition report includes task execution guidance."""
    output = io.StringIO()
    coordinator = TransitionCoordinator(control_plane, output_stream=output)

    coordinator._write_transition_guidance("INTAKE", "INTERVIEW", phase="before")

    rendered = output.getvalue()
    assert "Execution-unit guidance (advisory)" in rendered
    assert "work_package" in rendered
    assert "task" in rendered
    assert "slice" in rendered
    assert "execution_step" in rendered


def test_guidance_exposes_advisory_execution_unit_contract(control_plane):
    """Every transition snapshot explains how to execute the work around it."""
    task_id = "guidance-execution-units-001"
    control_plane.create_task(task_id=task_id, title="Execution guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id)
    execution = guidance["execution_guidance"]

    assert set(execution) == EXECUTION_GUIDANCE_UNITS
    for unit_name, unit in execution.items():
        assert unit["advisory"] is True, unit_name
        assert set(unit["required_fields"]) == EXECUTION_GUIDANCE_FIELDS, unit_name
        assert unit["instruction"], unit_name


def test_each_edge_guidance_carries_execution_unit_contract():
    """Edge guidance and execution guidance must be rendered from one snapshot."""
    registry = TransitionRegistry.load_default()

    for template in registry.get_all_templates():
        snapshot = registry.get_transition_guidance(template.from_state, template.to_state)
        assert set(snapshot["execution_guidance"]) == EXECUTION_GUIDANCE_UNITS
