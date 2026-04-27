---
concept: support-both-layouts-eval-dirs-directly-under-benchmark-dir-or-under-runs
source: plugin-code
source_file: agent-scaffolders/scripts/aggregate_benchmark.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.207572+00:00
cluster: json
content_hash: ac7faf57dfba2c46
---

# Support both layouts: eval dirs directly under benchmark_dir, or under runs/

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/aggregate_benchmark.py -->
#!/usr/bin/env python
"""
Aggregate individual run results into benchmark summary statistics.

Reads grading.json files from run directories and produces:
- run_summary with mean, stddev, min, max for each metric
- delta between with_skill and without_skill configurations

Credits: Inspired by and adapted from Anthropic's skill-creator.

Usage:
    python aggregate_benchmark.py <benchmark_dir>

Example:
    python aggregate_benchmark.py benchmarks/2026-01-15T10-30-00/

The script supports two directory layouts:

    Workspace layout (from skill-creator iterations):
    <benchmark_dir>/
    └── eval-N/
        ├── with_skill/
        │   ├── run-1/grading.json
        │   └── run-2/grading.json
        └── without_skill/
            ├── run-1/grading.json
            └── run-2/grading.json

    Legacy layout (with runs/ subdirectory):
    <benchmark_dir>/
    └── runs/
        └── eval-N/
            ├── with_skill/
            │   └── run-1/grading.json
            └── without_skill/
                └── run-1/grading.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def calculate_stats(values: list[float]) -> dict:
    """Calculate mean, stddev, min, max for a list of values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4)
    }


def load_run_results(benchmark_dir: Path) -> dict:
    """
    Load all run results from a benchmark directory.

    Returns dict keyed by config name (e.g. "with_skill"/"without_skill",
    or "new_skill"/"old_skill"), each containing a list of run results.
    """
    # Support both layouts: eval dirs directly under benchmark_dir, or under runs/
    runs_dir = benchmark_dir / "runs"
    if runs_dir.exists():
        search_dir = runs_dir
    elif list(benchmark_dir.glob("eval-*")):
        search_dir = benchmark_dir
    else:
        print(f"No eval directories found in {benchmark_dir} or {benchmark_dir / 'runs'}")
        return {}

    results: dict[str, list] = {}

    for eval_idx, eval_dir in enumerate(sorted(search_dir.glob("eval-*"))):
        metadata_path = eval_dir / "eval_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path) as mf:
                    eval_id = json.load(mf).get("eval_id", eval_idx)
            except (json.JSONDecodeError, OSError):
                eval_id = eval_idx
        else:
            try:
                eval_id = int(eval_dir.name.split("-")[1])
            except ValueError:
                eval_id = eval_idx

        # Discover config directories dynamically rather than hardcoding names
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            # Skip non-config directories (inputs, outputs, etc.)
            if not list(config_dir.glob("run-*")):
                continue
            config = config_dir.name
            if config not in results:
                results[config] = []

            for run_dir in sorted(config_dir.glob("run-*")):
                run_number = int(run_dir.name.split("-")[1])
                grading_file = run_dir / "grading.json"

                if not grading_file.exists():
                    print(f"Warning: grading.json not found in {run_dir}")
                    continue

                try:
                    with open(grading_file) as f:
                        grading = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in {grading_file}: {e}")
                    conti

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/benchmarking/aggregate_benchmark.py -->
#!/usr/bin/env python
"""
aggregate_benchmark.py (CLI)
=====================================

Purpose:
    Aggregate individual run results into benchmark summary statistics.
    Reads grading.json files from run directories and produces:
    - run_summary with mean, stddev, min, max for each metric
    - delta between with_skill and without_skill configurations

Layer: Meta-Execution

Usage Examples:
    python aggregate_benchmark.py <benchmark_dir>

Supported Object Types:
    - Benchmark run folders (eval-N)
    - Legacy layouts with runs/ subdirectory

CLI Arguments:
    benchmark_dir: Path to the benchmark directory
    --skill-name: Name of the skill being benchmarked
    --skill-path: Path to the skill being benchmarked
    --output: Output path for benchmark.json

Input Files:
    - grad

*(combined content truncated)*

## See Also

- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[determine-spec-dir]]
- [[fallback-to-appending-directly-if-kernel-is-missing]]
- [[fix-patterns-like-or]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]
- [[load-and-validate-eval-results-data-from-tsv]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/aggregate_benchmark.py`
- **Indexed:** 2026-04-27T05:21:04.207572+00:00
