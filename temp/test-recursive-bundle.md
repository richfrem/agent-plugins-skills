# Agent Scaffolders Bundle Test
**Generated:** 2026-02-21 14:38:21

A recursive test of the agent-scaffolders directory.

## Index
1. `plugins/agent-scaffolders/scripts/audit.py` - Testing recursive directory generation (from plugins/agent-scaffolders/scripts)
2. `plugins/agent-scaffolders/scripts/scaffold.py` - Testing recursive directory generation (from plugins/agent-scaffolders/scripts)

---

## File: `plugins/agent-scaffolders/scripts/audit.py`
> Note: Testing recursive directory generation (from plugins/agent-scaffolders/scripts)

```python
#!/usr/bin/env python3
"""
audit.py (CLI)
=====================================

Purpose:
    Audit plugins against the Agent Skills Open Standard to ensure architectural and resource compliance.

Layer: Meta-Execution

Usage Examples:
    python3 audit.py --path <plugin-directory>

Supported Object Types:
    - .claude-plugin formatted directories
    - Agent Skills

CLI Arguments:
    --path: The absolute or relative path to the plugin directory to audit.

Input Files:
    - plugin.json
    - SKILL.md files
    - .mcp.json and hooks.json structures

Output:
    - Terminal stdout (Success/Fail metrics)
    - Warnings for minor structural deviations

Key Functions:
    - audit_plugin(): Recursively checks directory presence and constraints.

Script Dependencies:
    None

Consumed by:
    - User (CLI)
    - ecosystem-standards (Agent Skill)
"""
import argparse
import os
import json
import glob

def audit_plugin(plugin_path):
    print(f"Auditing Plugin at: {plugin_path}")
    errors = []
    warnings = []

    # 1. Check Root Structure
    claude_plugin_dir = os.path.join(plugin_path, ".claude-plugin")
    if not os.path.isdir(claude_plugin_dir):
        errors.append("Missing `.claude-plugin/` directory.")
    else:
        manifest_path = os.path.join(claude_plugin_dir, "plugin.json")
        if not os.path.isfile(manifest_path):
            errors.append("Missing `plugin.json` inside `.claude-plugin/`.")

    # 1.2. Check standard file layout
    if os.path.isfile(os.path.join(plugin_path, "mcp.json")):
        errors.append("Found `mcp.json` at root. The officially supported standard is `.mcp.json`.")
    if os.path.isfile(os.path.join(plugin_path, "hooks.json")):
        errors.append("Found `hooks.json` at root. The officially supported standard requires `hooks/hooks.json`.")

    # 1.5. Check for README
    readme_path = os.path.join(plugin_path, "README.md")
    if not os.path.isfile(readme_path):
        warnings.append("Missing root `README.md`.")
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "├──" not in content and "└──" not in content:
                warnings.append("The `README.md` is missing a file tree structure. It is highly recommended to include one.")

    # 2. Check Skills
    skills_dir = os.path.join(plugin_path, "skills")
    if os.path.isdir(skills_dir):
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if not os.path.isdir(skill_path):
                continue
            
            skill_md = os.path.join(skill_path, "SKILL.md")
            if not os.path.isfile(skill_md):
                errors.append(f"Skill '{skill_name}' is missing `SKILL.md`.")
            else:
                with open(skill_md, "r") as f:
                    lines = f.readlines()
                    if len(lines) > 500:
                        warnings.append(f"Skill '{skill_name}' SKILL.md exceeds 500 lines ({len(lines)} lines). Extract logic to scripts.")
            
            # Check for illegal bash/powershell scripts
            scripts_dir = os.path.join(skill_path, "scripts")
            if os.path.isdir(scripts_dir):
                for script_file in os.listdir(scripts_dir):
                    if script_file.endswith(".sh") or script_file.endswith(".ps1"):
                        errors.append(f"Skill '{skill_name}' contains illegal script '{script_file}'. Only Python (.py) is allowed.")
                        
            # Check for Microsoft Progressive Disclosure & Testing standard
            references_dir = os.path.join(skill_path, "references")
            if not os.path.isdir(references_dir):
                warnings.append(f"Skill '{skill_name}' is missing a `references/` directory. Progressive Disclosure is highly recommended.")
            else:
                acceptance_file = os.path.join(references_dir, "acceptance-criteria.md")
                if not os.path.isfile(acceptance_file):
                    errors.append(f"Skill '{skill_name}' is missing `references/acceptance-criteria.md`. All skills must have test criteria.")

    if errors:
        print("\n❌ AUDIT FAILED ❌")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✅ AUDIT PASSED - Fully Open Standard Compliant ✅")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    return len(errors) == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit a plugin for agent ecosystem standard compliance.")
    parser.add_argument("--path", required=True, help="Path to the plugin directory to audit")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' does not exist or is not a directory.")
        exit(1)
        
    success = audit_plugin(args.path)
    if not success:
        exit(1)
```

---

## File: `plugins/agent-scaffolders/scripts/scaffold.py`
> Note: Testing recursive directory generation (from plugins/agent-scaffolders/scripts)

```python
import argparse
import os
import json
import re

"""
scaffold.py (CLI)
=====================================

Purpose:
    Deterministically generates compliant directory architectures and boilerplate logic for Agent Skills, Plugins, Hooks, Commands, and Sub-Agents.

Layer: Meta-Execution

Usage Examples:
    python3 scaffold.py --type skill --name <skill-name> --path <output-dir> --desc "<description>"

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
    references_dir = os.path.join(skill_dir, "references")
    examples_dir = os.path.join(skill_dir, "examples")
    
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(references_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)
    
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
        
    # 2. Add sample reference and testing files
    with open(os.path.join(references_dir, "architecture.md"), "w") as f:
        f.write(f"# {name} Protocol Reference\\n\\nPut deep context here so it is not loaded into context implicitly.")
        
    with open(os.path.join(references_dir, "acceptance-criteria.md"), "w") as f:
        f.write(f"# Acceptance Criteria: {name}\\n\\nDefine at least two testable criteria or correct/incorrect operational patterns here to ensure the skill functions correctly.")
        
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
    full_path = os.path.join(path, f"{name}.md")
    
    def get_template(filename):
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

def create_command(name, path, desc):
    full_path = os.path.join(path, f"{name}.md")
    
    def get_template(filename):
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

def main():
    parser = argparse.ArgumentParser(description="Agent Ecosystem Scaffolder CLI")
    parser.add_argument("--type", choices=["plugin", "skill", "hook", "sub-agent", "command", "mcp"], required=True, help="Type of resource to scaffold")
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
    elif args.type == "command":
        create_command(args.name, args.path, args.desc)
    elif args.type == "mcp":
        print("MCP generation requires modifying claude.json. This CLI feature is a stub.")

if __name__ == "__main__":
    main()
```

---

