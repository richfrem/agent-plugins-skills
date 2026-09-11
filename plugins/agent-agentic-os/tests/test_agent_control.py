"""
test_agent_control.py — Contract Test for SQLite Control Plane & State Machine
=============================================================================

Purpose:
    Contract verification suite for the lightweight SQLite control plane,
    verifier sovereignty guards, state machine transitions, session-aware
    runtime detection, and cost tier model resolution.

Key Input Dependencies:
    - Temporary SQLite databases created in pytest fixtures
    - Reference catalogs: plugins/cli-agents/references/*.json

Key Functions:
    - temp_db_path() — Pytest fixture yielding temporary database path
    - control_plane() — Pytest fixture initializing ControlPlane instance
    - test_schema_initialization_and_pragmas() — Validates tables and WAL mode
    - test_task_lifecycle_transitions() — Validates canonical DAG transitions
    - test_invalid_state_transition_fails() — Validates illegal transition rejections
    - test_verifier_sovereignty_lock_and_violation() — Validates SHA256 locking
    - test_verification_receipt_generation() — Validates receipt generation
    - test_session_aware_native_detection() — Validates session-aware environment detection
    - test_cost_tier_resolution_and_task_columns() — Validates cost tier columns and resolution
    - test_evolution_task_blocked_without_prior_art_scan() — Validates EVOLUTION prior art gate
    - test_evolution_task_passes_with_prior_art_scan() — Validates EVOLUTION prior art gate success path
"""

import os
import sqlite3
import tempfile
import time
import pytest
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from interview_helpers import stage_interview_answers

