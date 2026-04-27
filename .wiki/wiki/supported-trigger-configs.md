---
concept: supported-trigger-configs
source: plugin-code
source_file: agent-scaffolders/scripts/scaffold_agentic_workflow.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.139850+00:00
cluster: agent
content_hash: f911c51aef8c3dca
---

# --- Supported trigger configs ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/scaffold_agentic_workflow.py -->
#!/usr/bin/env python
"""
Scaffold Agentic Workflow
=====================================

Purpose:
    Scaffolds a GitHub Agent from an existing Agent Skill. Supports two
    distinct output modes:

    - ide   : Generates a Copilot IDE/UI agent (.agent.md + .prompt.md)
              Invoked by humans via Copilot Chat slash commands in VS Code
              or GitHub.com. Supports chained `handoffs` between agents.

    - cicd  : Generates a CI/CD autonomous agent (.agent.md + .yml runner)
              Triggered automatically by GitHub Actions events.
              Produces a Kill Switch quality gate that can fail the build.

    - both  : Generates all three files (shared .agent.md for both modes).

Layer: Codify

Usage:
    python scaffold_agentic_workflow.py --skill-dir <path/to/skill> [OPTIONS]

    Options:
      --mode {ide,cicd,both}           Agent type to generate (default: cicd)
      --triggers TRIGGER [TRIGGER ...] [cicd/both] Which GitHub events trigger the
                                       workflow. Choices: pull_request, push,
                                       schedule, issues, release.
                                       workflow_dispatch is always included.
      --kill-switch TEXT               [cicd/both] Custom kill switch phrase

Related:
    - create-agentic-workflow/SKILL.md
    - reference/github-agentic-workflows.md
"""

import re
import shutil
import argparse
from pathlib import Path
import textwrap
from typing import Optional

# --- Supported trigger configs ---
TRIGGER_CONFIGS: dict[str, str] = {
    "pull_request": "  pull_request:",
    "push": "  push:\n    branches: [\"main\"]",
    "schedule": "  schedule:\n    - cron: '0 9 * * 1'  # Mondays at 9am UTC",
    "issues": "  issues:\n    types: [opened, labeled]",
    "release": "  release:\n    types: [published]",
}


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """
    Parses YAML frontmatter from a Markdown file string.

    Args:
        content: The raw string content of the Markdown file.

    Returns:
        A tuple of (frontmatter_dict, body_string).
    """
    metadata: dict[str, str] = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        fm_block: str = str(match.group(1))
        body: str = content[match.end():]
        for line in fm_block.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                metadata[key.strip()] = value.strip().strip('"').strip("'")
        return metadata, body
    return metadata, content


def extract_workflow_steps(body: str) -> str:
    """
    Extracts top-level headings from the skill body to use as workflow steps.

    Args:
        body: Markdown body from the source SKILL.md.

    Returns:
        A numbered list of steps derived from headings, or a generic fallback.
    """
    headings: list[str] = re.findall(r"^#{1,3} (.+)$", body, re.MULTILINE)
    if headings:
        top_five: list[str] = headings[:5]
        return "\n".join(f"{i + 1}. **{h}**" for i, h in enumerate(top_five))
    return textwrap.dedent("""\
        1. **Analyze Context:** Review the target pull request or repository state.
        2. **Execute Checks:** Apply the operational procedures defined for this agent.
        3. **Draft Report:** Summarize findings with clear pass/fail criteria.""")


def generate_agent_file(
    name: str, description: str, body: str, agents_dir: Path, full_content: bool = True
) -> Path:
    """
    Generates the shared .agent.md persona file used by both IDE and CI/CD modes.

    When full_content=True (default), the entire SKILL.md body is ported directly
    into the agent file — matching spec-kit's approach of rich agent personas.
    When False, a stub skeleton is generated instead.

    Args:
        name: Agent name (kebab-case).
        description: Agent description from skill frontmatter.
        body: Markdown body from the source SKILL.md.
        agents_

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-agentic-workflow/scripts/scaffold_agentic_workflow.py -->
#!/usr/bin/env python3
"""
Scaffold Agentic Workflow
=====================================

Purpose:
    Scaffolds a GitHub Agent from an existing Agent Skill. Supports two
    distinct output modes:

    - ide   : Generates a Copilot IDE/UI agent (.agent.md + .prompt.md)
              Invoked by humans via Copilot Chat slash commands in VS Code
              or GitHub.com. Supports chained `handoffs` between agents.

    - cicd  : Generates a CI/CD autonomous agent (.agent.md + .yml runner)
              Triggered automatically by GitHub Actions events.
              Produces a Kill Switch quality gate that can fail the build.

    - both  : Generates all three files (shared .agent.md for both modes).

Layer: Codify

Usage:
    python scaffold_agentic_workf

*(combined content truncated)*

## See Also

- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]
- [[separate-by-should-trigger]]
- [[trigger-block-builders]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/scaffold_agentic_workflow.py`
- **Indexed:** 2026-04-27T05:21:04.139850+00:00
