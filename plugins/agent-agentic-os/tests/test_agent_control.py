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
import pytest
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

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
from interview_spec_engine import (
    detect_intake_mode,
)


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

    # 3. Transition to PLAN_REVIEW
    control_plane.record_plan_mode_entry(task_id=task_id, actor="interview-spec")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="interview-spec", reason="4-Pillar Spec compiled")
    assert control_plane.get_task(task_id)["state"] == "PLAN_REVIEW"

    # 4. Critic review passes, move to AWAITING_APPROVAL
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="Spec is solid")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Clean context review passed")
    assert control_plane.get_task(task_id)["state"] == "AWAITING_APPROVAL"

    # 5. Human gate endorsement moves to APPROVED
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
    assert rec_high["model_id"] == "claude-sonnet-5"
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
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-done-001", worktree_branch="b1", worktree_state="written_in_worktree")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    
    # Attempt transition to DONE with no receipts or persistence log. The DONE guard requires
    # a receipt specifically for gate_name='test_suite' — the human_approval receipt recorded
    # above (needed for the APPROVED->IN_WORKTREE gate) does NOT satisfy this, closing the gap
    # where any unrelated exit_code=0 receipt used to count.
    with pytest.raises(PersistenceInvariantViolation, match="No passing test_suite verification receipt"):
        control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Attempt complete")

    # Add general test receipt (exit_code=0)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)

    # Still blocked: missing asymmetric persistence log
    with pytest.raises(PersistenceInvariantViolation, match="Asymmetric persistence required"):
        control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Attempt complete")

    # Add asymmetric persistence log
    control_plane.log_asymmetric_persistence(
        task_id=task_id,
        destination="wiki/decisions/2026-09-05-decision.md",
        status="CONFIRMED",
        details="Documented architectural patterns"
    )

    # Still blocked: missing leak check receipt
    with pytest.raises(PersistenceInvariantViolation, match="Missing clean leak check receipt"):
        control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Attempt complete")


def test_transition_to_done_succeeds_with_valid_receipts_and_wiki_log(control_plane):
    """Test that transition to DONE succeeds when deterministic receipts, persistence log, and leak check exist."""
    task_id = "task-done-success-001"
    control_plane.create_task(task_id=task_id, title="Successful Done Task", runtime_tool="antigravity")
    
    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
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

    # Transition to DONE succeeds
    control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="All exit gates passed")
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
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.record_human_approval(task_id=task_id, approver="human")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)

    # Mutate the locked verifier after all receipts were stamped
    verifier_file.write_text("def evaluate(): return False  # tampered\n", encoding="utf-8")

    with pytest.raises(VerifierSovereigntyViolation, match="mutated"):
        control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Attempt complete")

    # Restore the verifier and confirm DONE now succeeds
    verifier_file.write_text("def evaluate(): return True\n", encoding="utf-8")
    control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="Verifier restored")
    assert control_plane.get_task(task_id)["state"] == "DONE"


def test_transition_to_rolled_back_requires_asymmetric_persistence(control_plane):
    """Test that transitioning to ROLLED_BACK requires documenting failure mode in asymmetric persistence log."""
    task_id = "task-rollback-guard-001"
    control_plane.create_task(task_id=task_id, title="Rollback Task", runtime_tool="antigravity")
    
    control_plane.record_plan_mode_entry(task_id=task_id, actor="system")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
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


