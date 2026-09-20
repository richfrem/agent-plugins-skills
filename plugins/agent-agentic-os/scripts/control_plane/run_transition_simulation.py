#!/usr/bin/env python3
"""
run_transition_simulation.py
=============================

Purpose:
    Manual, opt-in cheap-agent dry-run for one specific transition edge (or all
    edges). Run this whenever you change a transition's YAML guidance/questions
    or the coordinator's Python logic, targeted at just the edge you changed --
    not as part of the normal pytest suite (LLM calls cost real time/money; see
    plugins/agent-agentic-os/references/cheap-agent-transition-simulation.md).

    Grades each case against the 4 fixed criteria (transition_simulation_cases.
    grade_reply) plus the guidance-compliance answer match, using the `claude`
    CLI directly (no API key/SDK needed -- confirmed working).

Key Input Dependencies:
    - control_plane.registry.TransitionRegistry (transition_templates.yaml)
    - the `claude` CLI binary on PATH, with --model haiku support
    - transition_simulation_cases.py (case generation + grading)

Usage:
    python3 run_transition_simulation.py --from INTAKE --to INTERVIEW
    python3 run_transition_simulation.py --from INTAKE --to INTERVIEW --condition HUMAN_REJECTS
    python3 run_transition_simulation.py --all   # full 151-case suite, ~25 min
    python3 run_transition_simulation.py --behavior --from INTAKE --to INTERVIEW --print-prompt   # no model call
    python3 run_transition_simulation.py --behavior --all --iteration 1 --log iterations.jsonl --note baseline

Index:
    - run_case() -- runs one case through the claude CLI and grades it
    - format_actor_classification_line() -- pure formatter for a case's edge
      authorized_actor + (for adversarial cases) the expected denial reason
    - run_behavior_case() -- one BEHAVIOR run (WHO runs it, command, message to the human)
    - run_behavior() -- BEHAVIOR mode driver: one edge, or --all edges, logged per iteration
    - main() -- CLI entry point
"""

import argparse
import concurrent.futures
import subprocess
import sys
import time
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from control_plane.edge_matrix import build_edge_matrix
from control_plane.registry import TransitionRegistry, TransitionTemplate
from control_plane.transition_simulation_cases import (
    SimulationCase,
    append_iteration_log,
    build_agent_spoof_adversarial_cases,
    build_behavior_prompt,
    grade_behavior_reply,
    build_dry_run_prompt,
    build_simulation_cases,
    grade_reply,
)


import shutil
from typing import Optional

SUPPORTED_BACKENDS = ("auto", "agy", "claude", "codex", "copilot")


def resolve_backend(backend_choice: str = "auto") -> str:
    """Resolve which CLI binary to dispatch simulation runs to."""
    if backend_choice in ("agy", "claude", "codex", "copilot"):
        return backend_choice
    for b in ("agy", "claude", "codex", "copilot"):
        if shutil.which(b):
            return b
    return "agy"


def build_cli_cmd(
    backend: str,
    prompt: str,
    model: Optional[str] = None,
    effort: Optional[str] = None,
    disallow_tools: bool = True,
) -> list:
    """Construct non-interactive execution command for the target harness CLI."""
    if backend == "agy":
        cmd = ["agy", "-p", prompt]
        if model:
            cmd.extend(["--model", model])
        if effort:
            cmd.extend(["--effort", effort])
        return cmd
    elif backend == "claude":
        cmd = ["claude", "-p", prompt]
        if disallow_tools:
            cmd.extend(["--disallowedTools", "Bash,Edit,Write,Read,Grep,Glob"])
        if model:
            cmd.extend(["--model", model])
        if effort:
            cmd.extend(["--effort", effort])
        return cmd
    elif backend == "copilot":
        cmd = ["copilot", "-p", prompt, "-s"]
        if model:
            cmd.extend(["--model", model])
        return cmd
    elif backend == "codex":
        cmd = ["codex", "exec", prompt]
        if model:
            cmd.extend(["-m", model])
        return cmd
    else:
        cmd = [backend, "-p", prompt]
        if model:
            cmd.extend(["--model", model])
        return cmd


def format_actor_classification_line(case: SimulationCase, template: TransitionTemplate) -> str:
    """Pure formatter: shows the edge's authorized_actor classification, and for
    an adversarial (AGENT_SPOOF_DENIED) case, the expected denial reason."""
    line = f"  authorized_actor: {template.authorized_actor}"
    if case.condition == "AGENT_SPOOF_DENIED":
        line += " -- expected: DENIED (human_only edge, non-interactive agent actor)"
    return line


def run_case(case: SimulationCase, purpose: str, next_steps_hint: str, backend: str = "auto", model: Optional[str] = None) -> dict:
    prompt = build_dry_run_prompt(case, purpose, next_steps_hint)
    start = time.monotonic()
    active_backend = resolve_backend(backend)
    cmd = build_cli_cmd(active_backend, prompt, model=model or ("haiku" if active_backend == "claude" else None))
    proc = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=60,
    )
    elapsed = time.monotonic() - start
    result = grade_reply(case, proc.stdout)
    result["elapsed_seconds"] = round(elapsed, 1)
    result["backend"] = active_backend
    return result


def run_behavior_case(row: dict, registry: TransitionRegistry, model: Optional[str] = None, effort: Optional[str] = None, backend: str = "auto") -> dict:
    """Run one BEHAVIOR case through the CLI (no tools) and grade it deterministically."""
    prompt = build_behavior_prompt(row, registry)
    start = time.monotonic()
    active_backend = resolve_backend(backend)
    cmd = build_cli_cmd(active_backend, prompt, model=model, effort=effort, disallow_tools=True)
    proc = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=240,
    )
    result = grade_behavior_reply(row, proc.stdout)
    result["elapsed_seconds"] = round(time.monotonic() - start, 1)
    result["backend"] = active_backend
    return result


