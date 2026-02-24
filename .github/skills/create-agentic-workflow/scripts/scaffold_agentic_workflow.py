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
        agents_dir: Path to the .github/agents/ directory.
        full_content: If True, port the full SKILL.md body; if False, generate a stub.

    Returns:
        Path to the created .agent.md file.
    """
    if full_content and body.strip():
        # Rich mode: use the full SKILL.md body as the agent instructions
        # (matches spec-kit's approach — agents are as rich as the source skill)
        agent_content = f"""---
description: {description}
---

{body.strip()}
"""
    else:
        # Stub mode: generate a minimal skeleton
        steps_text = extract_workflow_steps(body)
        agent_content = textwrap.dedent(f"""\
        ---
        description: {description}
        ---

        # 🤖 {name.replace('-', ' ').title()}

        **Purpose:** {description}

        ## 🎯 Core Workflow

        {steps_text}
        """)

    agent_file = agents_dir / f"{name}.agent.md"
    agent_file.write_text(agent_content, encoding="utf-8")
    return agent_file


def generate_prompt_file(name: str, prompts_dir: Path) -> Path:
    """
    Generates the thin .prompt.md companion pointer file for IDE agent mode.

    The prompt file registers the agent as a slash command in Copilot Chat.
    All instructions live in the .agent.md — this file is intentionally minimal.

    Args:
        name: Agent name (must match the .agent.md filename without extension).
        prompts_dir: Path to the .github/prompts/ directory.

    Returns:
        Path to the created .prompt.md file.
    """
    prompt_content = textwrap.dedent(f"""\
    ---
    agent: {name}
    ---
    """)
    prompt_file = prompts_dir / f"{name}.prompt.md"
    prompt_file.write_text(prompt_content, encoding="utf-8")
    return prompt_file


def build_trigger_block(triggers: list[str]) -> str:
    """
    Builds the YAML `on:` trigger block from the selected trigger list.

    workflow_dispatch is always included as the baseline manual trigger.
    Additional triggers are appended from the TRIGGER_CONFIGS map.

    Args:
        triggers: List of trigger names (e.g. ['pull_request', 'push']).

    Returns:
        Indented YAML string for the `on:` block.
    """
    lines = ["  workflow_dispatch:"]
    for trigger in triggers:
        config = TRIGGER_CONFIGS.get(trigger)
        if config:
            lines.append(config)
    return "\n".join(lines)


def generate_workflow_file(
    name: str,
    kill_switch: str,
    triggers: list[str],
    workflows_dir: Path,
) -> Path:
    """
    Generates the .yml GitHub Actions runner file for CI/CD agent mode.

    Args:
        name: Agent name (kebab-case).
        kill_switch: Exact phrase the agent must output to fail the build.
        triggers: List of GitHub event triggers (e.g. ['pull_request', 'push']).
        workflows_dir: Path to the .github/workflows/ directory.

    Returns:
        Path to the created .yml file.
    """
    trigger_block = build_trigger_block(triggers)

    yaml_content = textwrap.dedent(f"""\
    name: {name.replace('-', ' ').title()} Agent Workflow

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
              PROMPT+=$'\\n\\nTask: Execute instructions and write findings to /report.md'

              # 3. Execute Headless
              copilot --prompt "$PROMPT" --allow-all-tools --model claude-sonnet-4.5 < /dev/null

          - name: Quality Gate (Smart Fail)
            if: always()
            run: |
              if grep -q "{kill_switch}" report.md; then
                echo "❌ QUALITY GATE FAILED: {kill_switch}"
                exit 1
              else
                echo "✅ Agent review passed."
              fi
    """)

    yaml_file = workflows_dir / f"{name}-agent.yml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    return yaml_file


def generate_agentic_workflow(
    skill_file: Path,
    target_repo_root: Path,
    mode: str = "cicd",
    triggers: Optional[list[str]] = None,
    kill_switch: str = "",
) -> None:
    """
    Orchestrates generation of GitHub agent files from an existing SKILL.md.

    Args:
        skill_file: Path to the source SKILL.md file.
        target_repo_root: Root of the repository where .github/ will be written.
        mode: One of 'ide', 'cicd', or 'both'.
        triggers: List of GitHub event names for CI/CD mode. Defaults to [].
        kill_switch: Custom kill switch phrase. Auto-generated if empty.
    """
    if triggers is None:
        triggers = []

    agents_dir = target_repo_root / ".github" / "agents"
    prompts_dir = target_repo_root / ".github" / "prompts"
    workflows_dir = target_repo_root / ".github" / "workflows"

    agents_dir.mkdir(parents=True, exist_ok=True)

    if not skill_file.exists():
        print(f"Error: Could not find {skill_file}")
        return

    content = skill_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    name = fm.get("name", skill_file.parent.name)
    description = fm.get("description", f"Agentic workflow for {name}")

    if not kill_switch:
        kill_switch = f"CRITICAL FAILURE: {name.upper().replace('-', '_')}"

    # --- Shared .agent.md persona ---
    agent_file = generate_agent_file(name, description, body, agents_dir)
    generated = [f"  -> Persona:  {agent_file}"]

    # --- IDE mode: .prompt.md ---
    if mode in ("ide", "both"):
        prompts_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = generate_prompt_file(name, prompts_dir)
        generated.append(f"  -> Prompt:   {prompt_file}")

    # --- CI/CD mode: .yml runner ---
    if mode in ("cicd", "both"):
        workflows_dir.mkdir(parents=True, exist_ok=True)
        yaml_file = generate_workflow_file(name, kill_switch, triggers, workflows_dir)
        generated.append(f"  -> Action:   {yaml_file}")
        trigger_names = ["workflow_dispatch"] + triggers
        generated.append(f"  -> Triggers: {', '.join(trigger_names)}")
        generated.append(f"  -> Kill Switch: \"{kill_switch}\"")

    print(f"\nGenerated {mode.upper()} agent '{name}':")
    for line in generated:
        print(line)

    if mode in ("cicd", "both"):
        print("\n⚠️  Requirements:")
        print("  - Add COPILOT_GITHUB_TOKEN to your repository secrets.")
        print(f"  - Ensure the kill switch phrase appears verbatim in {agent_file.name}.")
    if mode in ("ide", "both"):
        print("\n💡 IDE Usage:")
        print(f"  - Open GitHub Copilot Chat and select '{name}' from the agent dropdown.")
        print(f"  - Or type '/{name}' as a slash command.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scaffold a GitHub Agent from an existing Skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Mode guide:
          ide   -> .agent.md + .prompt.md  (Copilot Chat / VS Code UI)
          cicd  -> .agent.md + .yml runner (GitHub Actions quality gate)
          both  -> all three files         (shared persona, dual use)

        Format guide (cicd/both only):
          smart-failure  Kill Switch grep pattern — works in any repo today (default)
          official       Official GitHub Agentic Workflow .md + .lock.yml
                         Requires: gh extension install github/gh-aw && gh aw compile

        Trigger guide (cicd/both only — workflow_dispatch always included):
          pull_request  On PR open/update (spec review, code quality gates)
          push          On push to main   (doc sync, post-merge checks)
          schedule      On cron schedule  (daily health reports, triage)
          issues        On issue creation (auto-labeling, routing)
          release       On release publish (release readiness validation)

        Batch mode (--plugin-dir):
          Walks all skills/ subdirectories in a plugin and scaffolds each SKILL.md.
          Example: --plugin-dir plugins/spec-kitty-plugin --mode ide
        """),
    )

    # Mutually exclusive: single skill OR entire plugin directory
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--skill-dir",
        help="Path to a single skill directory containing SKILL.md",
    )
    source_group.add_argument(
        "--plugin-dir",
        help="Path to a plugin directory — scaffolds ALL skills/ subdirectories in batch",
    )

    parser.add_argument(
        "--mode",
        choices=["ide", "cicd", "both"],
        default="cicd",
        help="Agent type: 'ide' (Copilot Chat), 'cicd' (GitHub Actions), or 'both'",
    )
    parser.add_argument(
        "--format",
        choices=["smart-failure", "official"],
        default="smart-failure",
        dest="fmt",
        help=(
            "[cicd/both] 'smart-failure' = Kill Switch YAML runner (default); "
            "'official' = Official GitHub Agentic Workflow .md + .lock.yml (requires gh aw compile)"
        ),
    )
    parser.add_argument(
        "--triggers",
        nargs="*",
        choices=list(TRIGGER_CONFIGS.keys()),
        default=[],
        metavar="TRIGGER",
        help=(
            "[cicd/both] GitHub events that trigger the workflow "
            f"(choices: {', '.join(TRIGGER_CONFIGS.keys())}). "
            "workflow_dispatch is always included."
        ),
    )
    parser.add_argument(
        "--kill-switch",
        default="",
        help="[cicd/both smart-failure] Custom kill switch phrase the agent outputs to fail the build",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Generate a skeleton stub instead of porting the full SKILL.md body into the .agent.md",
    )

    args = parser.parse_args()
    repo_path = Path.cwd()

    # Collect all skill files to process
    skill_files: list[Path] = []

    if args.plugin_dir:
        plugin_path = Path(args.plugin_dir).resolve()
        # Walk skills/ then commands/ for SKILL.md files
        for subdir_name in ("skills", "commands"):
            skills_root = plugin_path / subdir_name
            if skills_root.exists():
                for skill_subdir in sorted(skills_root.iterdir()):
                    candidate = skill_subdir / "SKILL.md"
                    if skill_subdir.is_dir() and candidate.exists():
                        skill_files.append(candidate)
        if not skill_files:
            print(f"No SKILL.md files found under {plugin_path}/skills or {plugin_path}/commands")
            raise SystemExit(1)
    else:
        skill_files.append(Path(args.skill_dir).resolve() / "SKILL.md")  # type: ignore[arg-type]

    print(f"\nScaffolding {len(skill_files)} skill(s) | mode={args.mode} | format={args.fmt}")
    print("-" * 60)

    for skill_file in skill_files:
        generate_agentic_workflow(
            skill_file,
            repo_path,
            mode=args.mode,
            triggers=args.triggers or [],
            kill_switch=args.kill_switch,
        )

    if args.fmt == "official" and args.mode in ("cicd", "both"):
        print("\n📦 Next step — compile the official format:")
        print("  gh extension install github/gh-aw")
        print("  gh aw compile")
        print("  git add .github/workflows/*.md .github/workflows/*.lock.yml")
        print("  git commit -m 'feat: add official github agentic workflows'")
