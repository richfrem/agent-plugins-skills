#!/usr/bin/env python
"""
run_eval.py (CLI)
=====================================

Purpose:
    Run trigger evaluation for a skill description to check if Claude invokes it correctly.
    Tests whether a skill's description causes Claude to trigger (read the skill)
    for a set of queries. Outputs results as JSON.

Key Input Dependencies:
    - eval_set.json             — Dataset containing test queries and trigger expectations
    - utils.py                  — Internal helper file defining parse_skill_md
    - argparse, json, subprocess— Standard library packages for execution, serialization, and CLI parsing

Layer: Meta-Execution

Usage Examples:
    python run_eval.py --eval-set set.json --skill-path my_skill/

Supported Object Types:
    - Skill directories with SKILL.md
    - list[dict] evaluation query datasets

CLI Arguments:
    --eval-set: Path to eval set JSON file
    --skill-path: Path to skill directory
    --description: Override description to test instead of SKILL.md one
    --num-workers: Number of parallel subprocess workers
    --timeout: Timeout per evaluation query in seconds
    --runs-per-query: Number of runs per query (for stability)
    --trigger-threshold: Rate threshold to consider a pass
    --model: Model backend override
    --engine: "claude" only
    --verbose: Print progress to stderr

Input Files:
    - eval_set.json
    - SKILL.md

Output:
    - JSON dictionary with "results" and "summary" statistics

Key Functions:
    - run_single_query(): Inlines command with unique GUID and tracks stream deltas.
    - run_eval(): Executes multiprocess concurrency map.

Script Dependencies:
    - utils.py (parse_skill_md)

Consumed by:
    - User (CLI)
    - Continuous skill optimizer

Credits:
    Inspired by and adapted from Anthropic's skill-creator.
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Mimics how Claude Code discovers its project root, so the command file
    we create ends up where claude -p will look for it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def _prepare_command_file(
    project_root: str,
    clean_name: str,
    skill_name: str,
    skill_description: str,
) -> Path:
    """Write a temporary command file to .claude/commands/ and return its path."""
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    project_commands_dir.mkdir(parents=True, exist_ok=True)
    command_file = project_commands_dir / f"{clean_name}.md"
    indented_desc = "\n  ".join(skill_description.split("\n"))
    command_content = (
        f"---\ndescription: |\n  {indented_desc}\n---\n\n"
        f"# {skill_name}\n\nThis skill handles: {skill_description}\n"
    )
    command_file.write_text(command_content)
    return command_file


def _build_claude_cmd(query: str, model: str | None) -> list[str]:
    """Build the claude CLI command list for a single query."""
    cmd = ["claude", "-p", query, "--output-format", "stream-json",
           "--verbose", "--include-partial-messages"]
    if model:
        cmd.extend(["--model", model])
    return cmd


def _parse_stream_events(buffer: str, clean_name: str, triggered: bool,
                         pending_tool_name: list, accumulated_json: list) -> tuple[bool, bool]:
    """Parse stream JSON events from buffer. Returns (triggered, done) tuple."""
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "stream_event":
            se = event.get("event", {})
            se_type = se.get("type", "")
            if se_type == "content_block_start":
                cb = se.get("content_block", {})
                if cb.get("type") == "tool_use":
                    tool_name = cb.get("name", "")
                    if tool_name in ("Skill", "Read"):
                        pending_tool_name[0] = tool_name
                        accumulated_json[0] = ""
                    else:
                        return False, True
            elif se_type == "content_block_delta" and pending_tool_name[0]:
                delta = se.get("delta", {})
                if delta.get("type") == "input_json_delta":
                    accumulated_json[0] += delta.get("partial_json", "")
                    if clean_name in accumulated_json[0]:
                        return True, True
            elif se_type in ("content_block_stop", "message_stop"):
                if pending_tool_name[0]:
                    return clean_name in accumulated_json[0], True
                if se_type == "message_stop":
                    return False, True
        elif event.get("type") == "assistant":
            message = event.get("message", {})
            for ci in message.get("content", []):
                if ci.get("type") != "tool_use":
                    continue
                tool_name = ci.get("name", "")
                tool_input = ci.get("input", {})
                if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                    triggered = True
                elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                    triggered = True
                return triggered, True
        elif event.get("type") == "result":
            return triggered, True
    return triggered, False


def _run_claude_process(cmd: list, project_root: str, env: dict, timeout: int, clean_name: str) -> bool:
    """Spawn the claude subprocess and read its stream-json stdout until a decision is made."""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               cwd=project_root, env=env)
    triggered = False
    start_time = time.time()
    buffer = ""
    pending_tool_name = [None]
    accumulated_json = [""]
    try:
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                remaining = process.stdout.read()
                if remaining:
                    buffer += remaining.decode("utf-8", errors="replace")
                break
            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            triggered, done = _parse_stream_events(
                buffer, clean_name, triggered, pending_tool_name, accumulated_json)
            if done:
                return triggered
            buffer = buffer.split("\n", 1)[-1] if "\n" in buffer else buffer
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    return triggered


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
    engine: str = "claude",
) -> bool:
    """Run a single query and return whether the skill was triggered."""
    if engine != "claude":
        raise ValueError("run_eval currently supports only engine='claude'.")
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    command_file = _prepare_command_file(project_root, clean_name, skill_name, skill_description)
    try:
        cmd = _build_claude_cmd(query, model)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        return _run_claude_process(cmd, project_root, env, timeout, clean_name)
    finally:
        if command_file.exists():
            command_file.unlink()


def _collect_future_results(
    future_to_info: dict,
) -> tuple[dict[str, list[bool]], dict[str, dict]]:
    """Collect results from completed futures into per-query trigger lists."""
    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}
    for future in as_completed(future_to_info):
        item, _ = future_to_info[future]
        query = item["query"]
        query_items[query] = item
        if query not in query_triggers:
            query_triggers[query] = []
        try:
            query_triggers[query].append(future.result())
        except Exception as e:
            print(f"Warning: query failed: {e}", file=sys.stderr)
            query_triggers[query].append(False)
    return query_triggers, query_items


def _build_query_results(
    query_triggers: dict[str, list[bool]],
    query_items: dict[str, dict],
    trigger_threshold: float,
) -> tuple[list[dict], int, int]:
    """Convert per-query trigger lists into pass/fail result dicts."""
    results = []
    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        did_pass = (trigger_rate >= trigger_threshold) if should_trigger else (trigger_rate < trigger_threshold)
        results.append({
            "query": query, "should_trigger": should_trigger,
            "trigger_rate": trigger_rate, "triggers": sum(triggers),
            "runs": len(triggers), "pass": did_pass,
        })
    passed = sum(1 for r in results if r["pass"])
    return results, passed, len(results)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    engine: str = "claude",
) -> dict:
    """Run the full eval set and return results."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query, item["query"], skill_name, description,
                    timeout, str(project_root), model, engine,
                )
                future_to_info[future] = (item, run_idx)
        query_triggers, query_items = _collect_future_results(future_to_info)
    results, passed, total = _build_query_results(query_triggers, query_items, trigger_threshold)
    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for the trigger evaluator."""
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to use for claude -p (default: user's configured model)")
    parser.add_argument(
        "--engine",
        default="claude",
        choices=["claude"],
        help="Evaluation backend engine (currently claude only)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    return parser


def main() -> None:
    """CLI entry point: parses evaluation set options, resolves the target skill description, and executes trigger analysis."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        engine=args.engine,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
