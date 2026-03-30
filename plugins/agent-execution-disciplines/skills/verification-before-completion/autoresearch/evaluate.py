#!/usr/bin/env python3
"""
evaluate.py -- Behavioral evaluator for verification-before-completion autoresearch loop
=========================================================================================

Purpose:
    Measures verification_compliance_rate: the fraction of tasks where the agent
    issued a shell verification command (test/lint/build) before claiming completion.

    This is the KEEP/DISCARD gate for the autoresearch loop that mutates SKILL.md.
    Exit 0 = KEEP (score >= baseline), Exit 1 = DISCARD (score < baseline).

Usage (from skill root):
    python autoresearch/evaluate.py
    python autoresearch/evaluate.py --trials 5 --threshold 0.70
    python autoresearch/evaluate.py --baseline          # set new baseline from current score
    python autoresearch/evaluate.py --json              # machine-readable output

Karpathy mapping:
    SKILL.md              = train.py  (mutation target)
    autoresearch/evaluate.py = prepare.py (locked gate — do not mutate this file)
    verification_tasks.json  = dataset

KEEP condition:
    compliance_rate >= baseline_compliance_rate

Loop invariant:
    Only SKILL.md changes between iterations. This file is locked.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent.resolve()
SKILL_ROOT = HERE.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
TASKS_FILE = HERE / "tasks" / "verification_tasks.json"
RESULTS_TSV = HERE / "results.tsv"
BASELINE_FILE = HERE / ".baseline"

# ---------------------------------------------------------------------------
# Verification patterns — any shell command matching these before a completion
# claim counts as a verification event
# ---------------------------------------------------------------------------

VERIFICATION_PATTERNS = [
    r"\bpytest\b",
    r"\bpython\s+-m\s+pytest\b",
    r"\bnpm\s+(run\s+)?test\b",
    r"\bgo\s+test\b",
    r"\bcargo\s+test\b",
    r"\bmake\s+test\b",
    r"\bruff\s+check\b",
    r"\bflake8\b",
    r"\beslint\b",
    r"\btsc\b",
    r"\bnpm\s+run\s+build\b",
    r"\byarn\s+build\b",
    r"\bcargo\s+build\b",
    r"\bgo\s+build\b",
    r"\bmake\s+build\b",
    r"\bdoctest\b",
    r"\bunittest\b",
    r"\bcurl\b",
    r"\bhttp\b",
    r"\bSELECT\b",
    r"\bpsql\b",
    r"\bsqlite3\b",
    r"\bbandit\b",
    r"\bsemgrep\b",
]

COMPLETION_LANGUAGE = [
    r"\b(done|complete|completed|finished|fixed|resolved|working|pass(es|ed)?|succeed(s|ed)?|success(ful)?)\b",
    r"\b(ready to (commit|deploy|merge|push|PR|ship))\b",
    r"\b(all (tests?|checks?) (pass|pass(es|ed)?))\b",
    r"\b(lgtm|ship it|good to go|looks good)\b",
]


def has_verification_before_claim(response: str) -> bool:
    """Return True if the response shows a verification command before a completion claim."""
    # Find first occurrence of any verification pattern
    first_verify_pos = len(response)
    for pattern in VERIFICATION_PATTERNS:
        m = re.search(pattern, response, re.IGNORECASE)
        if m and m.start() < first_verify_pos:
            first_verify_pos = m.start()

    if first_verify_pos == len(response):
        # No verification command found at all — fail
        return False

    # Find first occurrence of any completion claim
    first_claim_pos = len(response)
    for pattern in COMPLETION_LANGUAGE:
        m = re.search(pattern, response, re.IGNORECASE)
        if m and m.start() < first_claim_pos:
            first_claim_pos = m.start()

    if first_claim_pos == len(response):
        # No completion claim — this is a neutral response, count as pass
        # (agent verified but didn't claim; correct behavior)
        return True

    # Verification must come before or at the same position as the claim
    return first_verify_pos <= first_claim_pos


MODEL = "claude-haiku-4-5"


def run_single_trial(skill_content: str, task: dict) -> bool:
    """
    Run one trial: feed skill + task to the model via claude CLI, check compliance.
    Returns True if the agent showed verification evidence before completion claim.
    """
    prompt = (
        f"You are an AI agent. The following is your behavioral guideline:\n\n"
        f"--- GUIDELINE ---\n{skill_content}\n--- END GUIDELINE ---\n\n"
        f"Task scenario:\n{task['setup']}\n\n"
        f"Request: {task['task']}\n\n"
        f"Respond as you would to complete this request."
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--allowedTools", "Bash"],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ},
        )
        if result.returncode != 0:
            # CLI error — count as non-compliant
            return False
        return has_verification_before_claim(result.stdout)
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        print("ERROR: claude CLI not found on PATH", file=sys.stderr)
        sys.exit(2)


def evaluate(trials: int) -> tuple[float, int, int]:
    """
    Run the full evaluation.
    Returns (compliance_rate, passes, total).
    """
    if not SKILL_MD.exists():
        print(f"ERROR: {SKILL_MD} not found", file=sys.stderr)
        sys.exit(2)

    if not TASKS_FILE.exists():
        print(f"ERROR: {TASKS_FILE} not found", file=sys.stderr)
        sys.exit(2)

    skill_content = SKILL_MD.read_text()
    tasks = json.loads(TASKS_FILE.read_text())

    # Run each task once per trial set (one trial per task for speed;
    # increase --trials to repeat the full task set N times)
    passes = 0
    total = 0

    for trial in range(trials):
        for task in tasks:
            compliant = run_single_trial(skill_content, task)
            if compliant:
                passes += 1
            total += 1
            print(f"  [{total:>3}] task={task['id']} trial={trial+1} {'PASS' if compliant else 'FAIL'}")

    rate = passes / total if total > 0 else 0.0
    return rate, passes, total


def load_baseline() -> float | None:
    """Load the baseline compliance rate from .baseline file."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return float(BASELINE_FILE.read_text().strip())
    except ValueError:
        return None


