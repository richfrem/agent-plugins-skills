import argparse
import os
import json
import re

def create_plugin(name, path):
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Plugin name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    full_path = os.path.join(path, name)
    claude_plugin_dir = os.path.join(full_path, ".claude-plugin")
    
    os.makedirs(claude_plugin_dir, exist_ok=True)
    os.makedirs(os.path.join(full_path, "skills"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "agents"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "commands"), exist_ok=True)
    
    # Initialize empty hooks schema
    with open(os.path.join(full_path, "hooks.json"), "w") as f:
        f.write("[\n  // Add plugin hook definitions here\n]\n")

    # Initialize empty MCP and LSP schemas
    with open(os.path.join(full_path, "mcp.json"), "w") as f:
        f.write("{\n  \"mcpServers\": {}\n}\n")
    with open(os.path.join(full_path, "lsp.json"), "w") as f:
        f.write("{\n  \"languageServers\": {}\n}\n")
    
    # Helper function to read a template
    def get_template(filename):
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    # 1. Standard Plugin Manifest
    manifest = {
        "version": "1.0",
        "name": name,
        "author": "Generated via Agent Scaffolder",
        "description": f"The {name} plugin."
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
        
    print(f"Success: Plugin '{name}' scaffolded at {full_path}")

def create_skill(name, path, description):
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Skill name '{name}' must contain only lowercase letters, numbers, and hyphens.")
        return
    if len(name) > 64:
        print(f"Error: Skill name '{name}' exceeds 64 characters.")
        return
    
    skill_dir = os.path.join(path, name)
    scripts_dir = os.path.join(skill_dir, "scripts")
    
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    
    def get_template(filename):
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", filename)
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None

    # 1. Standard Skill Frontend
    skill_template = get_template("SKILL.md.jinja")
    if skill_template:
        # Avoid format() errors with the literal ${{CLAUDE_PLUGIN_ROOT}} by replacing it temporarily
        template_safe = skill_template.replace("${{", "{").replace("}}", "}")
        skill_content = template_safe.format(
            name=name,
            description=description,
            title_name=name.replace("-", " ").title(),
            CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
        )
    else:
        skill_content = f"---snip---"
        
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)
        
    # 2. Recommended Best Practice: README/Reference documentation
    with open(os.path.join(skill_dir, "reference.md"), "w") as f:
        f.write(f"# {name} Reference Library\n\nPut deep context, logs, and documentation here so it is not loaded into context implicitly.")
        
    # 3. Recommended Best Practice: Mermaid Diagram for workflows
    mmd_content = f"""stateDiagram-v2
    [*] --> Init
    Init --> Process : Execute {name}
    Process --> [*]
    """
    with open(os.path.join(skill_dir, f"{name}-flow.mmd"), "w") as f:
        f.write(mmd_content)

    # 4. Mandatory Specification: Python Scripts over Bash/PS1
    execute_template = get_template("execute.py.jinja")
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

def create_hook(event, path, action_type):
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

def create_sub_agent(name, path, desc):
    if not name.endswith(".md"):
        name += ".md"
        
    agent_path = os.path.join(path, name)
    os.makedirs(os.path.dirname(agent_path), exist_ok=True)
    
    content = f"""---
name: {name.replace('.md', '')}
description: {desc}
tools: [Bash, Glob, Grep, Read, Replace, Write]
---

# Sub-Agent Instructions
You are a highly capable sub-agent. Focus purely on testing or background computation based on the user's task.
"""
    with open(agent_path, "w") as f:
        f.write(content)
        
    print(f"Success: Sub-Agent scaffolded at {agent_path}")

def main():
    parser = argparse.ArgumentParser(description="Agent Ecosystem Scaffolder CLI")
    parser.add_argument("--type", choices=["plugin", "skill", "hook", "sub-agent", "mcp"], required=True, help="Type of resource to scaffold")
    parser.add_argument("--name", required=True, help="Name of the resource")
    parser.add_argument("--path", required=True, help="Destination directory path")
    parser.add_argument("--desc", default="A generated resource.", help="Description for skills or agents")
    parser.add_argument("--event", default="PreToolUse", help="Lifecycle event for hooks")
    parser.add_argument("--action", default="command", choices=["command", "prompt", "agent"], help="Hook action type")
    
    args = parser.parse_args()
    
    if args.type == "plugin":
        create_plugin(args.name, args.path)
    elif args.type == "skill":
        create_skill(args.name, args.path, args.desc)
    elif args.type == "hook":
        create_hook(args.event, args.path, args.action)
    elif args.type == "sub-agent":
        create_sub_agent(args.name, args.path, args.desc)
    elif args.type == "mcp":
        print("MCP generation requires modifying claude.json. This CLI feature is a stub.")

if __name__ == "__main__":
    main()