# Target modules to import once implemented
from agent_control import (
    ControlPlane,
    CANONICAL_STATES,
    WORKTREE_STATES,
    VerifierSovereigntyViolation,
    InvalidStateTransition,
    PersistenceInvariantViolation,
    ConcurrentModificationError,
    CURRENT_SCHEMA_VERSION,
)
from control_plane.coordinator import TransitionCoordinatorError
from interview_spec_engine import (
    detect_intake_mode,
)
from helpers.implementation_ledger import stage_implementation_ledger


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary SQLite database path for isolated testing."""
    db_file = tmp_path / "control_plane.db"
    return db_file


@pytest.fixture
def control_plane(temp_db_path):
    """Initializes and returns a ControlPlane test fixture instance."""
    cp = ControlPlane(db_path=temp_db_path)
    cp.init_db()
    return cp


def stage_human_decisions(cp, task_id, from_state, to_state, actor="human", answer="Approved"):
    """Helper for test scaffolding to stage required human decisions for human-gated transitions."""
    conn = sqlite3.connect(cp.db_path)
    cur = conn.cursor()
    row = cur.execute(
        "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
        (task_id,)
    ).fetchone()
    occupancy_id = row[0] if row else None
    questions = cur.execute(
        "SELECT question_id FROM required_transition_questions WHERE from_state = ? AND to_state = ?",
        (from_state, to_state)
    ).fetchall()
    now = time.time()
    for (q_id,) in questions:
        cur.execute(
            """
            INSERT INTO transition_decisions (
                task_id, source_occupancy_transition_id, from_state, to_state,
                question_id, answer, decision_type, actor, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'ANSWER', ?, ?)
            """,
            (task_id, occupancy_id, from_state, to_state, q_id, answer, actor, now)
        )
    conn.commit()
    conn.close()


def stage_worktree_metadata(cp, task_id, path=None, branch=None):
    """Stage the explicit worktree metadata required before IN_WORKTREE."""
    cp.update_worktree(
        task_id,
        path or f".worktrees/{task_id}",
        branch or f"feature/{task_id}",
        "written_in_worktree",
    )


def complete_retrospective(cp, task_id, actor="human"):
    """Move from VERIFY_EXIT through the new retrospective gate to DONE."""
    cp.record_verification_receipt(task_id, "full_test_suite", "pytest -q", 0)
    stage_implementation_ledger(cp, task_id)
    cp.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Enter retrospective")
    cp.save_retrospective(
        task_id,
        {
            "decision": "opt_in",
            "completion_mode": "completed",
            "actor": actor,
            "outcome": "completed",
            "strengths": "tests passed",
            "friction": "none",
            "learning": "none",
            "improvement": "none",
            "follow_up": "none",
        },
        [],
    )
    stage_human_decisions(cp, task_id, "RETROSPECTIVE", "DONE", actor="human", answer="complete")
    cp.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Retrospective complete")


def test_schema_initialization_and_pragmas(control_plane, temp_db_path):
    """Test that SQLite DB initializes with WAL mode, foreign keys, and tables."""
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    # Check PRAGMAs
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.lower() == "wal"
    
    # Check tables existence
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "tasks" in tables
    assert "task_transitions" in tables
    assert "locked_verifier_baselines" in tables
    assert "critic_reviews" in tables
    assert "verification_receipts" in tables
    assert "asymmetric_persistence_log" in tables
    conn.close()


def test_critic_review_normalizes_request_changes_to_revise(control_plane):
    """External review wording is stored using the canonical REVISE verdict."""
    task_id = "task-critic-vocabulary-001"
    control_plane.create_task(task_id=task_id, title="Critic Vocabulary", runtime_tool="claude")

    control_plane.record_critic_review(
        task_id=task_id,
        iteration=1,
        model="claude-sonnet-5",
        verdict="REQUEST_CHANGES",
        findings="Revise the plan boundary.",
    )

    conn = sqlite3.connect(control_plane.db_path)
    try:
        verdict = conn.execute(
            "SELECT verdict FROM critic_reviews WHERE task_id = ?", (task_id,)
        ).fetchone()[0]
    finally:
        conn.close()
    assert verdict == "REVISE"


def test_control_cli_exposes_critic_review_recording():
    """The documented critic-review branch is reachable through the CLI parser."""
    from agent_control import _build_parser

    assert "record-critic-review" in _build_parser().format_help()


def test_task_lifecycle_transitions(control_plane):
    """Test valid state transitions through the canonical pipeline DAG."""
    task_id = "task-test-001"
    
    # 1. Create task in INTAKE
    control_plane.create_task(task_id=task_id, title="Test Lifecycle Task", runtime_tool="antigravity")
    task = control_plane.get_task(task_id)
    assert task["state"] == "INTAKE"
    assert task["title"] == "Test Lifecycle Task"
    
    # 2. Transition to INTERVIEW
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting Socratic interview")
    assert control_plane.get_task(task_id)["state"] == "INTERVIEW"

    # 3. Transition to DRAFT_PLAN
    control_plane.record_plan_mode_entry(task_id=task_id, actor="interview-spec")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="interview-spec", reason="4-Pillar Spec compiled")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"

    # 4. Critic review passes, merge at PLAN_REVIEW, then move to AWAITING_APPROVAL
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="Spec is solid")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer="No — accept plan as-is and skip independent review [Recommended]")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="critic", reason="Plan disposition")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Clean context review passed")
    assert control_plane.get_task(task_id)["state"] == "AWAITING_APPROVAL"

    # 5. Human gate endorsement moves to APPROVED (stage required human decisions)
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="User approved with Proceed")
    assert control_plane.get_task(task_id)["state"] == "APPROVED"

    # 6. Setup worktree and move to IN_WORKTREE
    control_plane.update_worktree(
        task_id=task_id,
        worktree_path=".worktrees/task-test-001",
        worktree_branch="task-test-001",
        worktree_state="written_in_worktree"
    )
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")
    t = control_plane.get_task(task_id)
    assert t["state"] == "IN_WORKTREE"
    assert t["worktree_state"] == "written_in_worktree"


def test_invalid_state_transition_fails(control_plane):
    """Test that jumping directly from INTAKE to IN_WORKTREE is forbidden."""
    task_id = "task-test-002"
    control_plane.create_task(task_id=task_id, title="Invalid Jump Task", runtime_tool="claude")
    
    with pytest.raises(InvalidStateTransition):
        control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="bad-actor", reason="Skipping gates")


def test_verifier_sovereignty_lock_and_violation(control_plane, tmp_path):
    """Test that locked verifiers cannot be mutated without triggering exit/exception."""
    task_id = "task-test-003"
    control_plane.create_task(task_id=task_id, title="Verifier Sovereignty Task", runtime_tool="copilot")
    
    test_file = tmp_path / "test_dummy.py"
    test_file.write_text("def test_ok(): assert True\n", encoding="utf-8")
    
    # Lock verifier
    control_plane.lock_verifiers(task_id=task_id, file_paths=[test_file])
    
    # Verify intact
    assert control_plane.verify_sovereignty(task_id=task_id) is True
    
    # Mutate protected verifier
    test_file.write_text("def test_ok(): assert False # mutated\n", encoding="utf-8")
    
    # Verify raises violation
    with pytest.raises(VerifierSovereigntyViolation):
        control_plane.verify_sovereignty(task_id=task_id)


def test_verification_receipt_generation(control_plane):
    """Test recording a deterministic exit code receipt with token generation."""
    task_id = "task-test-004"
    control_plane.create_task(task_id=task_id, title="Receipt Task", runtime_tool="gemini")
    
    token = control_plane.record_verification_receipt(
        task_id=task_id,
        gate_name="pytest",
        command_executed="pytest tests/test_agent_control.py",
        exit_code=0
    )
    
    assert token.startswith(f"EVO-INTEGRITY-{task_id}-")
    receipts = control_plane.get_verification_receipts(task_id=task_id)
    assert len(receipts) == 1
    assert receipts[0]["gate_name"] == "pytest"
    assert receipts[0]["exit_code"] == 0
    assert receipts[0]["receipt_token"] == token


def test_session_aware_native_detection(monkeypatch):
    """Test detect_intake_mode uses active session environment variables, NOT blind binary presence."""
    # Clear ambient IDE env vars first for clean test isolation
    monkeypatch.delenv("ANTIGRAVITY_AGENT", raising=False)
    monkeypatch.delenv("ANTIGRAVITY_IDE", raising=False)
    monkeypatch.delenv("CLAUDE_CODE_ENTRY", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.delenv("GITHUB_COPILOT_CLI", raising=False)
    monkeypatch.delenv("COPILOT_CLI", raising=False)

    # 1. Claude Code session marker present
    monkeypatch.setenv("CLAUDE_CODE_ENTRY", "1")
    assert detect_intake_mode() == "DEFER_CLAUDE_NATIVE"

    # 2. Antigravity IDE session marker present
    monkeypatch.delenv("CLAUDE_CODE_ENTRY", raising=False)
    monkeypatch.setenv("ANTIGRAVITY_IDE", "1")
    assert detect_intake_mode() == "DEFER_ANTIGRAVITY"

    # 3. Running inside Copilot CLI (even if claude/agy binaries exist on host system)
    monkeypatch.delenv("ANTIGRAVITY_IDE", raising=False)
    monkeypatch.setenv("GITHUB_COPILOT_CLI", "1")
    assert detect_intake_mode() == "EXECUTE_SOCRATIC_FALLBACK"

    # 4. Headless fallback
    monkeypatch.delenv("GITHUB_COPILOT_CLI", raising=False)
    assert detect_intake_mode() == "EXECUTE_SOCRATIC_FALLBACK"


def test_cost_tier_resolution_and_task_columns(control_plane):
    """Test model_tier and model_id columns and ADR-001/004 compliant JSON catalog resolution."""
    task_id = "task-tier-001"
    
    # 1. Resolve recommendation from cheapest_models.json
    rec_low = control_plane.resolve_recommended_model(runtime_tool="copilot", tier="low")
    assert rec_low["model_id"] == "gpt-5.4-nano"
    assert rec_low["tier"] == "low"
    
    rec_high = control_plane.resolve_recommended_model(runtime_tool="copilot", tier="high")
    assert rec_high["model_id"] == "claude-opus-5"
    assert rec_high["tier"] == "high"

    # 2. Create task specifying model_tier and model_id
    control_plane.create_task(
        task_id=task_id,
        title="Cost Tier Task",
        runtime_tool="copilot",
        model_tier="low",
        model_id=rec_low["model_id"]
    )
    
    task = control_plane.get_task(task_id)
    assert task["model_tier"] == "low"
    assert task["model_id"] == "gpt-5.4-nano"


def test_diagnostic_brief_auto_locate(tmp_path):
    """Test that interview_spec_engine locates and parses DIAGNOSTIC_BRIEF.md from exploration."""
    from interview_spec_engine import locate_and_parse_diagnostic_brief
    
    # Missing initially
    assert locate_and_parse_diagnostic_brief(search_dir=tmp_path) is None
    
    # Created in exploration/
    diag_dir = tmp_path / "exploration"
    diag_dir.mkdir(parents=True, exist_ok=True)
    brief_file = diag_dir / "DIAGNOSTIC_BRIEF.md"
    brief_file.write_text(
        "# DIAGNOSTIC BRIEF: Test Task\n"
        "## 1. Coupling Surface\n- `path/a.py`\n"
        "## 2. Hidden Assumptions\n| A | B | C |\n"
        "## 3. Candidate Architectural Forks\n### Fork 1\n",
        encoding="utf-8"
    )
    
    result = locate_and_parse_diagnostic_brief(search_dir=tmp_path)
    assert result is not None
    assert result["has_coupling_surface"] is True
    assert result["has_hidden_assumptions"] is True
    assert result["has_architectural_forks"] is True


def test_transition_to_done_blocked_without_persistence_receipt(control_plane):
    """Test that transitioning to DONE is blocked when verification receipts or persistence logs are missing."""
    task_id = "task-done-guard-001"
    control_plane.create_task(task_id=task_id, title="Done Guard Task", runtime_tool="antigravity")
    
    # Progress through valid steps to VERIFY_EXIT
    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-done-001", worktree_branch="b1", worktree_state="written_in_worktree")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    
    # Attempt transition to RETROSPECTIVE with no receipts or persistence log. The exit guard requires
    # a receipt specifically for gate_name='test_suite' — the human_approval receipt recorded
    # above (needed for the APPROVED->IN_WORKTREE gate) does NOT satisfy this, closing the gap
    # where any unrelated exit_code=0 receipt used to count.
    with pytest.raises(PersistenceInvariantViolation, match="No passing test_suite verification receipt"):
        control_plane.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Attempt complete")

    # Add general test receipt (exit_code=0)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)

    # Still blocked: missing asymmetric persistence log
    with pytest.raises(PersistenceInvariantViolation, match="Asymmetric persistence required"):
        control_plane.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Attempt complete")

    # Add asymmetric persistence log
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="wiki/decisions/2026-09-05-decision.md",
        status="CONFIRMED",
        details="Documented architectural patterns"
    )

    # Still blocked: missing leak check receipt
    with pytest.raises(PersistenceInvariantViolation, match="Missing clean leak check receipt"):
        control_plane.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Attempt complete")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="full_test_suite", command_executed="pytest -q", exit_code=0)
    stage_implementation_ledger(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Exit gates passed")
    stage_human_decisions(control_plane, task_id, "RETROSPECTIVE", "DONE", actor="human", answer="skip")
    with pytest.raises(PersistenceInvariantViolation, match="retrospective is incomplete"):
        control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Attempt without retrospective")


def test_transition_to_done_succeeds_with_valid_receipts_and_wiki_log(control_plane):
    """Test that transition to DONE succeeds when deterministic receipts, persistence log, and leak check exist."""
    task_id = "task-done-success-001"
    control_plane.create_task(task_id=task_id, title="Successful Done Task", runtime_tool="antigravity")
    
    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-done-success", worktree_branch="b2", worktree_state="written_in_worktree")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    
    # Add requirements
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="references/map-debt.md",
        status="RESOLVED",
        details="Resolved debt item"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)

    # Transition through the retrospective gate to DONE succeeds
    complete_retrospective(control_plane, task_id)
    assert control_plane.get_task(task_id)["state"] == "DONE"


def test_transition_to_done_blocked_when_locked_verifier_mutated(control_plane, tmp_path):
    """Test that DONE is blocked if a locked verifier file was mutated, even when every
    other DONE prerequisite (receipts, persistence log) is satisfied."""
    task_id = "task-sovereignty-001"
    control_plane.create_task(task_id=task_id, title="Sovereignty Task", runtime_tool="antigravity")

    verifier_file = tmp_path / "evaluate.py"
    verifier_file.write_text("def evaluate(): return True\n", encoding="utf-8")
    control_plane.lock_verifiers(task_id=task_id, file_paths=[verifier_file])

    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="full_test_suite", command_executed="pytest -q", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)
    stage_implementation_ledger(control_plane, task_id)

    # Mutate the locked verifier after all receipts were stamped
    verifier_file.write_text("def evaluate(): return False  # tampered\n", encoding="utf-8")

    with pytest.raises(VerifierSovereigntyViolation, match="mutated"):
        control_plane.transition(task_id=task_id, to_state="RETROSPECTIVE", actor="controller", reason="Attempt complete")

    # Restore the verifier and confirm DONE now succeeds
    verifier_file.write_text("def evaluate(): return True\n", encoding="utf-8")
    complete_retrospective(control_plane, task_id)
    assert control_plane.get_task(task_id)["state"] == "DONE"


def test_transition_to_rolled_back_requires_asymmetric_persistence(control_plane):
    """Test that transitioning to ROLLED_BACK requires documenting failure mode in asymmetric persistence log."""
    task_id = "task-rollback-guard-001"
    control_plane.create_task(task_id=task_id, title="Rollback Task", runtime_tool="antigravity")
    
    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-rb", worktree_branch="b3", worktree_state="written_in_worktree")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")

    # Attempt rollback without asymmetric persistence log
    with pytest.raises(PersistenceInvariantViolation, match="Asymmetric persistence required"):
        control_plane.transition(task_id=task_id, to_state="ROLLED_BACK", actor="controller", reason="Attempt rollback")

    # Document failure in asymmetric persistence log
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="wiki/decisions/failure-analysis.md",
        status="OBSERVED",
        details="Recorded failure mode learning"
    )

    # Rollback succeeds
    control_plane.transition(task_id=task_id, to_state="ROLLED_BACK", actor="controller", reason="Verified rollback")
    assert control_plane.get_task(task_id)["state"] == "ROLLED_BACK"


def test_evolution_task_blocked_without_prior_art_scan(control_plane):
    """Test that EVOLUTION tasks cannot advance from INTAKE to INTERVIEW without a prior art scan."""
    task_id = "task-evo-gate-001"
    control_plane.create_task(task_id=task_id, title="Evolution Task", runtime_tool="antigravity", task_type="EVOLUTION")

    # Attempt to move to INTERVIEW without logging prior art scan
    with pytest.raises(PersistenceInvariantViolation, match="Prior art scan required"):
        control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="controller", reason="Starting interview")

    # Confirm task remains in INTAKE
    assert control_plane.get_task(task_id)["state"] == "INTAKE"


def test_evolution_task_passes_with_prior_art_scan(control_plane):
    """Test that EVOLUTION tasks advance from INTAKE to INTERVIEW once prior art scan is logged."""
    task_id = "task-evo-gate-002"
    control_plane.create_task(task_id=task_id, title="Evolution Task Passing", runtime_tool="antigravity", task_type="EVOLUTION")

    # Log the prior art scan
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="references/map-debt.md",
        status="OBSERVED",
        details="prior_art_scan: summary=Reviewed map-debt and wiki/decisions — no Repeat:YES blockers; repeat_yes_entries=none"
    )

    # Transition to INTERVIEW succeeds
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="controller", reason="Prior art scanned")
    assert control_plane.get_task(task_id)["state"] == "INTERVIEW"


def test_general_task_advances_without_prior_art_scan(control_plane):
    """Test that GENERAL tasks can advance from INTAKE to INTERVIEW without a prior art scan."""
    task_id = "task-general-gate-001"
    control_plane.create_task(task_id=task_id, title="General Task", runtime_tool="antigravity", task_type="GENERAL")

    # GENERAL tasks do not require prior art scan
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="controller", reason="Starting interview")
    assert control_plane.get_task(task_id)["state"] == "INTERVIEW"


def test_facade_coordinate_transition_records_skip_before_plan_acceptance(control_plane):
    """A review skip is recorded before the PLAN_REVIEW acceptance edge."""
    task_id = "task-facade-skip-review-001"
    control_plane.create_task(task_id=task_id, title="Facade skip_review test", runtime_tool="claude")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="human")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="human", reason="test")

    spec_path = Path(f"docs/plans/{task_id}-spec.md")
    plan_path = Path(f"docs/plans/{task_id}-implementation-plan.md")
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text("spec")
    plan_path.write_text("plan")
    try:
        stage_human_decisions(
            control_plane,
            task_id,
            "DRAFT_PLAN",
            "PLAN_REVIEW",
            answer="No — accept plan as-is and skip independent review [Recommended]",
        )
        control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="human", reason="Plan disposition")
        control_plane.record_review_skip(task_id, "multi_agent_review", "human", "test skip")
        stage_human_decisions(
            control_plane,
            task_id,
            "PLAN_REVIEW",
            "AWAITING_APPROVAL",
            answer="Accept plan and proceed to human approval [Recommended]",
        )
        control_plane.coordinate_transition(
            task_id=task_id, to_state="AWAITING_APPROVAL", actor="human", reason="test",
        )
        assert control_plane.get_task(task_id)["state"] == "AWAITING_APPROVAL"
    finally:
        spec_path.unlink(missing_ok=True)
        plan_path.unlink(missing_ok=True)


def test_facade_rejects_noninteractive_human_provenance(control_plane):
    """The public facade must reject programmatic answers labeled as human input.

    This is the RED provenance contract for Task 1.  The interactive path is the
    only supported source of a human-gated decision; ``--answers --actor human``
    must fail explicitly before a database-trigger error obscures the cause.
    """
    task_id = "task-facade-human-provenance-001"
    control_plane.create_task(task_id=task_id, title="Human provenance test", runtime_tool="claude")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="human")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="human", reason="test")

    spec_path = Path(f"docs/plans/{task_id}-spec.md")
    plan_path = Path(f"docs/plans/{task_id}-implementation-plan.md")
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text("spec")
    plan_path.write_text("plan")
    try:
        stage_human_decisions(
            control_plane,
            task_id,
            "DRAFT_PLAN",
            "PLAN_REVIEW",
            answer="No — accept plan as-is and skip independent review [Recommended]",
        )
        control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="human", reason="Plan disposition")
        control_plane.record_review_skip(task_id, "multi_agent_review", "human", "Test isolates the later human approval boundary")
        stage_human_decisions(
            control_plane,
            task_id,
            "PLAN_REVIEW",
            "AWAITING_APPROVAL",
            answer="Accept plan and proceed to human approval [Recommended]",
        )
        control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="human", reason="Review skipped for provenance test setup")
        with pytest.raises(TransitionCoordinatorError, match="interactive human provenance"):
            control_plane.coordinate_transition(
                task_id=task_id,
                to_state="APPROVED",
                actor="human",
                reason="Programmatic answer must not impersonate human input",
                provided_answers={"human_implementation_approval": "Yes, approve implementation [Recommended]"},
                approval_decision="APPROVAL",
            )
    finally:
        spec_path.unlink(missing_ok=True)
        plan_path.unlink(missing_ok=True)


def test_cli_transition_parsers_accept_skip_review_flags():
    """Regression test: the 'transition' and 'coordinate-transition' argparse subparsers
    must expose --skip-review/--skip-reason — _dispatch_command() reads them via
    getattr(args, "skip_review", False) with a silent False/None fallback, which means
    an unregistered flag doesn't fail loudly; it silently no-ops. A user passing
    --skip-review on the actual CLI got 'unrecognized arguments' before this fix,
    since neither subparser declared the flag at all."""
    from agent_control import _build_parser

    parser = _build_parser()
    for subcommand in ("transition", "coordinate-transition"):
        args = parser.parse_args([
            subcommand, "--task-id", "t1", "--to", "AWAITING_APPROVAL",
            "--skip-review", "--skip-reason", "user requested skip",
        ])
        assert args.skip_review is True
        assert args.skip_reason == "user requested skip"

def test_worktree_post_implementation_review_stage_gate(control_plane):
    """Test transitions through WORKTREE_REVIEW and MULTI_AGENT_CODE_REVIEW before VERIFY_EXIT."""
    task_id = "task-review-gate-001"
    control_plane.create_task(task_id=task_id, title="Review Gate Task", runtime_tool="antigravity")

    # Move to APPROVED -> IN_WORKTREE
    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="Not needed for this test")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    # 1. Implementation done -> transition to WORKTREE_REVIEW
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    stage_human_decisions(control_plane, task_id, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="controller",
        reason="Implementation complete; presenting diff to user"
    )
    assert control_plane.get_task(task_id)["state"] == "WORKTREE_REVIEW"

    # 2. User chooses multi-agent code review -> MULTI_AGENT_CODE_REVIEW
    stage_human_decisions(control_plane, task_id, "WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW")
    control_plane.transition(
        task_id=task_id,
        to_state="MULTI_AGENT_CODE_REVIEW",
        actor="controller",
        reason="Running multi-agent adversarial code review"
    )
    assert control_plane.get_task(task_id)["state"] == "MULTI_AGENT_CODE_REVIEW"

    # 3. Review completed -> can return to WORKTREE_REVIEW or advance to VERIFY_EXIT
    stage_human_decisions(control_plane, task_id, "MULTI_AGENT_CODE_REVIEW", "WORKTREE_REVIEW")
    control_plane.transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="controller",
        reason="Review complete; user authorized merge"
    )
    assert control_plane.get_task(task_id)["state"] == "WORKTREE_REVIEW"

    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_code_review", actor="user", reason="Not needed for this test")
    control_plane.transition(
        task_id=task_id,
        to_state="VERIFY_EXIT",
        actor="controller",
        reason="Ready to verify exit receipts"
    )
    assert control_plane.get_task(task_id)["state"] == "VERIFY_EXIT"


def test_worktree_push_barrier_enforcement(control_plane):
    """Test update_worktree rejects pushed_to_origin until the task actually reaches DONE
    — reaching WORKTREE_REVIEW alone is not sufficient to clear the push barrier."""
    task_id = "task-push-barrier-001"
    control_plane.create_task(task_id=task_id, title="Push Barrier Task", runtime_tool="antigravity")

    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="Not needed for this test")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    # Attempting to set pushed_to_origin while in IN_WORKTREE must fail
    with pytest.raises(PersistenceInvariantViolation, match="Task must be in final state 'DONE' before pushing"):
        control_plane.update_worktree(
            task_id=task_id,
            worktree_path="/tmp/worktree",
            worktree_branch="feat/test",
            worktree_state="pushed_to_origin"
        )

    # Reaching WORKTREE_REVIEW does not clear the push barrier — only DONE does.
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    stage_human_decisions(control_plane, task_id, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="controller",
        reason="Entering post-implementation review"
    )
    with pytest.raises(PersistenceInvariantViolation, match="Task must be in final state 'DONE' before pushing"):
        control_plane.update_worktree(
            task_id=task_id,
            worktree_path="/tmp/worktree",
            worktree_branch="feat/test",
            worktree_state="pushed_to_origin"
        )

    # Only once the task actually reaches DONE does the push barrier clear.
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_code_review", actor="user", reason="Not needed for this test")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Ready to verify exit receipts")
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="references/map-debt.md",
        status="RESOLVED",
        details="Resolved debt item"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)
    complete_retrospective(control_plane, task_id)

    control_plane.update_worktree(
        task_id=task_id,
        worktree_path="/tmp/worktree",
        worktree_branch="feat/test",
        worktree_state="pushed_to_origin"
    )


def _build_legacy_pre_v2_schema(db_path):
    """Builds a pre-schema-version-2 DB: old tasks CHECK constraint (missing
    WORKTREE_REVIEW/task_type), with child tables already referencing tasks(task_id).
    Mirrors this repo's actual historical schema before PR #517."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE tasks (
            task_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            state TEXT NOT NULL CHECK (
                state IN ('INTAKE','INTERVIEW','PLAN_REVIEW','AWAITING_APPROVAL',
                          'APPROVED','IN_WORKTREE','VERIFY_EXIT','DONE','ROLLED_BACK','ESCALATED')
            ),
            runtime_tool TEXT NOT NULL,
            worktree_path TEXT,
            worktree_branch TEXT,
            worktree_state TEXT,
            spec_path TEXT,
            model_tier TEXT,
            model_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE task_transitions (
            transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            from_state TEXT NOT NULL, to_state TEXT NOT NULL, actor TEXT NOT NULL,
            reason TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE locked_verifier_baselines (
            baseline_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            file_path TEXT NOT NULL, expected_sha256 TEXT NOT NULL,
            verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE critic_reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            iteration INTEGER NOT NULL, model_used TEXT NOT NULL, verdict TEXT NOT NULL,
            critique_findings TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE verification_receipts (
            receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            gate_name TEXT NOT NULL, command_executed TEXT NOT NULL, exit_code INTEGER NOT NULL,
            receipt_token TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE asymmetric_persistence_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            destination TEXT NOT NULL, status TEXT NOT NULL, details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
        ("legacy-task-001", "Pre-existing legacy task", "INTAKE", "claude")
    )
    conn.commit()
    conn.close()


def test_self_heal_repairs_legacy_schema_and_preserves_data(temp_db_path):
    """Test that init_db() migrates a legacy pre-v2 schema and preserves existing rows."""
    _build_legacy_pre_v2_schema(temp_db_path)

    cp = ControlPlane(db_path=temp_db_path)
    cp.init_db()

    conn = sqlite3.connect(str(temp_db_path))
    # Data survived the rebuild
    row = conn.execute("SELECT title, state FROM tasks WHERE task_id = ?", ("legacy-task-001",)).fetchone()
    assert row == ("Pre-existing legacy task", "INTAKE")

    # Schema is now current (WORKTREE_REVIEW present, task_type column exists)
    tasks_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone()[0]
    assert "WORKTREE_REVIEW" in tasks_sql
    assert "task_type" in tasks_sql

    # No orphaned migration artifacts remain
    leftover = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_migrating' OR name = '_tasks_old')"
    ).fetchall()
    assert leftover == []

    # A new task_id can be inserted and referenced by a child table without FK errors
    conn.execute("INSERT INTO tasks (task_id, title, state, task_type, runtime_tool) VALUES (?, ?, 'INTAKE', 'GENERAL', ?)",
                 ("new-task-001", "New task", "claude"))
    conn.execute("INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'NONE', 'INTAKE', 'system', 'x')",
                 ("new-task-001",))
    conn.commit()
    conn.close()


def test_self_heal_repairs_dangling_orphaned_tasks_old(temp_db_path):
    """Test that init_db() repairs a DB stuck mid-migration: dangling _tasks_old plus
    child tables whose stored FK still points at _tasks_old (this repo's actual incident)."""
    _build_legacy_pre_v2_schema(temp_db_path)
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("PRAGMA foreign_keys = OFF;")
    # Reproduce the real bug mechanism: renaming `tasks` while child tables reference it
    # forces SQLite to auto-repoint their stored FK clauses to the new name.
    conn.execute("ALTER TABLE tasks RENAME TO _tasks_old;")
    conn.commit()
    conn.close()

    # Sanity check: child tables now really do reference _tasks_old (bug precondition)
    conn = sqlite3.connect(str(temp_db_path))
    child_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='task_transitions'"
    ).fetchone()[0]
    assert "_tasks_old" in child_sql
    conn.close()

    cp = ControlPlane(db_path=temp_db_path)
    cp.init_db()

    conn = sqlite3.connect(str(temp_db_path))
    # tasks table exists again with the legacy row preserved
    row = conn.execute("SELECT title FROM tasks WHERE task_id = ?", ("legacy-task-001",)).fetchone()
    assert row == ("Pre-existing legacy task",)

    # Child table FK now correctly points at tasks, not _tasks_old
    child_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='task_transitions'"
    ).fetchone()[0]
    assert '"_tasks_old"' not in child_sql
    assert "_tasks_old" not in child_sql

    # No orphaned tables remain
    leftover = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_migrating' OR name = '_tasks_old')"
    ).fetchall()
    assert leftover == []

    # A brand-new task can be created via the real API without FK errors (this is the
    # exact failure that blocked TASK-AGENTIC-OS-AUDIT registration this session)
    conn.close()
    cp.create_task(task_id="post-heal-task", title="Post heal", runtime_tool="claude")
    task = cp.get_task("post-heal-task")
    assert task["state"] == "INTAKE"