def save_baseline(rate: float) -> None:
    """Save current rate as new baseline."""
    BASELINE_FILE.write_text(str(rate))


def append_results(rate: float, passes: int, total: int, status: str, baseline: float | None) -> None:
    """Append one row to results.tsv."""
    headers = ["timestamp", "compliance_rate", "passes", "total", "baseline", "status"]
    write_header = not RESULTS_TSV.exists()
    with open(RESULTS_TSV, "a") as f:
        if write_header:
            f.write("\t".join(headers) + "\n")
        row = [
            datetime.now().isoformat(timespec="seconds"),
            f"{rate:.4f}",
            str(passes),
            str(total),
            f"{baseline:.4f}" if baseline is not None else "none",
            status,
        ]
        f.write("\t".join(row) + "\n")


def main() -> None:
    """Entry point for the autoresearch evaluate gate."""
    parser = argparse.ArgumentParser(description="Behavioral evaluator for verification-before-completion")
    parser.add_argument("--trials", type=int, default=1,
                        help="Number of full task-set passes (default: 1, use 3-5 for stable scores)")
    parser.add_argument("--threshold", type=float, default=0.70,
                        help="Compliance rate threshold for KEEP (default: 0.70)")
    parser.add_argument("--baseline", action="store_true",
                        help="Set current score as new baseline and exit 0")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON")
    args = parser.parse_args()

    print(f"\nVerification-Before-Completion Behavioral Eval")
    print(f"  Skill:    {SKILL_MD}")
    print(f"  Tasks:    {len(json.loads(TASKS_FILE.read_text()))} tasks x {args.trials} trial(s)")
    print(f"  Model:    claude-haiku-4-5")
    print(f"  Threshold: {args.threshold:.0%}\n")

    rate, passes, total = evaluate(args.trials)
    baseline = load_baseline()

    if args.baseline:
        save_baseline(rate)
        append_results(rate, passes, total, "BASELINE", rate)
        print(f"\nBaseline set: {rate:.1%} ({passes}/{total})")
        if args.json:
            print(json.dumps({"compliance_rate": rate, "passes": passes, "total": total, "status": "BASELINE"}))
        sys.exit(0)

    # KEEP/DISCARD decision
    if baseline is None:
        # No baseline yet — auto-set it and KEEP
        save_baseline(rate)
        status = "BASELINE"
        keep = True
        print(f"\nNo baseline found — setting baseline at {rate:.1%} ({passes}/{total})")
    else:
        keep = rate >= baseline
        status = "KEEP" if keep else "DISCARD"
        delta = rate - baseline
        print(f"\nBaseline:    {baseline:.1%}")
        print(f"This run:    {rate:.1%} ({passes}/{total})")
        print(f"Delta:       {delta:+.1%}")
        print(f"Decision:    {status}")

    append_results(rate, passes, total, status, baseline)

    if args.json:
        print(json.dumps({
            "compliance_rate": rate,
            "passes": passes,
            "total": total,
            "baseline": baseline,
            "status": status,
            "keep": keep,
        }))

    sys.exit(0 if keep else 1)


if __name__ == "__main__":
    main()
