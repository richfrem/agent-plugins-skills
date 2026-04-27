---
concept: evaluatepy-lives-at-pluginsautoresearch-improvementscriptsevaluatepy
source: plugin-code
source_file: agent-agentic-os/scripts/evaluate.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.284980+00:00
cluster: evaluate
content_hash: 24263b877190667b
---

# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/scripts/evaluate.py -->
#!/usr/bin/env python
"""
evaluate.py -- Locked loop gate for the autoresearch loop
==========================================================

Purpose:
    Single responsibility: "Should the loop keep or discard this change?"

    Calls eval_runner.py once (--json), reads the last BASELINE row from
    <target-skill>/evals/results.tsv, compares score and f1, appends one row
    to that same TSV, then exits 0 (KEEP) or 1 (DISCARD).

    DO NOT MODIFY THIS FILE. It is the locked evaluator. Only the target
    SKILL.md is the mutation target.

Usage (run from the plugin root or any directory):
    python scripts/evaluate.py --skill <path/to/mutation-target>
    python scripts/evaluate.py --target <path/to/mutation-target> --desc "what changed"
    python scripts/evaluate.py --skill <path/to/mutation-target> --baseline

    --skill and --target are aliases. evaluate.py accepts any file as input,
    but eval_runner.py scoring is optimized for SKILL.md targets (YAML frontmatter
    + <example> tags). Non-SKILL.md targets score accuracy=0.0 and receive heuristic
    penalties for missing SKILL.md structure — see eval_runner.py Known Limitations.

Karpathy mapping:
    This file = prepare.py (gate logic half)
    eval_runner.py = prepare.py (metric producer half)
    <mutation-target> = train.py (SKILL.md, .py, config, or any file type)

KEEP condition: score >= baseline_score AND f1 >= baseline_f1
    Dual guard prevents keyword-stuffing exploit (padding triggers raises
    recall but drops precision, so F1 falls even as accuracy rises).
"""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py
HERE = Path(__file__).parent.resolve()
EVAL_RUNNER = HERE / "eval_runner.py"

HEADERS = ["timestamp", "commit", "score", "baseline", "accuracy", "heuristic", "f1", "status", "description"]

# Supported primary metrics and their KEEP logic.
# Each entry: (metric_key_in_data, guard_key_in_data_or_None)
# KEEP requires: primary >= baseline_primary AND (guard >= baseline_guard if guard exists)
METRIC_OPTIONS = {
    "quality_score": ("quality_score", "f1"),       # default: quality gate + F1 anti-stuffing guard
    "f1":            ("f1",            None),        # optimize F1 directly
    "precision":     ("precision",     "recall"),    # optimize precision, guard on recall floor
    "recall":        ("recall",        "precision"), # optimize recall, guard on precision floor
    "heuristic":     ("heuristic",     None),        # structural quality only
}

# Files the loop must never modify — checked at startup
LOCKED_FILES = [HERE / "evaluate.py", HERE / "eval_runner.py"]

# Name of the SHA256 snapshot file saved alongside results.tsv at baseline time
LOCK_HASHES_FILENAME = ".lock.hashes"


def check_locked_files(skill_root: Path, evals_json: Path, results_tsv: Path) -> None:
    """Abort if any locked files have uncommitted modifications.

    Relying on the agent to obey 'Locked:' in program.md is not enough.
    An agent in a deep loop will eventually rewrite evaluate.py to always
    return exit 0. This check turns convention into a runtime guarantee.

    NOTE: Skipped on fresh installs (no baseline yet). A baseline cannot
    exist before the locked files are committed, so checking git-status
    before the first --baseline run would always false-abort on npx installs.
    """
    # Skip integrity check if no baseline exists yet — the scripts are freshly
    # installed and haven't been committed. Once --baseline is run and the
    # snapshot is saved, this check activates on all subsequent iterations.
    lock_hashes_path = results_tsv.parent / LOCK_HASHES_FILENAME
    if not lock_hashes_path.exists():
        return  # Pre-baseline: no snapshot to guard against yet

    to_check = LOCKED_FILES + [evals_json]
    try:
        repo_root_result = subprocess.run(
            ["git"

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-eval-runner/scripts/evaluate.py -->
#!/usr/bin/env python3
"""
evaluate.py -- Locked loop gate for the autoresearch loop
==========================================================

Purpose:
    Single responsibility: "Should the loop keep or discard this change?"

    Calls eval_runner.py once (--json), reads the last BASELINE row from
    <target-skill>/evals/results.tsv, compares score and f1, appends one row
    to that same TSV, then exits 0 (KEEP) or 1 (DISCARD).

    DO NOT MODIFY THIS FILE. It is the locked evaluator. Only the target
    SKILL.md is the mutation target.

Usage (run from the plugin root or any directory):
    python scripts/evaluate.py --skill <path/to/mutation-target>
    python scripts/evaluate.py --target <path/to/mutation-target> --desc "what changed"
    python scripts/evaluate.py --skill <path/to/mutation-ta

*(combined content truncated)*

## See Also

- [[script-lives-at-pluginspluginskillsskillscripts]]
- [[security-flaw-hardcoded-api-key-constructed-at-runtime]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/evaluate.py`
- **Indexed:** 2026-04-27T05:21:04.284980+00:00
