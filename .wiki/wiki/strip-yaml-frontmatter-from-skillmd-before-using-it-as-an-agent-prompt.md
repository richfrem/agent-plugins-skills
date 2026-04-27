---
concept: strip-yaml-frontmatter-from-skillmd-before-using-it-as-an-agent-prompt
source: plugin-code
source_file: exploration-cycle-plugin/scripts/exploration_optimizer_execute.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.233208+00:00
cluster: path
content_hash: bfff0a2c1725d70c
---

# Strip YAML frontmatter from SKILL.md before using it as an agent prompt.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/exploration-cycle-plugin/scripts/exploration_optimizer_execute.py -->
#!/usr/bin/env python
"""
exploration_optimizer_execute.py
=====================================

Purpose:
    Implements an autoresearch-style optimization loop: Propose -> Test -> Decide.
    Optimizes skills based on routing and artifact quality evaluations.

Layer: Execution / Optimization

Usage Examples:
    pythonexploration_optimizer_execute.py --target skill.md --eval-script eval.py --goal "improve clarity"

Supported Object Types:
    SKILL.md files

CLI Arguments:
    --target: Path to the skill file to optimize.
    --eval-script: Path to eval_runner.py.
    --goal: Optimization goal.
    --iterations: Number of iterations.
    --ledger: Path to results TSV.
    --dispatch-script: Enabling artifact quality eval.
    --scenario-brief: Canonical session brief for eval.
    --check-gaps-script: Counting gap markers in output.

Input Files:
    - Target skill.md file
    - scenario brief

Output:
    - Updated skill file.
    - Updated ledger results TSV.

Key Functions:
    run_eval(): Runs routing evaluation.
    run_artifact_eval(): Runs artifact quality evaluation.
    propose_change(): Proposes optimization changes.
    main(): Coordinates the optimization loop.

Script Dependencies:
    os, sys, argparse, subprocess, json, shutil, re, pathlib, datetime

Consumed by:
    - Exploration cycle orchestrator
"""
import argparse
import re
import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def run_eval(eval_script: Path, target: Path) -> float:
    """Runs the routing/structural evaluation script and returns the score."""
    try:
        cmd = [sys.executable, str(eval_script), "--target", str(target), "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data.get("quality_score") or data.get("score") or 0.0)
    except Exception as e:
        print(f"Error running eval: {e}", file=sys.stderr)
        return -1.0


def run_artifact_eval(
    dispatch_script: Path,
    target_skill: Path,
    scenario_brief: Path,
    check_gaps_script: Path,
    artifact_output: Path,
    timeout: int = 180,
) -> float:
    """Artifact quality eval: runs the skill against a canonical scenario and counts gaps.

    Score = 1.0 - (gap_count / 10), floored at 0.0.
    A skill that produces zero gaps scores 1.0; each gap costs 0.1.

    Args:
        dispatch_script: path to dispatch.py
        target_skill:    the SKILL.md being optimized (used as agent)
        scenario_brief:  path to a fixed canonical session brief for the eval run
        check_gaps_script: path to check_gaps.py
        artifact_output: temp path to write the dispatch output
        timeout:         subprocess timeout in seconds

    Returns float score, or -1.0 on failure.
    """
    try:
        # Strip YAML frontmatter from SKILL.md before using it as an agent prompt.
        # Frontmatter (---\n...\n---) is metadata, not instructions — injecting it
        # verbatim confuses the model into treating descriptions as directives.
        skill_content = Path(target_skill).read_text(encoding="utf-8")
        stripped = re.sub(r'^---[\r\n]+.*?[\r\n]+---[\r\n]+', '', skill_content, count=1, flags=re.DOTALL)
        stripped_path = Path(target_skill).with_suffix(".stripped.md")
        stripped_path.write_text(stripped, encoding="utf-8")

        # Run dispatch against the canonical scenario
        cmd = [
            sys.executable, str(dispatch_script),
            "--agent", str(stripped_path),
            "--context", str(scenario_brief),
            "--instruction", "Mode: problem-framing. Capture the problem statement, user groups, and goals.",
            "--output", str(artifact_output),
            "--timeout", str(timeout),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        stripped_path.unlink(missing_ok=True)

        if result.returnc

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/exploration-optimizer/scripts/execute.py -->
#!/usr/bin/env python3
"""
exploration_optimizer_execute.py
=====================================

Purpose:
    Implements an autoresearch-style optimization loop: Propose -> Test -> Decide.
    Optimizes skills based on routing and artifact quality evaluations.

Layer: Execution / Optimization

Usage Examples:
    python3 exploration_optimizer_execute.py --target skill.md --eval-script eval.py --goal "improve clarity"

Supported Object Types:
    SKILL.md files

CLI Arguments:
    --target: Path to the skill file to optimize.
    --eval-script: Path to eval_runner.py.
    --goal: Optimization goal.
    --iterations: Number of iterations.
    --ledger: Path to results TSV.
    --dispatch-script: Enabling artifact quality eval.
    --scenario-brief: Canonical session 

*(combined content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[removed-plugin-inventory-import-as-it-is-now-obsolete]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/scripts/exploration_optimizer_execute.py`
- **Indexed:** 2026-04-27T05:21:04.233208+00:00
