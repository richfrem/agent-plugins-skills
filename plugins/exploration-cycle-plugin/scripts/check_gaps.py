#!/usr/bin/env python
"""
check_gaps.py
=====================================

Purpose:
    Counts [NEEDS HUMAN INPUT] markers in one or more capture files and exits non-zero if threshold exceeded.

Layer: Analysis / Verification

Usage Examples:
    pythoncheck_gaps.py --files exploration/captures/brd-draft.md --threshold 3

Supported Object Types:
    - Markdown files (.md)

CLI Arguments:
    --files: Capture files to check.
    --threshold: Max allowed gap markers (default: 3).

Input Files:
    - Target files to check for gaps.

Output:
    - Printed gap counts and status.

Key Functions:
    - count_gaps()

Script Dependencies:
    None

Consumed by:
    - Exploration cycle dispatch chain
"""

import argparse
import os
import sys

MARKER = "[NEEDS HUMAN INPUT]"


def count_gaps(filepaths: list[str]) -> tuple[int, dict[str, int]]:
    total = 0
    per_file = {}
    missing = []
    for fp in filepaths:
        if not os.path.exists(fp):
            print(f"Error: required file not found: {fp}", file=sys.stderr)
            missing.append(fp)
            continue
        text = open(fp, encoding="utf-8").read()
        count = text.count(MARKER)
        per_file[fp] = count
        total += count
    if missing:
        print(f"\nSTOP: {len(missing)} required file(s) missing — treat as unreviewed capture(s).", file=sys.stderr)
        sys.exit(1)
    return total, per_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Gap marker checker for exploration captures")
    parser.add_argument("--files", nargs="+", required=True, help="Capture files to check")
    parser.add_argument("--threshold", type=int, default=3, help="Max allowed gap markers (default: 3)")
    args = parser.parse_args()

    total, per_file = count_gaps(args.files)

    for fp, count in per_file.items():
        print(f"  {count:>3} gap(s)  {fp}")

    print(f"\nTotal: {total} '{MARKER}' marker(s) across {len(per_file)} file(s). Threshold: {args.threshold}.")

    if total > args.threshold:
        print(
            f"\nSTOP: {total} gaps exceed threshold of {args.threshold}. "
            "Refine the session brief and re-run from the affected pass before continuing.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("OK: gap count within threshold. Safe to continue.")


if __name__ == "__main__":
    main()
