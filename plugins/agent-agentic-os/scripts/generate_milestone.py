#!/usr/bin/env python3
"""
generate_milestone.py -- Write milestone summary files for long autoresearch runs.
==================================================================================

Purpose:
    Reads evals/results.tsv and evals/traces/*.json for a skill experiment directory.
    Writes a milestone_NNN.md summary every N iterations (default: 25).
    Enables the proposer to read distant history without losing context — the
    Meta-Harness equivalent of proactive summarization (Lee et al., arXiv:2603.28052).

    This is a pure read-then-write utility. It does not affect KEEP/DISCARD decisions
    and must never be added to LOCKED_FILES in evaluate.py.

Usage:
    python3 generate_milestone.py --experiment-dir <path> [--every 25] [--force]

    --experiment-dir   Path to the experiment directory (contains evals/ and references/)
    --every N          Write a milestone every N iterations (default: 25)
    --force            Write a milestone even if iteration count is not a multiple of --every

Output:
    evals/traces/milestone_NNN.md  where NNN = the iteration count at time of writing

Exit codes:
    0  Milestone written (or --force used)
    0  No milestone needed yet (iteration count not a multiple of --every, no --force)
    2  Error (bad path, missing results.tsv, etc.)
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_tsv(results_tsv: Path) -> list[dict]:
    if not results_tsv.exists():
        return []
    rows = []
    with open(results_tsv, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def _load_traces(traces_dir: Path) -> list[dict]:
    """Load all iter_*.json trace files, sorted by name."""
    traces = []
    if not traces_dir.exists():
        return traces
    for path in sorted(traces_dir.glob("iter_*.json")):
        try:
            traces.append(json.loads(path.read_text()))
        except Exception:
            pass
    return traces


def _best_keeps(iter_rows: list[dict], top_n: int = 3) -> list[str]:
    """Return descriptions of the top-N highest-delta KEEP iterations."""
    keep_rows = [r for r in iter_rows if r.get("status") == "KEEP"]
    keep_rows_sorted = sorted(keep_rows, key=lambda r: float(r.get("score", 0)), reverse=True)
    results = []
    for row in keep_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        score = float(row.get("score", 0))
        baseline = float(row.get("baseline", 0))
        delta = score - baseline
        results.append(f"  - +{delta:.4f}: \"{desc}\" (score={score:.4f})")
    return results


def _worst_discards(iter_rows: list[dict], top_n: int = 3) -> list[str]:
    """Return descriptions of the top-N most negative-delta DISCARD iterations, with failure reasons."""
    discard_rows = [r for r in iter_rows if r.get("status") == "DISCARD"]
    discard_rows_sorted = sorted(discard_rows, key=lambda r: float(r.get("score", 0)))
    results = []
    seen_descs: dict[str, int] = {}
    for row in discard_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        seen_descs[desc] = seen_descs.get(desc, 0) + 1
    for row in discard_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        score = float(row.get("score", 0))
        baseline = float(row.get("baseline", 0))
        delta = score - baseline
        repeat = f" [tried {seen_descs[desc]}x]" if seen_descs.get(desc, 1) > 1 else ""
        results.append(f"  - {delta:.4f}: \"{desc}\"{repeat} (score={score:.4f})")
    return results


def _current_fp_fn(traces: list[dict]) -> tuple[float | None, float | None, int, int, int, int]:
    """Return (fp_rate, fn_rate, fp, fn, total_false, total_true) from the most recent trace."""
    for trace in reversed(traces):
        detail = trace.get("routing_detail", [])
        if not detail:
            continue
        fp = sum(1 for d in detail if not d.get("correct") and d.get("should_trigger") is False)
        fn = sum(1 for d in detail if not d.get("correct") and d.get("should_trigger") is True)
        total_false = sum(1 for d in detail if d.get("should_trigger") is False)
        total_true = sum(1 for d in detail if d.get("should_trigger") is True)
        fp_rate = fp / total_false if total_false else 0.0
        fn_rate = fn / total_true if total_true else 0.0
        return fp_rate, fn_rate, fp, fn, total_false, total_true
    return None, None, 0, 0, 0, 0


def _recurring_false_positives(traces: list[dict], recent_n: int = 5) -> list[str]:
    """Return inputs that appear as false positives in the last N traces."""
    fp_inputs: dict[str, int] = {}
    for trace in traces[-recent_n:]:
        for d in trace.get("routing_detail", []):
            if not d.get("correct") and d.get("should_trigger") is False:
                inp = d.get("input", "")
                fp_inputs[inp] = fp_inputs.get(inp, 0) + 1
    # Only include those appearing in 2+ of the last N traces
    recurring = [(inp, count) for inp, count in fp_inputs.items() if count >= 2]
    recurring.sort(key=lambda x: -x[1])
    return [f"  - \"{inp}\" (seen in {count}/{recent_n} recent traces)" for inp, count in recurring]


def generate_milestone(experiment_dir: Path, every: int = 25, force: bool = False) -> bool:
    """
    Generate a milestone summary if the iteration count is a multiple of `every` (or force=True).

    Returns True if a milestone was written, False if not needed yet.
    Exits with code 2 on error.
    """
    results_tsv = experiment_dir / "evals" / "results.tsv"
    traces_dir = experiment_dir / "evals" / "traces"

    if not results_tsv.exists():
        print(f"ERROR: results.tsv not found at {results_tsv}", file=sys.stderr)
        sys.exit(2)

    rows = _load_tsv(results_tsv)
    iter_rows = [r for r in rows if r.get("status") in ("KEEP", "DISCARD")]
    iteration_count = len(iter_rows)

    if iteration_count == 0:
        print("No iterations yet — nothing to summarize.")
        return False

    if not force and (iteration_count % every != 0):
        print(f"Iteration {iteration_count} is not a multiple of {every} — no milestone needed.")
        return False

    traces = _load_traces(traces_dir)
    baseline_rows = [r for r in rows if r.get("status") == "BASELINE"]
    keep_rows = [r for r in iter_rows if r.get("status") == "KEEP"]
    discard_rows = [r for r in iter_rows if r.get("status") == "DISCARD"]

    baseline_score = float(baseline_rows[-1]["score"]) if baseline_rows else 0.0
    current_score = float(rows[-1]["score"]) if rows else 0.0
    net_delta = current_score - baseline_score
    acceptance_rate = len(keep_rows) / iteration_count if iteration_count else 0.0

    best_row = max(iter_rows, key=lambda r: float(r["score"])) if iter_rows else None
    best_score = float(best_row["score"]) if best_row else baseline_score
    best_desc = best_row.get("description", "baseline") if best_row else "baseline"

    fp_rate, fn_rate, *_ = _current_fp_fn(traces)

    if fp_rate is not None and fn_rate is not None:
        if fp_rate > fn_rate:
            dominant = f"PRECISION (fp_rate={fp_rate:.2f}, fn_rate={fn_rate:.2f})"
            recommendation = "Remove broad keywords or add adversarial <example> blocks. Do NOT add more keywords."
        elif fn_rate > fp_rate:
            dominant = f"RECALL (fp_rate={fp_rate:.2f}, fn_rate={fn_rate:.2f})"
            recommendation = "Add specific trigger phrases. Check 4-char word floor (no 'fix', 'run', 'doc')."
        elif fp_rate == 0.0 and fn_rate == 0.0:
            dominant = "NONE — routing is clean"
            recommendation = "Focus on heuristic structural improvements (examples, body length, references)."
        else:
            dominant = f"BOTH precision and recall (fp_rate={fp_rate:.2f}, fn_rate={fn_rate:.2f})"
            recommendation = "Add specific trigger phrases AND adversarial <example> blocks."
    else:
        dominant = "unknown (no trace data)"
        recommendation = "Run an iteration to generate trace data first."

    milestone_num = iteration_count
    lines = [
        f"# Milestone Summary: Iterations 1–{milestone_num}\n",
        f"\nGenerated: {datetime.now(timezone.utc).isoformat()}\n",
        f"Experiment: `{experiment_dir}`\n",
        "\n---\n",
        "\n## Score Trajectory\n",
        f"- Baseline:        {baseline_score:.4f}\n",
        f"- Best achieved:   {best_score:.4f}  (\"{best_desc}\")\n",
        f"- Current:         {current_score:.4f}\n",
        f"- Net delta:       {net_delta:+.4f}\n",
        "\n## KEEP/DISCARD Breakdown\n",
        f"- {len(keep_rows)} KEEP, {len(discard_rows)} DISCARD  ({acceptance_rate:.0%} acceptance rate)\n",
    ]

    best_lines = _best_keeps(iter_rows, top_n=3)
    if best_lines:
        lines.append("\n## What Worked (top KEEPs by score delta)\n")
        lines.extend(line + "\n" for line in best_lines)

    worst_lines = _worst_discards(iter_rows, top_n=3)
    if worst_lines:
        lines.append("\n## What Did Not Work (worst DISCARDs — do not retry these)\n")
        lines.extend(line + "\n" for line in worst_lines)

    recurring_fp = _recurring_false_positives(traces)
    if recurring_fp:
        lines.append("\n## Recurring False-Positive Inputs (from last 5 traces)\n")
        lines.extend(line + "\n" for line in recurring_fp)

    lines.append("\n## Dominant Problem\n")
    lines.append(f"- {dominant}\n")
    lines.append(f"\n## Recommended Focus for Next {every} Iterations\n")
    lines.append(f"- {recommendation}\n")

    milestone_filename = f"milestone_{milestone_num:03d}.md"
    traces_dir.mkdir(parents=True, exist_ok=True)
    out_path = traces_dir / milestone_filename
    out_path.write_text("".join(lines))
    print(f"-> milestone written: {out_path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write milestone summary files for long autoresearch runs"
    )
    parser.add_argument(
        "--experiment-dir", required=True,
        help="Path to the experiment directory (contains evals/ and references/)"
    )
    parser.add_argument(
        "--every", type=int, default=25,
        help="Write a milestone every N iterations (default: 25)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Write a milestone even if iteration count is not a multiple of --every"
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir).resolve()
    if not experiment_dir.exists():
        print(f"ERROR: experiment-dir not found: {experiment_dir}", file=sys.stderr)
        sys.exit(2)

    generate_milestone(experiment_dir, every=args.every, force=args.force)


if __name__ == "__main__":
    main()
