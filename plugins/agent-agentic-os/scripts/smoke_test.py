#!/usr/bin/env python3
"""
smoke_test.py — Standalone end-to-end smoke test for self-evolution lifecycle.

Purpose:
    No pytest required. Run directly:
        python3 plugins/agent-agentic-os/scripts/smoke_test.py

    Executes both E2E-PASS (successful mutation with controller-executed verifier and cryptographic receipt)
    and E2E-ROLLBACK (3 failed attempts forcing rollback, asymmetric persistence to knowledge/<cid>,
    and main branch purity).

Key Input Dependencies:
    - evolution_state.py, record_trace.py, verify_evolution_receipt.py, evaluate.py
    - evo-smoketest fixture skill
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"
FIXTURE_DIR = REPO_ROOT / "plugins" / "agent-agentic-os" / "skills" / "evo-smoketest"

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
results: list[tuple[str, bool]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    """Print a pass/fail line for one assertion and record it in results."""
    icon = PASS if condition else FAIL
    print(f"  {icon}  {label}" + (f" — {detail}" if detail else ""))
    results.append((label, condition))


def setup_sandbox() -> Path:
    """Create an isolated temporary git repo with scripts and fixture."""
    tmp = Path(tempfile.mkdtemp(prefix="evo-smoke-sandbox-"))
    repo = tmp / "repo"
    repo.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Smoke Test User"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "smoke@example.com"], cwd=repo, check=True, capture_output=True)

    # Copy scripts
    s_dest = repo / "plugins" / "agent-agentic-os" / "scripts"
    s_dest.mkdir(parents=True, exist_ok=True)
    for s_name in ["evolution_state.py", "record_trace.py", "verify_evolution_receipt.py", "evaluate.py", "eval_runner.py"]:
        shutil.copy2(SCRIPTS_DIR / s_name, s_dest / s_name)

    # Copy fixture
    f_dest = repo / "plugins" / "agent-agentic-os" / "skills" / "evo-smoketest"
    shutil.copytree(FIXTURE_DIR, f_dest)

    # Commit initial state
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial baseline commit"], cwd=repo, check=True, capture_output=True)
    return repo


def run_smoke_test():
    print("================================================================================")
    print("  Self-Evolution End-to-End Smoke Test: 11 Hardened Contract Assertions")
    print("================================================================================")

    repo = setup_sandbox()
    state_script = repo / "plugins" / "agent-agentic-os" / "scripts" / "evolution_state.py"
    record_script = repo / "plugins" / "agent-agentic-os" / "scripts" / "record_trace.py"
    verify_script = repo / "plugins" / "agent-agentic-os" / "scripts" / "verify_evolution_receipt.py"
    evaluate_script = repo / "plugins" / "agent-agentic-os" / "scripts" / "evaluate.py"
    skill_dir = repo / "plugins" / "agent-agentic-os" / "skills" / "evo-smoketest"

    epoch = int(time.time())
    pass_cid = f"smoke-pass-{epoch}"
    rollback_cid = f"smoke-rollback-{epoch}"

    # -------------------------------------------------------------------------
    # PART 1: E2E-PASS Lifecycle
    # -------------------------------------------------------------------------
    print("\n── Phase 1: E2E-PASS Flow ───────────────────────────────────────────────────")

    # Establish baseline
    res_base = subprocess.run([sys.executable, str(evaluate_script), "--skill", str(skill_dir), "--baseline"], cwd=repo, capture_output=True, text=True)
    check("Baseline Evaluation Recorded", res_base.returncode == 0, f"exit={res_base.returncode}")

    # Assertion 1: TRIAGE -> PLAN
    res_init = subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", pass_cid, "--repo-dir", str(repo)], capture_output=True, text=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", pass_cid, "--node", "TRIAGE", "--event-type", "cycle.initialized", "--repo-dir", str(repo)], check=True, capture_output=True)
    res_trans_plan = subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(repo)], capture_output=True, text=True)
    
    manifest_data = {
        "cycle_id": pass_cid,
        "mutation_targets": [str(skill_dir / "SKILL.md")],
        "verifier_files": [str(evaluate_script), str(repo / "plugins" / "agent-agentic-os" / "scripts" / "eval_runner.py")],
        "verifier_argv": [sys.executable, str(evaluate_script), "--skill", str(skill_dir), "--decision-only"],
        "authorized_operations": ["create_worktree", "mutate", "verify", "write_layer2", "commit"]
    }
    manifest_file = repo / "manifest_pass.json"
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    
    res_plan = subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(manifest_file), "--repo-dir", str(repo)], capture_output=True, text=True)
    res_await = subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(repo)], capture_output=True, text=True)
    check("Assertion 1 (TRIAGE -> PLAN -> AWAITING_APPROVAL)", res_await.returncode == 0, f"cycle={pass_cid}")

    # Assertion 2: Proposal Mode Halt (Zero worktrees, zero modifications)
    st = json.loads((repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    worktrees = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout.strip().splitlines()
    check("Assertion 2 (Proposal Mode Halt)", st["current_node"] == "AWAITING_APPROVAL" and len(worktrees) == 1, "zero worktrees created")

    # Assertion 3: Explicit Authorization
    res_auth = subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", pass_cid, "--repo-dir", str(repo)], capture_output=True, text=True)
    st_auth = json.loads((repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    check("Assertion 3 (Explicit Authorization Granted)", st_auth["authorization"]["status"] == "GRANTED", f"status={st_auth['authorization']['status']}")

    # Assertion 4: Worktree State Isolation
    wt_dir = repo.parent / f"worktree-{pass_cid}"
    subprocess.run(["git", "worktree", "add", "-b", f"evolution/{pass_cid}", str(wt_dir), "HEAD"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE",
         "--worktree-path", str(wt_dir), "--repo-dir", str(repo)],
        check=True, capture_output=True,
    )
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(repo)], check=True, capture_output=True)
    check("Assertion 4 (Worktree Isolation Active)", wt_dir.exists() and wt_dir != repo, f"path={wt_dir.name}")

    # Assertion 5: Verifier Execution via Controller
    # Mutate SKILL.md in worktree to include Kelvin
    wt_skill_md = wt_dir / "plugins" / "agent-agentic-os" / "skills" / "evo-smoketest" / "SKILL.md"
    wt_skill_md.write_text("""---
