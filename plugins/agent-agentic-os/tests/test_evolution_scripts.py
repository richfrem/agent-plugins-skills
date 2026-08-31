"""
Unit tests for evolution scripts:
- evolution_state.py
- record_trace.py
- verify_evolution_receipt.py
- export_upstream_pr.py
- evaluate.py (--decision-only)
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"


@pytest.fixture
def test_git_repo(tmp_path):
    """Initializes a clean git repository in tmp_path for testing."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)
    
    # Create an initial file and commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)
    
    return repo_dir


# ============================================================================
# evolution_state.py Tests
# ============================================================================

def test_evolution_state_initializes_in_proposal_mode(test_git_repo):
    """Verifies attempt_count: 0, current_node: TRIAGE, status: IN_PROGRESS."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-001"
    res = subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0, f"init failed: {res.stderr}"
    
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    assert state_file.exists()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["cycle_id"] == cycle_id
    assert state["attempt_count"] == 0
    assert state["current_node"] == "TRIAGE"
    assert state["status"] == "IN_PROGRESS"
    assert state["authorization"]["status"] == "PENDING"


def test_proposal_mode_forbids_worktree_creation_before_authorize(test_git_repo):
    """Asserts transition --to CREATE_WORKTREE fails without prior authorize."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-002"
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    # Attempt to transition straight to CREATE_WORKTREE
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode != 0
    assert "Authorization required" in res.stderr or "Illegal transition" in res.stderr or res.returncode == 1


