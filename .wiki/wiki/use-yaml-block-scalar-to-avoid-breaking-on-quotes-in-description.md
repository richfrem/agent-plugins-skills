---
concept: use-yaml-block-scalar-to-avoid-breaking-on-quotes-in-description
source: plugin-code
source_file: agent-scaffolders/scripts/benchmarking/run_eval.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.211345+00:00
cluster: skill
content_hash: d5122492ea5d432f
---

# Use YAML block scalar to avoid breaking on quotes in description

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/benchmarking/run_eval.py -->
#!/usr/bin/env python
"""
run_eval.py (CLI)
=====================================

Purpose:
    Run trigger evaluation for a skill description to check if Claude invokes it correctly.
    Tests whether a skill's description causes Claude to trigger (read the skill)
    for a set of queries. Outputs results as JSON.

Layer: Meta-Execution

Usage Examples:
    python run_eval.py --eval-set set.json --skill-path my_skill/

Supported Object Types:
    - Skill directories with SKILL.md
    - list[dict] evaluation query datasets

CLI Arguments:
    --eval-set: Path to eval set JSON file
    --skill-path: Path to skill directory
    --description: Override description to test instead of SKILL.md one
    --num-workers: Number of parallel subprocess workers
    --timeout: Timeout per evaluation query in seconds
    --runs-per-query: Number of runs per query (for stability)
    --trigger-threshold: Rate threshold to consider a pass
    --model: Model backend override
    --engine: "claude" only
    --verbose: Print progress to stderr

Input Files:
    - eval_set.json
    - SKILL.md

Output:
    - JSON dictionary with "results" and "summary" statistics

Key Functions:
    - run_single_query(): Inlines command with unique GUID and tracks stream deltas.
    - run_eval(): Executes multiprocess concurrency map.

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
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Mimics how Claude Code discovers its project root, so the command file
    we create ends up where claude -p will look for it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
    engine: str = "claude",
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.
    """
    if engine != "claude":
        raise ValueError(
            "run_eval currently supports only engine='claude' because trigger "
            "detection relies on Claude stream events and skill routing."
        )

    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env va

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/run_eval.py -->
#!/usr/bin/env python
"""
run_eval.py (CLI)
=====================================

Purpose:
    Tests whether a skill's description causes Claude to trigger (read the skill)
    for a set of queries. Outputs results as JSON. Inspired by skill-creator.

Layer: Investigate / Curate / Retrieve

Usage Examples:
    pythonrun_eval.py --eval-set eval_set.json --skill-path plugins/agent-scaffolders/skills/audit-plugin
    pythonrun_eval.py --eval-set eval_set.json --skill-path path/to/skill --verbose

Supported Object Types:
    Any structured prompt payload or skill config.

CLI Arguments:
    --eval-set: Path to eval set JSON file (Required)
    --skill-path: Path to skill directory (Required)
    --description: Override description to test
    --num-workers: Number of parallel workers (default: 10)
    --timeout: Timeout

*(combined content truncated)*

## See Also

- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[patterns-to-find-file-references-in-code]]
- [[thin-wrapper-delegates-to-the-canonical-implementation-in-scripts]]
- [[track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content]]
- [[use-npx-to-lazily-execute-mermaid-cli-so-the-user-doesnt-need-to-globally-install-it]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/benchmarking/run_eval.py`
- **Indexed:** 2026-04-27T05:21:04.211345+00:00