def test_init_db_idempotent_when_schema_current(control_plane, temp_db_path):
    """Test that calling init_db() again on an already-current schema is a no-op."""
    control_plane.create_task(task_id="idem-task", title="Idempotency check", runtime_tool="claude")
    control_plane.init_db()
    control_plane.init_db()

    conn = sqlite3.connect(str(temp_db_path))
    task = conn.execute("SELECT title FROM tasks WHERE task_id = ?", ("idem-task",)).fetchone()
    assert task == ("Idempotency check",)
    leftover = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_migrating' OR name = '_tasks_old')"
    ).fetchall()
    assert leftover == []
    conn.close()


def test_schema_version_table_present_and_seeded(control_plane, temp_db_path):
    """Test that schema_version table exists with the current version seeded."""
    conn = sqlite3.connect(str(temp_db_path))
    version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION
    conn.close()


def test_gate_allows_draft_plan_entry_after_complete_interview_without_separate_receipt(control_plane):
    """A complete INTERVIEW is sufficient evidence to enter the planning state."""
    task_id = "task-gate-draftplan-001"
    control_plane.create_task(task_id=task_id, title="Gate Draft Plan Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")

    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="claude", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"


def test_gate_any_of_accepts_socratic_receipt_alone(control_plane):
    """Test the socratic_intake_complete receipt independently satisfies the DRAFT_PLAN gate."""
    task_id = "task-gate-socratic-001"
    control_plane.create_task(task_id=task_id, title="Socratic Gate Task", runtime_tool="copilot")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")
    control_plane.record_socratic_intake_complete(task_id=task_id, summary="3 questions answered")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="copilot", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"


def test_plan_review_is_required_before_awaiting_approval(control_plane):
    """The plan branch must converge through PLAN_REVIEW before approval."""
    task_id = "task-gate-approval-001"
    control_plane.create_task(task_id=task_id, title="Gate Approval Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="claude")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="claude", reason="Compiled spec")

    with pytest.raises(InvalidStateTransition):
        control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="claude", reason="Ready")


def test_gate_blocks_in_worktree_entry_without_human_approval_receipt(control_plane):
    """Test APPROVED->IN_WORKTREE requires a recorded human_approval receipt (never skippable)."""
    task_id = "task-gate-humanapproval-001"
    control_plane.create_task(task_id=task_id, title="Gate Human Approval Task", runtime_tool="claude")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Reviewed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Proceed")

    with pytest.raises(PersistenceInvariantViolation, match="human_approval|human approval"):
        control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    control_plane.record_human_approval(task_id=task_id, approver="user")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")
    assert control_plane.get_task(task_id)["state"] == "IN_WORKTREE"


def test_gate_blocks_in_worktree_entry_without_isolated_worktree_metadata(control_plane):
    """APPROVED->IN_WORKTREE requires an isolated path and non-default branch."""
    task_id = "task-gate-worktree-isolation-001"
    control_plane.create_task(task_id=task_id, title="Worktree Isolation Task", runtime_tool="claude")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "controller", "Plan ready")
    control_plane.record_review_skip(task_id, "multi_agent_review", "user", "Not needed for this test")
    stage_human_decisions(
        control_plane,
        task_id,
        "PLAN_REVIEW",
        "AWAITING_APPROVAL",
        answer="Accept plan and proceed to human approval [Recommended]",
    )
    control_plane.transition(task_id, "AWAITING_APPROVAL", "controller", "Review ready")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "user", "Approved")
    control_plane.record_human_approval(task_id, "user")

    with pytest.raises(PersistenceInvariantViolation, match="worktree|branch|isolation"):
        control_plane.transition(task_id, "IN_WORKTREE", "controller", "Worktree created")


def test_gate_allows_explicit_existing_checkout_exception(control_plane, tmp_path):
    """An explicitly recorded exception permits an authorized existing checkout."""
    task_id = "task-gate-worktree-exception-001"
    control_plane.create_task(task_id=task_id, title="Existing Checkout Exception", runtime_tool="claude")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "controller", "Plan ready")
    control_plane.record_review_skip(task_id, "multi_agent_review", "user", "Not needed for this test")
    stage_human_decisions(
        control_plane,
        task_id,
        "PLAN_REVIEW",
        "AWAITING_APPROVAL",
        answer="Accept plan and proceed to human approval [Recommended]",
    )
    control_plane.transition(task_id, "AWAITING_APPROVAL", "controller", "Review ready")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "user", "Approved")
    control_plane.record_human_approval(task_id, "user")
    control_plane.update_worktree(task_id, str(tmp_path), "main", "written_in_worktree")
    control_plane.record_verification_receipt(
        task_id,
        "existing_worktree_exception",
        "approved-existing-checkout:user",
        0,
    )

    control_plane.transition(task_id, "IN_WORKTREE", "controller", "Authorized existing checkout")
    assert control_plane.get_task(task_id)["state"] == "IN_WORKTREE"


def test_gate_blocks_worktree_review_entry_without_test_suite_receipt(control_plane):
    """Test IN_WORKTREE->WORKTREE_REVIEW requires a recorded test_suite verification receipt."""
    task_id = "task-gate-testsuite-001"
    control_plane.create_task(task_id=task_id, title="Gate Test Suite Task", runtime_tool="claude")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Reviewed")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Proceed")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    # Python deterministic check fires first: PersistenceInvariantViolation for missing test_suite
    with pytest.raises(PersistenceInvariantViolation, match="test_suite|test suite"):
        control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    stage_human_decisions(control_plane, task_id, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    assert control_plane.get_task(task_id)["state"] == "WORKTREE_REVIEW"


def test_worktree_review_question_rejects_negative_answer_before_commit(control_plane, tmp_path):
    """A negative review-submission answer must not advance the persisted state."""
    task_id = "task-review-question-answer-001"
    control_plane.repo_root = tmp_path
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "docs" / "plans" / f"{task_id}-spec.md").write_text("# spec", encoding="utf-8")
    (tmp_path / "docs" / "plans" / f"{task_id}-implementation-plan.md").write_text("# plan", encoding="utf-8")
    (tmp_path / ".worktrees" / task_id).mkdir(parents=True)
    control_plane.create_task(task_id=task_id, title="Review question answer", runtime_tool="claude")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    stage_human_decisions(control_plane, task_id, "INTAKE", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "controller", "Plan ready")
    control_plane.record_review_skip(task_id, "multi_agent_review", "user", "Not needed for this test")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id, "AWAITING_APPROVAL", "controller", "Review ready")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "user", "Approved")
    control_plane.record_human_approval(task_id, "user")
    stage_worktree_metadata(control_plane, task_id, path=str(tmp_path / ".worktrees" / task_id), branch=f"worktree-{task_id}")
    control_plane.transition(task_id, "IN_WORKTREE", "controller", "Worktree created")
    control_plane.record_verification_receipt(task_id, "test_suite", "pytest", 0)

    from control_plane.coordinator import TransitionCoordinator

    negative = TransitionCoordinator(
        control_plane,
        input_fn=lambda _prompt: "1",
    )
    with pytest.raises(TransitionCoordinatorError, match="does not authorize"):
        negative.coordinate_transition(
            task_id=task_id,
            to_state="WORKTREE_REVIEW",
            actor="human",
            reason="User declined submission",
            interactive=True,
        )
    assert control_plane.get_task(task_id)["state"] == "IN_WORKTREE"

    positive = TransitionCoordinator(
        control_plane,
        input_fn=lambda _prompt: "2",
    )
    record = positive.coordinate_transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="human",
        reason="User approved submission",
        interactive=True,
    )
    assert record.to_state == "WORKTREE_REVIEW"