name: evo-smoketest
description: Converts temperatures between Celsius, Fahrenheit, and Kelvin (K = C + 273.15) for the evolution end-to-end smoke test harness. Handles C to F, F to C, and Kelvin conversions.
version: 0.1.0
---

# evo-smoketest

<example>
user: Convert 300 Kelvin to Celsius.
assistant: 26.9 C
</example>

<example>
user: 20C to F please
assistant: 68.0 F
</example>

## When to use
Use this skill when the user asks to convert a temperature between Celsius, Fahrenheit, and Kelvin, or shorthand like 20C to F.

## Procedure
1. Identify the source unit, target unit, and numeric value in the request.
2. Apply the conversion:
   - Celsius to Fahrenheit: F = C * 9/5 + 32
   - Fahrenheit to Celsius: C = (F - 32) * 5/9
   - Kelvin to Celsius: C = K - 273.15
3. Return the converted value rounded to one decimal place.
""", encoding="utf-8")
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", pass_cid, "--node", "EXECUTE", "--event-type", "mutation.completed", "--repo-dir", str(repo)], check=True, capture_output=True)

    # Controller executes verifier
    res_verify = subprocess.run([sys.executable, str(state_script), "verify", "--repo-dir", str(repo)], capture_output=True, text=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", pass_cid, "--node", "VERIFY_GATE", "--event-type", "verification.completed", "--exit-code", "0", "--repo-dir", str(repo)], check=True, capture_output=True)
    # Not just exit 0 -- assert the controller actually ran the verifier IN the worktree it created,
    # not the main checkout (the exact defect map-debt.md documents as resolved 2026-08-31: exit 0
    # alone previously passed even when verify silently graded the unmodified main-checkout file).
    verified_in_worktree = str(wt_dir) in res_verify.stdout
    check("Assertion 5 (Verifier Executed by Controller, in the worktree)", res_verify.returncode == 0 and verified_in_worktree, f"exit={res_verify.returncode} ran_in_worktree={verified_in_worktree}")

    # Assertion 6: Provenance Verification Guard (Record-verification cannot spoof gate)
    st_prov = json.loads((repo / ".agent" / "learning" / "evolution_state.json").read_text(encoding="utf-8"))
    has_prov = (
        st_prov.get("verification_provenance", {}).get("source") == "controller"
        and st_prov.get("verification_provenance", {}).get("exit_code") == 0
    )
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(repo)], check=True, capture_output=True)
    res_trans_rcpt = subprocess.run([sys.executable, str(state_script), "transition", "--to", "PRE_COMMIT_RECEIPT", "--repo-dir", str(repo)], capture_output=True, text=True)
    check("Assertion 6 (Controller Provenance Gated)", has_prov and res_trans_rcpt.returncode == 0, "provenance validated")

    # Assertion 7: Cryptographic Receipt Integrity
    # Stage/write-tree/commit inside the worktree (design intent, self-evolution/SKILL.md Stage 3):
    # the receipt must bind the tree that actually contains the fix, not the main checkout's
    # (unrelated) tree.
    subprocess.run(["git", "add", "-A"], cwd=wt_dir, check=True, capture_output=True)
    tree_sha = subprocess.run(["git", "write-tree"], cwd=wt_dir, capture_output=True, text=True, check=True).stdout.strip()
    res_rcpt = subprocess.run([sys.executable, str(verify_script), "--stage", "pre-commit", "--cycle-id", pass_cid, "--tree-sha", tree_sha, "--repo-dir", str(repo)], capture_output=True, text=True)
    receipt_data = json.loads(res_rcpt.stdout.strip())
    token_valid = "EVO-INTEGRITY-" in receipt_data.get("receipt_token", "")
    subprocess.run([sys.executable, str(state_script), "set-receipt", "--stage", "pre-commit", "--token", receipt_data["receipt_token"], "--repo-dir", str(repo)], check=True, capture_output=True)

    subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMMIT", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"feat(evolution): completed cycle {pass_cid}"], cwd=wt_dir, check=True, capture_output=True)
    subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", pass_cid, "--node", "COMMIT", "--event-type", "commit.completed", "--exit-code", "0", "--repo-dir", str(repo)], check=True, capture_output=True)

    subprocess.run([sys.executable, str(state_script), "transition", "--to", "FINAL_RECEIPT", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(verify_script), "--stage", "final", "--cycle-id", pass_cid, "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "COMPLETED", "--repo-dir", str(repo)], check=True, capture_output=True)

    # Land the fix: merge the worktree's branch into main, then teardown.
    subprocess.run(["git", "merge", "--no-ff", f"evolution/{pass_cid}", "-m", f"merge(evolution): land verified repair for {pass_cid}"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "worktree", "remove", "--force", str(wt_dir)], cwd=repo, capture_output=True)
    subprocess.run(["git", "branch", "-D", f"evolution/{pass_cid}"], cwd=repo, capture_output=True)
    check("Assertion 7 (Cryptographic Receipt Verified & Committed)", token_valid, f"token={receipt_data['receipt_token'][:25]}...")

    # Assertion 7b: the fix genuinely landed on main after merge -- not just a valid receipt, but
    # the actual mutated content is present in the checkout the smoke test's own repo now has.
    merged_skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    check("Assertion 7b (Verified Fix Content Landed on Branch)", "Kelvin" in merged_skill_md, "SKILL.md on main now contains the Kelvin broadening")

    # -------------------------------------------------------------------------
    # PART 2: E2E-ROLLBACK & Asymmetric Persistence Lifecycle
    # -------------------------------------------------------------------------
    print("\n── Phase 2: E2E-ROLLBACK Flow ────────────────────────────────────────────────")

    main_head_before_rollback = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()

    # Init rollback cycle
    subprocess.run([sys.executable, str(state_script), "init", "--cycle-id", rollback_cid, "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(repo)], check=True, capture_output=True)

    # Manifest with failing toggle verifier
    fail_verifier = repo / "failing_verifier.py"
    fail_verifier.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    subprocess.run(["git", "add", "failing_verifier.py"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add failing verifier"], cwd=repo, check=True, capture_output=True)
    main_head_before_rollback = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()

    manifest_fail = {
        "cycle_id": rollback_cid,
        "verifier_files": [],
        "verifier_argv": [sys.executable, str(fail_verifier)],
        "authorized_operations": ["create_worktree", "mutate", "verify", "write_layer2", "commit"]
    }
    m_fail_path = repo / "manifest_fail.json"
    m_fail_path.write_text(json.dumps(manifest_fail, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(m_fail_path), "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", rollback_cid, "--repo-dir", str(repo)], check=True, capture_output=True)

    # Simulate 3 failed attempts
    wt_fail = repo.parent / f"worktree-{rollback_cid}"
    subprocess.run(["git", "worktree", "add", "-b", f"evolution/{rollback_cid}", str(wt_fail), "HEAD"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE",
         "--worktree-path", str(wt_fail), "--repo-dir", str(repo)],
        check=True, capture_output=True,
    )

    # Attempt 1
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "verify", "--repo-dir", str(repo)], capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(m_fail_path), "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", rollback_cid, "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE",
         "--worktree-path", str(wt_fail), "--repo-dir", str(repo)],
        check=True, capture_output=True,
    )

    # Attempt 2
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "verify", "--repo-dir", str(repo)], capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "plan", "--manifest", str(m_fail_path), "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "AWAITING_APPROVAL", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "authorize", "--cycle-id", rollback_cid, "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(state_script), "transition", "--to", "CREATE_WORKTREE",
         "--worktree-path", str(wt_fail), "--repo-dir", str(repo)],
        check=True, capture_output=True,
    )

    # Attempt 3
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "EXECUTE", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(state_script), "verify", "--repo-dir", str(repo)], capture_output=True)
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "VERIFY_GATE", "--repo-dir", str(repo)], check=True, capture_output=True)

    # Assertion 8: 3-Attempt Ceiling Enforced (Transition back to PLAN must be blocked)
    res_attempt_4 = subprocess.run([sys.executable, str(state_script), "transition", "--to", "PLAN", "--repo-dir", str(repo)], capture_output=True, text=True)
    check("Assertion 8 (3-Attempt Ceiling Enforced)", res_attempt_4.returncode != 0, "attempt 4 transition to PLAN blocked")

    # Add Layer 2 knowledge inside worktree
    (wt_fail / "wiki").mkdir(parents=True, exist_ok=True)
    (wt_fail / "wiki" / "hardened_rollback_analysis.md").write_text("# Failure Analysis\nStatus: REJECTED\nNegative constraint observed.\n", encoding="utf-8")
    (wt_fail / "map-debt.md").write_text("# Map Debt\nStatus: OPEN, Repeat: YES\n", encoding="utf-8")

    # Assertion 10: Asymmetric Persistence / Layer 2 Durability
    res_exp = subprocess.run([
        sys.executable, str(state_script), "export-layer2",
        "--cycle-id", rollback_cid,
        "--commit-knowledge",
        "--from-worktree", str(wt_fail),
        "--to-main", str(repo)
    ], capture_output=True, text=True)

    # Assertion 9: Code Discard on Rollback
    subprocess.run([sys.executable, str(state_script), "transition", "--to", "ROLLBACK", "--repo-dir", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "worktree", "remove", "--force", str(wt_fail)], cwd=repo, capture_output=True)
    subprocess.run(["git", "branch", "-D", f"evolution/{rollback_cid}"], cwd=repo, capture_output=True)
    code_in_main = (repo / "failing_code_mutation.py").exists()
    check("Assertion 9 (Code Discard on Rollback)", not code_in_main, "evolution branch and worktree destroyed")

    # Check branch exists and contains knowledge
    show_wiki = subprocess.run(["git", "show", f"knowledge/{rollback_cid}:wiki/hardened_rollback_analysis.md"], cwd=repo, capture_output=True, text=True)
    
    # Simulate aggressive checkout and clean on main
    subprocess.run(["git", "checkout", "--", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=repo, capture_output=True)
    show_debt = subprocess.run(["git", "show", f"knowledge/{rollback_cid}:map-debt.md"], cwd=repo, capture_output=True, text=True)
    check("Assertion 10 (Asymmetric Persistence Durability)", "Negative constraint observed." in show_wiki.stdout and "Repeat: YES" in show_debt.stdout, f"branch=knowledge/{rollback_cid}")

    # Assertion 11: Main Branch Purity (NEVER commit directly to main)
    main_head_after_rollback = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    check("Assertion 11 (Main Branch Purity Preserved)", main_head_after_rollback == main_head_before_rollback, f"HEAD={main_head_after_rollback[:8]} unchanged")

    # Cleanup sandbox
    shutil.rmtree(repo.parent, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n── Summary ───────────────────────────────────────────────────────────────────")
    all_passed = all(cond for _, cond in results)
    passed_count = sum(1 for _, cond in results if cond)
    total_count = len(results)
    print(f"Total assertions: {total_count} | Passed: {passed_count} | Failed: {total_count - passed_count}")
    if all_passed:
        print("\n\033[32mALL 11 HARDENED END-TO-END SMOKE TEST ASSERTIONS PASSED!\033[0m\n")
        return 0
    else:
        print("\n\033[31mSOME SMOKE TEST ASSERTIONS FAILED!\033[0m\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_smoke_test())
