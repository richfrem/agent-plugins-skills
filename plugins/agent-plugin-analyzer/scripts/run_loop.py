#!/usr/bin/env python3
"""
run_loop.py (CLI)
=====================================

Purpose:
    Runs the evaluation and improvement loop for skill descriptions iteratively.
    Combines run_eval.py and improve_description.py in a single loop to track 
    scores and return the best found description candidate.

Layer: Investigate / Optimization / Execution

Usage Examples:
    python3 run_loop.py --eval-set eval_set.json --skill-path plugins/agent-plugin-analyzer/skills/audit-plugin
    python3 run_loop.py --eval-set set.json --skill-path path/to/skill --max-iterations 10

Supported Object Types:
    Optimizer execution benchmarks.

CLI Arguments:
    --eval-set: Path to eval set JSON file (Required)
    --skill-path: Path to skill directory (Required)
    --description: Override starting description 
    --num-workers: Number of parallel workers (default: 10)
    --timeout: Timeout per query in seconds (default: 30)
    --max-iterations: Max improvement iterations (default: 5)
    --runs-per-query: Number of runs per query (default: 3)
    --trigger-threshold: Trigger rate threshold (default: 0.5)
    --holdout: Fraction of eval set to hold out for testing (default: 0.4)
    --eval-model: Model with evaluation backend
    --improve-model: Model with improvement backend
    --verbose: Print progress to stderr
    --report: Generate HTML report path (default: auto)
    --results-dir: Save all outputs to a timestamped subdirectory

Input Files:
    - eval_set.json (Required)
    - SKILL.md (Inside skill path)

Output:
    - JSON results format via stdout.
    - Live HTML report page dashboards.
    - results.tsv metric logging.

Key Functions:
    - run_loop()
    - split_eval_set()

Script Dependencies:
    - generate_report
    - improve_description
    - run_eval
    - utils

Consumed by:
    trigger evaluation benchmarks, continuous-skill-optimizer.
"""

import argparse
import json
import random
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

from generate_report import generate_html
from improve_description import improve_description
from run_eval import find_project_root, run_eval
from utils import parse_skill_md


def _ensure_results_tsv(results_tsv_path: Path) -> None:
    """Create results.tsv with a header if it does not exist."""
    if results_tsv_path.exists():
        return
    header = "iteration\ttrain_score\ttest_score\tdecision\tnotes\tdescription\n"
    results_tsv_path.write_text(header)


def _append_results_tsv(
    results_tsv_path: Path,
    *,
    iteration: int,
    train_score: str,
    test_score: str,
    decision: str,
    notes: str,
    description: str,
) -> None:
    """Append one iteration row to results.tsv."""
    safe_description = description.replace("\t", " ").replace("\n", " ").strip()
    safe_notes = notes.replace("\t", " ").replace("\n", " ").strip()
    row = f"{iteration}\t{train_score}\t{test_score}\t{decision}\t{safe_notes}\t{safe_description}\n"
    with results_tsv_path.open("a") as f:
        f.write(row)


def _write_timing_json(timing_path: Path, payload: dict) -> None:
    """Persist timing metrics for benchmark observability."""
    timing_path.write_text(json.dumps(payload, indent=2))


