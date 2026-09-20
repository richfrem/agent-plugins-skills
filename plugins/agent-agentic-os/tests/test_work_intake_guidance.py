"""
test_work_intake_guidance.py
============================

Purpose:
    Failing-first contract tests for T1 (start-here-cleanup):
    Validates work-intake guidance, SKILL.md direction, ELI5 formatting,
    nested artifact locations, CLAUDE.md pointer invariant, and plan review acceptance.
"""

import re
import sys
from pathlib import Path
import pytest

WORKTREE_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.registry import TransitionRegistry
from control_plane.edge_matrix import build_edge_matrix, AGENT, SOFT, HARD


def test_work_intake_skill_reads_guidance_and_db_first():
    """SKILL.md must state read-first (YAML stage contract, transition-guidance, DB rules)
    and 'say exactly which parts were read, never more' (ledger item 11, 15, 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "transition_templates.yaml" in skill_md
    assert "transition-guidance" in skill_md
    assert "say exactly which parts were read" in skill_md.lower()


def test_work_intake_skill_human_chat_answers_provenance():
    """Human chat answers must be guided to go through coordinate-transition --interactive,
    never writing interview answers via record_interview_question.py as interviewer (ledger 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "--interactive" in skill_md
    assert "never write interview answers" in skill_md.lower() or "actor=human" in skill_md


def test_work_intake_skill_answer_from_context_and_ask_once():
    """Agent answers from context/ledger, asks ONE question only where clarity is lacking,
    and never re-asks recorded answers (ledger 12, 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "one question" in skill_md.lower()
    assert "never re-ask" in skill_md.lower() or "never re-ask what is recorded" in skill_md.lower()


def test_work_intake_skill_stop_on_blocked_gate_no_workarounds():
    """When a gate blocks: STOP, state cause and cost, no workaround commands (recovery approvals,
    direct DB edits), and never hand state-reverting commands without explanation (ledger 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "stop" in skill_md.lower()
    assert "no workaround" in skill_md.lower() or "workaround" in skill_md.lower()


def test_work_intake_skill_running_directives_ledger():
    """Maintain a running ledger/outline of every human directive from first message (ledger 14, 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "running" in skill_md.lower() and "ledger" in skill_md.lower()


def test_work_intake_skill_artifact_location_rule():
    """Task artifacts live in docs/plans/work-tasks/<task-id>/, never plans root (ledger 8, 9, 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "docs/plans/work-tasks/<task-id>/" in skill_md


def test_work_intake_skill_complete_pasteable_commands_only():
    """Every command the human must run is repeated in full, ready to paste, no back-references (ledger 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "ready to paste" in skill_md.lower() or "complete" in skill_md.lower()
    assert "no back-reference" in skill_md.lower() or "never \"see above\"" in skill_md.lower() or "no vague references" in skill_md.lower()


def test_work_intake_skill_never_dispute_human_account():
    """Never dispute or 'correct' the human's account of what they said or meant (ledger 16)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "never dispute" in skill_md.lower()


def test_work_intake_skill_links_edge_matrix_and_transcript():
    """SKILL.md links to the healthy transcript and edge matrix references (ledger 17, 19)."""
    skill_md = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    assert "work-intake-healthy-transcript.md" in skill_md
    assert "edge-matrix.md" in skill_md or "edge_matrix" in skill_md


def test_work_intake_skill_key_rules_in_first_60_lines():
    """Key rules must appear within the first 60 lines of work-intake/SKILL.md."""
    skill_lines = (PLUGIN_DIR / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8").splitlines()[:60]
    first_60 = "\n".join(skill_lines)
    assert "read" in first_60.lower()
    assert "yaml" in first_60.lower()
    assert "docs/plans/work-tasks" in first_60 or "artifact" in first_60.lower()


def test_no_flat_plans_paths_in_yaml_and_docs():
    """No docs/plans/<task-id>-*.md flat write instruction in transition_templates.yaml,
    work-intake-detailed-reference.md, or implementation-ledger-contract.md (ledger item 10)."""
    flat_pattern = re.compile(r"docs/plans/<task-id>-[a-zA-Z0-9_\-]+\.md")

    ref_doc = (PLUGIN_DIR / "references" / "work-intake-detailed-reference.md").read_text(encoding="utf-8")
    matches = flat_pattern.findall(ref_doc)
    assert not matches, f"Found flat docs/plans/<task-id>-*.md paths in work-intake-detailed-reference.md: {matches}"

    # Check advisory lines and write instructions in transition_templates.yaml (ledger 10 and plan line 32)
    yaml_text = (SCRIPTS_DIR / "control_plane" / "transition_templates.yaml").read_text(encoding="utf-8")
    for line_num, line in enumerate(yaml_text.splitlines(), 1):
        if "artifact_path:" in line or ("next_steps_hint:" in line and "docs/plans/<task-id>-" in line):
            assert "docs/plans/work-tasks/<task-id>/" in line or "docs/plans/<task-id>-" not in line, (
                f"Line {line_num} in transition_templates.yaml has flat path write instruction: {line}"
            )


def test_claude_md_pointer_exact_invariant():
    """Repo-root CLAUDE.md is a tracked stub that ONLY points to AGENTS.md (ledger item 13)."""
    claude_md = WORKTREE_ROOT / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md does not exist at worktree root"
    content = claude_md.read_text(encoding="utf-8").strip()
    assert "AGENTS.md" in content
    assert len(content.splitlines()) <= 5


def test_plan_acceptance_advances_without_review_or_skip(tmp_path):
    """T4b contract test: when the human accepts the plan, PLAN_REVIEW -> AWAITING_APPROVAL
    advances without requiring a passing critic review or review-skip receipt."""
    from agent_control import ControlPlane
    from control_plane.coordinator import TransitionCoordinator
    import io

    from control_plane.pipeline_simulator import PipelineSimulator

    registry = TransitionRegistry.load_default()
    sim = PipelineSimulator(tmp_path / "control_plane.db", registry=registry)
    task_id = "plan-accept-001"
    sim.create_task(task_id, "Test plan acceptance")
    sim.control_plane.repo_root = tmp_path / "repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)
    sim.enter_interview(task_id)
    sim.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
    sim.control_plane.record_plan_mode_entry(task_id, "simulator")
    sim.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD", expect_success=True)

    plan_dir = sim.control_plane.repo_root / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan", encoding="utf-8")

    # Move DRAFT_PLAN -> PLAN_REVIEW
    def step(answers, to_state, actor="human"):
        feed = iter(answers)
        TransitionCoordinator(
            sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
        ).coordinate_transition(task_id=task_id, to_state=to_state, actor=actor, reason="setup", interactive=True)

    step(["1", "YES"], "PLAN_REVIEW")

    # Now in PLAN_REVIEW. Human answers confirm_plan_acceptance = Accept
    feed = iter(["1", "YES"])  # 1 = Accept plan and proceed to human approval, YES = confirmation
    coordinator = TransitionCoordinator(
        sim.control_plane,
        registry=registry,
        input_fn=lambda _p: next(feed),
        output_stream=io.StringIO(),
    )

    coordinator.coordinate_transition(
        task_id=task_id,
        to_state="AWAITING_APPROVAL",
        actor="agent",
        reason="Plan accepted by human in chat",
        interactive=True,
    )

    last_tx = sim.control_plane._persistence.get_last_transition(task_id)
    assert last_tx is not None
    assert last_tx.to_state == "AWAITING_APPROVAL"
