---
concept: trigger-block-builders
source: plugin-code
source_file: agent-scaffolders/scripts/scaffold_github_action.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.140749+00:00
cluster: name
content_hash: feaef4d584bd1511
---

# --- Trigger block builders ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/scaffold_github_action.py -->
#!/usr/bin/env python
"""
Scaffold GitHub Action
=====================================

Purpose:
    Scaffolds a traditional deterministic GitHub Actions CI/CD workflow YAML.
    Supports common categories: test, build, lint, deploy, release, security,
    maintenance, and custom. Does NOT involve AI at runtime.

    This is distinct from scaffold_agentic_workflow.py which creates AI-powered
    GitHub Agentic Workflows (Official format or Smart Failure pattern).

Layer: Codify

Usage:
    python scaffold_github_action.py --category <category> [OPTIONS]

    Options:
      --category {test,build,lint,deploy,release,security,maintenance,custom}
      --platform {python,nodejs,go,docker,dotnet,generic}
      --triggers TRIGGER [TRIGGER ...]  (pull_request, push, schedule, etc.)
      --name TEXT                        Human-readable workflow name
      --branch TEXT                      Branch for push triggers (default: main)

Related:
    - create-github-action/SKILL.md
    - scaffold_agentic_workflow.py  (for AI-powered workflows)
"""

import argparse
import textwrap
from pathlib import Path
from typing import Optional

# --- Trigger block builders ---

TRIGGER_MAP: dict[str, str] = {
    "pull_request": "  pull_request:",
    "push_main": "  push:\n    branches: [\"{branch}\"]",
    "schedule_weekly": "  schedule:\n    - cron: '0 9 * * 1'  # Mondays 9am UTC",
    "schedule_daily": "  schedule:\n    - cron: '0 8 * * *'  # Daily 8am UTC",
    "workflow_dispatch": "  workflow_dispatch:",
    "release": "  release:\n    types: [published]",
    "issues": "  issues:\n    types: [opened]",
}


def build_on_block(triggers: list[str], branch: str) -> str:
    """Build the `on:` trigger block from the list of trigger keys."""
    lines = []
    for t in triggers:
        raw = TRIGGER_MAP.get(t, f"  {t}:")
        lines.append(raw.replace("{branch}", branch))
    return "\n".join(lines) if lines else "  workflow_dispatch:"


# --- Platform setup steps ---

PLATFORM_SETUP: dict[str, str] = {
    "python": textwrap.dedent("""\
          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: "3.12"

          - name: Cache pip dependencies
            uses: actions/cache@v4
            with:
              path: ~/.cache/pip
              key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
              restore-keys: ${{ runner.os }}-pip-

          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt"""),
    "nodejs": textwrap.dedent("""\
          - name: Set up Node.js
            uses: actions/setup-node@v4
            with:
              node-version: "20"
              cache: "npm"

          - name: Install dependencies
            run: npm ci"""),
    "go": textwrap.dedent("""\
          - name: Set up Go
            uses: actions/setup-go@v5
            with:
              go-version: "1.22"
              cache: true"""),
    "docker": textwrap.dedent("""\
          - name: Set up Docker Buildx
            uses: docker/setup-buildx-action@v3

          - name: Log in to GitHub Container Registry
            uses: docker/login-action@v3
            with:
              registry: ghcr.io
              username: ${{ github.actor }}
              password: ${{ secrets.GITHUB_TOKEN }}"""),
    "dotnet": textwrap.dedent("""\
          - name: Set up .NET
            uses: actions/setup-dotnet@v4
            with:
              dotnet-version: "8.0.x"

          - name: Restore dependencies
            run: dotnet restore"""),
    "generic": "",
}


# --- Category-specific job steps ---

def category_steps(category: str, platform: str, branch: str) -> str:
    """Return the core job steps for the given category + platform."""

    if category == "test":
        if platform == "python":
            return textwrap.dedent("""\
              - name: Run tests
                run

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-github-action/scripts/scaffold_github_action.py -->
#!/usr/bin/env python3
"""
Scaffold GitHub Action
=====================================

Purpose:
    Scaffolds a traditional deterministic GitHub Actions CI/CD workflow YAML.
    Supports common categories: test, build, lint, deploy, release, security,
    maintenance, and custom. Does NOT involve AI at runtime.

    This is distinct from scaffold_agentic_workflow.py which creates AI-powered
    GitHub Agentic Workflows (Official format or Smart Failure pattern).

Layer: Codify

Usage:
    python scaffold_github_action.py --category <category> [OPTIONS]

    Options:
      --category {test,build,lint,deploy,release,security,maintenance,custom}
      --platform {python,nodejs,go,docker,dotnet,generic}
      --triggers TRIGGER [TRIGGER ...]  (pull_request, push, sched

*(combined content truncated)*

## See Also

- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]
- [[separate-by-should-trigger]]
- [[supported-trigger-configs]]
- [[use-yaml-block-scalar-to-avoid-breaking-on-quotes-in-description]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/scaffold_github_action.py`
- **Indexed:** 2026-04-27T05:21:04.140749+00:00
