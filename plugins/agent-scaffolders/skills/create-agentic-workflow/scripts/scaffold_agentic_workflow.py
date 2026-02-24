#!/usr/bin/env python3
"""
Scaffold Agentic Workflow
=====================================

Purpose:
    Scaffolds a GitHub Agentic Workflow (Continuous AI/"Smart Failure") from an 
    existing Agent Skill by generating the required Persona (.agent.md) and 
    GitHub Action runner (.yml) files.

Layer: Codify

Usage:
    python scaffold_agentic_workflow.py --skill-dir <path/to/skill>

Related:
    - create-agentic-workflow/SKILL.md
"""

import os
import re
import argparse
from pathlib import Path
import textwrap

from typing import Tuple, Dict

def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Parses YAML frontmatter from a Markdown file string.

    Args:
        content: The raw string content of the Markdown file.

    Returns:
        A tuple containing a dictionary of the frontmatter metadata and 
        a string of the remaining body content.
    """
    metadata = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        fm_block = match.group(1)
        body = content[match.end():]
        for line in fm_block.splitlines():
            if ':' in line:
                key, _, value = line.partition(':')
                metadata[key.strip()] = value.strip().strip('"').strip("'")
        return metadata, body
    return metadata, content

def generate_agentic_workflow(skill_file: Path, target_repo_root: Path) -> None:
    """
    Generates the Persona (.agent.md) and Runner (.yml) files for a GitHub Action.

    Args:
        skill_file: Path object pointing to the source SKILL.md file.
        target_repo_root: Path object pointing to the root of the repository where 
                          the .github folder resides.
    """
    agents_dir = target_repo_root / ".github" / "agents"
    workflows_dir = target_repo_root / ".github" / "workflows"
    
    agents_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    if not skill_file.exists():
        print(f"Error: Could not find {skill_file}")
        return
        
    content = skill_file.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(content)
    
    name = fm.get('name', skill_file.parent.name)
    description = fm.get('description', f"Agentic workflow for {name}")
    
    kill_switch = f"CRITICAL FAILURE: {name.upper()}"
    
    # 1. Generate Persona (.agent.md)
    agent_content = textwrap.dedent(f"""\
    ---
    name: {name}
    description: {description}
    ---

    # 🤖 {name.replace('-', ' ').title()} Instructions

    **Purpose:** {description}

    ## 🎯 Core Workflow
    1. **Analyze Context:** Review the target pull request or issue to understand the required context for the `{name}` objective.
    2. **Execute Strict Checks:** Follow the standard operational procedures defined by the framework for this phase.
    3. **Draft Report:** Summarize the findings clearly, separating actionable feedback from pass/fail criteria.

    ### Kill Switch / Quality Gate
    - If the analysis determines a critical failure in the requirements, specification, or code quality, you MUST output exactly this phrase at the end of your report: `{kill_switch}`
    """)
    
    agent_file = agents_dir / f"{name}.agent.md"
    agent_file.write_text(agent_content, encoding='utf-8')
    
    # 2. Generate YAML Runner
    yaml_content = textwrap.dedent(f"""\
    name: {name.replace('-', ' ').title()} Agent Workflow

    on:
      workflow_dispatch:

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

          - name: Install Intelligence (Copilot CLI)
            run: npm i -g @github/copilot

          - name: Run {name}
            env:
              COPILOT_GITHUB_TOKEN: ${{{{ secrets.COPILOT_GITHUB_TOKEN }}}}
              GITHUB_REPOSITORY: ${{{{ github.repository }}}}
            run: |
              set -euo pipefail
              
              # 1. Load Persona
              AGENT_PROMPT=$(cat .github/agents/{name}.agent.md)
              
              # 2. Add Context
              PROMPT="$AGENT_PROMPT"
              PROMPT+=$'\\n\\nContext:\\n'
              PROMPT+="- Repository: $GITHUB_REPOSITORY"
              PROMPT+=$'\\n\\nTask: Execute instructions against the current repository state and generate report strictly to /report.md'
              
              # 3. Execute Headless
              copilot --prompt "$PROMPT" --allow-all-tools < /dev/null

          - name: The Logic Check (Smart Fail)
            if: always()
            run: |
              # 4. Grep for the Kill Switch
              if grep -q "{kill_switch}" report.md; then
                echo "❌ QUALITY GATE FAILED: {kill_switch}"
                exit 1
              else
                echo "✅ Agent review passed."
              fi
    """)
    
    yaml_file = workflows_dir / f"{name}-agent.yml"
    yaml_file.write_text(yaml_content, encoding='utf-8')
    
    print(f"Generated Workflow Config for {name}:")
    print(f"  -> Persona: {agent_file}")
    print(f"  -> Action: {yaml_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a GitHub Agentic Workflow from an existing Skill.")
    parser.add_argument("--skill-dir", required=True, help="Path to the directory containing the SKILL.md file")
    
    args = parser.parse_args()
    
    skill_path = Path(args.skill_dir).resolve()
    skill_file = skill_path / "SKILL.md"
    repo_path = Path.cwd() # Assume running from project root
    
    generate_agentic_workflow(skill_file, repo_path)