def test_transition_race_condition_guarded_by_state_predicate(control_plane, temp_db_path, monkeypatch):
    """Test that a stale internal state read (simulating a concurrent writer changing the
    row between read and write) raises ConcurrentModificationError instead of silently
    clobbering the real state (last-writer-wins)."""
    task_id = "task-race-001"
    control_plane.create_task(task_id=task_id, title="Race Task", runtime_tool="claude")

    # Simulate a concurrent writer having already changed state out from under this
    # transition, by mutating the row directly, then forcing transition()'s internal
    # state-read to return the now-stale value it would have read a moment earlier.
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("UPDATE tasks SET state = 'ESCALATED' WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()

    # issue-524 Step 5 (persistence extraction, revised after external review): this method's
    # signature dropped its `conn` parameter — ControlPlane no longer owns raw connections,
    # it delegates to self._persistence.read_current_state(task_id).
    monkeypatch.setattr(ControlPlane, "_read_current_state_for_update", lambda self, tid: "INTAKE")

    with pytest.raises(ConcurrentModificationError):
        control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Stale write attempt")

    # Real state (ESCALATED) was preserved, not clobbered
    monkeypatch.undo()
    assert control_plane.get_task(task_id)["state"] == "ESCALATED"


def test_schema_rebuild_triggered_by_stale_version_even_with_current_ddl(control_plane, temp_db_path):
    """Test that a stale schema_version.version triggers rebuild even when the tasks DDL
    already looks current (i.e. schema_version actually drives migration, not just DDL-sniffing)."""
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("UPDATE schema_version SET version = 1")
    conn.execute(
        "INSERT INTO tasks (task_id, title, state, task_type, runtime_tool) VALUES (?, ?, 'INTAKE', 'GENERAL', ?)",
        ("version-check-task", "Version Check", "claude")
    )
    conn.commit()
    conn.close()

    control_plane.init_db()

    conn = sqlite3.connect(str(temp_db_path))
    version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION
    # Data survived the version-triggered rebuild
    row = conn.execute("SELECT title FROM tasks WHERE task_id = ?", ("version-check-task",)).fetchone()
    assert row == ("Version Check",)
    conn.close()


def test_concurrent_modification_error_gets_distinct_exit_code():
    """Test that ConcurrentModificationError maps to its own exit code (3), distinguishable
    from a generic crash (1) or a control-plane invariant violation (2) — the one error
    that's explicitly retryable must not be indistinguishable from the others."""
    from agent_control import _map_exception_to_exit_code
    assert _map_exception_to_exit_code(ConcurrentModificationError("stale write")) == 3
    assert _map_exception_to_exit_code(InvalidStateTransition("bad edge")) == 2
    assert _map_exception_to_exit_code(PersistenceInvariantViolation("missing receipt")) == 2
    assert _map_exception_to_exit_code(RuntimeError("unrelated crash")) == 1


def test_migration_swallows_only_duplicate_column_not_other_errors(control_plane, temp_db_path, monkeypatch):
    """Test that SCHEMA_MIGRATIONS only silently ignores 'duplicate column' errors (the
    expected already-migrated case) — any other sqlite3.OperationalError (disk full,
    locked DB, corruption) must propagate instead of being silently swallowed."""
    import sqlite3 as sqlite3_module

    real_connect = sqlite3_module.connect

    class _FailingConn:
        def __init__(self, real_conn):
            self._real = real_conn

        def __getattr__(self, name):
            return getattr(self._real, name)

        def execute(self, sql, *args, **kwargs):
            if sql.strip().upper().startswith("ALTER TABLE"):
                raise sqlite3_module.OperationalError("disk I/O error")
            return self._real.execute(sql, *args, **kwargs)

    def _fake_connect(*args, **kwargs):
        return _FailingConn(real_connect(*args, **kwargs))

    monkeypatch.setattr(sqlite3_module, "connect", _fake_connect)

    with pytest.raises(sqlite3_module.OperationalError, match="disk I/O error"):
        ControlPlane(db_path=temp_db_path).init_db()


def test_critic_review_iteration_not_capped_at_three(control_plane):
    """Test that critic_reviews.iteration allows a 4th+ round — the schema's CHECK(1-3)
    contradicted the documented '1 or N review rounds' design (MULTI_AGENT_REVIEW/
    MULTI_AGENT_CODE_REVIEW support unbounded rounds, not a hardcoded max of 3)."""
    task_id = "task-iteration-cap-001"
    control_plane.create_task(task_id=task_id, title="Iteration Cap Task", runtime_tool="claude")
    for i in range(1, 6):
        control_plane.record_critic_review(
            task_id=task_id, iteration=i, model="gpt-5-mini", verdict="REVISE", findings=f"Round {i}"
        )
    # No exception raised for iteration=4 or 5 — the old CHECK(iteration BETWEEN 1 AND 3)
    # would have raised sqlite3.IntegrityError on the 4th insert.


# ==============================================================================
# issue-529 Slice 1: TransitionRegistry, Schema Conformance & Bidirectional Parity
# ==============================================================================

def test_registry_covers_every_allowed_edge():
    """Test 1: TransitionRegistry loads transition_templates.yaml and covers every
    edge in state_machine.ALLOWED_TRANSITIONS, dynamically — count derived from
    the table itself, not a hardcoded literal (edge count changes whenever
    ALLOWED_TRANSITIONS does, e.g. reset_to_intake's wildcard expansion)."""
    from control_plane.registry import TransitionRegistry
    from control_plane.state_machine import ALLOWED_TRANSITIONS

    expected_edges = set()
    for from_state, to_states in ALLOWED_TRANSITIONS.items():
        for to_state in to_states:
            expected_edges.add((from_state, to_state))

    registry = TransitionRegistry.load_default()
    registered_edges = registry.get_all_edges()

    assert expected_edges == registered_edges
    assert len(registry) == len(expected_edges)


def test_registry_has_no_orphan_entries():
    """Test 2: Every entry in TransitionRegistry must correspond to a legal edge in
    state_machine.ALLOWED_TRANSITIONS (no orphan templates)."""
    from control_plane.registry import TransitionRegistry
    from control_plane.state_machine import ALLOWED_TRANSITIONS

    legal_edges = {
        (from_state, to_state)
        for from_state, to_states in ALLOWED_TRANSITIONS.items()
        for to_state in to_states
    }

    registry = TransitionRegistry.load_default()
    for template in registry.get_all_templates():
        assert (template.from_state, template.to_state) in legal_edges, (
            f"Orphan template '{template.transition_id}' defines non-DAG edge "
            f"({template.from_state} -> {template.to_state})"
        )


def test_registry_no_duplicate_transition_ids_or_edges():
    """Test 3: TransitionRegistry guarantees unique transition_id strings and
    unique (from_state, to_state) edge pairs."""
    from control_plane.registry import TransitionRegistry

    registry = TransitionRegistry.load_default()
    seen_ids = set()
    seen_edges = set()

    for template in registry.get_all_templates():
        assert template.transition_id not in seen_ids, f"Duplicate transition_id: {template.transition_id}"
        edge = (template.from_state, template.to_state)
        assert edge not in seen_edges, f"Duplicate edge: {edge}"
        seen_ids.add(template.transition_id)
        seen_edges.add(edge)


def test_registry_schema_validation_per_entry():
    """Test 4: Every template in TransitionRegistry conforms to the complete 15-field
    schema (including authority) with valid types and non-empty strings where required."""
    from control_plane.registry import TransitionRegistry, REQUIRED_TEMPLATE_FIELDS

    registry = TransitionRegistry.load_default()
    for template in registry.get_all_templates():
        d = template.to_dict()
        for field in REQUIRED_TEMPLATE_FIELDS:
            assert field in d, f"Template '{template.transition_id}' missing field '{field}'"
        assert isinstance(d["checklist"], list) and len(d["checklist"]) > 0
        assert isinstance(d["required_artifacts"], list)
        assert isinstance(d["deterministic_checks"], list)
        assert isinstance(d["human_questions"], list)
        assert isinstance(d["approval"], dict)
        assert isinstance(d["skip"], dict)
        assert isinstance(d["authority"], dict)
        assert isinstance(d["capabilities_released"], list)
        assert isinstance(d["capabilities_prohibited"], list)
        assert isinstance(d["denial_message"], str) and len(d["denial_message"]) > 0
        assert isinstance(d["next_steps_hint"], str) and len(d["next_steps_hint"].strip()) > 0


def test_every_transition_exposes_actionable_yaml_guidance():
    """Every legal edge must explain how to satisfy and invoke its transition."""
    from control_plane.registry import TransitionRegistry

    templates = TransitionRegistry.load_default().get_all_templates()

    assert templates
    for template in templates:
        assert template.next_steps_hint, template.transition_id
        assert "coordinate-transition" in template.next_steps_hint, template.transition_id

    approval = TransitionRegistry.load_default().get_template("APPROVED", "IN_WORKTREE")
    assert "record-human-approval" in approval.next_steps_hint
    assert "--task-id" in approval.next_steps_hint
    assert "--approver" in approval.next_steps_hint


def test_registry_malformed_field_fails_closed(tmp_path):
    """Test 5: TransitionRegistry fails closed with TransitionRegistryError when
    loading malformed YAML or missing required schema fields."""
    from control_plane.registry import TransitionRegistry, TransitionRegistryError

    import yaml

    bad_yaml = tmp_path / "bad_templates.yaml"
    source = yaml.safe_load(
        (SCRIPTS_DIR / "control_plane" / "transition_templates.yaml").read_text(encoding="utf-8")
    )
    bad_yaml.write_text(
        yaml.safe_dump(
            {
                "execution_guidance": source["execution_guidance"],
                "templates": [
                    {
                        "transition_id": "intake_to_interview",
                        "from_state": "INTAKE",
                        "to_state": "INTERVIEW",
                        "purpose": "Begin interview",
                        # Missing required template fields.
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(TransitionRegistryError, match="Missing required field"):
        TransitionRegistry.load_from_file(bad_yaml)


def test_registry_loads_stage_entry_question_contracts():
    """Stage entry questions are distinct from edge transition questions."""
    from control_plane.registry import TransitionRegistry

    registry = TransitionRegistry.load_default()

    interview = registry.get_stage_contract("INTERVIEW")
    assert interview is not None
    assert [q["question_id"] for q in interview["entry_questions"]] == [
        "interview_classification",
        "interview_summary",
        "interview_scope",
        "interview_verification",
    ]
    assert interview["adaptive_follow_up_rules"]
    planning_question = next(
        q for rule in interview["adaptive_follow_up_rules"]
        for q in rule.get("questions", [])
        if q["question_id"] == "interview_planning_model_effort"
    )
    assert planning_question["selection_mode"] == "confirm_or_change"
    assert planning_question["recommendation_source"] == "model_effort_guidance"
    assert planning_question["availability_sources"] == ["os-init", "project-setup", "cli-agents"]
    assert planning_question["complexity_options"]["high"]["recommended_effort"] == "medium"
    assert interview["progress_display"]["enabled"] is True
    assert interview["progress_display"]["count_adaptive_questions"] is True
    assert interview["exit_requirements"]
    trivial_edge = registry.get_template("INTERVIEW", "RETROSPECTIVE")
    assert [q["question_id"] for q in trivial_edge.human_questions] == [
        "confirm_interview_complete"
    ]
    assert trivial_edge.stage_question_ids == [
        "interview_classification",
        "interview_summary",
        "interview_scope",
        "interview_verification",
        "interview_trivial_evidence",
    ]
    assert trivial_edge.stage_route == {
        "question_id": "interview_classification",
        "equals": "TRIVIAL",
    }

    retrospective = registry.get_stage_contract("RETROSPECTIVE")
    assert retrospective is not None
    assert retrospective["entry_questions"]
    assert retrospective["question_policy"] == "one_at_a_time"


def test_closed_check_id_validation():
    """Test 6: All deterministic_checks check IDs declared across all 52 templates
    in transition_templates.yaml must exist in control_plane.policy's check registry."""
    from control_plane.registry import TransitionRegistry
    from control_plane import policy

    registry = TransitionRegistry.load_default()
    declared_check_ids = registry.get_all_declared_check_ids()
    available_check_ids = policy.get_registered_check_ids()

    for check_id in declared_check_ids:
        assert check_id in available_check_ids, (
            f"Check ID '{check_id}' declared in templates but missing from policy check registry"
        )


def test_legacy_policy_migration_parity():
    """Test 7: Every known-gated edge explicitly declares its required deterministic check.
    Guarantees against gate-omission regressions where an edge should be gated but
    deterministic_checks is left empty."""
    from control_plane.registry import TransitionRegistry

    registry = TransitionRegistry.load_default()

    REQUIRED_EDGE_CHECKS = {
        ("INTAKE", "INTERVIEW"): "prior_art_scan",
        ("INTERVIEW", "PLAN_REVIEW"): "plan_mode_or_socratic",
        ("PLAN_REVIEW", "AWAITING_APPROVAL"): "critic_review_or_skip",
        ("APPROVED", "IN_WORKTREE"): "human_approval",
        ("IN_WORKTREE", "WORKTREE_REVIEW"): "test_suite",
        ("WORKTREE_REVIEW", "VERIFY_EXIT"): "code_review_or_skip",
        ("VERIFY_EXIT", "RETROSPECTIVE"): "done_guard",
        ("RETROSPECTIVE", "DONE"): "retrospective_done_guard",
        ("VERIFY_EXIT", "ROLLED_BACK"): "rolled_back_guard",
        ("IN_WORKTREE", "ROLLED_BACK"): "rolled_back_guard",
        ("WORKTREE_REVIEW", "ROLLED_BACK"): "rolled_back_guard",
        ("MULTI_AGENT_CODE_REVIEW", "ROLLED_BACK"): "rolled_back_guard",
    }

    for (from_state, to_state), expected_check in REQUIRED_EDGE_CHECKS.items():
        template = registry.get_template(from_state, to_state)
        assert template is not None, f"No template found for gated edge ({from_state} -> {to_state})"
        assert expected_check in template.deterministic_checks, (
            f"Gated edge ({from_state} -> {to_state}) missing required check '{expected_check}'. "
            f"Found: {template.deterministic_checks}"
        )


def test_action_capability_mapping():
    """Test 8: Releasing inbound edges for all registered action capabilities
    resolve correctly from TransitionRegistry."""
    from control_plane.registry import TransitionRegistry

    registry = TransitionRegistry.load_default()

    interview_edges = registry.get_edges_releasing_capability("interview_question")
    assert ("INTAKE", "INTERVIEW") in interview_edges

    plan_edges = registry.get_edges_releasing_capability("plan_write")
    assert ("INTERVIEW", "DRAFT_PLAN") in plan_edges
    assert ("MULTI_AGENT_REVIEW", "DRAFT_PLAN") in plan_edges

    exit_edges = registry.get_edges_releasing_capability("exit_verification")
    assert ("WORKTREE_REVIEW", "VERIFY_EXIT") in exit_edges


# ==============================================================================
# issue-529 Slice 2: Typed Records, Adapter Read-Back & Multi-Edge Capability Resolution
# ==============================================================================

def test_multi_edge_action_resolution(control_plane):
    """Test 9: Multi-source actions (like plan_write) authorize correctly across
    all valid inbound edges into the destination state (INTERVIEW -> DRAFT_PLAN,
    MULTI_AGENT_REVIEW -> DRAFT_PLAN, etc.)."""
    from control_plane.ports import PhaseCapability

    task_id = "task-slice2-multi-edge-001"
    control_plane.create_task(task_id=task_id, title="Multi Edge Task", runtime_tool="claude")

    # In INTAKE: plan_write must be denied
    with pytest.raises(Exception) as exc_info:
        control_plane.verify_phase_capability(task_id, "plan_write")
    assert "PhaseCapabilityDenied" in type(exc_info.value).__name__

    # Transition INTAKE -> INTERVIEW
    control_plane.transition(task_id, "INTERVIEW", "tester", "Start interview")

    # Still in INTERVIEW: plan_write must be denied
    with pytest.raises(Exception) as exc_info:
        control_plane.verify_phase_capability(task_id, "plan_write")
    assert "PhaseCapabilityDenied" in type(exc_info.value).__name__

    # Satisfy DRAFT_PLAN gate and transition to DRAFT_PLAN
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Enter draft plan")

    # In DRAFT_PLAN via INTERVIEW -> DRAFT_PLAN: plan_write must succeed
    cap = control_plane.verify_phase_capability(task_id, "plan_write")
    assert isinstance(cap, PhaseCapability)
    assert cap.task_id == task_id
    assert cap.action_identity == "plan_write"
    assert cap.current_state == "DRAFT_PLAN"
    assert cap.releasing_edge == ("INTERVIEW", "DRAFT_PLAN")


def test_unregistered_action_identity_denies_closed(control_plane):
    """Test 10: Calling verify_phase_capability with an unregistered or unknown
    action identity must fail closed with PhaseCapabilityDenied, not KeyError."""
    from agent_control import PhaseCapabilityDenied

    task_id = "task-slice2-unregistered-001"
    control_plane.create_task(task_id=task_id, title="Unregistered Action Task", runtime_tool="claude")

    with pytest.raises(PhaseCapabilityDenied, match="Unregistered action identity"):
        control_plane.verify_phase_capability(task_id, "arbitrary_unregistered_action")


def test_get_last_transition_scoped_to_current_occupancy(control_plane):
    """Slice 2 Test: get_last_transition returns the latest transition row for a task,
    reflecting the exact current occupancy and isolating prior occupancies after leave/re-enter."""
    from control_plane.ports import TransitionRecord

    task_id = "task-slice2-occupancy-001"
    control_plane.create_task(task_id=task_id, title="Occupancy Test Task", runtime_tool="claude")

    # Creation transition was NONE -> INTAKE
    t1 = control_plane._persistence.get_last_transition(task_id)
    assert isinstance(t1, TransitionRecord)
    assert t1.task_id == task_id
    assert t1.from_state == "NONE"
    assert t1.to_state == "INTAKE"

    # Transition to INTERVIEW
    control_plane.transition(task_id, "INTERVIEW", "tester", "Move to interview")
    t2 = control_plane._persistence.get_last_transition(task_id)
    assert isinstance(t2, TransitionRecord)
    assert t2.transition_id > t1.transition_id
    assert t2.from_state == "INTAKE"
    assert t2.to_state == "INTERVIEW"

    # Specific edge query: matching edge vs non-matching edge
    match_edge = control_plane._persistence.get_last_transition(task_id, from_state="INTAKE", to_state="INTERVIEW")
    assert match_edge is not None and match_edge.transition_id == t2.transition_id

    no_match = control_plane._persistence.get_last_transition(task_id, from_state="INTERVIEW", to_state="DRAFT_PLAN")
    assert no_match is None


def test_future_capability_denied_until_persisted_transition(control_plane):
    """Regression Test for Slice 2 Capability Resolution:
    GIVEN task state is INTERVIEW
    AND INTERVIEW -> DRAFT_PLAN releases plan_write
    WHEN plan_write is requested before the transition to DRAFT_PLAN
    THEN it is denied.
    THEN prove plan_write succeeds only after a real persisted transition into DRAFT_PLAN.
    """
    from agent_control import PhaseCapabilityDenied
    from control_plane.ports import PhaseCapability

    task_id = "task-slice2-future-cap-001"
    control_plane.create_task(task_id=task_id, title="Future Capability Denial Test", runtime_tool="claude")

    # Move task to INTERVIEW
    control_plane.transition(task_id, "INTERVIEW", "tester", "Start interview")
    assert control_plane._persistence.read_current_state(task_id) == "INTERVIEW"

    # In INTERVIEW, plan_write is a future capability (released by INTERVIEW -> DRAFT_PLAN)
    # verify_phase_capability must fail closed and deny it
    with pytest.raises(PhaseCapabilityDenied) as exc_info:
        control_plane.verify_phase_capability(task_id, "plan_write")
    assert "not authorized in state 'INTERVIEW'" in str(exc_info.value)

    # Now satisfy gate precondition and persist real transition to DRAFT_PLAN
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Enter draft plan")
    assert control_plane._persistence.read_current_state(task_id) == "DRAFT_PLAN"

    # Only after real persisted transition into DRAFT_PLAN does plan_write succeed
    cap = control_plane.verify_phase_capability(task_id, "plan_write")
    assert isinstance(cap, PhaseCapability)
    assert cap.task_id == task_id
    assert cap.action_identity == "plan_write"
    assert cap.current_state == "DRAFT_PLAN"
    assert cap.releasing_edge == ("INTERVIEW", "DRAFT_PLAN")


# ==============================================================================
# issue-529 Slice 3: Atomic Persistence Contracts, Decisions Schema & Recovery Lifecycle
# ==============================================================================

def test_persistence_structural_inconsistency_rejection(control_plane):
    """Test 18: apply_transition_with_receipts rejects structurally inconsistent requests:
    - task state does not match expected_from_state
    - source_occupancy_transition_id does not match latest transition
    - edge is illegal per DAG
    - decision record fields mismatch request (from_state, to_state, occupancy ID)
    - duplicate question_ids exist
    - invalid decision_type
    """
    from control_plane.ports import TransitionCommitRequest, TransitionDecision
    import time

    task_id = "task-slice3-structural-001"
    control_plane.create_task(task_id=task_id, title="Structural Invariant Task", runtime_tool="claude")

    last_trans = control_plane._persistence.get_last_transition(task_id)
    assert last_trans is not None
    occ_id = last_trans.transition_id

    # 1. State mismatch: task is INTAKE, request claims DRAFT_PLAN
    req_bad_state = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="DRAFT_PLAN",
        to_state="PLAN_REVIEW",
        source_occupancy_transition_id=occ_id,
        template_id="draft_plan_to_plan_review",
        actor="tester",
        reason="test",
        staged_decisions=[],
        staged_receipts=[]
    )
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_transition_with_receipts(req_bad_state)
    assert "state mismatch" in str(exc_info.value).lower() or "structural" in str(exc_info.value).lower()

    # 2. Stale occupancy ID: occ_id + 999
    req_stale_occ = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="INTAKE",
        to_state="INTERVIEW",
        source_occupancy_transition_id=occ_id + 999,
        template_id="intake_to_interview",
        actor="tester",
        reason="test",
        staged_decisions=[],
        staged_receipts=[]
    )
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_transition_with_receipts(req_stale_occ)
    assert "occupancy" in str(exc_info.value).lower() or "stale" in str(exc_info.value).lower()

    # 3. Illegal DAG edge: INTAKE -> VERIFY_EXIT (INTAKE's only legal edges are
    # INTERVIEW, DRAFT_PLAN, PLAN_REVIEW, DONE (trivial fast-track), ESCALATED)
    req_illegal_edge = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="INTAKE",
        to_state="VERIFY_EXIT",
        source_occupancy_transition_id=occ_id,
        template_id="intake_to_verify_exit",
        actor="tester",
        reason="test",
        staged_decisions=[],
        staged_receipts=[]
    )
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_transition_with_receipts(req_illegal_edge)
    assert "illegal" in str(exc_info.value).lower() or "edge" in str(exc_info.value).lower()

    # 4. Duplicate question_ids in staged decisions
    d1 = TransitionDecision(
        task_id=task_id,
        source_occupancy_transition_id=occ_id,
        from_state="INTAKE",
        to_state="INTERVIEW",
        question_id="q_duplicate",
        answer="yes",
        decision_type="ANSWER",
        actor="tester",
        recorded_at=time.time()
    )
    d2 = TransitionDecision(
        task_id=task_id,
        source_occupancy_transition_id=occ_id,
        from_state="INTAKE",
        to_state="INTERVIEW",
        question_id="q_duplicate",
        answer="no",
        decision_type="ANSWER",
        actor="tester",
        recorded_at=time.time()
    )
    req_dup_q = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="INTAKE",
        to_state="INTERVIEW",
        source_occupancy_transition_id=occ_id,
        template_id="intake_to_interview",
        actor="tester",
        reason="test",
        staged_decisions=[d1, d2],
        staged_receipts=[]
    )
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_transition_with_receipts(req_dup_q)
    assert "duplicate" in str(exc_info.value).lower()

    # 5. Invalid decision_type
    d_bad_type = TransitionDecision(
        task_id=task_id,
        source_occupancy_transition_id=occ_id,
        from_state="INTAKE",
        to_state="INTERVIEW",
        question_id="q1",
        answer="yes",
        decision_type="INVALID_TYPE",
        actor="tester",
        recorded_at=time.time()
    )
    req_bad_type = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="INTAKE",
        to_state="INTERVIEW",
        source_occupancy_transition_id=occ_id,
        template_id="intake_to_interview",
        actor="tester",
        reason="test",
        staged_decisions=[d_bad_type],
        staged_receipts=[]
    )
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_transition_with_receipts(req_bad_type)
    assert "decision_type" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()


def test_recovery_approval_issuance(control_plane):
    """Test 26: record_recovery_approval persists an unconsumed approval record
    bound to the current occupancy ID and returns a verifiable receipt token."""
    task_id = "task-slice3-recovery-001"
    control_plane.create_task(task_id=task_id, title="Recovery Approval Task", runtime_tool="claude")

    # Move to ESCALATED
    control_plane.transition(task_id, "ESCALATED", "tester", "Escalate task")
    occ_trans = control_plane._persistence.get_last_transition(task_id)
    assert occ_trans.to_state == "ESCALATED"

    token = control_plane._persistence.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ_trans.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="Operator approved de-escalation to INTAKE"
    )
    assert token is not None
    assert len(token) >= 16


