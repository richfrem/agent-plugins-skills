---
concept: build-scores-summary
source: plugin-code
source_file: agent-scaffolders/scripts/benchmarking/improve_description.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.210609+00:00
cluster: skill
content_hash: 9af54c629922c671
---

# Build scores summary

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/benchmarking/improve_description.py -->
"""
improve_description.py (CLI)
=====================================

Purpose:
    Improve a skill description based on eval results using iterative LLM feedback.
    Takes eval results (from run_eval.py) and generates an improved description
    by calling `claude -p` (or `copilot -p`) as a subprocess.

Layer: Meta-Execution

Usage Examples:
    python improve_description.py --eval-results results.json --skill-path my_skill/

Supported Object Types:
    - Agent Skill directories with SKILL.md
    - Evaluation results dictionary structure

CLI Arguments:
    --eval-results: Path to eval results JSON
    --skill-path: Path to skill directory
    --history: Path to previous attempts history JSON
    --model: Backend model override
    --engine: "claude" or "copilot"
    --verbose: Enable thinking prints to stderr

Input Files:
    - eval_results.json
    - history.json
    - SKILL.md

Output:
    - JSON dictionary with "description" and "history"

Key Functions:
    - _call_model(): Direct invocation of CLI model backend.
    - improve_description(): Generates optimization prompt and parses description.

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
import re
import subprocess
import sys
from pathlib import Path

from utils import parse_skill_md


def _call_model(
    prompt: str,
    model: str | None,
    engine: str = "claude",
    timeout: int = 300,
) -> str:
    """Run the selected CLI model backend and return plain text output."""
    if engine == "claude":
        cmd = ["claude", "-p", "--output-format", "text"]
        if model:
            cmd.extend(["--model", model])
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude -p exited {result.returncode}\nstderr: {result.stderr}"
            )
        return result.stdout

    if engine == "copilot":
        cmd = ["copilot", "-p", prompt, "--output-format", "text", "--allow-all-tools"]
        if model:
            cmd.extend(["--model", model])
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"copilot -p exited {result.returncode}\nstderr: {result.stderr}"
            )
        return result.stdout

    raise ValueError(f"Unsupported engine: {engine}")


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    model: str | None,
    engine: str = "claude",
    test_results: dict | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    """Call the configured model backend to improve the description."""
    failed_triggers = [
        r for r in eval_results["results"]
        if r["should_trigger"] and not r["pass"]
    ]
    false_triggers = [
        r for r in eval_results["results"]
        if not r["should_trigger"] and not r["pass"]
    ]

    # Build scores summary
    train_score = f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"
    if test_results:
        test_score = f"{test_results['summary']['passed']}/{test_results['summary']['total']}"
        scores_summary = f"Train: {train_score}, Test: {test_score}"
    else:
        scores_summary = f"Train: {train_score}"

    prompt = f"""You are optimizing a skill description for a CLI coding agent skill called "{skill_name}". A "skill" is sort of like a prompt, but with progressive disclosure -- th

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/improve_description.py -->
"""
improve_description.py
=====================================

Purpose:
    Improve a skill description iteratively derived from eval test fail vectors 
    utilizing background solver model engines.

Layer: Repair / Synthesis

Usage Examples:
    pythonimprove_description.py --eval-results results.json --skill-path path/to -v
    pythonimprove_description.py --eval-results results.json --skill-path path/to --engine copilot

Supported Object Types:
    Evaluative diagnostics streams.

CLI Arguments:
    --eval-results: Evaluated diagnostic summary stream JSON. (Required)
    --skill-path: Skill components root. (Required)
    --history: Preceded attempts cache.
    --model: Overrides target controller model.
    --engine: solver dispatch backend selector (claude / copilot)
    --verbose: Stan

*(combined content truncated)*

## See Also

- [[build-capability-index]]
- [[rlm-summary-cache-manifest]]
- [[update-scores-for-an-existing-entry]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/benchmarking/improve_description.py`
- **Indexed:** 2026-04-27T05:21:04.210609+00:00
