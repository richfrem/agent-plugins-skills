#!/usr/bin/env python
"""
run_loop.py (CLI)
=====================================

Purpose:
    Run the eval + improve loop until all pass or max iterations reached.
    Combines run_eval.py and improve_description.py in an automated keep-discard loop,
    tracking history and returning the best description found.
    Supports train/test split to prevent overfitting.

Key Input Dependencies:
    - cheapest_models.json       — Configuration detailing low-cost model selections
    - eval_set.json              — Evaluation database of queries and trigger criteria
    - generate_report.py         — HTML report template builder
    - improve_description.py     — Core optimization logic handler
    - run_eval.py                — Evaluation process executor
    - argparse, json, random, sys— Standard library packages for CLI arguments, file loads, and splits

Layer: Meta-Execution

Usage Examples:
    python run_loop.py --eval-set set.json --skill-path my_skill/

Supported Object Types:
    - Skill directories with SKILL.md
    - list[dict] evaluation datasets

CLI Arguments:
    --eval-set: Path to eval set JSON file
    --skill-path: Path to skill directory
    --description: Override starting description override
    --num-workers: Number of parallel workers
    --timeout: Timeout per query in seconds
    --max-iterations: Max improvement iterations
    --runs-per-query: Number of runs per query (for stability)
    --trigger-threshold: Rate threshold to consider a pass
    --holdout: Fraction of eval set to hold out for testing (0 to disable)
    --model: Default backend model override
    --eval-model: Evaluator backend model override
    --improve-model: Optimizer backend model override
    --eval-engine: "claude" only
    --improve-engine: "claude" or "copilot"
    --verbose: Enable thinking prints to stderr
    --report: HTML generation path ("auto", "none")
    --results-dir: Save folder path for artifact persistence

Input Files:
    - eval_set.json
    - SKILL.md

Output:
    - HTML Report files
    - results.tsv running tracking
    - Json results summary

Key Functions:
    - split_eval_set(): Stratified divider dataset creator.
    - run_loop(): Coordinates backends with automated keep/discard logic gates.

Script Dependencies:
    - generate_report.py
    - improve_description.py
    - run_eval.py
    - utils.py

Consumed by:
    - User (CLI)
    - Continuous skill optimizer

Credits:
    Inspired by and adapted from Anthropic's skill-creator.
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


def _load_cheapest_model(engine: str, fallback: str, ref_path: "Path | None" = None) -> str:
    """Load cheapest model for engine from cheapest_models.json, falling back gracefully."""
    try:
        if ref_path is None:
            script_dir = Path(__file__).resolve().parent
            ref_path = script_dir.parents[2] / "references" / "cheapest_models.json"
        if ref_path.exists():
            data = json.loads(ref_path.read_text())
            return data.get(engine, {}).get("model", fallback)
    except Exception:
        pass
    return fallback


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


def print_eval_stats(label: str, results: list[dict], elapsed: float) -> None:
    """Print accuracy, precision, recall, and pass details for evaluated queries to stderr."""
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


def _split_train_test(eval_set: list[dict], holdout: float, verbose: bool) -> tuple:
    """Split into train/test if holdout > 0, else use the full eval set as train."""
    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []
    return train_set, test_set


def _init_loop_state(current_description: str) -> dict:
    """Initialize the mutable per-iteration state tracked across the improvement loop."""
    return {
        "history": [],
        "exit_reason": "unknown",
        "best_description_so_far": current_description,
        "best_train_passed": -1,
        "best_train_failed": 10**9,
        "iteration_timings": [],
        "current_description": current_description,
    }


def _build_loop_cfg(
    train_set: list, test_set: list, name: str, content: str, num_workers: int, timeout: int,
    project_root, runs_per_query: int, trigger_threshold: float, eval_model: str | None,
    eval_engine: str, improve_model: str | None, improve_engine: str, log_dir, results_tsv_path,
    timing_path, live_report_path, original_description: str, holdout: float, verbose: bool, loop_start: float,
) -> dict:
    """Bundle the static per-run configuration into a single dict for iteration helpers."""
    return {
        "train_set": train_set, "test_set": test_set, "name": name, "content": content,
        "num_workers": num_workers, "timeout": timeout, "project_root": project_root,
        "runs_per_query": runs_per_query, "trigger_threshold": trigger_threshold,
        "eval_model": eval_model, "eval_engine": eval_engine,
        "improve_model": improve_model, "improve_engine": improve_engine,
        "log_dir": log_dir, "results_tsv_path": results_tsv_path, "timing_path": timing_path,
        "live_report_path": live_report_path, "original_description": original_description,
        "holdout": holdout, "verbose": verbose, "loop_start": loop_start,
    }


def _run_eval_for_iteration(
    train_set: list[dict], test_set: list[dict], name: str, current_description: str,
    num_workers: int, timeout: int, project_root, runs_per_query: int, trigger_threshold: float,
    eval_model: str | None, eval_engine: str,
) -> dict:
    """Evaluate train+test together in one batch, then split results back out by query."""
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

    return {
        "eval_elapsed": eval_elapsed,
        "train_results": train_results,
        "train_summary": train_summary,
        "test_results": test_results,
        "test_summary": test_summary,
    }


def _decide_and_update_best(loop_state: dict, train_summary: dict, current_description: str) -> tuple:
    """Decide keep/discard based on train score; updates loop_state's best-tracking fields in place."""
    improved = (
        train_summary["passed"] > loop_state["best_train_passed"]
        or (
            train_summary["passed"] == loop_state["best_train_passed"]
            and train_summary["failed"] < loop_state["best_train_failed"]
        )
    )
    decision = "keep" if improved else "discard"
    notes = (
        "new best on train set"
        if improved
        else "regression/no gain; keep last known good description"
    )
    if improved:
        loop_state["best_train_passed"] = train_summary["passed"]
        loop_state["best_train_failed"] = train_summary["failed"]
        loop_state["best_description_so_far"] = current_description
    return decision, notes