def test_recovery_approval_denies_when_stale(control_plane):
    """Test 27: Stale recovery approval (bound to an older occupancy transition ID)
    is denied when attempting a recovery transition after state has moved."""
    task_id = "task-slice3-recovery-stale-001"
    control_plane.create_task(task_id=task_id, title="Stale Recovery Task", runtime_tool="claude")

    # Move to ESCALATED
    control_plane.transition(task_id, "ESCALATED", "tester", "Escalate task")
    t1 = control_plane._persistence.get_last_transition(task_id)

    # Issue approval bound to t1
    token = control_plane._persistence.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="PLAN_REVIEW",
        source_occupancy_transition_id=t1.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="Operator approved move to PLAN_REVIEW"
    )

    # Move task out of ESCALATED to PLAN_REVIEW via normal flow or simulated transition, then re-enter ESCALATED
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "Move to PLAN_REVIEW")
    control_plane.transition(task_id, "ESCALATED", "tester", "Re-escalated")
    t2 = control_plane._persistence.get_last_transition(task_id)
    assert t2.transition_id > t1.transition_id

    # Attempt to apply recovery transition using the old token bound to t1
    with pytest.raises(Exception) as exc_info:
        control_plane._persistence.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="ESCALATED",
            destination_state="PLAN_REVIEW",
            source_occupancy_transition_id=t2.transition_id,
            approval_receipt_token=token,
            actor="admin",
            reason="Attempt recovery with stale approval"
        )
    assert "stale" in str(exc_info.value).lower() or "occupancy" in str(exc_info.value).lower() or "unconsumed" in str(exc_info.value).lower()


def test_exact_recovery_occupancy_binding_after_leave_reenter(control_plane):
    """Test 28: Exact recovery occupancy binding after leave/re-enter.
    An approval granted during occupancy 1 of ESCALATED cannot be reused in occupancy 2."""
    task_id = "task-slice3-leave-reenter-001"
    control_plane.create_task(task_id=task_id, title="Leave Reenter Task", runtime_tool="claude")

    # Occupancy 1: INTAKE -> ESCALATED
    control_plane.transition(task_id, "ESCALATED", "tester", "First escalation")
    occ1 = control_plane._persistence.get_last_transition(task_id)
    token1 = control_plane._persistence.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ1.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="First approval"
    )

    # Leave ESCALATED -> INTAKE
    trans_rec1 = control_plane._persistence.apply_recovery_transition(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ1.transition_id,
        approval_receipt_token=token1,
        actor="admin",
        reason="Recover to INTAKE"
    )
    assert trans_rec1.to_state == "INTAKE"

    # Occupancy 2: Re-enter ESCALATED
    control_plane.transition(task_id, "ESCALATED", "tester", "Second escalation")
    occ2 = control_plane._persistence.get_last_transition(task_id)
    assert occ2.transition_id > occ1.transition_id

    # Trying to reuse token1 in occupancy 2 must fail closed
    with pytest.raises(Exception):
        control_plane._persistence.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="ESCALATED",
            destination_state="INTAKE",
            source_occupancy_transition_id=occ2.transition_id,
            approval_receipt_token=token1,
            actor="admin",
            reason="Reusing token 1"
        )


def test_atomic_recovery_transition_success(control_plane):
    """Test 29: Atomically executing a recovery transition updates task state,
    creates task_transition row, marks approval consumed, and records verification receipt."""
    task_id = "task-slice3-recovery-success-001"
    control_plane.create_task(task_id=task_id, title="Recovery Success Task", runtime_tool="claude")

    control_plane.transition(task_id, "ESCALATED", "tester", "Escalate task")
    occ = control_plane._persistence.get_last_transition(task_id)

    token = control_plane._persistence.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="Approved de-escalation"
    )

    trans_rec = control_plane._persistence.apply_recovery_transition(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ.transition_id,
        approval_receipt_token=token,
        actor="admin",
        reason="Executing recovery transition"
    )
    assert trans_rec.from_state == "ESCALATED"
    assert trans_rec.to_state == "INTAKE"
    assert control_plane._persistence.read_current_state(task_id) == "INTAKE"


def test_recovery_approval_denies_on_sequential_and_concurrent_replay(control_plane):
    """Test 30: Recovery approval token cannot be used twice (sequential replay)
    or concurrently replayed."""
    task_id = "task-slice3-recovery-replay-001"
    control_plane.create_task(task_id=task_id, title="Recovery Replay Task", runtime_tool="claude")

    control_plane.transition(task_id, "ESCALATED", "tester", "Escalate task")
    occ = control_plane._persistence.get_last_transition(task_id)

    token = control_plane._persistence.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="Approved once"
    )

    # First consumption succeeds
    control_plane._persistence.apply_recovery_transition(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ.transition_id,
        approval_receipt_token=token,
        actor="admin",
        reason="First recovery execution"
    )

    # Sequential replay attempt must fail (already consumed)
    with pytest.raises(Exception):
        control_plane._persistence.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="INTAKE",
            destination_state="INTAKE",
            source_occupancy_transition_id=occ.transition_id,
            approval_receipt_token=token,
            actor="admin",
            reason="Replaying same token"
        )

    # Concurrent replay attempt across genuinely separate threads / connections
    task_id_c = "task-slice3-recovery-concurrent-001"
    control_plane.create_task(task_id=task_id_c, title="Concurrent Recovery Task", runtime_tool="claude")
    control_plane.transition(task_id_c, "ESCALATED", "tester", "Escalate task for concurrent test")
    occ_c = control_plane._persistence.get_last_transition(task_id_c)

    token_c = control_plane._persistence.record_recovery_approval(
        task_id=task_id_c,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ_c.transition_id,
        approver="admin",
        decision="APPROVAL",
        reason="Approved once for concurrent race"
    )

    import concurrent.futures
    from control_plane.adapters import SqlitePersistenceAdapter

    db_path = control_plane.db_path

    def run_worker(worker_id: int):
        # Separate persistence adapter and connection per thread
        thread_adapter = SqlitePersistenceAdapter(db_path=db_path, fs_adapter=control_plane._fs)
        try:
            return (
                "SUCCESS",
                thread_adapter.apply_recovery_transition(
                    task_id=task_id_c,
                    expected_source_state="ESCALATED",
                    destination_state="INTAKE",
                    source_occupancy_transition_id=occ_c.transition_id,
                    approval_receipt_token=token_c,
                    actor=f"worker_{worker_id}",
                    reason="Concurrent recovery attempt"
                )
            )
        except Exception as e:
            return ("ERROR", type(e).__name__, str(e))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(run_worker, 1)
        f2 = executor.submit(run_worker, 2)
        r1 = f1.result()
        r2 = f2.result()

    statuses = [r1[0], r2[0]]
    assert statuses.count("SUCCESS") == 1, f"Expected exactly one success, got: r1={r1}, r2={r2}"
    assert statuses.count("ERROR") == 1, f"Expected exactly one error, got: r1={r1}, r2={r2}"


# ==============================================================================
# Slice 4: Action Wrappers, Shadow Writes, and Zero-Side-Effect Enforcement
# ==============================================================================

def test_wrapper_zero_side_effects_on_denial(control_plane, tmp_path):
    """Test 20: When action wrappers are denied, zero protected side effects occur.
    - interview_question wrapper creates NO interview_log row on denial.
    - plan_write wrapper writes NO destination file and leaves NO shadow file on denial.
    - exit_verification wrapper spawns NO subprocess and records NO receipt on denial."""
    from control_plane.wrappers.record_interview_question import record_interview_question
    from control_plane.wrappers.write_plan_document import write_plan_document
    from control_plane.wrappers.run_exit_verification import run_exit_verification

    task_id = "task-slice4-zero-effects-001"
    control_plane.create_task(task_id=task_id, title="Zero Effects Task", runtime_tool="claude")
    # Task is in INTAKE.

    # 1. interview_question wrapper denied in INTAKE
    with pytest.raises(Exception):
        record_interview_question(
            task_id=task_id,
            question="What is the scope?",
            options={"A": "Full", "B": "Partial"},
            recommended="A",
            control_plane=control_plane
        )
    # Verify no log entry in DB
    decisions = control_plane._persistence.get_connection().execute(
        "SELECT COUNT(*) FROM transition_decisions WHERE task_id = ?", (task_id,)
    ).fetchone()[0]
    assert decisions == 0

    # 2. plan_write wrapper denied in INTAKE
    plan_file = tmp_path / "docs" / "plans" / f"{task_id}-spec.md"
    with pytest.raises(Exception):
        write_plan_document(
            task_id=task_id,
            destination_path=plan_file,
            content="# Plan Spec Content",
            control_plane=control_plane
        )
    assert not plan_file.exists()
    # Check no shadow temp files left
    if plan_file.parent.exists():
        shadow_files = list(plan_file.parent.glob("*.tmp*"))
        assert len(shadow_files) == 0

    # 3. exit_verification wrapper denied in INTAKE
    with pytest.raises(Exception):
        run_exit_verification(
            task_id=task_id,
            command=["echo", "unauthorized command execution"],
            gate_name="exit_verification",
            control_plane=control_plane
        )
    receipts = control_plane.get_verification_receipts(task_id)
    assert len(receipts) == 0


def test_wrapper_success_path(control_plane, tmp_path):
    """Test 21: When action wrappers are authorized by current phase occupancy,
    side effects occur and succeed."""
    from control_plane.wrappers.record_interview_question import record_interview_question
    from control_plane.wrappers.write_plan_document import write_plan_document
    from control_plane.wrappers.run_exit_verification import run_exit_verification

    task_id = "task-slice4-success-path-001"
    control_plane.create_task(task_id=task_id, title="Success Path Task", runtime_tool="claude")

    # Move to INTERVIEW (releases interview_question)
    control_plane.transition(task_id, "INTERVIEW", "tester", "Begin interview")
    rec_result = record_interview_question(
        task_id=task_id,
        question="What is the objective?",
        options={"A": "Feature", "B": "Refactor"},
        recommended="A",
        control_plane=control_plane
    )
    assert rec_result["status"] == "RECORDED"
    # Verify row created in transition_decisions or interview log
    conn = control_plane._persistence.get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM transition_decisions WHERE task_id = ? AND decision_type = 'ANSWER'",
        (task_id,)
    ).fetchone()[0]
    assert count == 1
    stored = conn.execute(
        "SELECT answer FROM transition_decisions WHERE task_id = ? ORDER BY decision_id DESC LIMIT 1",
        (task_id,),
    ).fetchone()[0]
    assert stored == "A"
    conn.close()

    # Move to DRAFT_PLAN (releases plan_write)
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Interview complete")

    plan_file = tmp_path / "docs" / "plans" / f"{task_id}-spec.md"
    write_result = write_plan_document(
        task_id=task_id,
        destination_path=plan_file,
        content="# Plan Spec Content Authorized",
        control_plane=control_plane
    )
    assert write_result["status"] == "WRITTEN"
    assert plan_file.exists()
    assert plan_file.read_text(encoding="utf-8") == "# Plan Spec Content Authorized"

    # Move to IN_WORKTREE -> VERIFY_EXIT (releases exit_verification)
    control_plane.record_human_approval(task_id, "approver")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "review")
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "approver", "approved")
    stage_worktree_metadata(control_plane, task_id)
    control_plane.transition(task_id, "IN_WORKTREE", "tester", "created worktree")
    control_plane.transition(task_id, "VERIFY_EXIT", "tester", "running verification")

    exit_res = run_exit_verification(
        task_id=task_id,
        command=["python3", "-c", "print('verification passed')"],
        gate_name="exit_verification",
        control_plane=control_plane
    )
    assert exit_res["exit_code"] == 0
    receipts = control_plane.get_verification_receipts(task_id)
    assert any(r["gate_name"] == "exit_verification" for r in receipts)


