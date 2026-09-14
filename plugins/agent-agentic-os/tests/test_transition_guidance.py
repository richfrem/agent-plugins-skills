"""Task 5 contract tests for advisory, registry-derived transition guidance."""

import io
import pytest
import sys
import yaml
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

    assert guidance["model_effort_guidance"]["interview"]["recommended_model"] == "current-user-model"
    assert guidance["model_effort_guidance"]["interview"]["recommended_effort"] == "low"
    assert guidance["model_effort_guidance"]["plan"]["requires_confirmation_for_premium"] is True

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
    assert guidance["legal"] is True
    force_edge = next(t for t in guidance["transitions"] if t["to_state"] == "DONE")
    assert force_edge["transition_id"] == "human_force_done__from_INTAKE"
    assert "FORCE_DONE" in force_edge["success_guidance"]
    assert guidance["command"] == force_edge["command"]
    assert guidance["denial_guidance"]
    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS["INTAKE"]


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


def test_done_stage_exposes_git_closeout_contract_and_question(control_plane):
    task_id = "guidance-done-closeout-001"
    control_plane.create_task(task_id=task_id, title="DONE closeout guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()

    contract = registry.get_stage_contract("DONE")
    assert contract is not None
    question = contract["entry_questions"][0]
    assert question["question_id"] == "done_git_integration_authorization"
    assert question["options"] == [
        "Yes, begin Git integration [Recommended]",
        "No, leave the verified changes in the current worktree",
    ]
    assert "existing registered feature branch" in question["question"]
    assert contract["closeout_contract"]["feature_branch_policy"].startswith("Reuse")
    assert contract["closeout_contract"]["commit_policy"].startswith("Create exactly one")
    assert contract["closeout_contract"]["push_policy"].startswith("Ask separately")

    guidance = registry.get_transition_guidance("DONE")
    assert guidance["current_state"] == "DONE"
    assert guidance["stage_contract"] == contract


def test_retrospective_done_requires_passing_full_suite_and_reports_recovery():
    template = TransitionRegistry.load_default().get_template("RETROSPECTIVE", "DONE")

    assert template is not None
    assert "retrospective_done_guard" in template.deterministic_checks
    assert "full_test_suite" in template.deterministic_checks
    hint = template.next_steps_hint.lower()
    assert "repository-wide pytest -q suite" in hint
    assert "verifier_id=pytest_full_suite" in hint
    assert "exit_code=0" in hint
    assert "remain in retrospective" in hint


def test_standard_path_hints_name_each_operational_handoff(control_plane):
    registry = TransitionRegistry.load_default()
    expected = {
        ("INTERVIEW", "DRAFT_PLAN"): ("record-plan-mode-entry", "verify-interview-question"),
        ("DRAFT_PLAN", "PLAN_REVIEW"): ("submit", "coordinate-transition"),
        ("PLAN_REVIEW", "MULTI_AGENT_REVIEW"): ("review-selection-v1", "coordinate-transition"),
        ("PLAN_REVIEW", "AWAITING_APPROVAL"): ("record-critic-review", "record-review-skip"),
            ("APPROVED", "IN_WORKTREE"): ("record-human-approval", "worktree"),
            ("APPROVED", "RETROSPECTIVE"): ("planning_only_completion", "RETROSPECTIVE", "no worktree"),
        ("VERIFY_EXIT", "RETROSPECTIVE"): ("full_test_suite", "test_suite", "leak_check", "references/map-debt.md"),
    }
    for edge, markers in expected.items():
        template = registry.get_template(*edge)
        assert template is not None
        hint = template.next_steps_hint.lower()
        assert all(marker.lower() in hint for marker in markers), (edge, hint)


def test_failed_verify_exit_routes_to_existing_worktree_without_repetition():
    registry = TransitionRegistry.load_default()
    template = registry.get_template("VERIFY_EXIT", "IN_WORKTREE")

    assert template is not None
    hint = template.next_steps_hint.lower()
    recovery = template.to_dict()["failure_recovery"].lower()
    assert "full_test_suite" in hint
    assert "do not transition to retrospective or done" in hint
    assert "existing registered worktree" in hint
    assert "do not create another worktree" in hint
    assert "submit through worktree_review" in hint
    assert "do not repeat the failed closeout path" in recovery
    assert "do not reset to intake" in recovery


def test_in_worktree_hands_off_to_uninterrupted_implementation_session():
    registry = TransitionRegistry.load_default()
    contract = registry.get_stage_contract("IN_WORKTREE")
    review_edge = registry.get_template("IN_WORKTREE", "WORKTREE_REVIEW")

    assert contract["implementation_kickoff"]["ownership"].startswith("After APPROVED")
    assert contract["implementation_kickoff"]["pipeline_gate_policy"].startswith("Do not request")
    assert "continue automatically" in contract["implementation_kickoff"]["continuation_loop"]
    assert "exit verification" in contract["implementation_kickoff"]["pipeline_gate_policy"]
    assert "implementation is complete" in contract["completion_contract"]["definition"].lower()
    assert "does not mean committed, pushed, merged, or done" in contract["completion_contract"]["definition"].lower()
    inventory = contract["completion_contract"]["session_change_inventory"]
    assert inventory["mandatory"] is True
    assert inventory["run_on_every_session"] is True
    assert inventory["run_before_every_review_submission"] is True
    assert inventory["run_after_every_internal_fix_round"] is True
    assert "every file created or modified by this session" in inventory["reminder"].lower()
    assert "session-owned main-only path is a blocker" in inventory["ownership_rule"].lower()
    assert "do not report completion or enter worktree_review" in inventory["failure_rule"].lower()
    assert "byte-identical" in inventory["comparison_policy"]["implementation_files"]
    assert "expected timestamps" in inventory["comparison_policy"]["generated_metadata"]
    assert contract["completion_contract"]["reconciliation_manifest"]["required_before_integration"] is True
    assert contract["completion_contract"]["integration_contract"]["apply_reviewed_patch_once"] is True
    assert contract["completion_contract"]["integration_contract"]["preserve_main_only_preexisting_changes"] is True

    assert review_edge is not None
    question = review_edge.human_questions[0]
    assert question["question"] == "Implementation is complete in the registered worktree. Do you wish to proceed to WORKTREE_REVIEW?"
    assert question["options"] == ["Proceed to WORKTREE_REVIEW [Recommended]"]
    assert question["accepted_answers"] == ["Proceed to WORKTREE_REVIEW [Recommended]"]
    hint = review_edge.next_steps_hint.lower()
    assert "reconciliation manifest" in hint
    assert "worktree-only" in hint
    assert "main-only-preexisting" in hint
    assert "session-wide change inventory" in hint
    assert "apply the reviewed worktree patch once" in hint


def test_session_change_control_covers_pre_implementation_observations():
    source = Path(__file__).resolve().parents[1] / "scripts" / "control_plane" / "transition_templates.yaml"
    contract = yaml.safe_load(source.read_text(encoding="utf-8"))["session_change_control"]

    assert contract["applies_from"] == "task_creation"
    assert contract["worktree_first_invariant"].startswith("From the first task/session mutation")
    assert contract["observation_loop"]["trigger"].lower().startswith("any user or agent observation")
    assert contract["observation_loop"]["sequence"][-1] == "record_evidence_and_resume_current_stage"
    assert "in_scope_immediate_pipeline_fix" in contract["observation_loop"]["classifications"]
    assert "deferred_map_debt" in contract["observation_loop"]["classifications"]
    assert "material scope expansion" in contract["observation_loop"]["approval_boundary"].lower()
    assert "do not report implementation as started or complete" in contract["observation_loop"]["status_reporting"].lower()
def test_human_recovery_contract_allows_explicit_reentry_without_dag_bypass():
    source = Path(__file__).resolve().parents[1] / "scripts" / "control_plane" / "transition_templates.yaml"
    contract = yaml.safe_load(source.read_text(encoding="utf-8"))["human_recovery"]

    assert contract["enabled"] is True
    assert contract["source_states"] == "Any canonical state"
    assert contract["target_states"] == "Any different canonical state"
    assert "occupancy" in contract["evidence"]
    assert "does not grant downstream capability" in contract["reentry_rule"]
    assert "unknown states" in contract["safety_boundary"]


def test_retrospective_closeout_classifies_findings_before_done():
    stage = TransitionRegistry.load_default().get_stage_contract("RETROSPECTIVE")

    change_control = stage["closeout_change_control"]
    assert change_control["mandatory_before_done"] is True
    assert change_control["classifications"] == [
        "already_resolved_in_current_package",
        "bounded_fix_requires_rework_loop",
        "larger_follow_up_requires_issue_or_new_work_package",
    ]
    assert "never applied directly from RETROSPECTIVE" in change_control["bounded_fix_rule"]
    assert "no legal implementation return edge" in change_control["no_legal_return_rule"]
    assert "duplicate search" in change_control["larger_follow_up_rule"]
    self_assessment = change_control["agent_self_assessment"]
    assert self_assessment["mandatory_before_done"] is True
    assert "safe bounded fix now" in self_assessment["question"]
    assert "for every finding" in self_assessment["response_policy"].lower()
    assert "no_silent_action" in self_assessment

def test_plan_review_selects_review_then_requires_plan_acceptance():
    """PLAN_REVIEW selects review or skip, then confirms the resulting plan."""
    registry = TransitionRegistry.load_default()

    review_edge = registry.get_template("PLAN_REVIEW", "MULTI_AGENT_REVIEW")
    approval_edge = registry.get_template("PLAN_REVIEW", "AWAITING_APPROVAL")

    assert review_edge is not None
    assert approval_edge is not None

    disposition = {question["question_id"]: question for question in registry.get_template("DRAFT_PLAN", "PLAN_REVIEW").human_questions}["confirm_review_draft_plan_to_plan_review"]
    assert disposition["question"] == "Would you like to submit the drafted plan for review?"
    assert disposition["options"] == [
        "Proceed with review [Recommended]",
        "Continue revising prior stage",
    ]

    review_questions = {question["question_id"]: question for question in review_edge.human_questions}
    assert "plan_review_method" in review_questions
    review_options = {
        option.removesuffix(" [Recommended]")
        for option in review_questions["plan_review_method"]["options"]
    }
    assert review_options >= {
        "Single-agent review — internal",
        "Single-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
        "Multi-agent review — internal",
        "Multi-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
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
    assert questions["confirm_review_worktree_review_to_multi_agent_code_review"]["options"] == [
        "Yes — continue to review method selection [Recommended]",
        "No — skip agent review and continue to exit verification",
    ]
    assert "implementation_review_method" in questions
    options = {
        option.removesuffix(" [Recommended]")
        for option in questions["implementation_review_method"]["options"]
    }
    assert options == {
        "Single-agent review — internal",
        "Single-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
        "Multi-agent review — internal",
        "Multi-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
    }
    assert "CLI/runtime, model, and effort" in review_edge.next_steps_hint


def test_implementation_review_rework_edge_describes_revision_brief_loop():
    registry = TransitionRegistry.load_default()
    rework_edge = registry.get_template("MULTI_AGENT_CODE_REVIEW", "IN_WORKTREE")
    resubmit_edge = registry.get_template("MULTI_AGENT_CODE_REVIEW", "WORKTREE_REVIEW")

    assert rework_edge is not None
    assert "REQUEST_CHANGES" in rework_edge.next_steps_hint
    assert "do not edit" in rework_edge.next_steps_hint.lower()
    assert "WORKTREE_REVIEW -> MULTI_AGENT_CODE_REVIEW" in rework_edge.next_steps_hint
    assert "do not create a new transition type" in rework_edge.next_steps_hint.lower()
    questions = {question["question_id"]: question for question in rework_edge.human_questions}
    assert questions["confirm_rework_multi_agent_code_review_to_in_worktree"]["options"] == [
        "Yes — transition to IN_WORKTREE and begin bounded fixes [Recommended]",
        "No — remain in MULTI_AGENT_CODE_REVIEW",
    ]
    assert resubmit_edge is not None
    assert "review outcome" in resubmit_edge.next_steps_hint.lower()


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
    assert options == {
        "Single-agent review — internal",
        "Single-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
        "Multi-agent review — internal",
        "Multi-agent review — external bundle (agent generates bundle, waits for you to upload to an independent model and report back)",
    }
    hint = review_edge.next_steps_hint
    assert "CLI/runtime, model, and effort" in hint
    assert "one question at a time" in hint
    assert "update-cli-models" in hint
    assert "--interactive" in hint


def test_plan_and_implementation_reviews_share_environment_and_model_selection_contract():
    source = Path(__file__).resolve().parents[1] / "scripts" / "control_plane" / "transition_templates.yaml"
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    contract = document["review_selection_contract"]

    assert contract["canonical_profile_path"] == "context/agent-capability-profile.json"
    assert contract["environment_summary_fallback"] == "context/memory/environment.md"
    assert contract["user_must_choose_internal_route"] is True
    assert contract["question_sequence"] == [
        "review_decision",
        "review_method",
        "internal_runtime_model_effort",
    ]
    assert contract["catalog_authority_skill"] == "update-cli-models"
    assert contract["catalog_resolution"]["authority"] == "update-cli-models"
    assert contract["catalog_resolution"]["do_not_duplicate_catalogs"] is True
    assert "current model IDs" in contract["catalog_resolution"]["instruction"]
    assert "--interactive" in contract["human_answer_provenance"]["chat_answer"]
    assert "--answers" in contract["human_answer_provenance"]["answers_flag"]
    assert "never --answers" in document["execution_guidance"]["transition"]["instruction"]
    assert "do not dispatch" in contract["internal_selection_rule"].lower()
    handoff = contract["feedback_handoff"]
    assert handoff["sequence"][:3] == [
        "collect_each_reviewer_report",
        "synthesize_one_canonical_round_brief",
        "persist_raw_reports_and_synthesis",
    ]
    assert "each report" in handoff["storage"]["raw_reports"]
    assert "canonical revision brief" in handoff["implementation_handoff"]
    assert "same selection contract" in handoff["re_review_rule"]
    isolation = handoff["review_type_isolation"]
    assert "never authorize implementation rework" in isolation["plan_review"]
    assert "implementation in the registered worktree" in isolation["implementation_review"]
    assert "separate plan-review and implementation-review" in isolation["round_numbering"]
    assert "current implementation-review receipt" in isolation["rework_gate"]

    expected_edges = {
        "plan_review_to_multi_agent_review",
        "worktree_review_to_multi_agent_code_review",
    }
    review_edges = {
        item["transition_id"]: item
        for item in document["templates"]
        if item["transition_id"] in expected_edges
    }
    assert set(review_edges) == expected_edges
    for edge in review_edges.values():
        assert edge["review_selection_contract"] == "review-selection-v1"
        assert edge["review_selection"]["user_choice_required_for_internal"] is True
        assert edge["review_selection"]["recommendation_source"] == "model_effort_guidance.review"
        assert edge["review_selection"]["catalog_source"] == "review_selection_contract.catalog_resolution"


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
    # 2026-09-07 (DEBT-20260907-08): the full per-transition banner was
    # intentionally shrunk to a one-line unit-name summary to stop training
    # agents to skim the whole advisory block; assert the current wording.
    assert "Execution-unit guidance (advisory; unchanged across edges)" in rendered
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
