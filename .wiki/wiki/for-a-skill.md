---
concept: for-a-skill
source: plugin-code
source_file: agent-agentic-os/scripts/init_autoresearch.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.279597+00:00
cluster: experiment
content_hash: 9a44f5004623cd0b
---

# For a skill:

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/scripts/init_autoresearch.py -->
#!/usr/bin/env python
"""
init_autoresearch.py -- Scaffold the Karpathy autoresearch loop for any target
================================================================================

Purpose:
    Idempotent scaffold for the autoresearch structure inside an experiment directory.
    The mutation target is NOT assumed to be a SKILL.md — it can be any file:
    a skill definition, a Python script, a config file, a math model, etc.

    Reads all three templates from the os-eval-runner assets directory and
    renders/copies them into the experiment directory:

        <experiment-dir>/references/program.md   (from program.md.template, vars rendered)
        <experiment-dir>/evals/evals.json        (from evals.json.template, vars rendered)
        <experiment-dir>/evals/results.tsv       (from results.tsv.template — header only)

    Safe to re-run: never overwrites existing files.
    .lock.hashes is NOT created here — evaluate.py writes it at --baseline time.

Templates live at:
    skills/os-eval-runner/assets/templates/autoresearch/
        program.md.template      (uses {{EXPERIMENT_NAME}}, {{EXPERIMENT_PATH}},
                                   {{MUTATION_TARGET}}, {{PLUGIN_ROOT}})
        evals.json.template      (uses {{EXPERIMENT_NAME}})
        results.tsv.template     (schema header — no vars)

Usage:
    python scripts/init_autoresearch.py \\
        --experiment-dir <path/to/experiment-or-skill> \\
        [--mutation-target SKILL.md] \\
        [--plugin-root .agents/plugins/autoresearch-improvement]

    # For a skill:
    python scripts/init_autoresearch.py \\
        --experiment-dir .agents/skills/my-skill

    # For a Python script:
    python scripts/init_autoresearch.py \\
        --experiment-dir experiments/my-tuning-run \\
        --mutation-target optimizer.py

Workflow after scaffolding:
    1. Edit references/program.md  -- fill in Notes section
    2. Edit evals/evals.json       -- replace REPLACE placeholders with real inputs/outputs
    3. evaluate.py --baseline      -- establish baseline, write .lock.hashes
    4. Agent loop                  -- reads program.md, mutates target, runs evaluate.py
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
PLUGIN_ROOT = HERE.parent

# Templates live at assets/templates/autoresearch/ relative to the script's
# parent directory (the skill root). Using HERE.parent makes this agnostic
# to whether the skill is installed standalone (.agents/skills/os-eval-runner/)
# or inside the full plugin tree (plugins/agent-agentic-os/skills/os-eval-runner/).
TEMPLATES_DIR = PLUGIN_ROOT / "assets" / "templates" / "autoresearch"


def _load_template(name: str) -> str:
    """Read a template file, abort with a clear message if missing."""
    path = TEMPLATES_DIR / name
    if not path.exists():
        print(f"ERROR: template not found: {path}", file=sys.stderr)
        print(f"       Expected templates dir: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(2)
    return path.read_text(encoding="utf-8")


def _render(template: str, vars: dict[str, str]) -> str:
    """Replace all {{KEY}} placeholders in the template."""
    result = template
    for key, value in vars.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def scaffold(experiment_dir: Path, mutation_target: str, plugin_root: Path) -> None:
    """Deploy all three autoresearch templates into the experiment directory."""
    experiment_name = experiment_dir.name

    try:
        experiment_path_display = str(experiment_dir.relative_to(Path.cwd()))
    except ValueError:
        experiment_path_display = str(experiment_dir)

    try:
        plugin_root_display = str(plugin_root.relative_to(Path.cwd()))
    except ValueError:
        plugin_root_display = str(plugin_root)

    references_dir = experiment_dir / "references"
    evals_dir = experiment_dir / "evals"
    program_md = references_dir / "program.md"
    copilot_prompt_md = re

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-eval-runner/scripts/init_autoresearch.py -->
#!/usr/bin/env python3
"""
init_autoresearch.py -- Scaffold the Karpathy autoresearch loop for any target
================================================================================

Purpose:
    Idempotent scaffold for the autoresearch structure inside an experiment directory.
    The mutation target is NOT assumed to be a SKILL.md — it can be any file:
    a skill definition, a Python script, a config file, a math model, etc.

    Reads all three templates from the os-eval-runner assets directory and
    renders/copies them into the experiment directory:

        <experiment-dir>/references/program.md   (from program.md.template, vars rendered)
        <experiment-dir>/evals/evals.json        (from evals.json.template, vars rendered)
        <experiment-dir>/evals/results.tsv 

*(combined content truncated)*

## See Also

- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[as-a-library]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/init_autoresearch.py`
- **Indexed:** 2026-04-27T05:21:04.279597+00:00