def test_plan_write_shadow_file_atomic_replacement(control_plane, tmp_path):
    """Test 22: write_plan_document creates shadow file with O_CREAT | O_EXCL | O_NOFOLLOW,
    verifies capability before write, re-verifies occupancy immediately before os.replace,
    and cleans up shadow file on any error or occupancy change."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_id = "task-slice4-shadow-replace-001"
    control_plane.create_task(task_id=task_id, title="Shadow Replace Task", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Drafting plan")

    plan_file = tmp_path / "docs" / "plans" / f"{task_id}-spec.md"

    # Initial write succeeds
    write_plan_document(
        task_id=task_id,
        destination_path=plan_file,
        content="# Version 1",
        control_plane=control_plane
    )
    assert plan_file.read_text(encoding="utf-8") == "# Version 1"

    # If occupancy changes between start of write and replace, replace is aborted and shadow cleaned up
    # We simulate this by changing task state concurrently or having the pre-replace hook detect stale occupancy
    control_plane.record_human_approval(task_id, "approver")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "moved ahead")

    # Now task is in PLAN_REVIEW (plan_write is no longer authorized)
    with pytest.raises(Exception):
        write_plan_document(
            task_id=task_id,
            destination_path=plan_file,
            content="# Version 2 Overwrite Attempt",
            control_plane=control_plane
        )
    # File must NOT have been overwritten
    assert plan_file.read_text(encoding="utf-8") == "# Version 1"
    # No dangling .tmp shadow files
    assert len(list(plan_file.parent.glob("*.tmp*"))) == 0


def test_interview_wrapper_denies_in_intake_no_log_row(control_plane):
    """Test 23: Original issue #524 bug reproduction.
    Task in INTAKE attempting to record interview question must be denied with no side effects."""
    from control_plane.wrappers.record_interview_question import record_interview_question

    task_id = "task-slice4-524-bug-001"
    control_plane.create_task(task_id=task_id, title="Issue 524 Reproduction", runtime_tool="claude")

    with pytest.raises(Exception):
        record_interview_question(
            task_id=task_id,
            question="Should this work in INTAKE?",
            options={"A": "Yes", "B": "No"},
            recommended="B",
            control_plane=control_plane
        )

    conn = control_plane._persistence.get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM transition_decisions WHERE task_id = ?", (task_id,)
    ).fetchone()[0]
    conn.close()
    assert count == 0


def test_plan_write_wrapper_denies_in_interview_no_file_write(control_plane, tmp_path):
    """Test 24: Issue #529 bug reproduction (opposite direction).
    Task in INTERVIEW attempting to write plan document must be denied with no file created."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_id = "task-slice4-529-bug-001"
    control_plane.create_task(task_id=task_id, title="Issue 529 Reproduction", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Entering interview")

    plan_file = tmp_path / "docs" / "plans" / f"{task_id}-plan.md"

    with pytest.raises(Exception):
        write_plan_document(
            task_id=task_id,
            destination_path=plan_file,
            content="# Malicious or premature plan write",
            control_plane=control_plane
        )

    assert not plan_file.exists()
    if plan_file.parent.exists():
        assert len(list(plan_file.parent.glob("*.tmp*"))) == 0


def test_verify_phase_capability_denies_state_transition_log_inconsistency(control_plane):
    """Test 25: Direct SQL tamper of task state without a corresponding task_transitions
    occupancy entry fails closed with zero side effect."""
    task_id = "task-slice4-tamper-001"
    control_plane.create_task(task_id=task_id, title="Tamper Task", runtime_tool="claude")

    # Manually tamper with task state in DB directly
    conn = control_plane._persistence.get_connection()
    conn.execute("UPDATE tasks SET state = 'DRAFT_PLAN' WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()

    from control_plane.wrappers.write_plan_document import write_plan_document
    with pytest.raises(Exception):
        control_plane.verify_phase_capability(task_id, "plan_write")


def test_plan_write_authorized_bound_spec_and_plan(control_plane, tmp_path):
    """Test that issue-529 can modify its registered spec and implementation plan in DRAFT_PLAN."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_id = "issue-529"
    spec_path = tmp_path / "docs" / "plans" / "issue-529-spec.md"
    plan_path = tmp_path / "docs" / "plans" / "issue-529-implementation-plan.md"

    control_plane.create_task(
        task_id=task_id,
        title="Universal Transition Gate",
        runtime_tool="claude",
        spec_path=str(spec_path),
    )
    control_plane.transition(task_id, "INTERVIEW", "tester", "Interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Drafting plan")

    # 1. Writing registered spec succeeds
    res_spec = write_plan_document(
        task_id=task_id,
        destination_path=spec_path,
        content="# Issue 529 Spec",
        control_plane=control_plane,
    )
    assert res_spec["status"] == "WRITTEN"
    assert spec_path.read_text(encoding="utf-8") == "# Issue 529 Spec"

    # 2. Writing implementation plan succeeds
    res_plan = write_plan_document(
        task_id=task_id,
        destination_path=plan_path,
        content="# Issue 529 Plan",
        control_plane=control_plane,
    )
    assert res_plan["status"] == "WRITTEN"
    assert plan_path.read_text(encoding="utf-8") == "# Issue 529 Plan"


def test_plan_write_denies_another_tasks_plan(control_plane, tmp_path):
    """Test that task A cannot modify task B's plan in DRAFT_PLAN."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_a = "issue-529"
    task_b = "issue-530"

    control_plane.create_task(task_id=task_a, title="Task A", runtime_tool="claude")
    control_plane.transition(task_a, "INTERVIEW", "tester", "Interview")
    control_plane.record_plan_mode_entry(task_a, "tester")
    stage_interview_answers(control_plane, task_a)
    control_plane.transition(task_a, "DRAFT_PLAN", "tester", "Drafting plan")

    foreign_plan = tmp_path / "docs" / "plans" / "issue-530-plan.md"

    with pytest.raises(ValueError, match="does not match authorized task"):
        write_plan_document(
            task_id=task_a,
            destination_path=foreign_plan,
            content="# Unauthorized modification",
            control_plane=control_plane,
        )

    assert not foreign_plan.exists()
    if foreign_plan.parent.exists():
        assert len(list(foreign_plan.parent.glob("*.tmp*"))) == 0


def test_plan_write_denies_traversal_and_external_paths(control_plane, tmp_path):
    """Test that path traversal ('..') and external absolute paths outside repo fail closed."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_id = "issue-529"
    control_plane.create_task(task_id=task_id, title="Task", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Drafting plan")

    # 1. Traversal denial
    traversal_path = tmp_path / "docs" / "plans" / ".." / ".." / f"{task_id}-spec.md"
    with pytest.raises(ValueError, match="traversal"):
        write_plan_document(
            task_id=task_id,
            destination_path=str(traversal_path),
            content="# Traversal attempt",
            control_plane=control_plane,
        )

    # 2. External path outside repo / temp root denial
    external_path = Path("/etc/shadow_plan.md")
    with pytest.raises(ValueError):
        write_plan_document(
            task_id=task_id,
            destination_path=external_path,
            content="# External path attempt",
            control_plane=control_plane,
        )


# ==============================================================================
# Slice 5: Pre-Transition Checklist Coordinator & Single Entry Path
# ==============================================================================

def test_coordinator_interactive_checklist_and_question_flow(control_plane):
    """Test 11: TransitionCoordinator displays checklist, sequentially collects
    question responses, records decisions, and commits transition atomically."""
    import io
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-slice5-interactive-001"
    control_plane.create_task(task_id=task_id, title="Coordinator Task", runtime_tool="claude")

    out = io.StringIO()
    coordinator = TransitionCoordinator(control_plane=control_plane, output_stream=out)

    # Transition INTAKE -> INTERVIEW
    rec = coordinator.coordinate_transition(
        task_id=task_id,
        to_state="INTERVIEW",
        actor="tester",
        reason="Start interview",
    )
    assert rec.from_state == "INTAKE"
    assert rec.to_state == "INTERVIEW"
    output = out.getvalue()
    assert "TRANSITION PROPOSAL: INTAKE -> INTERVIEW" in output
    assert "Checklist:" in output
    assert "Capabilities released:" in output
    assert "interview_question" in output


def test_visible_transition_output_contract(control_plane):
    """Test 12: Visible transition output contains phase, purpose, checklist,
    questions, decisions, released/prohibited capabilities, and transition ID."""
    import io
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-slice5-visible-contract-001"
    control_plane.create_task(task_id=task_id, title="Visible Contract Task", runtime_tool="claude")

    out = io.StringIO()
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=out)

    coord.coordinate_transition(task_id=task_id, to_state="INTERVIEW", actor="tester", reason="interview")
    text = out.getvalue()
    assert "Current phase:   INTAKE" in text
    assert "Requested phase: INTERVIEW" in text
    assert "Purpose:" in text
    assert "Checklist:" in text
    assert "Persisted transition ID:" in text
    assert "Current state verified: INTERVIEW" in text
    assert "Capabilities released:" in text
    assert "Still prohibited:" in text


def test_sequential_question_pacing(control_plane, tmp_path):
    """Test 13: Questions are presented one at a time sequentially rather than batched."""
    import io
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-slice5-pacing-001"
    control_plane.create_task(task_id=task_id, title="Pacing Task", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    control_plane.repo_root = tmp_path

    out = io.StringIO()
    inputs = ["1"]  # review-method answer after entering PLAN_REVIEW
    input_prompts = []

    def mock_input(prompt: str) -> str:
        input_prompts.append(prompt)
        return inputs.pop(0)

    coord = TransitionCoordinator(control_plane=control_plane, input_fn=mock_input, output_stream=out)
    setup_coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda _prompt: "1", output_stream=io.StringIO())
    setup_coord.coordinate_transition(
        task_id=task_id,
        to_state="PLAN_REVIEW",
        actor="human",
        reason="Plan disposition",
        interactive=True,
    )
    rec = coord.coordinate_transition(
        task_id=task_id,
        to_state="MULTI_AGENT_REVIEW",
        actor="tester",
        reason="multi agent review",
        interactive=True,
    )
    assert rec.to_state == "MULTI_AGENT_REVIEW"
    # Verify input prompt was invoked individually
    assert len(input_prompts) == 1
    assert "Select option" in input_prompts[0]


def test_coordinator_rejection_on_failed_check_no_orphan_receipts(control_plane):
    """Test 14: When a deterministic policy check fails, coordinator rejects transition
    and leaves no orphan receipts or partial decisions in persistence."""
    import io
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-slice5-check-fail-001"
    # EVOLUTION task requires prior art scan to leave INTAKE
    control_plane.create_task(
        task_id=task_id, title="Evo Fail Task", runtime_tool="claude", task_type="EVOLUTION"
    )

    out = io.StringIO()
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=out)

    with pytest.raises(TransitionCoordinatorError, match="prior_art_scan"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="INTERVIEW",
            actor="tester",
            reason="Attempt without prior art",
        )

    # Verify no transition happened
    assert control_plane._persistence.read_current_state(task_id) == "INTAKE"
    # Verify no decisions or receipts persisted
    conn = control_plane._persistence.get_connection()
    dec_count = conn.execute("SELECT COUNT(*) FROM transition_decisions WHERE task_id = ?", (task_id,)).fetchone()[0]
    conn.close()
    assert dec_count == 0


def test_coordinator_atomic_rollback_on_concurrency_collision(control_plane):
    """Test 15: If another process modifies state while coordinator is prompting,
    commit_authorized_transition fails closed and rolls back all staged records."""
    from control_plane.coordinator import TransitionCoordinator
    from control_plane.ports import TransitionCommitRequest, TransitionDecision

    task_id = "task-slice5-collision-001"
    control_plane.create_task(task_id=task_id, title="Collision Task", runtime_tool="claude")

    # Stale request pretending task is still in INTAKE with occupancy 999
    req = TransitionCommitRequest(
        task_id=task_id,
        expected_from_state="INTAKE",
        to_state="INTERVIEW",
        source_occupancy_transition_id=999,  # Stale!
        template_id="intake_to_interview",
        actor="tester",
        reason="Concurrent collision",
        staged_decisions=[
            TransitionDecision(
                task_id=task_id,
                source_occupancy_transition_id=999,
                from_state="INTAKE",
                to_state="INTERVIEW",
                question_id="q1",
                answer="ans",
                decision_type="ANSWER",
                actor="tester",
                recorded_at=100.0,
            )
        ],
        staged_receipts=[],
    )

    with pytest.raises(Exception):
        control_plane.commit_authorized_transition(req)

    # State unchanged, no staged decisions committed
    assert control_plane._persistence.read_current_state(task_id) == "INTAKE"
    conn = control_plane._persistence.get_connection()
    count = conn.execute("SELECT COUNT(*) FROM transition_decisions WHERE task_id = ?", (task_id,)).fetchone()[0]
    conn.close()
    assert count == 0


def test_direct_transition_command_routes_through_coordinator(control_plane):
    """Test 16: agent_control.py transition routes through TransitionCoordinator
    and enforces pre-transition policy, checklists, and decisions."""
    task_id = "task-slice5-compat-alias-001"
    control_plane.create_task(task_id=task_id, title="Alias Task", runtime_tool="claude")

    # control_plane.coordinate_transition is the primary orchestration entry point
    rec = control_plane.coordinate_transition(
        task_id=task_id,
        to_state="INTERVIEW",
        actor="tester",
        reason="Testing coordinate_transition",
    )
    assert rec.to_state == "INTERVIEW"
    assert control_plane._persistence.read_current_state(task_id) == "INTERVIEW"


def test_coordinator_refuses_incomplete_request(control_plane, tmp_path):
    """Test 17: TransitionCoordinator refuses to construct a commit request when
    required template questions, approvals, or checks are incomplete."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-slice5-incomplete-001"
    control_plane.create_task(task_id=task_id, title="Incomplete Task", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    control_plane.repo_root = tmp_path
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plans / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer="No — accept plan as-is and skip independent review [Recommended]")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "plan disposition")
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")

    coord = TransitionCoordinator(control_plane=control_plane)

    # AWAITING_APPROVAL -> APPROVED requires explicit approval
    with pytest.raises(TransitionCoordinatorError, match="approval"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="tester",
            reason="Approve without decision",
            approval_decision=None,
            interactive=False,
        )


def test_production_transition_caller_migration_completeness():
    """Test 19: Scans production skills and code to ensure no production code calls raw
    apply_transition outside TransitionCoordinator."""
    import re
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    scripts_dir = repo_root / "plugins" / "agent-agentic-os" / "scripts"

    # Scan python files except tests and ports.py/adapters.py/agent_control.py for raw apply_transition
    for p in scripts_dir.rglob("*.py"):
        if "tests" in p.parts or "adapters.py" in p.name or "agent_control.py" in p.name or "ports.py" in p.name:
            continue
        content = p.read_text(encoding="utf-8")
        assert "apply_transition(" not in content, f"Raw apply_transition found in {p}"


def test_coordinator_allows_interview_to_draft_plan_without_artifacts(control_plane, tmp_path):
    """Plan artifacts are created in DRAFT_PLAN, not required to enter it."""
    import io
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-review-artifact-001"
    control_plane.create_task(task_id=task_id, title="Artifact Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Start interview")
    stage_interview_answers(control_plane, task_id)
    out = io.StringIO()
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=out)

    coord.coordinate_transition(
        task_id=task_id,
        to_state="DRAFT_PLAN",
        actor="tester",
        reason="Enter the plan-authoring state before plan artifacts exist",
    )
    assert control_plane._persistence.read_current_state(task_id) == "DRAFT_PLAN"