def _record_iteration(
    history: list, iteration: int, current_description: str, decision: str, notes: str,
    train_summary: dict, train_results: dict, test_summary, test_results,
    results_tsv_path, train_score: str, test_score: str,
) -> None:
    """Append this iteration's outcome to history and, if configured, results.tsv."""
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


def _write_live_report(
    live_report_path: Path, original_description: str, current_description: str,
    history: list, holdout: float, train_set: list, test_set: list, name: str,
) -> None:
    """Write the in-progress (auto-refreshing) live HTML report."""
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


def _process_eval_results(iteration: int, loop_state: dict, cfg: dict, current_description: str, eval_bundle: dict) -> tuple:
    """Score the eval outcome, record history/tsv/live-report, and build the timing entry.

    Returns (train_score, test_score, timing_entry).
    """
    eval_elapsed = eval_bundle["eval_elapsed"]
    train_results = eval_bundle["train_results"]
    train_summary = eval_bundle["train_summary"]
    test_results = eval_bundle["test_results"]
    test_summary = eval_bundle["test_summary"]

    train_score = f"{train_summary['passed']}/{train_summary['total']}"
    test_score = f"{test_summary['passed']}/{test_summary['total']}" if test_summary else "-"

    decision, notes = _decide_and_update_best(loop_state, train_summary, current_description)

    _record_iteration(
        loop_state["history"], iteration, current_description, decision, notes,
        train_summary, train_results, test_summary, test_results,
        cfg["results_tsv_path"], train_score, test_score,
    )

    if cfg["live_report_path"]:
        _write_live_report(
            cfg["live_report_path"], cfg["original_description"], current_description,
            loop_state["history"], cfg["holdout"], cfg["train_set"], cfg["test_set"], cfg["name"],
        )

    timing_entry = {
        "iteration": iteration,
        "eval_seconds": round(eval_elapsed, 3),
        "improve_seconds": 0.0,
        "train_score": train_score,
        "test_score": test_score,
        "decision": decision,
    }
    loop_state["iteration_timings"].append(timing_entry)

    return train_score, test_score, timing_entry


