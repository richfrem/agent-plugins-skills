"""
scaffold.py (CLI)
=====================================

Purpose:
    Deterministically generates compliant directory architectures and boilerplate logic for Agent Skills, Plugins, Hooks, Commands, and Sub-Agents.

Key Input Dependencies:
    - Format templates located in ../assets/templates/ (README.md.jinja, SKILL.md.jinja, execute.py.jinja, agent.md.jinja, command.md.jinja)
    - argparse for CLI argument parsing
    - pathlib for path resolution

Layer: Meta-Execution

Usage Examples:
    pythonfold.py --type skill --name <skill-name> --path <output-dir> --desc "<description>"

Supported Object Types:
    - Plugins
    - Skills
    - Hooks
    - Sub-Agents
    - Commands

CLI Arguments:
    --type: The resource type to scaffold (plugin, skill, hook, etc).
    --name: The unique slug identifier for the resource.
    --path: Destination deployment directory.
    --desc: Short contextual description.
    --event: Lifecycle hook event (e.g. PreToolUse).
    --action: Hook action type.

Output:
    - Generated directory tree and markdown/json files at the requested --path.

Key Functions:
    - create_plugin()
    - create_skill()
    - create_hook()
    - create_sub_agent()
    - create_command()

Consumed by:
    - Agent Scaffolders logic (create-plugin, create-skill, etc.)
"""

import argparse
import os
import json
import re
from pathlib import Path


def get_template(filename: str) -> str | None:
    """Load a format template relative to the invoked source or installed script."""
    template_path = Path(__file__).absolute().parent.parent / "assets/templates" / filename
    return template_path.read_text(encoding="utf-8") if template_path.is_file() else None


def _create_plugin_directories(full_path: str) -> None:
    """Create standard plugin directory structure."""
    claude_plugin_dir = os.path.join(full_path, ".claude-plugin")
    os.makedirs(claude_plugin_dir, exist_ok=True)
    os.makedirs(os.path.join(full_path, "skills"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "agents"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "commands"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "hooks", "scripts"), exist_ok=True)


def _create_plugin_configs(full_path: str, name: str) -> None:
    """Create plugin configuration files (hooks.json, mcp.json, lsp.json, plugin.json)."""
    with open(os.path.join(full_path, "hooks", "hooks.json"), "w") as f:
        f.write("{\\n}")
    with open(os.path.join(full_path, ".mcp.json"), "w") as f:
        f.write("{\\n  \"mcpServers\": {}\\n}\\n")
    with open(os.path.join(full_path, "lsp.json"), "w") as f:
        f.write("{\\n  \"languageServers\": {}\\n}\\n")

    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": f"The {name} plugin.",
        "author": {
            "name": "richfrem",
            "email": "connect.richfrem@gmail.com"
        },
        "repository": "https://github.com/richfrem/agent-plugins-skills",
        "license": "MIT",
        "keywords": [
            name
        ]
    }
    with open(os.path.join(full_path, ".claude-plugin", "plugin.json"), "w") as f:
        json.dump(manifest, f, indent=4)


def _create_plugin_readme_and_diagram(full_path: str, name: str) -> None:
    """Create README.md and architecture diagram for plugin."""
    readme_template = get_template("README.md.jinja")
    if readme_template:
        readme_content = readme_template.format(
            name=name,
            description="Define the purpose of this package here."
        )
    else:
        readme_content = f"# {name} Plugin\\n\\nGenerated via Agent Scaffolder.\\n\\n## Purpose\\nDefine the purpose of this package here."

    with open(os.path.join(full_path, "README.md"), "w") as f:
        f.write(readme_content)

    mmd_content = f"""graph TD
    A[{name} Plugin] --> B[.claude-plugin/plugin.json]
    A --> C[skills/]
    A --> D[agents/]
    A --> E[commands/]
    A --> F[hooks.json]
    A --> G[mcp.json]
    A --> H[lsp.json]
    A --> I[README.md]
    """
    with open(os.path.join(full_path, f"{name}-architecture.mmd"), "w") as f:
        f.write(mmd_content)


