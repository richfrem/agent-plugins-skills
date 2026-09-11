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

    guidance = control_plane.get_transition_guidance(task_id, requested_to_state="WORKTREE_REVIEW")

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
        ("DRAFT_PLAN", "PLAN_REVIEW"): ("plan artifacts", "coordinate-transition"),
        ("PLAN_REVIEW", "MULTI_AGENT_REVIEW"): ("plan_review_method", "coordinate-transition"),
        ("PLAN_REVIEW", "AWAITING_APPROVAL"): ("record-critic-review", "record-review-skip"),
        ("APPROVED", "IN_WORKTREE"): ("record-human-approval", "worktree"),
        ("VERIFY_EXIT", "RETROSPECTIVE"): ("full_test_suite", "test_suite", "leak_check", "references/map-debt.md"),
    }
    for edge, markers in expected.items():
        template = registry.get_template(*edge)
        assert template is not None
        hint = template.next_steps_hint.lower()
        assert all(marker.lower() in hint for marker in markers), (edge, hint)


def test_plan_review_selects_review_then_requires_plan_acceptance():
    """PLAN_REVIEW selects review or skip, then confirms the resulting plan."""
    registry = TransitionRegistry.load_default()

    review_edge = registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW")
    approval_edge = registry.get_template("PLAN_REVIEW", "AWAITING_APPROVAL")

    assert review_edge is not None
    assert approval_edge is not None

    review_questions = {question["question_id"]: question for question in review_edge.human_questions}
    assert "plan_review_method" in review_questions
    review_options = {
        option.removesuffix(" [Recommended]")
        for option in review_questions["plan_review_method"]["options"]
    }
    assert review_options >= {
        "Single-agent review — internal",
        "Single-agent review — external bundle",
        "Multi-agent review — internal",
        "Multi-agent review — external bundle",
        "Other — specify in chat",
    }

    approval_questions = {question["question_id"]: question for question in approval_edge.human_questions}
    assert "confirm_plan_acceptance" in approval_questions
    acceptance_options = {
        option.removesuffix(" [Recommended]")
        for option in approval_questions["confirm_plan_acceptance"]["options"]
    }
    assert "Accept plan and proceed to human approval" in acceptance_options
    assert "Require further revisions" in acceptance_options
    assert approval_edge.skip["allowed"] is False
    assert "acceptance" in approval_edge.purpose.lower()


def test_implementation_review_offers_other_review_method():
    """Implementation review must support a user-specified review method."""
    registry = TransitionRegistry.load_default()
    review_edge = registry.get_template("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW")

    assert review_edge is not None
    questions = {question["question_id"]: question for question in review_edge.human_questions}
    assert "confirm_review_worktree_review_to_multi_agent_code_review" in questions
    options = {
        option.removesuffix(" [Recommended]")
        for option in questions["confirm_review_worktree_review_to_multi_agent_code_review"]["options"]
    }
    assert "Other — specify in chat" in options


def test_plan_review_review_method_offers_other_review_method():
    """The PLAN_REVIEW branch offers an explicit review-method escape hatch."""
    registry = TransitionRegistry.load_default()
    review_edge = registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW")

    assert review_edge is not None
    questions = {question["question_id"]: question for question in review_edge.human_questions}
    assert "plan_review_method" in questions
    options = {
        option.removesuffix(" [Recommended]")
        for option in questions["plan_review_method"]["options"]
    }
    assert "Other — specify in chat" in options


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
    assert "DONE" in guidance["legal_next_states"]


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
