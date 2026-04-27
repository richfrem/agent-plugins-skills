---
concept: initialize-empty-hooks-schema-in-a-nested-hooks-dir
source: plugin-code
source_file: agent-scaffolders/scripts/scaffold.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.213281+00:00
cluster: path
content_hash: a4b7431f2d878fa5
---

# Initialize empty hooks schema in a nested hooks/ dir

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/scaffold.py -->
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
  

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-docker-skill/scripts/scaffold.py -->
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
    - Jinja templates 

*(combined content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]
- [[1-initialize-client]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[agent-agentic-os-hooks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/scaffold.py`
- **Indexed:** 2026-04-27T05:21:04.213281+00:00