def split_eval_set(eval_set: list[dict], holdout: float, seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test sets, stratified by should_trigger."""
    random.seed(seed)

    # Separate by should_trigger
    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]

    # Shuffle each group
    random.shuffle(trigger)
    random.shuffle(no_trigger)

    # Calculate split points
    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))

    # Split
    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]

    return train_set, test_set


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    eval_model: str | None,
    improve_model: str | None,
    verbose: bool,
    eval_engine: str = "claude",
    improve_engine: str = "claude",
    live_report_path: Path | None = None,
    log_dir: Path | None = None,
    results_tsv_path: Path | None = None,
    timing_path: Path | None = None,
) -> dict:
    """Run the eval + improvement loop with explicit keep/discard governance."""
    project_root = find_project_root()
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description

    # Split into train/test if holdout > 0
    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []

    history = []
    exit_reason = "unknown"
    best_description_so_far = current_description
    best_train_passed = -1
    best_train_failed = 10**9
    iteration_timings: list[dict] = []
    loop_start = time.time()

    if results_tsv_path:
        _ensure_results_tsv(results_tsv_path)

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
            print(f"Description: {current_description}", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

        # Evaluate train + test together in one batch for parallelism
        all_queries = train_set + test_set
        t0 = time.time()
        all_results = run_eval(
            eval_set=all_queries,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=eval_model,
            engine=eval_engine,
        )
        eval_elapsed = time.time() - t0

        # Split results back into train/test by matching queries
        train_queries_set = {q["query"] for q in train_set}
        train_result_list = [r for r in all_results["results"] if r["query"] in train_queries_set]
        test_result_list = [r for r in all_results["results"] if r["query"] not in train_queries_set]

        train_passed = sum(1 for r in train_result_list if r["pass"])
        train_total = len(train_result_list)
        train_summary = {"passed": train_passed, "failed": train_total - train_passed, "total": train_total}
        train_results = {"results": train_result_list, "summary": train_summary}

        if test_set:
            test_passed = sum(1 for r in test_result_list if r["pass"])
            test_total = len(test_result_list)
            test_summary = {"passed": test_passed, "failed": test_total - test_passed, "total": test_total}
            test_results = {"results": test_result_list, "summary": test_summary}
        else:
            test_results = None
            test_summary = None

        train_score = f"{train_summary['passed']}/{train_summary['total']}"
        test_score = (
            f"{test_summary['passed']}/{test_summary['total']}"
            if test_summary
            else "-"
        )
        improved = (
            train_summary["passed"] > best_train_passed
            or (
                train_summary["passed"] == best_train_passed
                and train_summary["failed"] < best_train_failed
            )
        )
        decision = "keep" if improved else "discard"
        notes = (
            "new best on train set"
            if improved
            else "regression/no gain; keep last known good description"
        )
        if improved:
            best_train_passed = train_summary["passed"]
            best_train_failed = train_summary["failed"]
            best_description_so_far = current_description

        history.append({
            "iteration": iteration,
            "description": current_description,
            "decision": decision,
            "notes": notes,
            "train_passed": train_summary["passed"],
            "train_failed": train_summary["failed"],
            "train_total": train_summary["total"],
            "train_results": train_results["results"],
            "test_passed": test_summary["passed"] if test_summary else None,
            "test_failed": test_summary["failed"] if test_summary else None,
            "test_total": test_summary["total"] if test_summary else None,
            "test_results": test_results["results"] if test_results else None,
            # For backward compat with report generator
            "passed": train_summary["passed"],
            "failed": train_summary["failed"],
            "total": train_summary["total"],
            "results": train_results["results"],
        })

        if results_tsv_path:
            _append_results_tsv(
                results_tsv_path,
                iteration=iteration,
                train_score=train_score,
                test_score=test_score,
                decision=decision,
                notes=notes,
                description=current_description,
            )

        # Write live report if path provided
        if live_report_path:
            partial_output = {
                "original_description": original_description,
                "best_description": current_description,
                "best_score": "in progress",
                "iterations_run": len(history),
                "holdout": holdout,
                "train_size": len(train_set),
                "test_size": len(test_set),
                "history": history,
            }
            live_report_path.write_text(generate_html(partial_output, auto_refresh=True, skill_name=name))

        timing_entry = {
            "iteration": iteration,
            "eval_seconds": round(eval_elapsed, 3),
            "improve_seconds": 0.0,
            "train_score": train_score,
            "test_score": test_score,
            "decision": decision,
        }
        iteration_timings.append(timing_entry)

        if verbose:
            def print_eval_stats(label: str, results: list[dict], elapsed: float) -> None:
                pos = [r for r in results if r["should_trigger"]]
                neg = [r for r in results if not r["should_trigger"]]
                tp = sum(r["triggers"] for r in pos)
                pos_runs = sum(r["runs"] for r in pos)
                fn = pos_runs - tp
                fp = sum(r["triggers"] for r in neg)
                neg_runs = sum(r["runs"] for r in neg)
                tn = neg_runs - fp
                total = tp + tn + fp + fn
                precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
                accuracy = (tp + tn) / total if total > 0 else 0.0
                print(f"{label}: {tp+tn}/{total} correct, precision={precision:.0%} recall={recall:.0%} accuracy={accuracy:.0%} ({elapsed:.1f}s)", file=sys.stderr)
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    rate_str = f"{r['triggers']}/{r['runs']}"
                    print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:60]}", file=sys.stderr)

            print_eval_stats("Train", train_results["results"], eval_elapsed)
            if test_summary:
                print_eval_stats("Test ", test_results["results"], 0)

        if train_summary["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            if verbose:
                print(f"\nAll train queries passed on iteration {iteration}!", file=sys.stderr)
            break

        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            if verbose:
                print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
            break

        # Improve the description based on train results.
        # Karpathy-style rule: single-hypothesis changes and explicit rollback on regression.
        if verbose:
            print(f"\nImproving description...", file=sys.stderr)

        t0 = time.time()
        # Strip test scores from history so improvement model can't see them
        blinded_history = [
            {k: v for k, v in h.items() if not k.startswith("test_")}
            for h in history
        ]
        try:
            new_description = improve_description(
                skill_name=name,
                skill_content=content,
                current_description=best_description_so_far,
                eval_results=train_results,
                history=blinded_history,
                model=improve_model,
                engine=improve_engine,
                log_dir=log_dir,
                iteration=iteration,
            )
        except Exception as e:
            # Crash/timeout discipline: log failure and continue from last known good.
            improve_elapsed = time.time() - t0
            timing_entry["improve_seconds"] = round(improve_elapsed, 3)
            timing_entry["decision"] = "crash"
            history[-1]["decision"] = "crash"
            history[-1]["notes"] = f"improvement backend failure: {e}"
            if results_tsv_path:
                _append_results_tsv(
                    results_tsv_path,
                    iteration=iteration,
                    train_score=train_score,
                    test_score=test_score,
                    decision="crash",
                    notes=f"improvement backend failure: {e}",
                    description=best_description_so_far,
                )
            current_description = best_description_so_far
            if verbose:
                print(f"Improve step failed: {e}", file=sys.stderr)
            continue

        improve_elapsed = time.time() - t0
        timing_entry["improve_seconds"] = round(improve_elapsed, 3)

        if timing_path:
            _write_timing_json(
                timing_path,
                {
                    "exit_reason": "in_progress",
                    "iterations": iteration_timings,
                    "total_duration_seconds": round(time.time() - loop_start, 3),
                },
            )

        if verbose:
            print(f"Proposed ({improve_elapsed:.1f}s): {new_description}", file=sys.stderr)

        current_description = new_description

    if not iteration_timings and history:
        iteration_timings = [
            {
                "iteration": h["iteration"],
                "eval_seconds": 0.0,
                "improve_seconds": 0.0,
                "train_score": f"{h['train_passed']}/{h['train_total']}",
                "test_score": (
                    f"{h['test_passed']}/{h['test_total']}"
                    if h.get("test_passed") is not None and h.get("test_total") is not None
                    else "-"
                ),
                "decision": h.get("decision", "keep"),
            }
            for h in history
        ]

    # Find the best iteration by TEST score (or train if no test set)
    if test_set:
        best = max(history, key=lambda h: h["test_passed"] or 0)
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda h: h["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit reason: {exit_reason}", file=sys.stderr)
        print(f"Best score: {best_score} (iteration {best['iteration']})", file=sys.stderr)

    if timing_path:
        _write_timing_json(
            timing_path,
            {
                "exit_reason": exit_reason,
                "iterations": iteration_timings,
                "total_duration_seconds": round(time.time() - loop_start, 3),
            },
        )

    return {
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval + improve loop")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.4, help="Fraction of eval set to hold out for testing (0 to disable)")
    parser.add_argument("--model", default=None, help="Legacy model flag (used as default for eval/improve models)")
    parser.add_argument("--eval-model", default=None, help="Model used for evaluation backend")
    parser.add_argument("--improve-model", default=None, help="Model used for improvement backend")
    parser.add_argument(
        "--eval-engine",
        default="claude",
        choices=["claude"],
        help="Evaluation backend engine (currently claude only)",
    )
    parser.add_argument(
        "--improve-engine",
        default="claude",
        choices=["claude", "copilot"],
        help="Improvement backend engine",
    )
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    parser.add_argument("--report", default="auto", help="Generate HTML report at this path (default: 'auto' for temp file, 'none' to disable)")
    parser.add_argument("--results-dir", default=None, help="Save all outputs (results.json, report.html, log.txt) to a timestamped subdirectory here")
    args = parser.parse_args()

    # Backward-compatible model routing
    if not args.eval_model:
        args.eval_model = args.model
    if not args.improve_model:
        args.improve_model = args.model
    if args.improve_engine == "copilot" and not args.improve_model:
        args.improve_model = "gpt-5-mini"

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, _, _ = parse_skill_md(skill_path)

    # Set up live report path
    if args.report != "none":
        if args.report == "auto":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            live_report_path = Path(tempfile.gettempdir()) / f"skill_description_report_{skill_path.name}_{timestamp}.html"
        else:
            live_report_path = Path(args.report)
        # Open the report immediately so the user can watch
        live_report_path.write_text("<html><body><h1>Starting optimization loop...</h1><meta http-equiv='refresh' content='5'></body></html>")
        webbrowser.open(str(live_report_path))
    else:
        live_report_path = None

    # Determine output directory (create before run_loop so logs can be written)
    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = None

    log_dir = results_dir / "logs" if results_dir else None
    results_tsv_path = results_dir / "results.tsv" if results_dir else None
    timing_path = results_dir / "timing.json" if results_dir else None

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        eval_model=args.eval_model,
        improve_model=args.improve_model,
        eval_engine=args.eval_engine,
        improve_engine=args.improve_engine,
        verbose=args.verbose,
        live_report_path=live_report_path,
        log_dir=log_dir,
        results_tsv_path=results_tsv_path,
        timing_path=timing_path,
    )

    # Save JSON output
    json_output = json.dumps(output, indent=2)
    print(json_output)
    if results_dir:
        (results_dir / "results.json").write_text(json_output)

    # Write final HTML report (without auto-refresh)
    if live_report_path:
        live_report_path.write_text(generate_html(output, auto_refresh=False, skill_name=name))
        print(f"\nReport: {live_report_path}", file=sys.stderr)

    if results_dir and live_report_path:
        (results_dir / "report.html").write_text(generate_html(output, auto_refresh=False, skill_name=name))

    if results_dir:
        print(f"Results saved to: {results_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
