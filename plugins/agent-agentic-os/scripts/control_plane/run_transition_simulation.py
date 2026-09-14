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

Index:
    - run_case() -- runs one case through the claude CLI and grades it
    - main() -- CLI entry point
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from control_plane.registry import TransitionRegistry
from control_plane.transition_simulation_cases import (
    SimulationCase,
    build_dry_run_prompt,
    build_simulation_cases,
    grade_reply,
)


def run_case(case: SimulationCase, purpose: str, next_steps_hint: str) -> dict:
    prompt = build_dry_run_prompt(case, purpose, next_steps_hint)
    start = time.monotonic()
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", "haiku"],
        capture_output=True, text=True, timeout=60,
    )
    elapsed = time.monotonic() - start
    result = grade_reply(case, proc.stdout)
    result["elapsed_seconds"] = round(elapsed, 1)
    return result


def print_result(result: dict) -> None:
    status = "PASS" if result["overall_pass"] else "FAIL"
    print(f"\n[{status}] {result['case_id']} ({result['elapsed_seconds']}s)")
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
    args = parser.parse_args()

    registry = TransitionRegistry.load_default()
    all_cases = build_simulation_cases(registry)

    if args.all:
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
        result = run_case(case, template.purpose, template.next_steps_hint)
        results.append(result)
        print_result(result)

    passed = sum(1 for r in results if r["overall_pass"])
    print(f"\n{passed}/{len(results)} cases passed.")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
