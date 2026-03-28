#!/usr/bin/env python3
"""
evaluate.py -- LOCKED autoresearch evaluator for skill-improvement-eval
=======================================================================

Purpose:
    Runs eval_runner.py against ../SKILL.md, compares score to the baseline
    row in autoresearch/results.tsv, records the result, and exits 0 (KEEP)
    or 1 (DISCARD).

    DO NOT MODIFY THIS FILE. It is the locked evaluator for the autoresearch
    loop. Only ../SKILL.md is the mutation target.

Usage:
    python autoresearch/evaluate.py
    python autoresearch/evaluate.py --desc "what you changed"
    python autoresearch/evaluate.py --baseline   # record as new baseline

Run from the skill root:
    cd plugins/agent-agentic-os/skills/skill-improvement-eval
    python autoresearch/evaluate.py --desc "added second example block"
"""

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
SKILL_ROOT = HERE.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
EVAL_RUNNER = SKILL_ROOT / "scripts" / "eval_runner.py"
RESULTS_TSV = HERE / "results.tsv"
HEADERS = ["timestamp", "commit", "score", "baseline", "f1", "status", "description"]


def get_commit() -> str:
    """Return short git commit hash, or 'uncommitted' if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
            cwd=SKILL_ROOT
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "uncommitted"


def run_eval_runner() -> dict:
    """Call eval_runner.py --json and return parsed JSON output."""
    result = subprocess.run(
        [sys.executable, str(EVAL_RUNNER), "--skill", str(SKILL_MD), "--json"],
        capture_output=True, text=True,
        cwd=SKILL_ROOT
    )
    if result.returncode != 0:
        print(f"ERROR: eval_runner.py failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"ERROR: could not parse eval_runner output: {result.stdout!r}", file=sys.stderr)
        sys.exit(2)


def load_baseline() -> tuple[float, float]:
    """Return (baseline_score, baseline_f1) from the first BASELINE row, or (0.0, 0.0)."""
    if not RESULTS_TSV.exists():
        return 0.0, 0.0
    with open(RESULTS_TSV, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") == "BASELINE":
                try:
                    return float(row["score"]), float(row.get("f1", 0))
                except (ValueError, KeyError):
                    return 0.0, 0.0
    return 0.0, 0.0


def get_f1_from_runner() -> float:
    """Run eval_runner in verbose mode to get f1 score from evals/results.tsv."""
    subprocess.run(
        [sys.executable, str(EVAL_RUNNER), "--skill", str(SKILL_MD), "--desc", "_f1_probe"],
        capture_output=True, text=True,
        cwd=SKILL_ROOT
    )
    evals_results = SKILL_ROOT / "evals" / "results.tsv"
    if not evals_results.exists():
        return 0.0
    with open(evals_results, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        last = None
        for row in reader:
            last = row
    if last:
        try:
            return float(last.get("f1_score", 0))
        except (ValueError, TypeError):
            return 0.0
    return 0.0


def write_row(commit: str, score: float, baseline: float, f1: float, status: str, desc: str) -> None:
    """Append a row to autoresearch/results.tsv."""
    write_header = not RESULTS_TSV.exists()
    with open(RESULTS_TSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, delimiter="\t")
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "commit": commit,
            "score": f"{score:.4f}",
            "baseline": f"{baseline:.4f}",
            "f1": f"{f1:.4f}",
            "status": status,
            "description": desc,
        })


def main() -> None:
    parser = argparse.ArgumentParser(description="Locked autoresearch evaluator")
    parser.add_argument("--desc", default="iteration", help="Description for results.tsv")
    parser.add_argument("--baseline", action="store_true", help="Record this run as the new baseline")
    args = parser.parse_args()

    commit = get_commit()
    data = run_eval_runner()
    score = float(data["quality_score"])

    baseline_score, baseline_f1 = load_baseline()
    f1 = get_f1_from_runner()

    if args.baseline or baseline_score == 0.0:
        status = "BASELINE"
    elif score >= baseline_score and f1 >= baseline_f1:
        status = "KEEP"
    else:
        status = "DISCARD"

    write_row(commit, score, baseline_score, f1, status, args.desc)

    print(f"score={score:.4f}  baseline={baseline_score:.4f}  f1={f1:.4f}  STATUS: {status}")
    print(f"commit={commit}  desc={args.desc!r}")

    if status == "DISCARD":
        print("-> git checkout -- ../SKILL.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
