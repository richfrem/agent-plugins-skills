#!/usr/bin/env python3
"""
Purpose: Idempotent cold-start scaffold for the self-improvement flywheel.

Creates improvement-ledger.md, tests/registry.md, and loop-reports/ directory
if they do not already exist. Safe to re-run (never overwrites existing content).

Addresses the cold-start stall identified in round-10 red team reviews:
ORCHESTRATOR stalls at Step 1 (Orientation) because ledger/registry do not
exist until initialized. This script is called by os-init Phase 3.

Usage:
    python3 init_flywheel_files.py [--project-dir /path/to/project]
"""

import argparse
import os
from pathlib import Path


# Markdown header content for each file

LEDGER_TEMPLATE = """\
# Improvement Ledger

Longitudinal record of self-improvement cycles. Append-only -- never edit or delete rows.

---

## Section 1 -- Eval Score Progression

One row per cycle (BASELINE, KEEP, or DISCARD). Written at Stage 4.7 of every loop cycle.

| Date | Cycle ID | Target | Baseline Score | After Score | Delta | Verdict | Sub-cycles | Change Summary |
|------|----------|--------|----------------|-------------|-------|---------|------------|----------------|

---

## Section 2 -- Survey-to-Action Trace

One row per friction item that generated a change. Written with grep verification
(see improvement-ledger-spec.md Section 2 protocol).

| Date | Survey File | Agent | Friction Quote (verbatim, <15 words) | Action Taken | Target File | What Changed | Eval Delta | Outcome |
|------|-------------|-------|--------------------------------------|--------------|-------------|--------------|------------|---------|

---

## Section 3 -- North Star Metric

Autonomous Workflow Completion Rate per session. Written once at session close.
Two consecutive rows with a declining trend trigger os-learning-loop Full Loop.

| Date | Session ID | Total Cycles | Cycles Without Human Rescue | Completion % | Human Interventions | Friction Events | Trend vs Prior |
|------|------------|--------------|----------------------------|--------------|---------------------|-----------------|----------------|

---

## Anti-Patterns (never do these)

- Never rewrite or delete a row -- append only.
- Never leave Section 2 blank after a cycle that used any survey finding.
- Never copy scores from memory -- always read from results.tsv for Section 1.
"""

REGISTRY_TEMPLATE = """\
# Test Registry

Tracks all test scenarios run against the self-improvement loop. One row per cycle.
See references/test-registry-protocol.md for the full before/after documentation protocol.

| Cycle ID | Date | Target | Hypothesis | Status | Verdict | Notes |
|----------|------|--------|------------|--------|---------|-------|

---

**Status values**: IN PROGRESS | CLOSED-KEEP | CLOSED-DISCARD | DO-NOT-RETEST

**DO NOT RE-TEST entries** (confirmed as already working or permanently falsified):
_(none yet)_
"""


def init_flywheel_files(project_dir: Path) -> None:
    """
    Create the three flywheel scaffold files if they do not already exist.
    Prints a status line for each file.
    """
    memory_dir = project_dir / "context" / "memory"
    tests_dir = memory_dir / "tests"
    loop_reports_dir = memory_dir / "loop-reports"

    # Ensure all directories exist
    for d in [memory_dir, tests_dir, loop_reports_dir]:
        d.mkdir(parents=True, exist_ok=True)

    ledger_path = memory_dir / "improvement-ledger.md"
    registry_path = tests_dir / "registry.md"

    files_to_create = [
        (ledger_path, LEDGER_TEMPLATE),
        (registry_path, REGISTRY_TEMPLATE),
    ]

    any_created = False
    for path, content in files_to_create:
        if path.exists():
            print(f"[flywheel-init] EXISTS (skipped): {path.relative_to(project_dir)}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"[flywheel-init] CREATED: {path.relative_to(project_dir)}")
            any_created = True

    # loop-reports/ dir (just needs to exist)
    if loop_reports_dir.exists():
        print(f"[flywheel-init] EXISTS (skipped): {loop_reports_dir.relative_to(project_dir)}/")
    else:
        loop_reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"[flywheel-init] CREATED: {loop_reports_dir.relative_to(project_dir)}/")
        any_created = True

    if any_created:
        print("[flywheel-init] Done. ORCHESTRATOR can now start at Step 1 without stalling.")
    else:
        print("[flywheel-init] All flywheel files already exist. Nothing to do.")


def main() -> None:
    """Entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Idempotent cold-start scaffold for the Agentic OS self-improvement flywheel."
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Project root directory. Defaults to CLAUDE_PROJECT_DIR env var or cwd."
    )
    args = parser.parse_args()

    raw_dir = args.project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project_dir = Path(raw_dir).resolve()

    print(f"[flywheel-init] Project dir: {project_dir}")
    init_flywheel_files(project_dir)


if __name__ == "__main__":
    main()
