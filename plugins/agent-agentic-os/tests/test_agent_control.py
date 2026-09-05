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
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-done-001", worktree_branch="b1", worktree_state="written_in_worktree")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree isolated")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")
    
    # Attempt transition to DONE with no receipts or persistence log
    with pytest.raises(PersistenceInvariantViolation, match="No passing verification receipt"):
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
    
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-done-success", worktree_branch="b2", worktree_state="written_in_worktree")
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


def test_transition_to_rolled_back_requires_asymmetric_persistence(control_plane):
    """Test that transitioning to ROLLED_BACK requires documenting failure mode in asymmetric persistence log."""
    task_id = "task-rollback-guard-001"
    control_plane.create_task(task_id=task_id, title="Rollback Task", runtime_tool="antigravity")
    
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="system", reason="Spec ready")
    control_plane.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="LGTM")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="critic", reason="Review passed")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="human", reason="Proceed")
    control_plane.update_worktree(task_id=task_id, worktree_path=".worktrees/task-rb", worktree_branch="b3", worktree_state="written_in_worktree")
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