def test_worktree_post_implementation_review_stage_gate(control_plane):
    """Test transitions through WORKTREE_REVIEW and MULTI_AGENT_CODE_REVIEW before VERIFY_EXIT."""
    task_id = "task-review-gate-001"
    control_plane.create_task(task_id=task_id, title="Review Gate Task", runtime_tool="antigravity")

    # Move to APPROVED -> IN_WORKTREE
    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="Not needed for this test")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    # 1. Implementation done -> transition to WORKTREE_REVIEW
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="controller",
        reason="Implementation complete; presenting diff to user"
    )
    assert control_plane.get_task(task_id)["state"] == "WORKTREE_REVIEW"

    # 2. User chooses multi-agent code review -> MULTI_AGENT_CODE_REVIEW
    control_plane.transition(
        task_id=task_id,
        to_state="MULTI_AGENT_CODE_REVIEW",
        actor="controller",
        reason="Running multi-agent adversarial code review"
    )
    assert control_plane.get_task(task_id)["state"] == "MULTI_AGENT_CODE_REVIEW"

    # 3. Review completed -> can return to WORKTREE_REVIEW or advance to VERIFY_EXIT
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
    """Test update_worktree rejects pushed_to_origin if task is still in IN_WORKTREE."""
    task_id = "task-push-barrier-001"
    control_plane.create_task(task_id=task_id, title="Push Barrier Task", runtime_tool="antigravity")

    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="Not needed for this test")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    # Attempting to set pushed_to_origin while in IN_WORKTREE must fail
    with pytest.raises(PersistenceInvariantViolation, match="Post-implementation review stage gate required"):
        control_plane.update_worktree(
            task_id=task_id,
            worktree_path="/tmp/worktree",
            worktree_branch="feat/test",
            worktree_state="pushed_to_origin"
        )

    # Transition to WORKTREE_REVIEW clears the push barrier
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(
        task_id=task_id,
        to_state="WORKTREE_REVIEW",
        actor="controller",
        reason="Entering post-implementation review"
    )
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
    assert version == 2
    conn.close()


def test_gate_blocks_draft_plan_entry_without_plan_mode_or_socratic_proof(control_plane):
    """Test INTERVIEW->DRAFT_PLAN is blocked without a plan_mode_entry or socratic receipt."""
    task_id = "task-gate-draftplan-001"
    control_plane.create_task(task_id=task_id, title="Gate Draft Plan Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")

    with pytest.raises(PersistenceInvariantViolation, match="Plan Mode|Socratic"):
        control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="claude", reason="Compiled spec")

    control_plane.record_plan_mode_entry(task_id=task_id, actor="claude")
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="claude", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"


def test_gate_any_of_accepts_socratic_receipt_alone(control_plane):
    """Test the socratic_intake_complete receipt independently satisfies the DRAFT_PLAN gate."""
    task_id = "task-gate-socratic-001"
    control_plane.create_task(task_id=task_id, title="Socratic Gate Task", runtime_tool="copilot")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")
    control_plane.record_socratic_intake_complete(task_id=task_id, summary="3 questions answered")
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="copilot", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"


def test_gate_blocks_awaiting_approval_without_critic_review_or_skip(control_plane):
    """Test DRAFT_PLAN->AWAITING_APPROVAL requires either a critic PASS or an explicit recorded skip."""
    task_id = "task-gate-approval-001"
    control_plane.create_task(task_id=task_id, title="Gate Approval Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="claude")
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="claude", reason="Compiled spec")

    with pytest.raises(PersistenceInvariantViolation, match="critic review|skip"):
        control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="claude", reason="Ready")

    # An explicit recorded skip (not a critic review) satisfies the gate
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="Not needed this time")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="claude", reason="Ready")
    assert control_plane.get_task(task_id)["state"] == "AWAITING_APPROVAL"


def test_gate_blocks_in_worktree_entry_without_human_approval_receipt(control_plane):
    """Test APPROVED->IN_WORKTREE requires a recorded human_approval receipt (never skippable)."""
    task_id = "task-gate-humanapproval-001"
    control_plane.create_task(task_id=task_id, title="Gate Human Approval Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Reviewed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Proceed")

    with pytest.raises(PersistenceInvariantViolation, match="human_approval|human approval"):
        control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")
    assert control_plane.get_task(task_id)["state"] == "IN_WORKTREE"


def test_gate_blocks_worktree_review_entry_without_test_suite_receipt(control_plane):
    """Test IN_WORKTREE->WORKTREE_REVIEW requires a recorded test_suite verification receipt."""
    task_id = "task-gate-testsuite-001"
    control_plane.create_task(task_id=task_id, title="Gate Test Suite Task", runtime_tool="claude")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Reviewed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Proceed")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")

    with pytest.raises(PersistenceInvariantViolation, match="test_suite|test suite"):
        control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    assert control_plane.get_task(task_id)["state"] == "WORKTREE_REVIEW"


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

    monkeypatch.setattr(ControlPlane, "_read_current_state_for_update", lambda self, conn, tid: "INTAKE")

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
