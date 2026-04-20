"""
scaffold.py (CLI)
=====================================

Purpose:
    Deterministically generates compliant directory architectures and boilerplate logic for Agent Skills, Plugins, Hooks, Commands, and Sub-Agents.

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

Input Files:
    - Jinja templates located in ../templates/

Output:
    - Generated directory tree and markdown/json files at the requested --path.

Key Functions:
    - create_plugin()
    - create_skill()
    - create_hook()
    - create_sub_agent()
    - create_command()

Script Dependencies:
    None

Consumed by:
    - Agent Scaffolders logic (create-plugin, create-skill, etc.)
"""

import argparse
import os
import json
import re

def create_plugin(name: str, path: str, iteration: int | None = None) -> None:
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Plugin name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
        
    if iteration:
        full_path = os.path.join(path, ".history", f"iteration-{iteration}", name)
    else:
        full_path = os.path.join(path, name)
        
    claude_plugin_dir = os.path.join(full_path, ".claude-plugin")
    
    os.makedirs(claude_plugin_dir, exist_ok=True)
    os.makedirs(os.path.join(full_path, "skills"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "agents"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "commands"), exist_ok=True)
    
    # Initialize empty hooks schema in a nested hooks/ dir
    os.makedirs(os.path.join(full_path, "hooks", "scripts"), exist_ok=True)
    with open(os.path.join(full_path, "hooks", "hooks.json"), "w") as f:
        f.write("{\\n}")

    # Initialize empty MCP and LSP schemas
    with open(os.path.join(full_path, ".mcp.json"), "w") as f:
        f.write("{\\n  \"mcpServers\": {}\\n}\\n")
    with open(os.path.join(full_path, "lsp.json"), "w") as f:
        f.write("{\\n  \"languageServers\": {}\\n}\\n")
    
    # Helper function to read a template
    def get_template(filename: str) -> str | None:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    # 1. Standard Plugin Manifest (Authoritative Schema)
    # CRITICAL: No `skills`, `scripts`, or `commands` arrays.
    # Skills are auto-discovered from skills/*/SKILL.md directory structure.
    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": f"The {name} plugin.",
        "author": {
            "name": "Generated via Agent Scaffolder"
        }
    }
    with open(os.path.join(claude_plugin_dir, "plugin.json"), "w") as f:
        json.dump(manifest, f, indent=4)
        
    # 2. Recommended Best Practice: README.md with File Tree
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

    # 3. Recommended Best Practice: Mermaid Architecture Diagram
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

    # 4. Mandatory Specification: Requirements tracking
    with open(os.path.join(full_path, "requirements.in"), "w") as f:
        f.write("# No external dependencies required. Standard library only.\\n")
        
    print(f"Success: Plugin '{name}' scaffolded at {full_path}")

