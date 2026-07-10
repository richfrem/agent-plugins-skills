# -*- coding: utf-8 -*-
"""
gh_agent_templates.py
=====================================
Purpose:
    Pure template functions for generating GitHub AI Agent configurations.
    Contains no I/O, making it fully unit-testable.
"""

import re
import yaml


def agent_md_github(
    name: str,
    description: str,
    body: str,
    target: str = "both",
    tools: list = None,
    model: str = None,
    disable_model_invocation: bool = False,
    user_invocable: bool = True,
    mcp_servers: dict = None,
    metadata: dict = None,
) -> str:
    """
    Target A: Custom Copilot Agent (.agent.md) frontmatter and body template.
    """
    fm = {
        "description": description,
        "name": name,
        "target": target,
        "user-invocable": user_invocable,
        "disable-model-invocation": disable_model_invocation,
        "generator": "scaffold_github_agent.py v2.1.0",
    }
    
    # per GitHub .agent.md spec:
    # - Unset (omitted / None) -> defaults to all tools.
    # - Explicit empty list [] -> zero tools are permitted (none).
    # - Specific list -> only those tools are permitted.
    if tools is not None:
        fm["tools"] = tools
    else:
        fm["tools"] = ["github", "terminal"]
        
    if model:
        fm["model"] = model
    if mcp_servers:
        fm["mcp-servers"] = mcp_servers
    if metadata:
        fm["metadata"] = metadata

    fm_yaml = yaml.dump(fm, sort_keys=False).strip()
    return f"---\n{fm_yaml}\n---\n\n{body.strip()}\n"


def gh_aw_workflow_md(
    name: str,
    description: str,
    instructions: str,
    on_trigger: dict,
    permissions: dict = None,
    engine: str = "copilot",
    tools: dict = None,
    safe_outputs: dict = None,
) -> str:
    """
    Target B: GitHub Agentic Workflow (gh-aw) Markdown format.
    """
    fm = {
        "on": on_trigger,
        "engine": engine,
        "generator": "scaffold_github_agent.py v2.1.0",
    }
    if permissions:
        fm["permissions"] = permissions
    else:
        fm["permissions"] = {
            "contents": "read",
            "issues": "read",
            "pull-requests": "read",
        }
        
    # tools structure:
    # - Unset (omitted / None) -> defaults to {"github": {"toolsets": ["issues", "pull-requests"]}}
    # - Empty list [] or dict {} -> no tools.
    if tools is not None:
        fm["tools"] = tools
    else:
        fm["tools"] = {"github": {"toolsets": ["issues", "pull-requests"]}}
        
    if safe_outputs:
        fm["safe-outputs"] = safe_outputs
    else:
        fm["safe-outputs"] = {
            "add-comment": {},
            "create-issue": {
                "title-prefix": f"[{name}] "
            }
        }

    fm_yaml = yaml.dump(fm, sort_keys=False).strip()
    # Quote the bare on: key so it round-trips as a string, not YAML 1.1 boolean
    fm_yaml = re.sub(r'^on:', '"on":', fm_yaml, flags=re.MULTILINE)
    
    body = instructions.strip() if instructions.strip() else f"# {name.replace('-', ' ').title()}\n\n{description}"
    return f"---\n{fm_yaml}\n---\n\n{body}\n"


def smart_failure_agent_md(
    name: str,
    description: str,
    instructions: str,
    kill_switch: str,
) -> str:
    """
    Target C: CI/CD Smart Failure Agent Persona (.agent.md).
    Must include the verbatim Kill Switch phrase and Escalation Trigger Taxonomy.
    NOTE: This is a prompt configuration executed headless via Copilot CLI,
    not a selectable/invocable chat agent.
    """
    body = instructions.strip() if instructions.strip() else f"# {name.replace('-', ' ').title()}"
    
    escalation_taxonomy = """
## 🚨 Escalation Trigger Taxonomy
- **CRITICAL**: Out-of-bounds tool execution, token limits exceeded, or safety policy violations. Action: Trigger Kill Switch immediately.
- **WARNING**: Missing optimal context files, low confidence in analysis, or minor lint warnings. Action: Output warnings, but do not fail build.
- **INFO**: Success state reached, all validations clean. Action: Auto-approve and exit cleanly.
"""

    kill_switch_section = f"""
## 🛑 Kill Switch / Quality Gate
If a critical failure or validation violation is detected, you MUST output the following exact phrase verbatim:
`{kill_switch}`
"""

    fm = {
        "name": name,
        "description": description,
        "generator": "scaffold_github_agent.py v2.1.0",
    }
    fm_yaml = yaml.dump(fm, sort_keys=False).strip()
    
    comment_header = "# NOTE: This is a prompt configuration executed headless via Copilot CLI,\n# not a selectable/invocable chat agent.\n"
    
    return f"---\n{fm_yaml}\n---\n\n{comment_header}\n{body}\n\n{escalation_taxonomy.strip()}\n\n{kill_switch_section.strip()}\n"


def runner_yml(
    name: str,
    kill_switch: str,
    triggers: list,
    model: str = None,
) -> str:
    """
    Target C: CI/CD Smart Failure Agent Workflow Runner (.github/workflows/<name>-agent.yml).
    """
    trigger_lines = ["  workflow_dispatch:"]
    for t in triggers:
        if t == "push":
            trigger_lines.append("  push:\n    branches: [\"main\"]")
        elif t == "pull_request":
            trigger_lines.append("  pull_request:")
        elif t == "schedule":
            trigger_lines.append("  schedule:\n    - cron: '0 9 * * 1'  # Mondays at 9am UTC")
        elif t == "issues":
            trigger_lines.append("  issues:\n    types: [opened, labeled]")
        elif t == "release":
            trigger_lines.append("  release:\n    types: [published]")
            
    trigger_block = "\n".join(trigger_lines)
    
    # Plumb model option
    model_opt = f" --model {model}" if model else ""

    return f"""name: {name.replace('-', ' ').title()} Agent Workflow

on:
{trigger_block}

jobs:
  run-agent:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Copilot CLI
        run: npm i -g @github/copilot

      - name: Run {name} agent
        env:
          COPILOT_GITHUB_TOKEN: ${{{{ secrets.COPILOT_GITHUB_TOKEN }}}}
          GITHUB_REPOSITORY: ${{{{ github.repository }}}}
        run: |
          set -euo pipefail

          # 1. Load Persona
          AGENT_PROMPT=$(cat .github/agents/{name}.agent.md)

          # 2. Add Dynamic Context
          PROMPT="$AGENT_PROMPT"
          PROMPT+=$'\\n\\nContext:\\n'
          PROMPT+="- Repository: $GITHUB_REPOSITORY"
          PROMPT+=$'\\n\\nTask: Execute instructions and write findings to report.md'

          # Execute Headless
          copilot{model_opt} --allow-tool read write shell --prompt "$PROMPT" < /dev/null

      - name: Quality Gate (Smart Fail)
        if: always()
        run: |
          if [ ! -f report.md ]; then
            echo "❌ QUALITY GATE FAILED: agent produced no report.md"
            exit 1
          fi
          if grep -q -F -- "{kill_switch}" report.md; then
            echo "❌ QUALITY GATE FAILED: {kill_switch}"
            exit 1
          else
            echo "✅ Agent review passed."
          fi
"""
