#!/usr/bin/env python3
"""
evaluate.py -- Locked loop gate for the autoresearch loop
==========================================================

Purpose:
    Single responsibility: "Should the loop keep or discard this change?"

    Calls eval_runner.py once (--json), reads the last BASELINE row from
    <target-skill>/evals/results.tsv, compares score and f1, appends one row
    to that same TSV, then exits 0 (KEEP) or 1 (DISCARD).

    DO NOT MODIFY THIS FILE. It is the locked evaluator. Only the target
    SKILL.md is the mutation target.

Usage (run from the plugin root or any directory):
    python scripts/evaluate.py --skill <path/to/SKILL.md>
    python scripts/evaluate.py --skill <path/to/SKILL.md> --desc "what changed"
    python scripts/evaluate.py --skill <path/to/SKILL.md> --baseline

Karpathy mapping:
    This file = prepare.py (gate logic half)
    eval_runner.py = prepare.py (metric producer half)
    SKILL.md = train.py (mutation target)

KEEP condition: score >= baseline_score AND f1 >= baseline_f1
    Dual guard prevents keyword-stuffing exploit (padding triggers raises
    recall but drops precision, so F1 falls even as accuracy rises).
"""

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# evaluate.py lives at plugins/agent-agentic-os/scripts/evaluate.py
HERE = Path(__file__).parent.resolve()
EVAL_RUNNER = HERE / "eval_runner.py"

HEADERS = ["timestamp", "commit", "score", "baseline", "accuracy", "heuristic", "f1", "status", "description"]


def get_commit(cwd: Path) -> str:
    """Return short git commit hash, or 'uncommitted' if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "uncommitted"


def run_eval_runner(skill_md: Path) -> dict:
    """Call eval_runner.py --json once and return all metric fields."""
    result = subprocess.run(
        [sys.executable, str(EVAL_RUNNER), "--skill", str(skill_md), "--json"],
        capture_output=True, text=True,
        cwd=skill_md.parent
    )
    if result.returncode != 0:
        print(f"ERROR: eval_runner.py failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"ERROR: could not parse eval_runner output: {result.stdout!r}", file=sys.stderr)
        sys.exit(2)


def load_baseline(results_tsv: Path) -> tuple[float, float]:
    """Return (baseline_score, baseline_f1) from the LAST BASELINE row, or (0.0, 0.0)."""
    if not results_tsv.exists():
        return 0.0, 0.0
    last_baseline: dict | None = None
    with open(results_tsv, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") == "BASELINE":
                last_baseline = row
    if last_baseline is None:
        return 0.0, 0.0
    try:
        score = float(last_baseline.get("score", 0))
        # Support both "f1" (new schema) and "llm_routing_score" (legacy)
        f1_raw = last_baseline.get("f1") or last_baseline.get("llm_routing_score") or "0"
        try:
            f1 = float(f1_raw)
        except (ValueError, TypeError):
            f1 = 0.0
        return score, f1
    except (ValueError, KeyError):
        return 0.0, 0.0


def write_row(results_tsv: Path, commit: str, score: float, baseline: float,
              accuracy: float, heuristic: float, f1: float,
              status: str, desc: str) -> None:
    """Append one row to <target-skill>/evals/results.tsv."""
    results_tsv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not results_tsv.exists()
    with open(results_tsv, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, delimiter="\t")
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "commit": commit,
            "score": f"{score:.4f}",
            "baseline": f"{baseline:.4f}",
            "accuracy": f"{accuracy:.4f}",
            "heuristic": f"{heuristic:.4f}",
            "f1": f"{f1:.4f}",
            "status": status,
            "description": desc,
        })


def main() -> None:
    parser = argparse.ArgumentParser(description="Locked autoresearch loop gate")
    parser.add_argument(
        "--skill", required=True,
        help="Path to the target SKILL.md (e.g. skills/my-skill/SKILL.md)"
    )
    parser.add_argument("--desc", default="iteration", help="Description for results.tsv")
    parser.add_argument("--baseline", action="store_true", help="Record this run as the new baseline")
    args = parser.parse_args()

    skill_md = Path(args.skill).resolve()
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at {skill_md}", file=sys.stderr)
        sys.exit(2)

    skill_root = skill_md.parent
    results_tsv = skill_root / "evals" / "results.tsv"

    commit = get_commit(skill_root)
    data = run_eval_runner(skill_md)

    score = float(data["quality_score"])
    accuracy = float(data.get("accuracy", 0.0))
    heuristic = float(data.get("heuristic", 0.0))
    f1 = float(data.get("f1", 0.0))

    baseline_score, baseline_f1 = load_baseline(results_tsv)

    if args.baseline or baseline_score == 0.0:
        status = "BASELINE"
    elif score >= baseline_score and f1 >= baseline_f1:
        status = "KEEP"
    else:
        status = "DISCARD"

    write_row(results_tsv, commit, score, baseline_score, accuracy, heuristic, f1, status, args.desc)

    print(f"score={score:.4f}  baseline={baseline_score:.4f}  f1={f1:.4f}  baseline_f1={baseline_f1:.4f}  STATUS: {status}")
    print(f"commit={commit}  skill={skill_md.parent.name}  desc={args.desc!r}")

    if status == "DISCARD":
        sys.exit(1)


if __name__ == "__main__":
    main()
