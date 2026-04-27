---
concept: separate-by-should-trigger
source: plugin-code
source_file: agent-scaffolders/scripts/benchmarking/run_loop.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.212460+00:00
cluster: path
content_hash: 5ff9197b78110a8d
---

# Separate by should_trigger

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/benchmarking/run_loop.py -->
#!/usr/bin/env python
"""
run_loop.py (CLI)
=====================================

Purpose:
    Run the eval + improve loop until all pass or max iterations reached.
    Combines run_eval.py and improve_description.py in an automated keep-discard loop,
    tracking history and returning the best description found.
    Supports train/test split to prevent overfitting.

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
    test_set = trigger[:n_trigge

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/run_loop.py -->
#!/usr/bin/env python
"""
run_loop.py (CLI)
=====================================

Purpose:
    Runs the evaluation and improvement loop for skill descriptions iteratively.
    Combines run_eval.py and improve_description.py in a single loop to track 
    scores and return the best found description candidate.

Layer: Investigate / Optimization / Execution

Usage Examples:
    pythonrun_loop.py --eval-set eval_set.json --skill-path plugins/agent-scaffolders/skills/audit-plugin
    pythonrun_loop.py --eval-set set.json --skill-path path/to/skill --max-iterations 10

Supported Object Types:
    Optimizer execution benchmarks.

CLI Arguments:
    --eval-set: Path to eval set JSON file (Required)
    --skill-path: Path to skill directory (Required)
    --description: Override starting description 
    --num-workers: Numb

*(combined content truncated)*

## See Also

- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[sample-payloads-keyed-by-claude-code-event-type-name]]
- [[supported-trigger-configs]]
- [[trigger-block-builders]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/benchmarking/run_loop.py`
- **Indexed:** 2026-04-27T05:21:04.212460+00:00
