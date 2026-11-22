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
from control_plane.constants import (
    STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE,
)


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
    assert guidance["current_state"] == STATE_INTAKE
    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS[STATE_INTAKE]
    assert {edge["to_state"] for edge in guidance["transitions"]} == set(ALLOWED_TRANSITIONS[STATE_INTAKE])
    assert all("python3 " in edge["command"] for edge in guidance["transitions"])
    draft = next(edge for edge in guidance["transitions"] if edge["to_state"] == STATE_DRAFT_PLAN)
    assert draft["transition_id"] == "intake_to_draft_plan"
    assert "DRAFT_PLAN" in draft["command"]


def test_guidance_cannot_authorize_illegal_requested_edge(control_plane):
    task_id = "guidance-denial-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id, requested_to_state=STATE_DONE)

    assert guidance["advisory"] is True
    assert guidance["legal"] is True
    force_edge = next(t for t in guidance["transitions"] if t["to_state"] == STATE_DONE)
    assert force_edge["transition_id"] == "human_force_done__from_INTAKE"
    assert "FORCE_DONE" not in force_edge["success_guidance"] and "FORCE_CLOSE" not in force_edge["success_guidance"]
    assert "ssh-keygen -Y sign" in force_edge["success_guidance"]  # closure takes the same human signature
    assert guidance["command"] == force_edge["command"]
    assert guidance["denial_guidance"]
    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS[STATE_INTAKE]