def _check_exit_conditions(iteration: int, max_iterations: int, train_summary: dict, loop_state: dict, verbose: bool) -> bool:
    """Check all-passed / max-iterations exit conditions, updating loop_state['exit_reason']."""
    if train_summary["failed"] == 0:
        loop_state["exit_reason"] = f"all_passed (iteration {iteration})"
        if verbose:
            print(f"\nAll train queries passed on iteration {iteration}!", file=sys.stderr)
        return True

    if iteration == max_iterations:
        loop_state["exit_reason"] = f"max_iterations ({max_iterations})"
        if verbose:
            print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
        return True

    return False


def _run_iteration_eval_and_score(iteration: int, max_iterations: int, loop_state: dict, cfg: dict) -> tuple:
    """Run eval, score/record the outcome, and check exit conditions for one iteration.

    Returns (should_break, train_results, train_score, test_score, timing_entry).
    """
    verbose = cfg["verbose"]
    current_description = loop_state["current_description"]

    if verbose:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
        print(f"Description: {current_description}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    eval_bundle = _run_eval_for_iteration(
        cfg["train_set"], cfg["test_set"], cfg["name"], current_description,
        cfg["num_workers"], cfg["timeout"], cfg["project_root"], cfg["runs_per_query"],
        cfg["trigger_threshold"], cfg["eval_model"], cfg["eval_engine"],
    )
    train_results = eval_bundle["train_results"]
    train_summary = eval_bundle["train_summary"]

    train_score, test_score, timing_entry = _process_eval_results(
        iteration, loop_state, cfg, current_description, eval_bundle
    )

    if verbose:
        print_eval_stats("Train", train_results["results"], eval_bundle["eval_elapsed"])
        if eval_bundle["test_summary"]:
            print_eval_stats("Test ", eval_bundle["test_results"]["results"], 0)

    should_break = _check_exit_conditions(iteration, max_iterations, train_summary, loop_state, verbose)

    return should_break, train_results, train_score, test_score, timing_entry


def _handle_improve_crash(
    e: Exception, iteration: int, train_score: str, test_score: str,
    best_description_so_far: str, history: list, timing_entry: dict,
    results_tsv_path, verbose: bool,
) -> None:
    """Log an improvement-backend crash: mark history/timing, append tsv row, print if verbose."""
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
    if verbose:
        print(f"Improve step failed: {e}", file=sys.stderr)


def _attempt_improvement(
    name: str, content: str, best_description_so_far: str, train_results: dict, history: list,
    improve_model: str | None, improve_engine: str, log_dir, iteration: int,
    train_score: str, test_score: str, results_tsv_path, timing_entry: dict, verbose: bool,
) -> tuple:
    """Call improve_description(), falling back to the last known good description on failure.

    Karpathy-style rule: single-hypothesis changes and explicit rollback on regression.
    Returns (new_description_or_None, improve_elapsed, crashed).
    """
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
        _handle_improve_crash(
            e, iteration, train_score, test_score, best_description_so_far,
            history, timing_entry, results_tsv_path, verbose,
        )
        return None, improve_elapsed, True

    improve_elapsed = time.time() - t0
    timing_entry["improve_seconds"] = round(improve_elapsed, 3)
    return new_description, improve_elapsed, False


def _run_iteration(iteration: int, max_iterations: int, loop_state: dict, cfg: dict) -> bool:
    """Run one full loop iteration (eval+score, then improve). Returns True if the loop should stop."""
    should_break, train_results, train_score, test_score, timing_entry = _run_iteration_eval_and_score(
        iteration, max_iterations, loop_state, cfg
    )
    if should_break:
        return True

    verbose = cfg["verbose"]
    if verbose:
        print(f"\nImproving description...", file=sys.stderr)

    new_description, improve_elapsed, crashed = _attempt_improvement(
        cfg["name"], cfg["content"], loop_state["best_description_so_far"], train_results,
        loop_state["history"], cfg["improve_model"], cfg["improve_engine"], cfg["log_dir"], iteration,
        train_score, test_score, cfg["results_tsv_path"], timing_entry, verbose,
    )

    if crashed:
        loop_state["current_description"] = loop_state["best_description_so_far"]
        return False

    if cfg["timing_path"]:
        _write_timing_json(
            cfg["timing_path"],
            {
                "exit_reason": "in_progress",
                "iterations": loop_state["iteration_timings"],
                "total_duration_seconds": round(time.time() - cfg["loop_start"], 3),
            },
        )

    if verbose:
        print(f"Proposed ({improve_elapsed:.1f}s): {new_description}", file=sys.stderr)

    loop_state["current_description"] = new_description
    return False


