#!/usr/bin/env python3
"""
turn_evolution_guard.py — Mechanical Mid-Session Stop Hook Guard
================================================================
Purpose:
    Inspects the current session git status.
    If the agent performed modifications to logic/source files in this turn
    without writing to map-debt.md, evolution-log.md, wiki/, or emitting
    an Evolution-Check: none trailer, it outputs a prominent warning and
    nudge to prevent unrecorded map debt before the turn concludes.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    target_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project_root = Path(target_dir).resolve()

    # 1. Check if git repo
    try:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=project_root, capture_output=True, text=True, check=True)
        changed_files = [line[3:].strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return

    # 2. Check if source logic changed
    src_prefixes = (
        "plugins/",
        "investment_screener/backend/py_services/",
        "src/",
        "investment_screener/backend/src/",
        "py_services/",
    )
    modified_src = [f for f in changed_files if any(f.startswith(p) for p in src_prefixes)]

    if not modified_src:
        return

    # 3. Check if evolution/map-debt/wiki files were touched
    has_map_debt = any(
        f == "references/map-debt.md"
        or f.startswith("wiki/")
        or "references/evolution-log.md" in f
        for f in changed_files
    )

    if not has_map_debt:
        warning_banner = (
            "\n"
            + ("!" * 72) + "\n"
            + "⚠️  MECHANICAL TURN GUARD: Code was modified without Map Debt / Wiki logging!\n"
            + "Modified code files:\n"
        )
        for f in modified_src[:5]:
            warning_banner += f"   • {f}\n"
        warning_banner += (
            "\nMANDATORY ACTION BEFORE YIELDING TURN:\n"
            + "   1. Update 'references/map-debt.md' or 'wiki/playbook-*.md' with friction/fixes, OR\n"
            + "   2. Proactively emit the PRE-COMPLETION GATE receipt with Evolution-Check: none.\n"
            + ("!" * 72) + "\n"
        )
        print(warning_banner, file=sys.stderr)


if __name__ == "__main__":
    main()
