# -*- coding: utf-8 -*-
"""
scaffold_github_agent.py
=====================================
Purpose:
    Dispatcher script to generate GitHub AI Agents (Target A, B, or C).
    Writes files and outputs a JSON manifest of created artifacts.
"""

import os
import sys
import argparse
import json
import re
from pathlib import Path
import yaml

# Resolve imports cleanly from the real directory (resolving symlinks)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

# Import templates
import gh_agent_templates as templates


def parse_frontmatter(content: str) -> tuple[dict, str]:
    fm = {}
    body = content
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
        except Exception:
            pass
        body = content[match.end():]
        
    # PyYAML boolean trap: YAML 1.1 converts "on" -> True, "off" -> False
    # Normalize these keys back to strings for proper validation
    if fm:
        for bad, good in ((True, "on"), (False, "off")):
            if bad in fm:
                fm[good] = fm.pop(bad)
                
    return fm, body


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a GitHub Agent (Target A, B, or C).")
    parser.add_argument(
        "--target",
        choices=["A", "B", "C"],
        required=True,
        help="Target type to scaffold (A: Custom Copilot Agent, B: gh-aw Workflow, C: Smart Failure)",
    )
    parser.add_argument("--name", required=True, help="Name of the agent (kebab-case)")
    parser.add_argument("--description", help="Description for the agent")
    parser.add_argument("--engine", default="copilot", choices=["copilot", "claude", "codex"], help="AI Engine to use")
    parser.add_argument(
        "--triggers",
        nargs="*",
        default=[],
        help="Triggers (e.g. pull_request push schedule issues release) or custom cron schedule",
    )
    parser.add_argument("--safe-outputs", help="Comma-separated safe outputs (e.g. add-comment,create-issue)")
    parser.add_argument("--kill-switch", help="Verbatim Kill Switch phrase for Target C")
    parser.add_argument("--skill-dir", help="Path to a skill directory containing SKILL.md to extract info from")
    parser.add_argument("--output-dir", default=".", help="Root directory for generating the .github folders")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files without error")
    parser.add_argument("--model", help="Specify a model for Target A (default: let it inherit)")
    parser.add_argument("--with-agents-md", action="store_true", help="Create starter stub AGENTS.md")
    parser.add_argument("--with-copilot-instructions", action="store_true", help="Create starter stub .github/copilot-instructions.md")

    args = parser.parse_args()

    # Smart name sanitize: replace spaces/underscores with dashes, then strip other non-alphanumeric chars
    name = re.sub(r'[\s_]+', '-', args.name.strip().lower())
    name = re.sub(r'[^a-zA-Z0-9-]', '', name)
    
    output_root = Path(args.output_dir).resolve()

    # Determine instructions body and description
    description = args.description or f"GitHub Agent for {name}"
    body = f"# Instructions for {name.replace('-', ' ').title()}\n\nAdd operational procedures here."

    if args.skill_dir:
        skill_path = Path(args.skill_dir).resolve()
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            print(f"Error: SKILL.md not found in {args.skill_dir}", file=sys.stderr)
            sys.exit(1)
        try:
            content = skill_file.read_text(encoding="utf-8")
            fm, skill_body = parse_frontmatter(content)
            description = fm.get("description", description)
            body = skill_body
        except Exception as e:
            print(f"Error reading SKILL.md: {e}", file=sys.stderr)
            sys.exit(1)

    created_files = []
    skipped_files = []
    next_steps = []

    def write_file_safe(file_path: Path, content: str) -> None:
        if file_path.exists() and not args.force:
            skipped_files.append(str(file_path.relative_to(output_root)))
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        created_files.append(str(file_path.relative_to(output_root)))

    # Target A: Custom Copilot Agent
    if args.target == "A":
        agents_dir = output_root / ".github" / "agents"
        prompts_dir = output_root / ".github" / "prompts"

        agent_content = templates.agent_md_github(
            name=name,
            description=description,
            body=body,
            target="both",
            tools=["github", "terminal"],
            model=args.model,
        )
        write_file_safe(agents_dir / f"{name}.agent.md", agent_content)
        write_file_safe(prompts_dir / f"{name}.prompt.md", f"---\nagent: {name}\n---\n")
        
        next_steps.extend([
            "Select the agent from the Copilot Chat dropdown in VS Code or GitHub.com",
            f"Type /{name} to invoke the agent in your IDE"
        ])

    # Target B: GitHub Agentic Workflow (gh-aw)
    elif args.target == "B":
        workflows_dir = output_root / ".github" / "workflows"

        on_trigger = {}
        if args.triggers:
            for t in args.triggers:
                if ":" in t:
                    k, _, v = t.partition(":")
                    on_trigger[k.strip()] = v.strip()
                else:
                    on_trigger[t] = {}
        else:
            on_trigger = {"schedule": "daily"}

        safe_outputs = {}
        if args.safe_outputs:
            for item in args.safe_outputs.split(","):
                item = item.strip()
                if item:
                    safe_outputs[item] = {}
        else:
            safe_outputs = {
                "add-comment": {},
                "create-issue": {
                    "title-prefix": f"[{name}] "
                }
            }

        workflow_content = templates.gh_aw_workflow_md(
            name=name,
            description=description,
            instructions=body,
            on_trigger=on_trigger,
            engine=args.engine,
            safe_outputs=safe_outputs,
        )
        write_file_safe(workflows_dir / f"{name}.md", workflow_content)

        next_steps.extend([
            "gh extension install github/gh-aw",
            f"gh aw init --engine {args.engine}",
            "set COPILOT_GITHUB_TOKEN (fine-grained PAT with Copilot Requests write permission)",
            "gh aw compile (generates the .lock.yml file)"
        ])

    # Target C: CI/CD Smart Failure Agent
    elif args.target == "C":
        agents_dir = output_root / ".github" / "agents"
        workflows_dir = output_root / ".github" / "workflows"

        kill_switch = args.kill_switch or f"CRITICAL FAILURE: {name.upper().replace('-', '_')}"

        agent_content = templates.smart_failure_agent_md(
            name=name,
            description=description,
            instructions=body,
            kill_switch=kill_switch,
        )
        write_file_safe(agents_dir / f"{name}.agent.md", agent_content)

        triggers = args.triggers if args.triggers else ["pull_request", "push"]
        runner_content = templates.runner_yml(
            name=name,
            kill_switch=kill_switch,
            triggers=triggers,
            model=args.model,
        )
        write_file_safe(workflows_dir / f"{name}-agent.yml", runner_content)

        next_steps.extend([
            "Add COPILOT_GITHUB_TOKEN to your repository secrets",
            f"Ensure the kill switch phrase '{kill_switch}' is output on critical validation failures"
        ])

    # Optional Starter Stubs
    if args.with_agents_md:
        agents_md_path = output_root / "AGENTS.md"
        agents_md_stub = f"# Repository Agents\n\n- @{name}: {description}\n"
        write_file_safe(agents_md_path, agents_md_stub)
        
    if args.with_copilot_instructions:
        copilot_instr_path = output_root / ".github" / "copilot-instructions.md"
        copilot_instr_stub = f"# Copilot Custom Instructions\n\nIdentify @{name} agent for specific code and workflow tasks.\n"
        write_file_safe(copilot_instr_path, copilot_instr_stub)

    # If any file was skipped and not forced, output status and warning
    status = "success"
    warnings = []
    if skipped_files:
        status = "partial_skipped"
        warnings.append(f"Skipped existing files (use --force to overwrite): {', '.join(skipped_files)}")

    result = {
        "status": status,
        "target": args.target,
        "name": name,
        "created": created_files,
        "skipped": skipped_files,
        "next_steps": next_steps,
    }
    if warnings:
        result["warnings"] = warnings
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
