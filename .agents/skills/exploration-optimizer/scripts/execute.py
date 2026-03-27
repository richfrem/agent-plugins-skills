#!/usr/bin/env python3
"""
exploration_optimizer_execute.py
=====================================

Purpose:
    Implements an autoresearch-style optimization loop: Propose -> Test -> Decide.
    Optimizes skills based on routing and artifact quality evaluations.

Layer: Execution / Optimization

Usage Examples:
    python3 exploration_optimizer_execute.py --target skill.md --eval-script eval.py --goal "improve clarity"

Supported Object Types:
    SKILL.md files

CLI Arguments:
    --target: Path to the skill file to optimize.
    --eval-script: Path to eval_runner.py.
    --goal: Optimization goal.
    --iterations: Number of iterations.
    --ledger: Path to results TSV.
    --dispatch-script: Enabling artifact quality eval.
    --scenario-brief: Canonical session brief for eval.
    --check-gaps-script: Counting gap markers in output.

Input Files:
    - Target skill.md file
    - scenario brief

Output:
    - Updated skill file.
    - Updated ledger results TSV.

Key Functions:
    run_eval(): Runs routing evaluation.
    run_artifact_eval(): Runs artifact quality evaluation.
    propose_change(): Proposes optimization changes.
    main(): Coordinates the optimization loop.

Script Dependencies:
    os, sys, argparse, subprocess, json, shutil, re, pathlib, datetime

Consumed by:
    - Exploration cycle orchestrator
"""
import argparse
import re
import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def run_eval(eval_script: Path, target: Path) -> float:
    """Runs the routing/structural evaluation script and returns the score."""
    try:
        cmd = [sys.executable, str(eval_script), "--target", str(target), "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data.get("quality_score") or data.get("score") or 0.0)
    except Exception as e:
        print(f"Error running eval: {e}", file=sys.stderr)
        return -1.0


def run_artifact_eval(
    dispatch_script: Path,
    target_skill: Path,
    scenario_brief: Path,
    check_gaps_script: Path,
    artifact_output: Path,
    timeout: int = 180,
) -> float:
    """Artifact quality eval: runs the skill against a canonical scenario and counts gaps.

    Score = 1.0 - (gap_count / 10), floored at 0.0.
    A skill that produces zero gaps scores 1.0; each gap costs 0.1.

    Args:
        dispatch_script: path to dispatch.py
        target_skill:    the SKILL.md being optimized (used as agent)
        scenario_brief:  path to a fixed canonical session brief for the eval run
        check_gaps_script: path to check_gaps.py
        artifact_output: temp path to write the dispatch output
        timeout:         subprocess timeout in seconds

    Returns float score, or -1.0 on failure.
    """
    try:
        # Strip YAML frontmatter from SKILL.md before using it as an agent prompt.
        # Frontmatter (---\n...\n---) is metadata, not instructions — injecting it
        # verbatim confuses the model into treating descriptions as directives.
        skill_content = Path(target_skill).read_text(encoding="utf-8")
        stripped = re.sub(r'^---[\r\n]+.*?[\r\n]+---[\r\n]+', '', skill_content, count=1, flags=re.DOTALL)
        stripped_path = Path(target_skill).with_suffix(".stripped.md")
        stripped_path.write_text(stripped, encoding="utf-8")

        # Run dispatch against the canonical scenario
        cmd = [
            sys.executable, str(dispatch_script),
            "--agent", str(stripped_path),
            "--context", str(scenario_brief),
            "--instruction", "Mode: problem-framing. Capture the problem statement, user groups, and goals.",
            "--output", str(artifact_output),
            "--timeout", str(timeout),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        stripped_path.unlink(missing_ok=True)

        if result.returncode != 0:
            print(f"Artifact eval dispatch failed: {result.stderr}", file=sys.stderr)
            return -1.0

        # Count gaps in the output artifact
        gap_cmd = [
            sys.executable, str(check_gaps_script),
            "--files", str(artifact_output),
            "--threshold", "999",  # never halt; we just want the count
        ]
        gap_result = subprocess.run(gap_cmd, capture_output=True, text=True)

        # Clean up temp artifact regardless of score
        Path(artifact_output).unlink(missing_ok=True)

        # Parse gap count from output: "Total: N '[NEEDS HUMAN INPUT]' marker(s)"
        for line in gap_result.stdout.splitlines():
            if line.startswith("Total:"):
                gap_count = int(line.split()[1])
                score = max(0.0, 1.0 - gap_count * 0.1)
                print(f"Artifact eval: {gap_count} gap(s) → score {score:.2f}")
                return score
        return -1.0
    except Exception as e:
        print(f"Error running artifact eval: {e}", file=sys.stderr)
        Path(artifact_output).unlink(missing_ok=True)
        return -1.0

def propose_change(target: Path, goal: str, timeout: int = 120) -> str | None:
    """Uses copilot-cli to propose a single change to the target file."""
    try:
        prompt = f"""
Objective: Optimize the following SKILL.md file to improve its performance in an Agentic OS.
Goal: {goal}
Constraint: Propose exactly ONE focused change. Do not refactor the whole file.
Output: Return only the full modified content of the file.

---
FILE CONTENT:
{target.read_text()}
"""
        cmd = ["copilot", "-p", prompt, "Propose an improved version of this skill file."]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"Error: copilot timed out after {timeout}s during proposal", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error proposing change: {e}", file=sys.stderr)
        return None

def main() -> None:
    parser = argparse.ArgumentParser(description="Exploration Optimizer Engine")
    parser.add_argument("--target", required=True, help="Path to the skill file to optimize")
    parser.add_argument("--eval-script", required=True, help="Path to eval_runner.py (routing/structural score)")
    parser.add_argument("--goal", default="Improve instruction clarity and example accuracy", help="Optimization goal")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations to run")
    parser.add_argument("--ledger", default="evals/results.tsv", help="Path to the results TSV")
    # Artifact quality eval (primary signal)
    parser.add_argument("--dispatch-script", default=None,
                        help="Path to dispatch.py. If provided, enables artifact quality eval.")
    parser.add_argument("--scenario-brief", default=None,
                        help="Path to a fixed canonical session brief for artifact eval runs.")
    parser.add_argument("--check-gaps-script", default=None,
                        help="Path to check_gaps.py for counting gap markers in artifact output.")

    args = parser.parse_args()
    target_path = Path(args.target)
    eval_script = Path(args.eval_script)
    ledger_path = Path(args.ledger)

    dispatch_script = None
    scenario_brief = None
    check_gaps_script = None
    artifact_output = None
    artifact_eval_enabled = all([args.dispatch_script, args.scenario_brief, args.check_gaps_script])
    if artifact_eval_enabled:
        dispatch_script = Path(args.dispatch_script)
        scenario_brief = Path(args.scenario_brief)
        check_gaps_script = Path(args.check_gaps_script)
        artifact_output = target_path.parent / "_eval_artifact_output.md"
        print("Artifact quality eval enabled (primary signal: gap count).")
    else:
        print("Artifact quality eval disabled — routing/structural score only. "
              "Pass --dispatch-script, --scenario-brief, --check-gaps-script to enable.")
    
    # Ensure ledger directory exists
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if ledger exists, if not, create header
    if not ledger_path.exists():
        with open(ledger_path, "w") as f:
            f.write("timestamp\tscore\tstatus\tchange\n")

    print(f"Starting optimization loop for {target_path.name}...")

    artifact_fail_streak = [0]  # mutable counter accessible inside closure
    MAX_ARTIFACT_FAILURES = 3

    def combined_score(skill_path: Path) -> float:
        """Blended score: 30% routing/structural, 70% artifact quality (if enabled)."""
        routing = run_eval(eval_script, skill_path)
        if routing < 0:
            return -1.0
        if not artifact_eval_enabled:
            return routing
        assert dispatch_script is not None
        assert scenario_brief is not None
        assert check_gaps_script is not None
        assert artifact_output is not None
        artifact = run_artifact_eval(
            dispatch_script, skill_path, scenario_brief, check_gaps_script, artifact_output
        )
        if artifact < 0:
            artifact_fail_streak[0] += 1
            print(f"Warning: artifact eval failed ({artifact_fail_streak[0]}/{MAX_ARTIFACT_FAILURES}) "
                  "— falling back to routing score only this iteration.")
            if artifact_fail_streak[0] >= MAX_ARTIFACT_FAILURES:
                print(f"Fatal: artifact eval failed {MAX_ARTIFACT_FAILURES} consecutive times. "
                      "Restoring from backup and aborting.", file=sys.stderr)
                if backup_path.exists():
                    shutil.copy(backup_path, target_path)
                    os.remove(backup_path)
                sys.exit(1)
            return routing
        artifact_fail_streak[0] = 0  # reset on success
        blended = (artifact * 0.7) + (routing * 0.3)
        print(f"  Routing: {routing:.3f}  Artifact: {artifact:.3f}  Blended: {blended:.3f}")
        return blended

    # 1. Baseline
    current_score = combined_score(target_path)
    print(f"Baseline Score: {current_score:.4f}")

    if current_score < 0:
        print("Fatal: Baseline evaluation failed. Aborting.")
        sys.exit(1)

    for i in range(args.iterations):
        print(f"\n--- Iteration {i+1} ---")
        
        # Backup the current version
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        if backup_path.exists():
            print(f"Warning: orphaned backup found at {backup_path} — a previous run may have "
                  "exited uncleanly. Overwriting with fresh backup. If you want to restore from "
                  "the previous run, copy it manually before continuing.", file=sys.stderr)
        shutil.copy(target_path, backup_path)
        
        # 2. Propose
        proposal = propose_change(target_path, args.goal)
        if not proposal:
            print("Failed to generate proposal. Skipping.")
            continue
        
        # 3. Apply — write to a temp file first, then atomically replace.
        # This ensures target_path is never left in a partial state, even on SIGKILL.
        tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
        try:
            with open(tmp_path, "w") as f:
                f.write(proposal)
            os.replace(tmp_path, target_path)  # atomic on POSIX

            # 4. Test
            new_score = combined_score(target_path)
            print(f"New Score: {new_score:.4f}")

            # 5. Decide
            timestamp = datetime.now().isoformat()
            if new_score > current_score:
                print("Improvement found! Keeping change.")
                current_score = new_score
                status = "keep"
                os.remove(backup_path)
            else:
                print("Regressed or equal. Discarding change.")
                shutil.copy(backup_path, target_path)
                os.remove(backup_path)
                status = "discard"
        except Exception as e:
            # Restore from backup on any failure; continue to next iteration (don't abort all remaining)
            print(f"Error during apply/eval: {e} — restoring from backup and continuing", file=sys.stderr)
            if backup_path.exists():
                shutil.copy(backup_path, target_path)
                os.remove(backup_path)
            if tmp_path.exists():
                os.remove(tmp_path)
            timestamp = datetime.now().isoformat()
            status = "error"
            new_score = -1.0
            
        # 6. Ledger
        with open(ledger_path, "a") as f:
            f.write(f"{timestamp}\t{new_score}\t{status}\t{args.goal}\n")

    print(f"\nOptimization complete. Final Score: {current_score}")

if __name__ == "__main__":
    main()