def test_done_guidance_names_retrospective_recording_protocol(control_plane):
    task_id = "guidance-retrospective-001"
    control_plane.create_task(task_id=task_id, title="Retrospective guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()
    template = registry.get_template(STATE_VERIFY_EXIT, STATE_DONE)

    assert template is not None
    hint = template.next_steps_hint.lower()
    assert "record_retrospective" in hint
    assert "before" in hint and "done" in hint
    assert "full_test_suite" in hint and "focused_test_suite" in hint


def test_done_stage_exposes_git_closeout_contract_and_question(control_plane):
    task_id = "guidance-done-closeout-001"
    control_plane.create_task(task_id=task_id, title="DONE closeout guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()

    contract = registry.get_stage_contract(STATE_DONE)
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

    guidance = registry.get_transition_guidance(STATE_DONE)
    assert guidance["current_state"] == STATE_DONE
    assert guidance["stage_contract"] == contract


def test_retrospective_done_requires_passing_full_suite_and_reports_recovery():
    template = TransitionRegistry.load_default().get_template(STATE_VERIFY_EXIT, STATE_DONE)

    assert template is not None
    assert "done_guard" in template.deterministic_checks
    assert "full_test_suite_or_trivial_focused" in template.deterministic_checks
    hint = template.next_steps_hint.lower()
    assert "repository-wide pytest -q suite" in hint
    assert "record full_test_suite" in hint
    assert "focused_test_suite" in hint
    assert "retrospective_done_guard" in hint


def test_standard_path_hints_name_each_operational_handoff(control_plane):
    registry = TransitionRegistry.load_default()
    expected = {
        (STATE_INTAKE, STATE_DRAFT_PLAN): ("coordinate-transition", "draft_plan"),
        (STATE_DRAFT_PLAN, STATE_PLAN_REVIEW): ("plan_review", "coordinate-transition"),
        (STATE_PLAN_REVIEW, STATE_APPROVED): ("ssh-keygen -y sign", "approved"),
        (STATE_APPROVED, STATE_IN_WORKTREE): ("human_approval", "worktree"),
        (STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW): ("test_suite", "worktree_review"),
        (STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT): ("ssh-keygen -y sign", "verify_exit"),
        (STATE_VERIFY_EXIT, STATE_DONE): ("full_test_suite", "record_retrospective", "done"),
    }
    for edge, markers in expected.items():
        template = registry.get_template(*edge)
        assert template is not None
        hint = template.next_steps_hint.lower()
        assert all(marker.lower() in hint for marker in markers), (edge, hint)


def test_failed_verify_exit_routes_to_existing_worktree_without_repetition():
    registry = TransitionRegistry.load_default()
    template = registry.get_template(STATE_VERIFY_EXIT, STATE_IN_WORKTREE)

    assert template is not None
    hint = template.next_steps_hint.lower()
    recovery = template.to_dict()["failure_recovery"].lower()
    assert "full_test_suite" in hint
    assert "do not transition to done" in hint
    assert "existing registered worktree" in hint
    assert "do not create another worktree" in hint
    assert "submit through worktree_review" in hint
    assert "do not repeat the failed closeout path" in recovery
    assert "do not reset to intake" in recovery


def test_in_worktree_hands_off_to_uninterrupted_implementation_session():
    registry = TransitionRegistry.load_default()
    contract = registry.get_stage_contract(STATE_IN_WORKTREE)
    review_edge = registry.get_template(STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW)

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
    assert review_edge.human_questions == []
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
    source = Path(__file__).resolve().parents[1] / "scripts" / "control_plane" / "transition_templates.yaml"
    stages = yaml.safe_load(source.read_text(encoding="utf-8"))["stages"]
    stage = stages.get(STATE_VERIFY_EXIT) or stages.get(STATE_RETROSPECTIVE)

    change_control = stage["closeout_change_control"]
    assert change_control["mandatory_before_done"] is True
    assert change_control["classifications"] == [
        "already_resolved_in_current_package",
        "bounded_fix_requires_rework_loop",
        "larger_follow_up_requires_issue_or_new_work_package",
    ]
    assert "never applied directly from VERIFY_EXIT" in change_control["bounded_fix_rule"]
    assert "no legal implementation return edge" in change_control["no_legal_return_rule"]
    assert "duplicate search" in change_control["larger_follow_up_rule"]
    self_assessment = change_control["agent_self_assessment"]
    assert self_assessment["mandatory_before_done"] is True
    assert "safe bounded fix now" in self_assessment["question"]
    assert "for every finding" in self_assessment["response_policy"].lower()
    assert "no_silent_action" in self_assessment

def test_plan_review_selects_review_then_requires_plan_acceptance():
    """In schema v15, DRAFT_PLAN -> PLAN_REVIEW enters review and PLAN_REVIEW -> APPROVED is Gate 1 (signed)."""
    registry = TransitionRegistry.load_default()

    draft_to_review = registry.get_template(STATE_DRAFT_PLAN, STATE_PLAN_REVIEW)
    approval_edge = registry.get_template(STATE_PLAN_REVIEW, STATE_APPROVED)

    assert draft_to_review is not None
    assert approval_edge is not None
    assert approval_edge.requires_cryptographic_proof is True
    assert approval_edge.authorized_actor == "human_only"
    assert approval_edge.skip["allowed"] is False


def test_implementation_review_offers_other_review_method():
    """In schema v15, WORKTREE_REVIEW absorbs code review and exits to VERIFY_EXIT via Gate 3 signature."""
    registry = TransitionRegistry.load_default()
    exit_edge = registry.get_template(STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT)

    assert exit_edge is not None
    assert exit_edge.requires_cryptographic_proof is True
    assert exit_edge.authorized_actor == "human_only"
    assert "ssh-keygen -y sign" in exit_edge.next_steps_hint.lower()


def test_implementation_review_rework_edge_describes_revision_brief_loop():
    """In schema v15, WORKTREE_REVIEW -> IN_WORKTREE is the implementation rework edge."""
    registry = TransitionRegistry.load_default()
    rework_edge = registry.get_template(STATE_WORKTREE_REVIEW, STATE_IN_WORKTREE)
    resubmit_edge = registry.get_template(STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW)

    assert rework_edge is not None
    assert "coordinate-transition" in rework_edge.next_steps_hint.lower()
    assert resubmit_edge is not None
    assert "worktree_review" in resubmit_edge.next_steps_hint.lower()


def test_plan_review_review_method_offers_other_review_method():
    """In schema v15, PLAN_REVIEW -> DRAFT_PLAN is the plan rework edge and PLAN_REVIEW -> APPROVED is Gate 1."""
    registry = TransitionRegistry.load_default()
    rework_edge = registry.get_template(STATE_PLAN_REVIEW, STATE_DRAFT_PLAN)
    approve_edge = registry.get_template(STATE_PLAN_REVIEW, STATE_APPROVED)

    assert rework_edge is not None
    assert approve_edge is not None
    assert "ssh-keygen -y sign" in approve_edge.next_steps_hint.lower()


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
    assert contract["catalog_authority_skill"] == "cli-agent"
    assert contract["catalog_resolution"]["authority"] == "cli-agent"
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

    # In schema v15, MULTI_AGENT_REVIEW and MULTI_AGENT_CODE_REVIEW are retired; review happens inside
    # PLAN_REVIEW and WORKTREE_REVIEW governed by the shared review_selection_contract above.
    assert contract["catalog_authority_skill"] == "cli-agent"


def test_worktree_review_exit_hint_names_the_signature_flow_and_no_skip_branch():
    """auth-ciba-increment-b (2026-09-20): this edge's guidance used to describe a --skip-review/--skip-reason
    branch and a confirm_worktree_review_accept_implementation question. Both are gone: the hint must name the
    signed flow and must not advertise any skip flag or soft question."""
    registry = TransitionRegistry.load_default()
    template = registry.get_template(STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT)

    assert template is not None
    assert [q["question_id"] for q in template.human_questions] == []
    hint = template.next_steps_hint.lower()
    assert "confirm_worktree_review_accept_implementation" not in hint
    assert "--skip-review" not in hint and "--skip-reason" not in hint
    assert "ssh-keygen -y sign" in hint and "allowed_signers" in hint


def test_stale_yaml_next_state_claim_is_ignored_for_guidance_legality(control_plane):
    task_id = "guidance-stale-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()
    control_plane._transition_registry = registry
    registry.get_template(STATE_INTAKE, STATE_DRAFT_PLAN).guidance["legal_next_states"] = [STATE_DONE]

    guidance = control_plane.get_transition_guidance(task_id)

    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS[STATE_INTAKE]
    assert STATE_DONE in guidance["legal_next_states"]


def test_coordinator_surfaces_advisory_guidance_before_and_after_transition(control_plane):
    task_id = "guidance-output-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    output = io.StringIO()
    coordinator = TransitionCoordinator(control_plane, output_stream=output)

    coordinator._write_transition_guidance(STATE_INTAKE, STATE_DRAFT_PLAN, phase="before")
    coordinator._write_next_steps_hint(STATE_INTAKE)

    rendered = output.getvalue()
    assert "Advisory transition guidance" in rendered
    assert "registry version" in rendered
    assert "INTAKE -> DRAFT_PLAN" in rendered
    assert "advisory only" in rendered.lower()
    assert "Next possible transitions from INTAKE" in rendered


def test_coordinator_renders_execution_unit_guidance(control_plane):
    """The model-facing transition report includes task execution guidance."""
    output = io.StringIO()
    coordinator = TransitionCoordinator(control_plane, output_stream=output)

    coordinator._write_transition_guidance(STATE_INTAKE, STATE_DRAFT_PLAN, phase="before")

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


def test_coordinate_transition_subprocess_cp1252_encoding(tmp_path):
    """Failure 1 regression: coordinate-transition prints checklist without charmap/cp1252 encoding crash."""
    import subprocess
    import os

    db_path = tmp_path / "control_plane.db"
    script = SCRIPTS_DIR / "agent_control.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    env["AGENT_CONTROL_DB"] = str(db_path)

    # 1. Initialize DB and create task in INTAKE
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--db-path",
            str(db_path),
            "init",
            "--task-id",
            "cp1252-test-01",
            "--title",
            "Test cp1252",
            "--runtime",
            "codex",
            "--human-confirmed",
            "HUMAN-CONFIRMED: create task",
        ],
        check=True,
        capture_output=True,
        env=env,
    )

    # 2. Run coordinate-transition with PYTHONIOENCODING=cp1252
    res = subprocess.run(
        [
            sys.executable,
            str(script),
            "--db-path",
            str(db_path),
            "coordinate-transition",
            "--task-id",
            "cp1252-test-01",
            "--to",
            "DRAFT_PLAN",
            "--human-confirmed",
            "HUMAN-CONFIRMED: test cp1252 encoding without crashing",
            "--answers",
            '{"intake_outline_confirmation": "Confirm outline and enter DRAFT_PLAN [Recommended]"}',
        ],
        capture_output=True,
        env=env,
        cwd=str(tmp_path),
    )
    # Must not crash with UnicodeEncodeError: 'charmap' codec can't encode character
    stderr_text = res.stderr.decode("cp1252", errors="replace")
    stdout_text = res.stdout.decode("cp1252", errors="replace")
    assert "UnicodeEncodeError" not in stderr_text
    assert "UnicodeEncodeError" not in stdout_text
    assert "Checklist:" in stdout_text
    assert res.returncode == 0