def test_coordinator_denies_plan_review_without_draft_artifacts(control_plane, tmp_path):
    """A DRAFT_PLAN cannot be submitted for review until both plan artifacts exist."""
    import io
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-draft-submission-artifact-001"
    control_plane.create_task(task_id=task_id, title="Draft Submission Artifact Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Start interview")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Enter draft plan")
    control_plane.repo_root = tmp_path

    out = io.StringIO()
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=out)
    with pytest.raises(TransitionCoordinatorError, match="[Aa]rtifact|denied"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="tester",
            reason="Submit a draft without its required artifacts",
            interactive=False,
            provided_answers={},
        )

    assert "Missing required artifact" in out.getvalue()
    assert control_plane._persistence.read_current_state(task_id) == "DRAFT_PLAN"


def test_rejected_plan_requires_artifact_revision_before_resubmission(control_plane, tmp_path):
    """A rejected plan cannot be resubmitted with unchanged artifact identities."""
    import io
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-plan-revision-001"
    control_plane.create_task(task_id=task_id, title="Plan Revision Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Start interview")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "Enter draft plan")

    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    spec_path = plan_dir / f"{task_id}-spec.md"
    plan_path = plan_dir / f"{task_id}-implementation-plan.md"
    spec_path.write_text("# Spec v1", encoding="utf-8")
    plan_path.write_text("# Plan v1", encoding="utf-8")
    control_plane.repo_root = tmp_path
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=io.StringIO())
    answers = {"plan_review_disposition": "No — accept plan as-is and skip independent review [Recommended]"}
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer=answers["plan_review_disposition"])

    coord.coordinate_transition(
        task_id=task_id,
        to_state="PLAN_REVIEW",
        actor="tester",
        reason="Submit v1",
        provided_answers=answers,
    )
    revision_answer = "Require further revisions"
    stage_human_decisions(
        control_plane,
        task_id,
        "PLAN_REVIEW",
        "DRAFT_PLAN",
        answer=revision_answer,
    )
    coord.coordinate_transition(
        task_id=task_id,
        to_state="DRAFT_PLAN",
        actor="reviewer",
        reason="Changes requested",
        provided_answers={"confirm_plan_revision": revision_answer},
    )

    with pytest.raises(TransitionCoordinatorError, match="unchanged|revision"):
        stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer=answers["plan_review_disposition"])
        coord.coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="tester",
            reason="Resubmit unchanged v1",
            provided_answers=answers,
        )

    submission = [
        receipt for receipt in control_plane.get_verification_receipts(task_id)
        if receipt["gate_name"] == "plan_artifact_submission"
    ][-1]
    control_plane.record_verification_receipt(
        task_id,
        gate_name="plan_artifact_revision",
        command_executed=submission["command_executed"],
        exit_code=0,
    )
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer=answers["plan_review_disposition"])
    same_identity_record = coord.coordinate_transition(
        task_id=task_id,
        to_state="PLAN_REVIEW",
        actor="tester",
        reason="Resubmit v1 with explicit revision receipt",
        provided_answers=answers,
    )
    assert same_identity_record.to_state == "PLAN_REVIEW"

    stage_human_decisions(
        control_plane,
        task_id,
        "PLAN_REVIEW",
        "DRAFT_PLAN",
        answer=revision_answer,
    )
    coord.coordinate_transition(
        task_id=task_id,
        to_state="DRAFT_PLAN",
        actor="reviewer",
        reason="Changes requested again",
        provided_answers={"confirm_plan_revision": revision_answer},
    )
    plan_path.write_text("# Plan v2", encoding="utf-8")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer=answers["plan_review_disposition"])
    record = coord.coordinate_transition(
        task_id=task_id,
        to_state="PLAN_REVIEW",
        actor="tester",
        reason="Submit revised v2",
        provided_answers=answers,
    )
    assert record.to_state == "PLAN_REVIEW"


def test_coordinator_checklist_evaluator_truthfulness(control_plane, tmp_path):
    """Architecture Review Finding 1: Checklist items must execute deterministic evaluators and never print [✓] without passing."""
    import io
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-review-truthful-001"
    control_plane.create_task(task_id=task_id, title="Truthful Checklist Test", runtime_tool="claude")
    out = io.StringIO()
    coord = TransitionCoordinator(control_plane=control_plane, output_stream=out)

    # Create the required artifacts for INTAKE -> DRAFT_PLAN
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")

    # Set repo_root on control_plane to tmp_path
    control_plane.repo_root = tmp_path

    coord.coordinate_transition(
        task_id=task_id,
        to_state="DRAFT_PLAN",
        actor="tester",
        reason="Transitioning with existing artifacts",
    )
    output = out.getvalue()
    # Output must show evaluated checklist with PASS
    assert "[✓]" in output or "PASS" in output
    assert control_plane._persistence.read_current_state(task_id) == "DRAFT_PLAN"


def test_coordinator_non_interactive_missing_answer_fails_closed_despite_default(control_plane, tmp_path):
    """Architecture Review Finding 2: Missing non-interactive answer fails despite a configured recommended default."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-review-nodefault-001"
    control_plane.create_task(task_id=task_id, title="Default Answer Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    control_plane.repo_root = tmp_path

    coord = TransitionCoordinator(control_plane=control_plane)

    # Transitioning DRAFT_PLAN -> PLAN_REVIEW has questions with recommendations.
    # In non-interactive mode without provided_answers, it MUST fail closed.
    with pytest.raises(TransitionCoordinatorError, match="Missing required response|explicit"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="tester",
            reason="Transitioning without answering question",
            interactive=False,
            provided_answers={},
        )


def test_coordinator_empty_interactive_input_rejected_and_undeclared_option_rejected(control_plane, tmp_path):
    """Architecture Review Finding 2: Empty interactive input does not authorize default, and undeclared options fail."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-review-invalid-ans-001"
    control_plane.create_task(task_id=task_id, title="Interactive Answer Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    control_plane.repo_root = tmp_path

    # 1. Empty input must not silently pick the recommendation
    coord_empty = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: "")
    with pytest.raises(TransitionCoordinatorError, match="Missing required response|Invalid"):
        coord_empty.coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="tester",
            reason="Interactive empty input",
            interactive=True,
        )

    # 2. Undeclared option must be rejected
    coord_bogus = TransitionCoordinator(control_plane=control_plane)
    with pytest.raises(TransitionCoordinatorError, match="Invalid|undeclared|option"):
        coord_bogus.coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="tester",
            reason="Undeclared answer option",
            interactive=False,
            provided_answers={"plan_review_disposition": "Completely Bogus Option"},
        )


def test_coordinator_skip_review_policy_enforcement_and_justification(control_plane):
    """Architecture Review Finding 3: Permitted skip requires explicit selection and justification."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-review-skip-001"
    control_plane.create_task(task_id=task_id, title="Skip Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "plan review")

    coord = TransitionCoordinator(control_plane=control_plane)

    # 1. Skip on PLAN_REVIEW -> AWAITING_APPROVAL without justification must fail
    with pytest.raises(TransitionCoordinatorError, match="not allowed|cannot be skipped"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="AWAITING_APPROVAL",
            actor="tester",
            reason="Skip without reason",
            skip_review=True,
            skip_reason="",
        )

    # 2. Non-skippable edge (e.g. APPROVED -> IN_WORKTREE) must reject skip
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "Valid skip reason")
    stage_human_decisions(
        control_plane,
        task_id,
        "PLAN_REVIEW",
        "AWAITING_APPROVAL",
        answer="Accept plan and proceed to human approval [Recommended]",
    )
    coord.coordinate_transition(
        task_id=task_id,
        to_state="AWAITING_APPROVAL",
        actor="tester",
        reason="Proceed after recorded review skip",
    )
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "admin", "approved")

    with pytest.raises(TransitionCoordinatorError, match="not allowed|cannot be skipped"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="IN_WORKTREE",
            actor="tester",
            reason="Illegal skip on human approval gate",
            skip_review=True,
            skip_reason="Trying to skip human approval",
        )


def test_coordinator_stale_skip_invalidated_after_leave_and_reenter(control_plane):
    """Architecture Review Finding 3: Stale skip decision from previous occupancy is invalidated upon re-entry."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-review-skip-reenter-001"
    control_plane.create_task(task_id=task_id, title="Skip Re-entry Test", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "plan review")

    coord = TransitionCoordinator(control_plane=control_plane)

    # Coordinate transition with valid skip
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "Architecture review approved single-agent bypass")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    rec = coord.coordinate_transition(
        task_id=task_id,
        to_state="AWAITING_APPROVAL",
        actor="tester",
        reason="Valid skip in occupancy 1",
    )
    assert rec.to_state == "AWAITING_APPROVAL"

    # Reject back to DRAFT_PLAN, then back to PLAN_REVIEW (new occupancy)
    control_plane.transition(task_id, "DRAFT_PLAN", "reviewer", "Needs changes")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "Ready for review again")

    # Now attempting to enter AWAITING_APPROVAL without providing new skip or review must fail
    with pytest.raises(TransitionCoordinatorError, match="critic review or explicit recorded skip"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="AWAITING_APPROVAL",
            actor="tester",
            reason="Attempting transition without fresh skip",
            skip_review=False,
        )


def test_wrappers_prohibit_raw_sql_and_private_persistence_attributes():
    """Architecture Review Finding 5: Wrappers must NOT import sqlite3, call get_connection(), or execute raw SQL."""
    from pathlib import Path

    wrappers_dir = Path(__file__).resolve().parent.parent / "scripts" / "control_plane" / "wrappers"
    forbidden_tokens = ["sqlite3", "get_connection", "SELECT ", "INSERT ", "UPDATE ", "DELETE "]

    for wrapper_file in wrappers_dir.glob("*.py"):
        content = wrapper_file.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in content, (
                f"Architecture leak in {wrapper_file.name}: contains forbidden token '{token}'."
            )
        assert "cp._persistence" not in content, (
            f"Architecture leak in {wrapper_file.name}: accesses private cp._persistence directly."
        )


def test_policy_py_contains_no_transition_rules_or_to_state_rules():
    """Architecture Review Finding 6: policy.py must NOT contain TRANSITION_RULES or TO_STATE_RULES."""
    from control_plane import policy

    assert not hasattr(policy, "TRANSITION_RULES"), "policy.py still contains legacy TRANSITION_RULES"
    assert not hasattr(policy, "TO_STATE_RULES"), "policy.py still contains legacy TO_STATE_RULES"
    # Ensure CHECK_REGISTRY and OPERATION_RULES remain
    assert hasattr(policy, "CHECK_REGISTRY"), "policy.py missing CHECK_REGISTRY"
    assert hasattr(policy, "OPERATION_RULES"), "policy.py missing OPERATION_RULES"


def test_plan_writer_strictly_authorizes_registered_artifact_paths_only(control_plane, tmp_path):
    """Architecture Review Finding 7: Writable plan paths restricted to registered artifacts; arbitrary task-prefixed files rejected."""
    from control_plane.wrappers.write_plan_document import write_plan_document

    task_id = "task-review-paths-001"
    control_plane.create_task(
        task_id=task_id,
        title="Path Hardening Task",
        runtime_tool="claude",
        spec_path="docs/plans/task-review-paths-001-spec.md",
    )
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")

    control_plane.repo_root = tmp_path
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)

    # 1. Registered spec path is authorized
    res1 = write_plan_document(
        task_id=task_id,
        destination_path=str(plan_dir / f"{task_id}-spec.md"),
        content="# Registered Spec Content",
        control_plane=control_plane,
    )
    assert res1["status"] == "WRITTEN"

    # 2. Registered implementation plan path is authorized
    res2 = write_plan_document(
        task_id=task_id,
        destination_path=str(plan_dir / f"{task_id}-implementation-plan.md"),
        content="# Registered Plan Content",
        control_plane=control_plane,
    )
    assert res2["status"] == "WRITTEN"

    # 3. Arbitrary task-prefixed file (e.g. task-review-paths-001-arbitrary-notes.md) must be DENIED
    with pytest.raises(ValueError, match="Unregistered plan filename|not authorized"):
        write_plan_document(
            task_id=task_id,
            destination_path=str(plan_dir / f"{task_id}-arbitrary-notes.md"),
            content="# Arbitrary Content",
            control_plane=control_plane,
        )


def test_run_exit_verification_verifier_allowlist_and_worktree_cwd_binding(control_plane, tmp_path):
    """Architecture Review Finding 8: Exit verification requires registered verifier ID, worktree cwd, and allowed gate."""
    from control_plane.wrappers.run_exit_verification import run_exit_verification

    task_id = "task-review-verif-001"
    control_plane.create_task(task_id=task_id, title="Verifier Allowlist Task", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft plan")
    control_plane.repo_root = tmp_path
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plans / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer="No — accept plan as-is and skip independent review [Recommended]")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "plan disposition")
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "admin", "approved")
    control_plane.record_human_approval(task_id, "admin")
    stage_worktree_metadata(control_plane, task_id, path=str(tmp_path / ".worktrees" / task_id), branch=f"worktree-{task_id}")
    control_plane.transition(task_id, "IN_WORKTREE", "developer", "worktree")
    control_plane.record_verification_receipt(task_id, "test_suite", "pytest", 0)
    stage_human_decisions(control_plane, task_id, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(task_id, "WORKTREE_REVIEW", "tester", "review")
    control_plane.record_review_skip(task_id, "multi_agent_code_review", "tester", "skip")
    control_plane.transition(task_id, "VERIFY_EXIT", "tester", "verify exit")

    worktree_dir = tmp_path / ".worktrees" / task_id
    worktree_dir.mkdir(parents=True, exist_ok=True)
    control_plane.update_worktree(task_id, str(worktree_dir), f"worktree-{task_id}", "written_in_worktree")

    # 1. Unregistered verifier ID / arbitrary command rejected
    with pytest.raises(ValueError, match="Unregistered verifier|allowlist"):
        run_exit_verification(
            task_id=task_id,
            verifier_id="unregistered_custom_command",
            control_plane=control_plane,
        )

    # 2. External working directory outside authorized worktree rejected
    external_dir = tmp_path / "outside_worktree"
    external_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError, match="outside authorized worktree"):
        run_exit_verification(
            task_id=task_id,
            verifier_id="pytest_unit_tests",
            cwd=str(external_dir),
            control_plane=control_plane,
        )

    # 3. Spoofed unallowed gate name rejected
    with pytest.raises(ValueError, match="unauthorized gate|not allowed"):
        run_exit_verification(
            task_id=task_id,
            verifier_id="pytest_unit_tests",
            gate_name="arbitrary_spoofed_gate",
            cwd=str(worktree_dir),
            control_plane=control_plane,
        )


