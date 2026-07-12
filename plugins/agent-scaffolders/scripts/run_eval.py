#!/usr/bin/env python
"""
run_eval.py (CLI)
=====================================

Purpose:
    Tests whether a skill's description causes Claude to trigger (read the skill)
    for a set of queries. Outputs results as JSON. Inspired by skill-creator.

Layer: Investigate / Curate / Retrieve

Usage Examples:
    pythonrun_eval.py --eval-set eval_set.json --skill-path plugins/agent-scaffolders/skills/audit-plugin
    pythonrun_eval.py --eval-set eval_set.json --skill-path path/to/skill --verbose

Supported Object Types:
    Any structured prompt payload or skill config.

CLI Arguments:
    --eval-set: Path to eval set JSON file (Required)
    --skill-path: Path to skill directory (Required)
    --description: Override description to test
    --num-workers: Number of parallel workers (default: 10)
    --timeout: Timeout per query in seconds (default: 30)
    --runs-per-query: Number of runs per query (default: 3)
    --trigger-threshold: Trigger rate threshold (default: 0.5)
    --model: Model to use for claude -p
    --engine: Evaluation backend engine (default: claude)
    --verbose: Print progress to stderr

Input Files:
    - eval_set.json (Required)
    - SKILL.md (Inside skill path)

Output:
    JSON results string containing pass rate and details via stdout.

Key Functions:
    - find_project_root()
    - run_single_query()
    - run_eval()

Script Dependencies:
    - utils (for parse_skill_md)

Consumed by:
    trigger evaluation benchmarks.
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


def _write_command_file(command_file: Path, skill_name: str, skill_description: str) -> None:
    """Write the temporary command markdown file so the skill appears in available_skills."""
    command_file.parent.mkdir(parents=True, exist_ok=True)
    # Use YAML block scalar to avoid breaking on quotes in description
    indented_desc = "\n  ".join(skill_description.split("\n"))
    command_content = (
        f"---\n"
        f"description: |\n"
        f"  {indented_desc}\n"
        f"---\n\n"
        f"# {skill_name}\n\n"
        f"This skill handles: {skill_description}\n"
    )
    command_file.write_text(command_content)


def _build_claude_cmd(query: str, model: str | None) -> list:
    """Build the claude -p CLI command for stream-json trigger detection."""
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


def _process_stream_event(se: dict, se_type: str, clean_name: str, state: dict) -> bool | None:
    """Handle one 'stream_event' sub-type, updating state in place.

    Returns the trigger verdict if a decision was reached, else None.
    """
    if se_type == "content_block_start":
        cb = se.get("content_block", {})
        if cb.get("type") == "tool_use":
            tool_name = cb.get("name", "")
            if tool_name in ("Skill", "Read"):
                state["pending_tool_name"] = tool_name
                state["accumulated_json"] = ""
            else:
                return False

    elif se_type == "content_block_delta" and state["pending_tool_name"]:
        delta = se.get("delta", {})
        if delta.get("type") == "input_json_delta":
            state["accumulated_json"] += delta.get("partial_json", "")
            if clean_name in state["accumulated_json"]:
                return True

    elif se_type in ("content_block_stop", "message_stop"):
        if state["pending_tool_name"]:
            return clean_name in state["accumulated_json"]
        if se_type == "message_stop":
            return False

    return None


def _process_stream_line(line: str, clean_name: str, state: dict) -> bool | None:
    """Parse one stream-json line and update trigger-detection state in place.

    Returns the trigger verdict (True/False) if a decision was reached this line,
    else None to keep reading.
    """
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None

    # Early detection via stream events
    if event.get("type") == "stream_event":
        se = event.get("event", {})
        se_type = se.get("type", "")
        decision = _process_stream_event(se, se_type, clean_name, state)
        if decision is not None:
            return decision

    # Fallback: full assistant message
    elif event.get("type") == "assistant":
        message = event.get("message", {})
        for content_item in message.get("content", []):
            if content_item.get("type") != "tool_use":
                continue
            tool_name = content_item.get("name", "")
            tool_input = content_item.get("input", {})
            if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                state["triggered"] = True
            elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                state["triggered"] = True
            return state["triggered"]

    elif event.get("type") == "result":
        return state["triggered"]

    return None


def _read_stream_and_detect_trigger(process, timeout: int, clean_name: str) -> bool:
    """Read claude -p's stream-json stdout, detecting skill trigger from stream events."""
    start_time = time.time()
    buffer = ""
    state = {"pending_tool_name": None, "accumulated_json": "", "triggered": False}

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

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                decision = _process_stream_line(line, clean_name, state)
                if decision is not None:
                    return decision
    finally:
        # Clean up process on any exit path (return, exception, timeout)
        if process.poll() is None:
            process.kill()
            process.wait()

    return state["triggered"]


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
    engine: str = "claude",
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.
    """
    if engine != "claude":
        raise ValueError(
            "run_eval currently supports only engine='claude' because trigger "
            "detection relies on Claude stream events and skill routing."
        )

    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        _write_command_file(command_file, skill_name, skill_description)

        cmd = _build_claude_cmd(query, model)

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        return _read_stream_and_detect_trigger(process, timeout, clean_name)
    finally:
        if command_file.exists():
            command_file.unlink()


def _dispatch_queries(
    executor: ProcessPoolExecutor, eval_set: list[dict], skill_name: str, description: str,
    timeout: int, project_root: Path, runs_per_query: int, model: str | None, engine: str,
) -> dict:
    """Submit runs_per_query executions for each eval item. Returns future -> (item, run_idx)."""
    future_to_info = {}
    for item in eval_set:
        for run_idx in range(runs_per_query):
            future = executor.submit(
                run_single_query,
                item["query"],
                skill_name,
                description,
                timeout,
                str(project_root),
                model,
                engine,
            )
            future_to_info[future] = (item, run_idx)
    return future_to_info


def _collect_query_triggers(future_to_info: dict) -> tuple:
    """Collect futures as they complete, grouping trigger booleans by query."""
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


def _score_results(query_triggers: dict, query_items: dict, trigger_threshold: float) -> list:
    """Compute trigger rate and pass/fail for each query."""
    results = []
    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })
    return results


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
        future_to_info = _dispatch_queries(
            executor, eval_set, skill_name, description, timeout, project_root,
            runs_per_query, model, engine,
        )
        query_triggers, query_items = _collect_query_triggers(future_to_info)

    results = _score_results(query_triggers, query_items, trigger_threshold)

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
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


def _print_verbose_results(output: dict) -> None:
    """Print the pass/fail summary and per-query results to stderr."""
    summary = output["summary"]
    print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
    for r in output["results"]:
        status = "PASS" if r["pass"] else "FAIL"
        rate_str = f"{r['triggers']}/{r['runs']}"
        print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)


def main() -> None:
    """Parse CLI arguments and execute trigger evaluation on the skill."""
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
        _print_verbose_results(output)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