def run_behavior(args, registry: TransitionRegistry) -> int:
    """BEHAVIOR mode: judge whether the guidance tells an agent who runs each edge and what to say to the human."""
    rows = build_edge_matrix(registry)
    if not args.all:
        if not args.from_state or not args.to_state:
            print("--behavior needs --from and --to, or --all")
            return 2
        rows = [r for r in rows if r["from_state"] == args.from_state and r["to_state"] == args.to_state]
        if not rows:
            print(f"No edge {args.from_state} -> {args.to_state} found in the registry.")
            return 1
    if args.print_prompt:
        for row in rows:
            print(build_behavior_prompt(row, registry))
        return 0
    log_path = Path(args.log) if args.log else None
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_behavior_case, row, registry, args.model, args.effort, args.backend): row for row in rows}
        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                result = future.result()
            except Exception as error:  # a model/timeout failure is a FAIL for that edge, not a crash
                result = {"transition_id": row["transition_id"], "criteria": {}, "overall_pass": False,
                          "raw_reply": f"RUNNER ERROR: {error}", "elapsed_seconds": 0}
            failures += 0 if result["overall_pass"] else 1
            print(f"[{'PASS' if result['overall_pass'] else 'FAIL'}] {row['from_state']}->{row['to_state']} "
                  f"({row['run_by']}) {result['elapsed_seconds']}s "
                  + " ".join(k for k, v in result["criteria"].items() if not v))
            if log_path:
                append_iteration_log(log_path, iteration=args.iteration, row=row, result=result, change_note=args.note)
    print(f"\n{len(rows) - failures}/{len(rows)} edges passed (iteration {args.iteration}).")
    return 0 if failures == 0 else 1


def print_result(result: dict, actor_line: str = "") -> None:
    status = "PASS" if result["overall_pass"] else "FAIL"
    print(f"\n[{status}] {result['case_id']} ({result['elapsed_seconds']}s)")
    if actor_line:
        print(actor_line)
    for criterion, passed in result["criteria"].items():
        mark = "OK" if passed else "MISSING"
        print(f"  {criterion}: {mark}")
    guidance_mark = "OK" if result["guidance_answer_matches_expected"] else "MISMATCH"
    print(f"  guidance_compliance_answer: {guidance_mark}")
    if not result["overall_pass"]:
        print("  --- raw reply (for debugging YAML/coordinator.py) ---")
        print("  " + result["raw_reply"].replace("\n", "\n  "))


def main():
    parser = argparse.ArgumentParser(description="Cheap-agent dry-run simulation for control-plane transitions")
    parser.add_argument("--from", dest="from_state", help="Source state (omit with --all)")
    parser.add_argument("--to", dest="to_state", help="Target state (omit with --all)")
    parser.add_argument("--condition", choices=["HUMAN_APPROVES", "HUMAN_REJECTS"], default=None,
                        help="Restrict to one condition (default: both, where applicable)")
    parser.add_argument("--all", action="store_true", help="Run the full case suite (~25 min)")
    parser.add_argument("--adversarial", action="store_true",
                        help="Run only the agent-spoof adversarial matrix (one denial case per human_only edge)")
    parser.add_argument("--behavior", action="store_true",
                        help="BEHAVIOR mode: does the guidance tell the agent WHO runs the edge and what to tell the human?")
    parser.add_argument("--print-prompt", action="store_true", help="With --behavior: print the prompt, call no model")
    parser.add_argument("--iteration", type=int, default=1, help="With --behavior: iteration number recorded in the log")
    parser.add_argument("--log", default=None, help="With --behavior: JSONL file to append one row per edge")
    parser.add_argument("--note", default="", help="With --behavior: what changed before this iteration")
    parser.add_argument("--model", default=None, help="With --behavior: model for the simulated agent (default: backend default)")
    parser.add_argument("--effort", default="medium", help="With --behavior: reasoning effort for the simulated agent")
    parser.add_argument("--workers", type=int, default=4, help="With --behavior: parallel model calls")
    parser.add_argument("--backend", choices=SUPPORTED_BACKENDS, default="auto",
                        help="CLI backend to execute simulations (default: auto)")
    args = parser.parse_args()

    registry = TransitionRegistry.load_default()
    if args.behavior:
        sys.exit(run_behavior(args, registry))
    all_cases = build_agent_spoof_adversarial_cases(registry) if args.adversarial else build_simulation_cases(registry)

    if args.adversarial:
        target_cases = all_cases
        if args.from_state and args.to_state:
            target_cases = [c for c in target_cases if c.from_state == args.from_state and c.to_state == args.to_state]
    elif args.all:
        target_cases = all_cases
    else:
        if not args.from_state or not args.to_state:
            parser.error("--from and --to are required unless --all is given")
        target_cases = [
            c for c in all_cases
            if c.from_state == args.from_state and c.to_state == args.to_state
            and (args.condition is None or c.condition == args.condition)
        ]
        if not target_cases:
            print(f"No edge {args.from_state} -> {args.to_state} found in the registry.")
            sys.exit(1)

    results = []
    for case in target_cases:
        template = registry.get_template(case.from_state, case.to_state)
        result = run_case(case, template.purpose, template.next_steps_hint, backend=args.backend)
        results.append(result)
        print_result(result, format_actor_classification_line(case, template))

    passed = sum(1 for r in results if r["overall_pass"])
    print(f"\n{passed}/{len(results)} cases passed.")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