def create_plugin(name: str, path: str, iteration: int | None = None) -> None:
    """Create a new plugin directory structure with required configuration files."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Plugin name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return

    if iteration:
        full_path = os.path.join(path, ".history", f"iteration-{iteration}", name)
    else:
        full_path = os.path.join(path, name)

    _create_plugin_directories(full_path)
    _create_plugin_configs(full_path, name)
    _create_plugin_readme_and_diagram(full_path, name)

    with open(os.path.join(full_path, "requirements.in"), "w") as f:
        f.write("# No external dependencies required. Standard library only.\\n")

    print(f"Success: Plugin '{name}' scaffolded at {full_path}")

def _create_skill_directories(skill_dir: str) -> None:
    """Create standard skill directory structure."""
    scripts_dir = os.path.join(skill_dir, "scripts")
    references_dir = os.path.join(skill_dir, "references")
    examples_dir = os.path.join(skill_dir, "examples")
    templates_dir = os.path.join(skill_dir, "templates")
    evals_dir = os.path.join(skill_dir, "evals")
    test_dir = os.path.join(skill_dir, "test")

    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(references_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(evals_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)


def _create_skill_documentation(skill_dir: str, name: str, description: str) -> None:
    """Create SKILL.md, CONNECTORS.md, and reference files."""
    skill_template = get_template("SKILL.md.jinja")
    if skill_template:
        template_safe = skill_template.replace("${{", "{").replace("}}", "}")
        skill_content = template_safe.format(
            name=name,
            description=description,
            title_name=name.replace("-", " ").title(),
            plugins="${plugins}"
        )
    else:
        skill_content = "---snip---"

    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)

    with open(os.path.join(skill_dir, "CONNECTORS.md"), "w") as f:
        f.write(f"# {name} Connectors Map\n\nMap abstract `~~category` tool requirements to exact system dependencies here to keep the plugin portable.")

    references_dir = os.path.join(skill_dir, "references")
    with open(os.path.join(references_dir, "architecture.md"), "w") as f:
        f.write(f"# {name} Protocol Reference\n\nPut deep context here so it is not loaded into context implicitly.")

    with open(os.path.join(references_dir, "acceptance-criteria.md"), "w") as f:
        f.write(f"# Acceptance Criteria: {name}\n\nDefine at least two testable criteria or correct/incorrect operational patterns here to ensure the skill functions correctly.")


def _create_skill_evals_and_diagram(skill_dir: str, name: str) -> None:
    """Create evals.json, results.tsv, and workflow diagram."""
    evals_dir = os.path.join(skill_dir, "evals")
    eval_set = [
        {"query": f"I need help using the {name} skill", "should_trigger": True},
        {"query": f"Can you use the {name} skill for me?", "should_trigger": True},
        {"query": "What time is it in New York?", "should_trigger": False},
        {"query": "How do I boil an egg?", "should_trigger": False}
    ]
    with open(os.path.join(evals_dir, "evals.json"), "w") as f:
        json.dump(eval_set, f, indent=2)

    with open(os.path.join(evals_dir, "results.tsv"), "w") as f:
        f.write("iteration\ttrain_score\ttest_score\tdecision\tnotes\tdescription\n")

    mmd_content = f"""stateDiagram-v2
    [*] --> Init
    Init --> Process : Execute {name}
    Process --> [*]
    """
    with open(os.path.join(skill_dir, f"{name}-flow.mmd"), "w") as f:
        f.write(mmd_content)


def _create_skill_execute_script(skill_dir: str, name: str, description: str) -> None:
    """Create execute.py script from template."""
    execute_template = get_template("execute.py.jinja")
    script_content = ""
    if execute_template:
        script_content = execute_template.format(
            description=description,
            name=name
        )
    else:
        script_content = "# Template failed to load"

    scripts_dir = os.path.join(skill_dir, "scripts")
    script_path = os.path.join(scripts_dir, "execute.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)


def create_skill(name: str, path: str, description: str, iteration: int | None = None,
                 variant: str = "instructional", plugin_root: str | None = None,
                 json_output: bool = False) -> dict:
    """Preflight a variant and generate hub-owned resources with proposed managed links."""
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        raise ValueError("Skill name must be 1–64 lowercase letters, numbers or hyphens")
    if not description.strip() or len(description) > 1024 or re.search(r"<[^>]+>", description):
        raise ValueError("Description must be nonempty, <=1024 characters and contain no XML tags")
    filename = "SKILL.md.jinja" if variant == "instructional" else "SKILL-executable.md.jinja"
    template = get_template(filename)
    if template is None:
        raise ValueError(f"Missing required template: {filename}")
    contract_path = Path(__file__).absolute().parent.parent / "references/skill-authoring-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    layout = contract["variants"][variant]
    if layout["template"] != filename:
        raise ValueError("Template and authoring contract disagree")
    base = Path(path).absolute()
    skill = base / ".history" / f"iteration-{iteration}" / name if iteration else base / name
    if skill.exists():
        raise ValueError(f"Output already exists: {skill}")
    root = Path(plugin_root).absolute() if plugin_root else (base.parent if base.name == "skills" else None)
    script_name = name.replace("-", "_") + ".py"
    links = []
    script_content = None
    script_path = None
    if variant == "executable":
        if root is None or base != root / "skills" or iteration:
            raise ValueError("Executable output requires a plugin-root/skills path and no history iteration")
        script_template = get_template(layout["script_template"])
        if script_template is None:
            raise ValueError("Missing required template: execute.py.jinja")
        script_path = root / "scripts" / script_name
        if script_path.exists():
            raise ValueError(f"Canonical script already exists: {script_path}")
        script_content = script_template.format(name=name, description=json.dumps(description))
        compile(script_content, str(script_path), "exec")
        links.append({"src": str(script_path), "dst": str(skill / "scripts" / script_name),
                      "strategy": "symlink", "description": f"Canonical executable for {name}"})
    content = template.format(name=name, description=json.dumps(description, ensure_ascii=False),
                              title_name=name.replace("-", " ").title(), purpose=description,
                              script_name=script_name)
    skill.mkdir(parents=True)
    for directory in layout["directories"]:
        (skill / directory).mkdir(exist_ok=True)
    (skill / "SKILL.md").write_text(content, encoding="utf-8")
    _create_skill_evals_and_diagram(str(skill), name)
    if script_path is not None:
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_content, encoding="utf-8")
    report = {"status": "pending_links" if links else "generated", "skill_path": str(skill),
              "contract_version": contract["version"], "variant": variant, "links": links}
    print(json.dumps(report, indent=2) if json_output else
          f"Generated {variant} skill at {skill}; status: {report['status']}. Customize and evaluate before publishing.")
    return report


def create_hook(event: str, path: str, action_type: str) -> None:
    """Create a new hook entry in a plugin's hooks.json file."""
    import pathlib
    resolved_path = pathlib.Path(path).resolve()
    if not (resolved_path / ".claude-plugin").exists():
        print(f"Error: Path '{resolved_path}' must be a plugin root containing .claude-plugin/")
        return
    hooks_file = os.path.join(path, "hooks.json")

    hooks_data = []
    if os.path.exists(hooks_file):
        with open(hooks_file, "r") as f:
            try:
                hooks_data = json.load(f)
            except json.JSONDecodeError:
                hooks_data = []

    new_hook = {
        "events": [event],
        "matcher": ".*",
        "hooks": [
            {
                "type": action_type,
                "command": "echo 'Add your command or prompt here'" if action_type == "command" else "Add prompt here",
                "async": False
            }
        ]
    }
    hooks_data.append(new_hook)

    with open(hooks_file, "w") as f:
        json.dump(hooks_data, f, indent=4)

    schema_file = os.path.join(path, "hook-schema-reference.json")
    if not os.path.exists(schema_file):
        with open(schema_file, "w") as f:
            f.write("{\n  \"continue\": false,\n  \"stopReason\": \"\",\n  \"decision\": \"block\",\n  \"reason\": \"\"\n}")

    print(f"Success: Hook appended to {hooks_file}")