def create_skill(name: str, path: str, description: str, iteration: int | None = None) -> None:
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Skill name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Skill name '{name}' exceeds 64 characters.")
        return
    
    if iteration:
        skill_dir = os.path.join(path, ".history", f"iteration-{iteration}", name)
    else:
        skill_dir = os.path.join(path, name)
        
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
    
    # 1. Standard Skill Frontend
    def get_template(filename: str) -> str | None:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    skill_template = get_template("SKILL.md.jinja")
    if skill_template:
        # Avoid format() errors with the literal ${{plugins}} by replacing it temporarily
        template_safe = skill_template.replace("${{", "{").replace("}}", "}")
        skill_content = template_safe.format(
            name=name,
            description=description,
            title_name=name.replace("-", " ").title(),
            plugins="${plugins}"
        )
    else:
        skill_content = f"---snip---"
        
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)
        
    # 2. Add sample reference and testing files
    with open(os.path.join(skill_dir, "CONNECTORS.md"), "w") as f:
        f.write(f"# {name} Connectors Map\n\nMap abstract `~~category` tool requirements to exact system dependencies here to keep the plugin portable.")
        
    with open(os.path.join(references_dir, "architecture.md"), "w") as f:
        f.write(f"# {name} Protocol Reference\n\nPut deep context here so it is not loaded into context implicitly.")
        
    with open(os.path.join(references_dir, "acceptance-criteria.md"), "w") as f:
        f.write(f"# Acceptance Criteria: {name}\n\nDefine at least two testable criteria or correct/incorrect operational patterns here to ensure the skill functions correctly.")

    # 3. Add Eval Set for Benchmarking Loop
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

    # 4. Recommended Best Practice: Mermaid Diagram for workflows
    mmd_content = f"""stateDiagram-v2
    [*] --> Init
    Init --> Process : Execute {name}
    Process --> [*]
    """
    with open(os.path.join(skill_dir, f"{name}-flow.mmd"), "w") as f:
        f.write(mmd_content)

    # 5. Mandatory Specification: Python Scripts over Bash/PS1
    execute_template = get_template("execute.py.jinja")
    script_content = ""
    if execute_template:
        script_content = execute_template.format(
            description=description,
            name=name
        )
    else:
        script_content = "# Template failed to load"
        
    script_path = os.path.join(scripts_dir, "execute.py")
    with open(script_path, "w") as f:
        f.write(script_content)
        
    # Make script executable
    os.chmod(script_path, 0o755)

    print(f"Success: Skill '{name}' scaffolded at {skill_dir}")

def create_hook(event: str, path: str, action_type: str) -> None:
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

    # 1. Explicit Standard Hook JSON Spec
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
        
    # 2. Reference Best Practice Schema
    schema_file = os.path.join(path, "hook-schema-reference.json")
    if not os.path.exists(schema_file):
        with open(schema_file, "w") as f:
            f.write("{\n  \"continue\": false,\n  \"stopReason\": \"\",\n  \"decision\": \"block\",\n  \"reason\": \"\"\n}")
        
    print(f"Success: Hook appended to {hooks_file}")

def create_sub_agent(name: str, path: str, desc: str) -> None:
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Sub-agent name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Sub-agent name '{name}' exceeds 64 characters.")
        return
    full_path = os.path.join(path, f"{name}.md")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    def get_template(filename: str) -> str | None:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    agent_template = get_template("agent.md.jinja")
    if agent_template:
        content = agent_template.format(
            name=name,
            description=desc
        )
    else:
        content = f"---snip---"

    with open(full_path, "w") as f:
        f.write(content)
        
    print(f"Success: Sub-agent saved to {full_path}")

def create_command(name: str, path: str, desc: str) -> None:
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Command name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Command name '{name}' exceeds 64 characters.")
        return
    full_path = os.path.join(path, f"{name}.md")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    def get_template(filename: str) -> str | None:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    cmd_template = get_template("command.md.jinja")
    if cmd_template:
        content = cmd_template.format(
            name=name,
            description=desc
        )
    else:
        content = f"---snip---"

    with open(full_path, "w") as f:
        f.write(content)
        
    print(f"Success: Command saved to {full_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Ecosystem Scaffolder CLI")
    parser.add_argument("--type", choices=["plugin", "skill", "hook", "sub-agent", "command", "mcp"], required=True, help="Type of resource to scaffold")
    parser.add_argument("--name", required=True, help="Name of the resource")
    parser.add_argument("--path", required=True, help="Destination directory path")
    parser.add_argument("--desc", default="A generated resource.", help="Description for skills or agents")
    parser.add_argument("--event", default="PreToolUse", help="Lifecycle event for hooks")
    parser.add_argument("--action", default="command", choices=["command", "prompt", "agent"], help="Hook action type")
    parser.add_argument("--iteration", type=int, help="Iteration number for safe rollback isolation (e.g., 1, 2)")
    
    args = parser.parse_args()
    
    if args.type == "plugin":
        create_plugin(args.name, args.path, args.iteration)
    elif args.type == "skill":
        create_skill(args.name, args.path, args.desc, args.iteration)
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