def test_atomic_state_transitions(test_git_repo):
    """Validates state transition DAG and asserts illegal transitions exit with code 1."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-003"
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # TRIAGE -> PLAN
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    
    # PLAN -> AWAITING_APPROVAL
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0

    # Illegal transition: AWAITING_APPROVAL -> COMMIT should fail
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 1

    # Authorize
    res = subprocess.run(
        [sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id,
         "--operations", "create_worktree,mutate,verify,write_layer2,commit",
         "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0

    # AUTHORIZED -> CREATE_WORKTREE
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0

    # CREATE_WORKTREE -> EXECUTE
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0

    # Illegal transition: EXECUTE directly to COMMIT must fail with code 1
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 1


def test_verifier_sovereignty_guard(test_git_repo):
    """Asserts mutating verifier scripts (evaluate.py, tests, policies) aborts execution with integrity exit code 2."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-004"
    
    # Create fake verifier file
    verifier = test_git_repo / "evaluate.py"
    verifier.write_text("# baseline verifier", encoding="utf-8")
    
    # Save plan with verifier
    manifest = {
        "verifier_files": ["evaluate.py"],
        "target_files": ["some_code.py"]
    }
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Mutate verifier maliciously
    verifier.write_text("# tampered verifier exit 0", encoding="utf-8")

    # Authorize & try to execute; verifier check should abort with exit code 2
    subprocess.run(
        [sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id,
         "--operations", "create_worktree,mutate,verify,write_layer2,commit",
         "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 2, f"Expected exit code 2 on verifier tampering, got {res.returncode}. Output: {res.stderr}"


def test_evolution_state_blocks_commit_without_pre_commit_receipt(test_git_repo):
    """Asserts transition --to COMMIT is rejected if pre_commit_receipt_token is null."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-005"
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id,
         "--operations", "create_worktree,mutate,verify,write_layer2,commit",
         "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    # Stamp controller verification provenance
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["verification_provenance"] = {
        "source": "controller",
        "attempt": 1,
        "exit_code": 0,
        "verifier_argv_sha256": "abc",
        "at": "2026-08-30T00:00:00Z"
    }
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Try COMMIT without setting receipt
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 1
    assert "pre_commit_receipt_token" in res.stderr or "receipt" in res.stderr.lower()


def test_evolution_state_blocks_commit_without_commit_in_authorization(test_git_repo):
    """Asserts transition --to COMMIT is rejected if commit is missing from authorized_operations."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-006"
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    # Authorize WITHOUT commit
    subprocess.run(
        [sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id,
         "--operations", "create_worktree,mutate,verify,write_layer2",
         "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    # Stamp controller verification provenance
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["verification_provenance"] = {
        "source": "controller",
        "attempt": 1,
        "exit_code": 0,
        "verifier_argv_sha256": "abc",
        "at": "2026-08-30T00:00:00Z"
    }
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    subprocess.run(
        [sys.executable, str(state_script), "set-receipt", "--stage", "pre-commit", "--token", "EVO-INTEGRITY-006-abc", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Try COMMIT
    res = subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 1
    assert "commit" in res.stderr.lower()


def test_evolution_state_sets_recovery_required_on_ambiguous_git_state(test_git_repo):
    """Simulates unresolvable git status during recovery; asserts status is set to RECOVERY_REQUIRED."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-007"
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Simulate dirty uncommitted changes not recorded in manifest
    untracked = test_git_repo / "untracked_unrecorded.txt"
    untracked.write_text("mystery file", encoding="utf-8")
    
    # Run recovery
    res = subprocess.run(
        [sys.executable, str(state_script), "recover", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["status"] == "RECOVERY_REQUIRED" or state["current_node"] == "RECOVERY_REQUIRED"


def test_advisory_lock_concurrency(test_git_repo):
    """Asserts a second concurrent init call fails while the lock is held."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id_1 = "test-cycle-008a"
    cycle_id_2 = "test-cycle-008b"
    
    res1 = subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id_1, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res1.returncode == 0

    # Second concurrent init while lock is held (lock_pid is active)
    res2 = subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id_2, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res2.returncode != 0
    assert "lock" in res2.stderr.lower()


def test_crash_recovery_cleans_or_resumes(test_git_repo):
    """Simulates interrupted session; asserts clean recovery according to deterministic evidence tree."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    record_script = SCRIPTS_DIR / "record_trace.py"
    cycle_id = "test-cycle-009"
    
    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    # Record only cycle.initialized
    subprocess.run(
        [sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "TRIAGE",
         "--event-type", "cycle.initialized", "--exit-code", "0", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Run recover: should cleanly reset to TRIAGE
    res = subprocess.run(
        [sys.executable, str(state_script), "recover", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["current_node"] == "TRIAGE"
    assert state["status"] == "IN_PROGRESS"


def test_layer2_survives_worktree_teardown_on_rollback(test_git_repo, tmp_path):
    """(R1 Contract Test) Simulates 3rd attempt failure in worktree; asserts Layer 2 knowledge files are durably transferred to main repository checkout before worktree deletion."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-cycle-010"
    
    # Create fake worktree directory
    worktree_dir = tmp_path / "fake-worktree"
    worktree_dir.mkdir()
    
    # In worktree, create Layer 2 wiki notes and map-debt.md
    wiki_file = worktree_dir / "wiki" / "failure_insight.md"
    wiki_file.parent.mkdir(parents=True, exist_ok=True)
    wiki_file.write_text("# Failure Playbook\nStatus: REJECTED\nRoot Cause: Negative constraint identified.", encoding="utf-8")
    
    debt_file = worktree_dir / "references" / "map-debt.md"
    debt_file.parent.mkdir(parents=True, exist_ok=True)
    debt_file.write_text("# Map Debt\nStatus: OPEN, Repeat: YES", encoding="utf-8")
    
    # Main repo currently does not have these
    assert not (test_git_repo / "wiki" / "failure_insight.md").exists()
    
    # Run export-layer2
    res = subprocess.run(
        [sys.executable, str(state_script), "export-layer2",
         "--from-worktree", str(worktree_dir),
         "--to-main", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0, f"export-layer2 failed: {res.stderr}"
    
    # Verify main repo has the files preserved
    main_wiki = test_git_repo / "wiki" / "failure_insight.md"
    main_debt = test_git_repo / "references" / "map-debt.md"
    assert main_wiki.exists()
    assert "Status: REJECTED" in main_wiki.read_text(encoding="utf-8")
    assert main_debt.exists()
    assert "Status: OPEN, Repeat: YES" in main_debt.read_text(encoding="utf-8")


# ============================================================================
# record_trace.py Tests
# ============================================================================

def test_cycle_manifest_schema_and_hash_chaining(test_git_repo):
    """Validates schema v1.1.0, event sequencing, previous-hash chaining, and timestamped event IDs."""
    record_script = SCRIPTS_DIR / "record_trace.py"
    cycle_id = "test-cycle-011"
    
    # Append event 1 (genesis)
    res1 = subprocess.run(
        [sys.executable, str(record_script), "append",
         "--cycle-id", cycle_id, "--node", "TRIAGE", "--event-type", "cycle.initialized",
         "--exit-code", "0", "--paths-affected", "plugins/test.py", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res1.returncode == 0, f"event 1 failed: {res1.stderr}"
    
    # Append event 2
    res2 = subprocess.run(
        [sys.executable, str(record_script), "append",
         "--cycle-id", cycle_id, "--node", "PLAN", "--event-type", "plan.completed",
         "--exit-code", "0", "--paths-affected", "plugins/test.py", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res2.returncode == 0, f"event 2 failed: {res2.stderr}"
    
    manifest_file = test_git_repo / ".agent" / "learning" / "traces" / "cycle_manifests.jsonl"
    assert manifest_file.exists()
    lines = [json.loads(l) for l in manifest_file.read_text(encoding="utf-8").strip().split("\n")]
    assert len(lines) == 2
    
    e1, e2 = lines[0], lines[1]
    assert e1["schema_version"] == "1.1.0"
    assert e1["event_seq"] == 1
    assert e1["previous_event_hash"] == "0" * 64
    assert re.match(r"^evt-[a-f0-9]{8}-[a-zA-Z0-9_-]{4,16}$", e1["event_id"])
    
    assert e2["event_seq"] == 2
    assert e2["previous_event_hash"] == e1["event_hash"]
    assert e2["event_hash"] != e1["event_hash"]


def test_raw_telemetry_gitignored_and_scrubbed(test_git_repo):
    """Validates that raw stdout/stderr is placed in gitignored directory and scrubbed for secrets."""
    record_script = SCRIPTS_DIR / "record_trace.py"
    cycle_id = "test-cycle-012"
    
    secret_text = "SECRET_KEY=sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456789 and http://user:pass@github.com/repo"
    res = subprocess.run(
        [sys.executable, str(record_script), "append",
         "--cycle-id", cycle_id, "--node", "EXECUTE", "--event-type", "mutation.completed",
         "--exit-code", "0", "--stdout-text", secret_text, "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    
    raw_dir = test_git_repo / ".agent" / "learning" / "traces" / "raw" / cycle_id
    assert raw_dir.exists()
    stdout_files = list(raw_dir.glob("*_stdout.log"))
    assert len(stdout_files) >= 1
    content = stdout_files[0].read_text(encoding="utf-8")
    
    # Secret should be scrubbed
    assert "sk-ant-api03-" not in content
    assert "[REDACTED" in content or "REDACTED" in content


# ============================================================================
# verify_evolution_receipt.py Tests
# ============================================================================

def test_pre_commit_receipt_blocks_commit_if_trace_missing(test_git_repo):
    """Asserts pre-commit validation fails if no event was recorded."""
    verify_script = SCRIPTS_DIR / "verify_evolution_receipt.py"
    cycle_id = "test-cycle-013"
    
    res = subprocess.run(
        [sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode != 0
    assert "trace" in res.stderr.lower() or "manifest" in res.stderr.lower() or "no events" in res.stderr.lower()


def test_cycle_bound_hash_detects_tampering(test_git_repo):
    """Asserts altering event data, cycle ID, or verifier exit code invalidates receipt token."""
    record_script = SCRIPTS_DIR / "record_trace.py"
    verify_script = SCRIPTS_DIR / "verify_evolution_receipt.py"
    cycle_id = "test-cycle-014"
    
    # Record an event
    subprocess.run(
        [sys.executable, str(record_script), "append",
         "--cycle-id", cycle_id, "--node", "VERIFY_GATE", "--event-type", "verification.completed",
         "--exit-code", "0", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True
    )
    
    # Generate receipt
    res = subprocess.run(
        [sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", cycle_id,
         "--tree-sha", "0123456789abcdef0123456789abcdef01234567", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    receipt_data = json.loads(res.stdout.strip())
    token = receipt_data["receipt_token"]
    
    # Tamper with the manifest file
    manifest_file = test_git_repo / ".agent" / "learning" / "traces" / "cycle_manifests.jsonl"
    lines = manifest_file.read_text(encoding="utf-8").strip().split("\n")
    e = json.loads(lines[0])
    e["exit_code"] = 1  # tampered!
    manifest_file.write_text(json.dumps(e) + "\n", encoding="utf-8")
    
    # Verify again - must fail validation
    res2 = subprocess.run(
        [sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", cycle_id,
         "--token", token, "--tree-sha", "0123456789abcdef0123456789abcdef01234567", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res2.returncode != 0
    assert "tamper" in res2.stderr.lower() or "invalid" in res2.stderr.lower() or "mismatch" in res2.stderr.lower()


def test_asymmetric_persistence_verification(test_git_repo):
    """Asserts code clean + wiki modified passes; uncommitted code modifications fail."""
    verify_script = SCRIPTS_DIR / "verify_evolution_receipt.py"
    cycle_id = "test-cycle-015"
    
    # Case 1: uncommitted code changes in plugins/
    bad_code = test_git_repo / "plugins" / "bad.py"
    bad_code.parent.mkdir(parents=True, exist_ok=True)
    bad_code.write_text("broken()", encoding="utf-8")
    
    res = subprocess.run(
        [sys.executable, str(verify_script), "--check-asymmetric", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode != 0
    
    # Clean code, leave only wiki/ modified
    bad_code.unlink()
    wiki = test_git_repo / "wiki" / "note.md"
    wiki.parent.mkdir(parents=True, exist_ok=True)
    wiki.write_text("# Knowledge", encoding="utf-8")
    
    res2 = subprocess.run(
        [sys.executable, str(verify_script), "--check-asymmetric", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res2.returncode == 0


# ============================================================================
# export_upstream_pr.py Tests
# ============================================================================

def test_export_pr_defaults_to_dry_run(test_git_repo):
    """Asserts running without --execute outputs simulated diff and touches zero git remotes."""
    export_script = SCRIPTS_DIR / "export_upstream_pr.py"
    
    res = subprocess.run(
        [sys.executable, str(export_script), "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    assert "DRY RUN" in res.stdout or "dry-run" in res.stdout.lower()


def test_export_pr_allowlist_sanitization(test_git_repo):
    """Asserts non-plugin files and credentials are strictly excluded."""
    export_script = SCRIPTS_DIR / "export_upstream_pr.py"
    
    # Create an unauthorized file outside plugins/
    secret_file = test_git_repo / ".env"
    secret_file.write_text("API_SECRET=supersecret\n", encoding="utf-8")
    
    res = subprocess.run(
        [sys.executable, str(export_script), "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True
    )
    assert "API_SECRET" not in res.stdout
    assert ".env" not in res.stdout


# ============================================================================
# evaluate.py Decision-Only Mode Test
# ============================================================================

def test_evaluate_decision_only_does_not_touch_git(test_git_repo, monkeypatch):
    """Executes evaluate.py --decision-only; asserts metrics/exit codes are returned without modifying git worktree."""
    evaluate_script = SCRIPTS_DIR / "evaluate.py"
    
    # Set up mock skill folder with results.tsv
    skill_dir = test_git_repo / "plugins" / "test-plugin" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    
    # SKILL.md
    (skill_dir / "SKILL.md").write_text("---\nname: test-skill\ndescription: A test skill\n---\n# Test", encoding="utf-8")
    # evals.json
    (evals_dir / "evals.json").write_text(json.dumps([{"query": "test", "should_trigger": True}]), encoding="utf-8")
    # baseline in results.tsv
    (evals_dir / "results.tsv").write_text(
        "timestamp\tcommit\tscore\tbaseline\taccuracy\theuristic\tf1\tstatus\tdescription\n"
        "2026-01-01T00:00:00\t0000000\t0.9000\t0.9000\t0.9000\t0.9000\t0.9000\tBASELINE\tinitial baseline\n",
        encoding="utf-8"
    )
    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add test skill"], cwd=test_git_repo, check=True, capture_output=True)
    
    # Mutate SKILL.md with lower quality or bad content
    (skill_dir / "SKILL.md").write_text("Mutated bad content without frontmatter", encoding="utf-8")
    status_before = subprocess.run(["git", "status", "--porcelain"], cwd=test_git_repo, capture_output=True, text=True).stdout
    assert "M " in status_before or " M" in status_before
    
    # Run evaluate.py with --decision-only
    res = subprocess.run(
        [sys.executable, str(evaluate_script), "--skill", str(skill_dir), "--decision-only"],
        capture_output=True, text=True, cwd=test_git_repo
    )
    
    # With bad content, it should DISCARD (exit 1)
    # BUT the mutated file should NOT have been reverted because of --decision-only
    assert res.returncode == 1
    content_after = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert content_after == "Mutated bad content without frontmatter", "File should not be reverted under --decision-only"


# ============================================================================
# Corrective Hardening Pass Negative-Capability Tests (Opus/GPT Directives)
# ============================================================================

def test_controller_executes_verifier_not_selfreport(test_git_repo):
    """T1 (Closes I1): Controller executes declared verifier command itself; caller-supplied exit codes are rejected/ignored."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t1"
    
    # 1. Init
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    # Create failing verifier script in repo
    verifier_script = test_git_repo / "failing_verifier.py"
    verifier_script.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "add failing verifier"], cwd=test_git_repo, check=True)
    
    # 2. Plan with verifier command
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({
        "verifier_files": ["failing_verifier.py"],
        "verifier_argv": [sys.executable, str(verifier_script)],
        "mutation_targets": ["README.md"]
    }), encoding="utf-8")
    
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(test_git_repo)], check=True)
    
    # Run the controller's verify command (controller executes verifier itself)
    verify_res = subprocess.run([sys.executable, str(state_script), "verify", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    # The verifier fails with exit 1
    assert verify_res.returncode != 0 or "failed" in verify_res.stdout.lower() or "exit code: 1" in verify_res.stdout.lower()
    
    # Ensure attempting transition to PRE_COMMIT_RECEIPT fails because the controller detected failure
    res = subprocess.run([sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    assert res.returncode != 0, "Controller must NOT allow transition to PRE_COMMIT_RECEIPT when verifier failed"


def test_undeclared_verifier_mutation_aborts_exit_2(test_git_repo):
    """T2 (Closes I2): Mutating an undeclared baseline protected file aborts cycle with exit code 2."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t2"
    
    # Create baseline protected file in repo
    eval_file = test_git_repo / "evaluate.py"
    eval_file.write_text("# evaluate logic\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "add evaluate"], cwd=test_git_repo, check=True)
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    # Manifest has EMPTY verifier_files
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({
        "verifier_files": [],
        "mutation_targets": ["README.md"]
    }), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    # Tamper with evaluate.py (which was not in manifest verifier_files!)
    eval_file.write_text("# HACKED evaluate logic\n", encoding="utf-8")
    
    # Next guarded transition must fail with exit code 2
    res = subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    assert res.returncode == 2, f"Expected exit code 2 on verifier tampering, got {res.returncode}: {res.stderr}"


def test_default_protected_set_is_immutable(test_git_repo):
    """T3 (Closes I2 Breadth): Verifies default protected set encompasses policies and evaluators."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t3"
    
    policy_file = test_git_repo / ".agent" / "rules" / "self-evolution-policy.md"
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    policy_file.write_text("# Self Evolution Policy\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "add policy"], cwd=test_git_repo, check=True)
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({"verifier_files": []}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    # Tamper with policy file
    policy_file.write_text("# Tampered policy\n", encoding="utf-8")
    res = subprocess.run([sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    assert res.returncode == 2, "Mutating default policy must trigger exit code 2"


def test_attempt_four_transition_rejected_and_forces_rollback(test_git_repo):
    """T4 (Closes I3): Programmatically rejects transition to PLAN when attempt_count >= 3."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t4"
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({"verifier_files": []}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["current_node"] = "VERIFY_GATE"
    state["attempt_count"] = 3
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    
    # Attempting to loop back to PLAN on attempt 3 must be REJECTED
    res = subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    assert res.returncode != 0, "Controller must reject transition to PLAN when attempt_count >= 3"
    assert "attempt" in res.stderr.lower() or "attempt" in res.stdout.lower() or "limit" in res.stderr.lower() or "rollback" in res.stderr.lower()


def test_commit_rejects_forged_or_stale_receipt_token(test_git_repo):
    """T5 (Closes I7 / C4): Controller re-verifies cryptographic receipt against git write-tree; rejects arbitrary strings."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t5"
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({"verifier_files": []}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["current_node"] = "PRE_COMMIT_RECEIPT"
    state["pre_commit_receipt_token"] = "EVO-INTEGRITY-fake-arbitrary-token"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    
    # Attempt COMMIT with forged token
    res = subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(test_git_repo)], capture_output=True, text=True)
    assert res.returncode != 0, "COMMIT must reject forged or non-verified receipt token"


def test_record_trace_cannot_write_state_directly(test_git_repo):
    """T6 (Closes Single-Writer / C6): Trace recording routes state events under controller lock."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    trace_script = SCRIPTS_DIR / "record_trace.py"
    cycle_id = "test-harden-t6"
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    
    # Call record_trace to log an event
    res = subprocess.run([
        sys.executable, str(trace_script),
        "append",
        "--event-type", "cycle.initialized",
        "--cycle-id", cycle_id,
        "--node", "TRIAGE",
        "--repo-dir", str(test_git_repo)
    ], capture_output=True, text=True)
    assert res.returncode == 0, f"record_trace failed: {res.stderr}"
    
    # Assert record_trace did not mutate evolution_state.json directly
    # Controller must enforce single-writer; record_trace only emits trace artifacts
    content = trace_script.read_text(encoding="utf-8")
    assert "evolution_state.json" not in content, "record_trace.py must NOT write or open evolution_state.json directly"


def test_layer2_survives_a_following_git_checkout_on_rollback(test_git_repo):
    """T7 (Closes I4 / R1 Residual): Exported Layer 2 knowledge survives a following git checkout -- . in main repo."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t7"
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    # Simulate worktree with Layer 2 knowledge
    worktree_dir = test_git_repo.parent / "wt-t7"
    worktree_dir.mkdir(parents=True, exist_ok=True)
    (worktree_dir / "wiki").mkdir(parents=True, exist_ok=True)
    (worktree_dir / "wiki" / "hardened_learnings.md").write_text("# Hardened Learnings\nCritical insight.\n", encoding="utf-8")
    (worktree_dir / "map-debt.md").write_text("# Map Debt\nUnresolved issue.\n", encoding="utf-8")
    
    # Export Layer 2 with commit-knowledge
    subprocess.run([
        sys.executable, str(state_script), "export-layer2",
        "--cycle-id", cycle_id,
        "--from-worktree", str(worktree_dir),
        "--to-main", str(test_git_repo),
        "--commit-knowledge"
    ], check=True)
    
    # Now simulate a following aggressive git checkout / reset in main checkout
    subprocess.run(["git", "checkout", "--", "."], cwd=test_git_repo, check=True)
    subprocess.run(["git", "clean", "-fd"], cwd=test_git_repo, check=True)
    
    # The exported wiki and map-debt files must survive on knowledge/<cycle_id> branch
    show = subprocess.run(["git", "show", f"knowledge/{cycle_id}:wiki/hardened_learnings.md"], cwd=test_git_repo, capture_output=True, text=True)
    assert "Critical insight." in show.stdout, "Layer 2 knowledge must survive git checkout and git clean on knowledge branch"


def test_replan_invalidates_authorization(test_git_repo):
    """T8 (Bonus / Closes I5): Mutating the transaction manifest invalidates prior authorization."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-harden-t8"
    
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)], check=True)
    
    manifest_v1 = test_git_repo / "manifest_v1.json"
    manifest_v1.write_text(json.dumps({"mutation_targets": ["fileA.txt"]}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_v1), "--repo-dir", str(test_git_repo)], check=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--repo-dir", str(test_git_repo)], check=True)
    
    # Re-plan with different manifest targets
    manifest_v2 = test_git_repo / "manifest_v2.json"
    manifest_v2.write_text(json.dumps({"mutation_targets": ["fileB.txt", "fileC.txt"]}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_v2), "--repo-dir", str(test_git_repo)], check=True)
    
    # Assert authorization status is now INVALIDATED in state
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["authorization"]["status"] == "INVALIDATED", f"Expected INVALIDATED on re-plan, got {state['authorization']['status']}"


def test_selfreport_cannot_drive_pre_commit_receipt(test_git_repo):
    """V1: record-verification (self-report) must NOT satisfy the PRE_COMMIT_RECEIPT gate."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-v1-selfreport"

    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id,
                    "--repo-dir", str(test_git_repo)], check=True, capture_output=True)
    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({"verifier_files": []}), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file),
                    "--repo-dir", str(test_git_repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id,
                    "--repo-dir", str(test_git_repo)], check=True, capture_output=True)

    # Drive to VERIFY_GATE via legal transitions.
    state_file = test_git_repo / ".agent" / "learning" / "evolution_state.json"
    for node in ["CREATE_WORKTREE", "EXECUTE", "VERIFY_GATE"]:
        subprocess.run([sys.executable, str(state_script), "transition", "--to", node,
                        "--repo-dir", str(test_git_repo)], check=True, capture_output=True)

    # Attacker path: self-report a passing exit code.
    subprocess.run([sys.executable, str(state_script), "record-verification",
                    "--exit-code", "0", "--repo-dir", str(test_git_repo)],
                   capture_output=True, text=True)

    # Gate MUST reject: no controller-executed provenance exists for this attempt.
    res = subprocess.run([sys.executable, str(state_script), "transition",
                          "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(test_git_repo)],
                         capture_output=True, text=True)
    assert res.returncode != 0, "Self-reported exit code must NOT drive PRE_COMMIT_RECEIPT"
    assert "provenance" in res.stderr.lower() or "self-report" in res.stderr.lower() \
        or "controller-executed" in res.stderr.lower()

    # And confirm the field was never written authoritatively.
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state.get("verification_provenance") in (None, {}), \
        "record-verification must not write verification_provenance"


def test_layer2_commits_to_knowledge_branch_not_main(test_git_repo):
    """V2: --commit-knowledge commits to knowledge/<cid>; main HEAD and working tree untouched."""
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-v2-knowledge"

    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", cycle_id,
                    "--repo-dir", str(test_git_repo)], check=True, capture_output=True)

    main_head_before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=test_git_repo,
                                      capture_output=True, text=True).stdout.strip()

    worktree_dir = test_git_repo.parent / "wt-v2"
    (worktree_dir / "wiki").mkdir(parents=True, exist_ok=True)
    (worktree_dir / "wiki" / "hardened_learnings.md").write_text(
        "# Hardened Learnings\nStatus: REJECTED\nCritical insight.\n", encoding="utf-8")
    (worktree_dir / "map-debt.md").write_text(
        "# Map Debt\nStatus: OPEN, Repeat: YES\n", encoding="utf-8")

    subprocess.run([sys.executable, str(state_script), "export-layer2",
                    "--cycle-id", cycle_id, "--commit-knowledge",
                    "--from-worktree", str(worktree_dir),
                    "--to-main", str(test_git_repo)], check=True, capture_output=True)

    # 1. knowledge/<cid> branch exists and carries the content.
    br = subprocess.run(["git", "branch", "--list", f"knowledge/{cycle_id}"],
                        cwd=test_git_repo, capture_output=True, text=True)
    assert f"knowledge/{cycle_id}" in br.stdout
    show = subprocess.run(["git", "show", f"knowledge/{cycle_id}:wiki/hardened_learnings.md"],
                          cwd=test_git_repo, capture_output=True, text=True)
    assert "Status: REJECTED" in show.stdout

    # 2. main HEAD unchanged (nothing committed to main).
    main_head_after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=test_git_repo,
                                     capture_output=True, text=True).stdout.strip()
    assert main_head_after == main_head_before, "export-layer2 must NOT commit to main"

    # 3. main working tree does not carry the exported wiki file.
    assert not (test_git_repo / "wiki" / "hardened_learnings.md").exists()

    # 4. Durability: destructive ops on main cannot erase branch content.
    subprocess.run(["git", "checkout", "--", "."], cwd=test_git_repo, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=test_git_repo, capture_output=True)
    show2 = subprocess.run(["git", "show", f"knowledge/{cycle_id}:map-debt.md"],
                           cwd=test_git_repo, capture_output=True, text=True)
    assert "Status: OPEN, Repeat: YES" in show2.stdout




def test_verify_reads_worktree_mutation_not_main_checkout(test_git_repo):
    """
    Regression test for the live-cycle finding (map-debt.md, 2026-08-31): `verify` must execute
    the declared verifier against the actual worktree where EXECUTE applied the mutation, not
    against the main checkout. state["worktree_path"] is currently never written anywhere in
    evolution_state.py (initialized to None at init, read once at verify, set nowhere in between),
    so verify silently grades the unmodified main-checkout file. This test proves the mutation is
    invisible to verify today and must fail (red) until cmd_verify resolves the real worktree path.
    """
    state_script = SCRIPTS_DIR / "evolution_state.py"
    cycle_id = "test-verify-worktree-mismatch"

    # A "verifier" that fails unless it can see the mutation (a marker file written only in the
    # worktree). If verify runs against the main checkout, the marker will be absent and this
    # will exit 1 -- exposing the mismatch instead of masking it.
    verifier_script = test_git_repo / "check_marker.py"
    verifier_script.write_text(
        "import sys\nfrom pathlib import Path\n"
        "sys.exit(0 if Path('MUTATION_MARKER.txt').exists() else 1)\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=test_git_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add marker-checking verifier"], cwd=test_git_repo, check=True, capture_output=True)

    subprocess.run(
        [sys.executable, str(state_script), "init", "--cycle-id", cycle_id, "--tier", "Tier 2", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True,
    )

    manifest_file = test_git_repo / "manifest.json"
    manifest_file.write_text(json.dumps({
        "cycle_id": cycle_id,
        "verifier_files": [],
        "verifier_argv": [sys.executable, str(verifier_script)],
        "mutation_targets": ["MUTATION_MARKER.txt"],
        "authorized_operations": ["create_worktree", "mutate", "verify", "write_layer2", "commit"],
    }), encoding="utf-8")

    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(test_git_repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(test_git_repo)], check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "authorize", "--cycle-id", cycle_id, "--operations",
         "create_worktree,mutate,verify,write_layer2,commit", "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True,
    )
    wt_dir = test_git_repo.parent / f"worktree-{cycle_id}"
    subprocess.run(["git", "worktree", "add", "-b", f"evolution/{cycle_id}", str(wt_dir), "HEAD"], cwd=test_git_repo, check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE",
         "--worktree-path", str(wt_dir), "--repo-dir", str(test_git_repo)],
        check=True, capture_output=True,
    )
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(test_git_repo)], check=True, capture_output=True)

    # The mutation: write the marker file ONLY inside the worktree, exactly as a real EXECUTE step would.
    (wt_dir / "MUTATION_MARKER.txt").write_text("mutation applied\n", encoding="utf-8")
    assert not (test_git_repo / "MUTATION_MARKER.txt").exists(), "sanity: marker must not exist in main checkout"

    verify_res = subprocess.run(
        [sys.executable, str(state_script), "verify", "--repo-dir", str(test_git_repo)],
        capture_output=True, text=True,
    )

    subprocess.run(["git", "worktree", "remove", "--force", str(wt_dir)], cwd=test_git_repo, capture_output=True)

    assert verify_res.returncode == 0, (
        "verify must execute the verifier against the worktree that EXECUTE mutated, not the main "
        f"checkout. Controller output:\n{verify_res.stdout}\n{verify_res.stderr}"
    )