def test_transition_templates_semantic_quality_no_boilerplate():
    """Architecture Review Finding 4: All templates must pass the semantic-quality
    contract without generic boilerplate. Sanity count derived dynamically from
    ALLOWED_TRANSITIONS (not hardcoded), since edge count changes whenever that
    table does, e.g. reset_to_intake's wildcard expansion."""
    from control_plane.registry import TransitionRegistry
    from control_plane.state_machine import ALLOWED_TRANSITIONS

    expected_edge_count = sum(len(to_states) for to_states in ALLOWED_TRANSITIONS.values())
    registry = TransitionRegistry.load_default()
    assert len(registry) == expected_edge_count

    forbidden_patterns = [
        "Transition task ",
        "Structural DAG transition from ",
        "is legal",
    ]

    for edge, template in registry._templates_by_edge.items():
        from_st, to_st = edge
        # 1. Purpose must not be generic placeholder
        for pat in forbidden_patterns:
            assert pat not in template.purpose, (
                f"Template {template.transition_id} ({from_st} -> {to_st}) has generic boilerplate purpose: '{template.purpose}'"
            )
        # 2. Authority must be declared
        raw_dict = template.to_dict()
        assert "authority" in raw_dict, f"Template {template.transition_id} missing authority declaration"
        auth = raw_dict["authority"]
        assert auth.get("type") in ("deterministic", "human_decision", "human_review"), (
            f"Template {template.transition_id} invalid authority type: {auth.get('type')}"
        )
        assert len(auth.get("explanation", "")) > 10, (
            f"Template {template.transition_id} authority explanation too short or missing"
        )
        # 3. For human-decision/review edges, real questions must be defined
        if auth.get("type") in ("human_decision", "human_review"):
            assert len(template.human_questions) > 0, (
                f"Template {template.transition_id} requires human decision but has empty human_questions"
            )


def test_coordinator_artifact_resolution_inside_registered_worktree(control_plane, tmp_path):
    """Regression test for coordinator artifact resolution:
    - Required plan files resolved inside the task's registered worktree root
    - Registered worktree directory accepted as a directory artifact
    - Missing artifacts still fail closed
    - Paths outside authorized repository/worktree roots rejected
    """
    import io
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-coord-art-reg-001"
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True)
    worktree_root = repo_root / ".worktrees" / task_id
    worktree_root.mkdir(parents=True)

    spec_file = worktree_root / "docs" / "plans" / f"{task_id}-spec.md"
    plan_file = worktree_root / "docs" / "plans" / f"{task_id}-implementation-plan.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan", encoding="utf-8")

    control_plane.create_task(
        task_id=task_id,
        title="Artifact Resolution Task",
        runtime_tool="claude-code",
        spec_path=str(spec_file),
    )
    control_plane.update_worktree(
        task_id=task_id,
        worktree_path=str(worktree_root),
        worktree_branch=f"worktree-{task_id}",
        worktree_state="written_in_worktree",
    )

    # Move task to WORKTREE_REVIEW
    control_plane.transition(task_id, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id, "tester")
    stage_interview_answers(control_plane, task_id)
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "draft")
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id, "DRAFT_PLAN", "PLAN_REVIEW", answer="No — accept plan as-is and skip independent review [Recommended]")
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "plan disposition")
    control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")
    control_plane.record_human_approval(task_id, "tester")
    stage_human_decisions(control_plane, task_id, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id, "APPROVED", "tester", "approved")
    control_plane.transition(task_id, "IN_WORKTREE", "tester", "in worktree")
    control_plane.record_verification_receipt(task_id, "test_suite", "pytest", 0)
    stage_human_decisions(control_plane, task_id, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(task_id, "WORKTREE_REVIEW", "tester", "to worktree review")

    out = io.StringIO()
    coord = TransitionCoordinator(
        control_plane=control_plane,
        output_stream=out,
        input_fn=lambda prompt: "Yes, multi-agent review — sub-agent (internal) [Recommended]",
    )

    # 1. Successful transition: plan files and worktree directory resolved.
    # A human-gated edge requires a genuine interactive answer (actor='human'), not a
    # programmatically provided_answers dict (actor='agent') — see coordinator.py.
    rec = coord.coordinate_transition(
        task_id=task_id,
        to_state="MULTI_AGENT_CODE_REVIEW",
        actor="tester",
        reason="Proceed with code review",
        interactive=True,
    )
    assert rec.to_state == "MULTI_AGENT_CODE_REVIEW"

    # 2. Missing artifact fails closed
    task_id_missing = "task-coord-art-missing-002"
    control_plane.create_task(task_id=task_id_missing, title="Missing Artifact Task", runtime_tool="claude-code")
    control_plane.update_worktree(
        task_id=task_id_missing,
        worktree_path=str(worktree_root),
        worktree_branch=f"worktree-{task_id_missing}",
        worktree_state="written_in_worktree",
    )
    control_plane.transition(task_id_missing, "INTERVIEW", "tester", "interview")
    control_plane.record_plan_mode_entry(task_id_missing, "tester")
    stage_interview_answers(control_plane, task_id_missing)
    control_plane.transition(task_id_missing, "DRAFT_PLAN", "tester", "draft")
    missing_plans = worktree_root / "docs" / "plans"
    missing_plans.mkdir(parents=True, exist_ok=True)
    missing_spec = missing_plans / f"{task_id_missing}-spec.md"
    missing_plan = missing_plans / f"{task_id_missing}-implementation-plan.md"
    missing_spec.write_text("# temporary setup artifact", encoding="utf-8")
    missing_plan.write_text("# temporary setup artifact", encoding="utf-8")
    stage_human_decisions(control_plane, task_id_missing, "DRAFT_PLAN", "PLAN_REVIEW", answer="No — accept plan as-is and skip independent review [Recommended]")
    control_plane.transition(task_id_missing, "PLAN_REVIEW", "tester", "plan disposition")
    control_plane.record_review_skip(task_id_missing, "multi_agent_review", "tester", "skip")
    control_plane.record_review_skip(task_id_missing, "multi_agent_review", "tester", "skip")
    stage_human_decisions(control_plane, task_id_missing, "PLAN_REVIEW", "AWAITING_APPROVAL", answer="Accept plan and proceed to human approval [Recommended]")
    control_plane.transition(task_id_missing, "AWAITING_APPROVAL", "tester", "awaiting")
    control_plane.record_human_approval(task_id_missing, "tester")
    stage_human_decisions(control_plane, task_id_missing, "AWAITING_APPROVAL", "APPROVED")
    control_plane.transition(task_id_missing, "APPROVED", "tester", "approved")
    control_plane.transition(task_id_missing, "IN_WORKTREE", "tester", "in worktree")
    control_plane.record_verification_receipt(task_id_missing, "test_suite", "pytest", 0)
    stage_human_decisions(control_plane, task_id_missing, "IN_WORKTREE", "WORKTREE_REVIEW")
    control_plane.transition(task_id_missing, "WORKTREE_REVIEW", "tester", "to worktree review")
    missing_spec.unlink()
    missing_plan.unlink()

    with pytest.raises(TransitionCoordinatorError, match="Missing required artifact"):
        coord.coordinate_transition(
            task_id=task_id_missing,
            to_state="MULTI_AGENT_CODE_REVIEW",
            actor="tester",
            reason="Attempt with missing spec/plan",
            provided_answers={"confirm_review_worktree_review_to_multi_agent_code_review": "Yes, multi-agent review — sub-agent (internal) [Recommended]"},
        )

    # 3. Path traversal / outside authorized roots rejected
    assert coord._resolve_artifact_path("docs/plans/../../outside.md", task={"task_id": "t1"}) is None


def test_no_prior_transition_history_has_clear_error_message(control_plane):
    """A task with no capability released yet (occupancy edge NONE -> INTAKE has
    no registered template) must fail closed with a plain-language message,
    not the internal 'No registry template found for inbound edge' phrasing."""
    from agent_control import PhaseCapabilityDenied

    task_id = "task-no-history-001"
    control_plane.create_task(task_id=task_id, title="No History Task", runtime_tool="claude")

    with pytest.raises(PhaseCapabilityDenied) as exc_info:
        control_plane.verify_phase_capability(task_id, "plan_write")

    message = str(exc_info.value)
    assert "no capabilities available" in message.lower()
    assert "no registry template found" not in message.lower()


def test_interview_spec_engine_cli_entrypoint_prints_intake_mode():
    """interview_spec_engine.py must be runnable directly (not just importable)
    and print the detect_intake_mode() result to stdout."""
    import subprocess

    script_path = SCRIPTS_DIR / "interview_spec_engine.py"
    env = {k: v for k, v in os.environ.items() if k not in (
        "GITHUB_COPILOT_CLI", "COPILOT_CLI",
        "CLAUDE_CODE_ENTRY", "CLAUDE_PROJECT_DIR",
        "ANTIGRAVITY_IDE", "ANTIGRAVITY_AGENT",
    )}

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "EXECUTE_SOCRATIC_FALLBACK"


# ==============================================================================
# issue-534/#547: TRIVIAL Triage Fast-Track (INTAKE -> INTERVIEW -> RETROSPECTIVE -> DONE)
# ==============================================================================

def test_trivial_fast_track_enters_retrospective_and_completes(control_plane):
    """A TRIVIAL task skips planning but still enters the mandatory retrospective gate."""
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-trivial-001"
    control_plane.create_task(task_id=task_id, title="Fix typo in error message", runtime_tool="claude")

    control_plane.transition(task_id, "INTERVIEW", "tester", "Begin the interview")
    stage_interview_answers(control_plane, task_id, to_state="RETROSPECTIVE", classification="TRIVIAL")

    # The retrospective transition has authority.type: human_decision — the DB trigger requires
    # a genuine interactive answer (actor='human'), not a programmatically provided_answers
    # dict (actor='agent') — see coordinator.py.
    interview_inputs = iter(["Yes [Recommended]"])
    coord = TransitionCoordinator(
        control_plane=control_plane,
        input_fn=lambda prompt: next(interview_inputs),
    )
    record = coord.coordinate_transition(
        task_id=task_id,
        to_state="RETROSPECTIVE",
        actor="tester",
        reason="TRIVIAL fast-track: one-line typo fix",
        interactive=True,
    )

    assert record.from_state == "INTERVIEW"
    assert record.to_state == "RETROSPECTIVE"

    control_plane.save_retrospective(
        task_id,
        {"decision": "skip", "completion_mode": "skipped", "actor": "human", "skip_reason": "one-line typo"},
        [],
    )
    done_coord = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: "skip")
    done_record = done_coord.coordinate_transition(
        task_id=task_id,
        to_state="DONE",
        actor="tester",
        reason="Retrospective skipped with reason",
        interactive=True,
    )
    assert done_record.to_state == "DONE"

    # No spec/plan artifacts were required or created for this path.
    assert not Path(f"docs/plans/{task_id}-spec.md").exists()
    assert not Path(f"docs/plans/{task_id}-implementation-plan.md").exists()

    # The transition decision is durably recorded for the edge.
    decisions = control_plane._persistence  # PersistencePort; query via raw connection for the assertion
    conn = decisions.get_connection()
    try:
        row = conn.execute(
            "SELECT question_id, answer FROM transition_decisions "
            "WHERE task_id = ? AND to_state = 'RETROSPECTIVE' "
            "AND question_id = 'confirm_interview_complete'",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "confirm_interview_complete"
    assert row[1] == "Yes [Recommended]"


def test_trivial_fast_track_requires_explicit_triage_answer(control_plane):
    """The triage question is the one mandatory, non-skippable step: an empty
    interactive answer or a missing non-interactive answer must fail closed,
    exactly like every other human_questions gate in the coordinator."""
    from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError

    task_id = "task-trivial-002"
    control_plane.create_task(task_id=task_id, title="Fix typo", runtime_tool="claude")
    control_plane.transition(task_id, "INTERVIEW", "tester", "Begin the interview")

    # Non-interactive with no provided answer must fail closed.
    coord = TransitionCoordinator(control_plane=control_plane)
    with pytest.raises(TransitionCoordinatorError, match="Missing required response"):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="RETROSPECTIVE",
            actor="tester",
            reason="attempt without interview completion answer",
            interactive=False,
        )

    # Interactive with empty input must not silently proceed.
    coord_empty = TransitionCoordinator(control_plane=control_plane, input_fn=lambda prompt: "")
    with pytest.raises(TransitionCoordinatorError, match="Missing required response"):
        coord_empty.coordinate_transition(
            task_id=task_id,
            to_state="RETROSPECTIVE",
            actor="tester",
            reason="attempt with empty interview completion answer",
            interactive=True,
        )


def test_trivial_misstriage_escape_hatch_to_escalated(control_plane):
    """If a task is provisionally triaged TRIVIAL but turns out not to be once the
    diff is underway, the existing INTAKE -> ESCALATED edge remains the escape
    hatch — no new edge or mechanism needed for re-triage before committing."""
    from control_plane.coordinator import TransitionCoordinator

    task_id = "task-trivial-escape-001"
    control_plane.create_task(task_id=task_id, title="Looked trivial, wasn't", runtime_tool="claude")

    # Task is still sitting in INTAKE (no trivial-path commitment made yet).
    assert control_plane.get_task(task_id)["state"] == "INTAKE"

    coord = TransitionCoordinator(control_plane=control_plane)
    record = coord.coordinate_transition(
        task_id=task_id,
        to_state="ESCALATED",
        actor="tester",
        reason="Mis-triaged as TRIVIAL; touches shared module, needs full pipeline",
    )

    assert record.from_state == "INTAKE"
    assert record.to_state == "ESCALATED"

    # ESCALATED can still route back into INTAKE for a proper full-pipeline restart.
    stage_human_decisions(control_plane, task_id, "ESCALATED", "INTAKE")
    control_plane.transition(task_id, "INTAKE", "tester", "Restarting via full pipeline")
    assert control_plane.get_task(task_id)["state"] == "INTAKE"


def test_interview_to_retrospective_edge_registered_and_capabilities_scoped(control_plane):
    """The trivial interview edge releases retrospective capture but never push access."""
    from control_plane.registry import TransitionRegistry

    registry = TransitionRegistry.load_default()
    template = registry.get_template("INTERVIEW", "RETROSPECTIVE")

    assert template is not None
    assert template.transition_id == "interview_to_retrospective_trivial"
    assert template.required_artifacts == []
    assert "retrospective_capture" in template.capabilities_released
    assert "push branch to origin" not in template.capabilities_released
    assert "push branch to origin" in template.capabilities_prohibited