def create_sub_agent(name: str, path: str, desc: str) -> None:
    """Create a new sub-agent markdown file from template."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Sub-agent name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Sub-agent name '{name}' exceeds 64 characters.")
        return
    full_path = os.path.join(path, f"{name}.md")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    agent_template = get_template("agent.md.jinja")
    if agent_template:
        content = agent_template.format(
            name=name,
            description=desc
        )
    else:
        content = "---snip---"

    with open(full_path, "w") as f:
        f.write(content)

    print(f"Success: Sub-agent saved to {full_path}")

def create_command(name: str, path: str, desc: str) -> None:
    """Create a new command markdown file from template."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Command name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Command name '{name}' exceeds 64 characters.")
        return
    full_path = os.path.join(path, f"{name}.md")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    cmd_template = get_template("command.md.jinja")
    if cmd_template:
        content = cmd_template.format(
            name=name,
            description=desc
        )
    else:
        content = "---snip---"

    with open(full_path, "w") as f:
        f.write(content)

    print(f"Success: Command saved to {full_path}")

def main() -> None:
    """Parse CLI arguments and dispatch to appropriate scaffolding function."""
    parser = argparse.ArgumentParser(description="Agent Ecosystem Scaffolder CLI")
    parser.add_argument("--type", choices=["plugin", "skill", "hook", "sub-agent", "command", "mcp"], required=True, help="Type of resource to scaffold")
    parser.add_argument("--name", required=True, help="Name of the resource")
    parser.add_argument("--path", required=True, help="Destination directory path")
    parser.add_argument("--desc", default="A generated resource.", help="Description for skills or agents")
    parser.add_argument("--event", default="PreToolUse", help="Lifecycle event for hooks")
    parser.add_argument("--action", default="command", choices=["command", "prompt", "agent"], help="Hook action type")
    parser.add_argument("--iteration", type=int, help="Iteration number for safe rollback isolation (e.g., 1, 2)")
    
    parser.add_argument("--variant", choices=("instructional", "executable"), default="instructional")
    parser.add_argument("--plugin-root", default=None, help="Output plugin root for executable resources")
    parser.add_argument("--json", action="store_true", help="JSON skill generation receipt")
    args = parser.parse_args()
    
    if args.type == "plugin":
        create_plugin(args.name, args.path, args.iteration)
    elif args.type == "skill":
        try:
            create_skill(args.name, args.path, args.desc, args.iteration, args.variant, args.plugin_root, args.json)
        except (ValueError, OSError, KeyError) as error:
            parser.exit(2, f"Error: {error}\n")
    elif args.type == "hook":
        create_hook(args.event, args.path, args.action)
    elif args.type == "sub-agent":
        create_sub_agent(args.name, args.path, args.desc)
    elif args.type == "command":
        create_command(args.name, args.path, args.desc)
    elif args.type == "mcp":
        print("MCP generation requires modifying claude.json. This CLI feature is a stub.")

if __name__ == "__main__":
    main()
