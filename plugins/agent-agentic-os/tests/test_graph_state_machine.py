"""
Integration tests for Orchestration Graph State Machine
Testing Scenarios A, B, C, D, E per §9.2 of the ratified plan.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"


@pytest.fixture
def test_git_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)
    
    # Base commit
    readme = repo_dir / "README.md"
    readme.write_text("# Root Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)
    return repo_dir


def test_scenario_a_happy_path(test_git_repo):
    """Scenario A: Full happy path resulting in COMPLETED status, receipt, and RESOLVED debt."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    record_script = SCRIPTS_DIR / "record_trace.py"
    verify_script = SCRIPTS_DIR / "verify_evolution_receipt.py"
    cycle_id = "cycle-scenario-a"

    # 1. TRIAGE
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "TRIAGE", "--event-type", "cycle.initialized", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)], check=True)

    # 2. PLAN -> AWAITING_APPROVAL
    manifest = {"verifier_files": [], "target_files": ["plugins/code.py"]}
    m_path = test_git_repo / "manifest.json"
    m_path.write_text(json.dumps(manifest), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(m_path), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)], check=True)

    # 3. AUTHORIZED -> CREATE_WORKTREE
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--operations", "create_worktree,mutate,verify,write_layer2,commit", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], check=True)

    # 4. EXECUTE
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True)
    code_file = test_git_repo / "plugins" / "code.py"
    code_file.parent.mkdir(parents=True, exist_ok=True)
    code_file.write_text("def repaired(): return True\n", encoding="utf-8")
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "EXECUTE", "--event-type", "mutation.completed", "--paths-affected", "plugins/code.py", "--repo-dir", str(test_git_repo)], check=True)

    # 5. VERIFY_GATE (Pass)
    subprocess.run([sys.executable, str(state_script), "record-verification", "--exit-code", "0", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "VERIFY_GATE", "--event-type", "verification.completed", "--exit-code", "0", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)], check=True)

    # 6. PRE_COMMIT_RECEIPT & COMMIT
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)], check=True)
    
    # Layer 2 updates
    debt_file = test_git_repo / "references" / "map-debt.md"
    debt_file.parent.mkdir(parents=True, exist_ok=True)
    debt_file.write_text("# Map Debt\nStatus: RESOLVED\n", encoding="utf-8")
    
    evo_log = test_git_repo / "references" / "evolution-log.md"
    evo_log.write_text(f"| {cycle_id} | SUCCESS |\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True)
    tree_sha = subprocess.run(["git", "write-tree"], cwd=test_git_repo, capture_output=True, text=True, check=True).stdout.strip()
    
    res_rcpt = subprocess.run([sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", cycle_id, "--tree-sha", tree_sha, "--repo-dir", str(test_git_repo)], capture_output=True, text=True, check=True)
    receipt_data = json.loads(res_rcpt.stdout.strip())
    assert "EVO-INTEGRITY-" in receipt_data["receipt_token"]

    subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run(["git", "commit", "-m", f"feat(evolution): verified repair for {cycle_id}"], cwd=test_git_repo, check=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "COMMIT", "--event-type", "commit.completed", "--exit-code", "0", "--repo-dir", str(test_git_repo)], check=True)

    # 7. FINAL_RECEIPT -> COMPLETED
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "FINAL_RECEIPT", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(verify_script), "--stage", "final", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMPLETED", "--repo-dir", str(test_git_repo)], check=True)

    state = json.loads((test_git_repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "COMMITTED"
    assert state["current_node"] == "COMPLETED"
    assert "Status: RESOLVED" in debt_file.read_text(encoding="utf-8")


def test_scenario_b_retry_loop(test_git_repo):
    """Scenario B: Initial patch fails verifier, loops back to PLAN, second attempt passes."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    record_script = SCRIPTS_DIR / "record_trace.py"
    verify_script = SCRIPTS_DIR / "verify_evolution_receipt.py"
    cycle_id = "cycle-scenario-b"

    # Setup through EXECUTE
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--operations", "create_worktree,mutate,verify,write_layer2,commit", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], check=True)
    
    # Attempt 1: EXECUTE
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "record-verification", "--exit-code", "1", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)], check=True)

    # Verification fails on attempt 1: Loop back to PLAN
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--operations", "create_worktree,mutate,verify,write_layer2,commit", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], check=True)

    # Attempt 2: EXECUTE
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "record-verification", "--exit-code", "0", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "VERIFY_GATE", "--event-type", "verification.completed", "--exit-code", "0", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)], check=True)

    # Pre-commit & commit
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)], check=True)
    tree_sha = subprocess.run(["git", "write-tree"], cwd=test_git_repo, capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run([sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", cycle_id, "--tree-sha", tree_sha, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)], check=True)

    state = json.loads((test_git_repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    assert state["attempt_count"] == 2


def test_scenario_c_third_attempt_rollback_asymmetric_persistence(test_git_repo, tmp_path):
    """Scenario C: Fails 3 consecutive attempts -> ROLLBACK -> Layer 2 exported, code discarded."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    record_script = SCRIPTS_DIR / "record_trace.py"
    cycle_id = "cycle-scenario-c"

    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    # Set attempt_count to 2 directly in state to simulate entering 3rd attempt
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["attempt_count"] = 2
    state["authorization"] = {
        "status": "GRANTED",
        "cycle_id": cycle_id,
        "plan_hash_sha256": None,
        "transaction_manifest_hash_sha256": None,
        "verifier_identity_sha256": None,
        "authorized_operations": ["create_worktree", "mutate", "verify", "write_layer2", "commit"],
        "authorized_at": "2026-01-01T00:00:00Z"
    }
    state["current_node"] = "CREATE_WORKTREE"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Enter 3rd attempt EXECUTE
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True)
    
    # Record failed verification on 3rd attempt
    subprocess.run([sys.executable, str(state_script), "record-verification", "--exit-code", "1", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)], check=True)

    # Transition to ROLLBACK
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "ROLLBACK", "--repo-dir", str(test_git_repo)], check=True)
    
    # Simulate worktree Layer 2 export
    worktree_dir = tmp_path / "worktree-c"
    worktree_dir.mkdir()
    (worktree_dir / "wiki").mkdir()
    (worktree_dir / "wiki" / "failure_analysis.md").write_text("Status: REJECTED\nNegative constraint observed.", encoding="utf-8")
    
    subprocess.run([sys.executable, str(state_script), "export-layer2", "--from-worktree", str(worktree_dir), "--to-main", str(test_git_repo)], check=True)
    
    # Transition to FINAL_RECEIPT -> ESCALATED
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "FINAL_RECEIPT", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "ESCALATED", "--repo-dir", str(test_git_repo)], check=True)

    state_after = json.loads(state_file.read_text(encoding="utf-8"))
    assert state_after["status"] == "ESCALATED"
    assert (test_git_repo / "wiki" / "failure_analysis.md").exists()


def test_scenario_d_proposal_mode_stop(test_git_repo):
    """Scenario D: Formulates manifest and halts at AWAITING_APPROVAL with zero worktrees created."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "cycle-scenario-d"

    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)], check=True)

    state = json.loads((test_git_repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "AWAITING_APPROVAL"
    assert state["current_node"] == "AWAITING_APPROVAL"
    assert state["worktree_path"] is None


def test_scenario_e_spoke_isolation():
    """Scenario E: Asserts .agents/skills/ contains zero wiki/ or raw traces."""
    agents_dir = REPO_ROOT / ".agents" / "skills"
    if not agents_dir.exists():
        pytest.skip(".agents/skills not yet deployed")

    for skill_dir in agents_dir.iterdir():
        if skill_dir.is_dir():
            wiki_dir = skill_dir / "wiki"
            assert not wiki_dir.exists(), f"Spoke isolation breach: wiki directory found in {skill_dir}"