def _backfill_iteration_timings(history: list) -> list:
    """Reconstruct iteration_timings from history when the loop broke before recording any."""
    return [
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


def _finalize_loop_result(
    loop_state: dict, train_set: list, test_set: list, holdout: float,
    original_description: str, verbose: bool, timing_path, loop_start: float,
) -> dict:
    """Backfill timings if the loop broke before recording any, pick the best iteration by
    test score (or train if no test set), and build the final result dict."""
    history = loop_state["history"]
    iteration_timings = loop_state["iteration_timings"]
    exit_reason = loop_state["exit_reason"]
    current_description = loop_state["current_description"]

    if not iteration_timings and history:
        iteration_timings = _backfill_iteration_timings(history)

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
    train_set, test_set = _split_train_test(eval_set, holdout, verbose)

    loop_state = _init_loop_state(current_description)
    loop_start = time.time()

    if results_tsv_path:
        _ensure_results_tsv(results_tsv_path)

    cfg = _build_loop_cfg(
        train_set, test_set, name, content, num_workers, timeout, project_root, runs_per_query,
        trigger_threshold, eval_model, eval_engine, improve_model, improve_engine, log_dir,
        results_tsv_path, timing_path, live_report_path, original_description, holdout, verbose, loop_start,
    )

    for iteration in range(1, max_iterations + 1):
        if _run_iteration(iteration, max_iterations, loop_state, cfg):
            break

    return _finalize_loop_result(
        loop_state, train_set, test_set, holdout, original_description, verbose, timing_path, loop_start
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for the eval + improve loop."""
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
    parser.add_argument("--mock", action="store_true", help="Resolve models from cheapest_models.json, print JSON, and exit without running the loop.")
    return parser


def _resolve_model_routing(args) -> None:
    """Backward-compatible model routing: fill eval/improve models from the legacy --model
    flag, and pick a cheap fallback model for the copilot improve engine when unspecified."""
    if not args.eval_model:
        args.eval_model = args.model
    if not args.improve_model:
        args.improve_model = args.model
    if args.improve_engine == "copilot" and not args.improve_model:
        args.improve_model = _load_cheapest_model("copilot", "gpt-5-mini")


def _setup_live_report(args, skill_path: Path):
    """Resolve the live report path (if enabled), write a starting placeholder, and open it."""
    if args.report == "none":
        return None

    if args.report == "auto":
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        live_report_path = Path(tempfile.gettempdir()) / f"skill_description_report_{skill_path.name}_{timestamp}.html"
    else:
        live_report_path = Path(args.report)
    # Open the report immediately so the user can watch
    live_report_path.write_text("<html><body><h1>Starting optimization loop...</h1><meta http-equiv='refresh' content='5'></body></html>")
    webbrowser.open(str(live_report_path))
    return live_report_path


def _setup_results_dir(args) -> tuple:
    """Create the timestamped results directory (if requested) and derive log/tsv/timing paths."""
    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = None

    log_dir = results_dir / "logs" if results_dir else None
    results_tsv_path = results_dir / "results.tsv" if results_dir else None
    timing_path = results_dir / "timing.json" if results_dir else None
    return results_dir, log_dir, results_tsv_path, timing_path


def _write_final_outputs(output: dict, results_dir, live_report_path, name: str) -> None:
    """Write the JSON result to stdout/results_dir and the final (non-refreshing) HTML report."""
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


def main() -> None:
    """CLI entry point: parses optimizer loop configuration and manages the end-to-end keep-discard evaluation process."""
    parser = _build_arg_parser()
    args = parser.parse_args()
    _resolve_model_routing(args)

    if args.mock:
        print(json.dumps({"improve_model": args.improve_model, "eval_model": args.eval_model}))
        sys.exit(0)

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, _, _ = parse_skill_md(skill_path)

    live_report_path = _setup_live_report(args, skill_path)
    results_dir, log_dir, results_tsv_path, timing_path = _setup_results_dir(args)

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

    _write_final_outputs(output, results_dir, live_report_path, name)


if __name__ == "__main__":
    main()
