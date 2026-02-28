#!/usr/bin/env python3
"""
bridge_installer.py (CLI)
=====================================

Purpose:
    Installs Agent Plugins (.claude-plugin structure) into target environments dynamically (e.g., .claude, .gemini, .agent, .github).

Layer: System Integration Layer

Usage Examples:
    python3 bridge_installer.py --plugin <path> [--target <auto|antigravity|github|gemini>]

Supported Object Types:
    - .claude-plugin directory structures
    - Markdown commands, skills, and agents
    - .mcp.json and hooks.json manifests

CLI Arguments:
    --plugin: Absolute or relative path to the plugin folder to install.
    --target: (Optional) Specific agent environment subset to install into. Defaults to "auto".

Input Files:
    - Target `plugin.json` for validation and namespace.

Output:
    - Copies formatted skills, rules, and commands directly into the active Agent IDE configuration folders.

Key Functions:
    - parse_frontmatter(): Isolates YAML from execution strings.
    - command_output_stem(): Builds flattened names.
    - install_{target}(): Specialized mapping strategies per ecosystem.

Script Dependencies:
    None

Consumed by:
    - User (CLI)
    - install_all_plugins.py
    - agent-bridge (Agent Skill)
"""

import os
import sys
import shutil
import json
import re
import argparse
from pathlib import Path

# --- Constants ---

TARGET_MAPPINGS = {
    "antigravity": {
        "check": ".agent",
        "workflows": ".agent/workflows",
        "skills": ".agent/skills",
        "rules": ".agent/rules",
        "tools": "tools"
    },
    "github": {
        "check": ".github",
        "workflows": ".github/prompts",
        "agents": ".github/agents",
        "github_workflows": ".github/workflows",
        "skills": ".github/skills",
        "instructions": ".github/copilot-instructions.md",
        "rules": ".github/rules"
    },
    "gemini": {
        "check": ".gemini",
        "workflows": ".gemini/commands",
        "skills": ".gemini/skills",
        "rules": ".gemini/rules"
    },
    "claude": {
        "check": ".claude",
        "commands": ".claude/commands",
        "skills": ".claude/skills",
        "rules": ".claude/rules"
    },
    "azure": {
        "check": ".azure",
        "skills": ".azure/skills",
        "agents": ".azure/agents"
    }
}

# --- Core Logic ---

def merge_mcp_config(plugin_path: Path, root: Path, plugin_name: str):
    """Merge plugin .mcp.json servers into the root .mcp.json.
    Creates root .mcp.json if it doesn't exist."""
    plugin_mcp = plugin_path / ".mcp.json"
    if not plugin_mcp.exists():
        return
    try:
        plugin_data = json.loads(plugin_mcp.read_text(encoding='utf-8'))
        plugin_servers = plugin_data.get('mcpServers', {})
        if not plugin_servers:
            return

        root_mcp = root / ".mcp.json"
        if root_mcp.exists():
            root_data = json.loads(root_mcp.read_text(encoding='utf-8'))
        else:
            root_data = {'mcpServers': {}}

        existing_servers = root_data.setdefault('mcpServers', {})
        added = []
        for server_name, config in plugin_servers.items():
            if server_name not in existing_servers:
                existing_servers[server_name] = config
                added.append(server_name)

        root_mcp.write_text(json.dumps(root_data, indent=2), encoding='utf-8')
        if added:
            print(f"    -> MCP: Merged servers {added} into {root_mcp.name}")
        else:
            print(f"    -> MCP: All servers already registered in {root_mcp.name}")
    except Exception as e:
        print(f"    -> MCP: Warning — could not merge .mcp.json: {e}")

def install_hooks(plugin_path: Path, root: Path, plugin_name: str):
    """Copy hooks/hooks.json to .claude/hooks/{plugin-name}-hooks.json.
    Hooks are Claude Code-specific; non-Claude targets are notified via a comment."""
    hooks_file = plugin_path / "hooks" / "hooks.json"
    if not hooks_file.exists():
        return
    
    target_hooks_dir = root / ".claude" / "hooks"
    target_hooks_dir.mkdir(parents=True, exist_ok=True)
    dest = target_hooks_dir / f"{plugin_name}-hooks.json"
    shutil.copy2(hooks_file, dest)
    print(f"    -> Hooks: {dest.relative_to(root)} (Claude only — review before activating)")

def parse_frontmatter(content: str) -> tuple[dict[str, str | list[str]], str]:
    """Parse YAML frontmatter block from markdown. Returns (metadata_dict, body_without_frontmatter)."""
    metadata: dict[str, str | list[str]] = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        fm_block = str(match.group(1))
        body = content[match.end():]
        # Simple key: value parse (no full YAML needed)
        for line in fm_block.splitlines():
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip().strip('"')

                # Check if it's an array syntax like ["github", "gemini"]
                if value.startswith('[') and value.endswith(']'):
                    inner = value[1:len(value) - 1]
                    items = inner.split(',')
                    metadata[key] = [item.strip().strip('"').strip("'") for item in items]
                else:
                    metadata[key] = value
        return metadata, body
    return metadata, content

def command_output_stem(commands_dir: Path, f: Path, plugin_name: str) -> str:
    """Build flat output filename from potentially nested command path.
    e.g. commands/refactor/extract.md -> plugin-name_refactor_extract"""
    try:
        rel = f.relative_to(commands_dir)
    except ValueError:
        rel = Path(f.name)
    parts = list(rel.parts)
    # Drop .md suffix on last part
    parts[-1] = Path(parts[-1]).stem
    return plugin_name + '_' + '_'.join(parts)

def transform_content(content: str, target_agent: str) -> str:
    """Transforms content for specific target agents."""
    # 1. Actor Swapping
    # Replace default actor with target
    if target_agent == "antigravity":
        content = content.replace('--actor "windsurf"', '--actor "antigravity"')
        content = content.replace('--actor "claude"', '--actor "antigravity"')
    elif target_agent == "github":
        content = content.replace('--actor "windsurf"', '--actor "copilot"')
        content = content.replace('--actor "claude"', '--actor "copilot"')
    elif target_agent == "gemini":
        content = content.replace('--actor "windsurf"', '--actor "gemini"')
        content = content.replace('--actor "claude"', '--actor "gemini"')
        content = content.replace('$ARGUMENTS', '{{args}}') # Gemini argument syntax
    elif target_agent == "claude":
        content = content.replace('--actor "windsurf"', '--actor "claude"')
        # No change needed if already "claude"

    return content

def transform_rule(content: str) -> str:
    """Strips Cursor-specific <rule> XML frontmatter from MDC files."""
    # Look for a <rule>...</rule> block at the very start of the file
    match = re.search(r"^<rule>\s*.*?</rule>\s*", content, re.DOTALL | re.IGNORECASE)
    if match:
        content = content[match.end():]
    return content

def detect_targets(root: Path):
    targets = []
    for name, config in TARGET_MAPPINGS.items():
        if (root / config["check"]).exists():
            targets.append(name)
    return targets

def build_rule_block(rules_dir: Path, plugin_name: str) -> str:
    """Compiles rules from MDC files into a monolithic block."""
    if not rules_dir.exists():
        return ""
        
    other_rules = []
    constitution = ""
    
    for f in rules_dir.glob("*"):
        if f.is_file():
            content = f.read_text(encoding='utf-8')
            content = transform_rule(content)
            
            # Special case for constitution as the primary project driver
            if f.stem.lower() == "constitution":
                constitution = f"## Constitution ({plugin_name})\n\n{content}\n\n---\n\n"
            else:
                other_rules.append(f"\n\n--- RULE: {f.stem} ({plugin_name}) ---\n\n{content}")
                
    rules_body = "".join(other_rules)
    if not constitution and not rules_body:
        return ""
        
    marker_start = f"<!-- BEGIN RULES FROM PLUGIN: {plugin_name} -->"
    marker_end = f"<!-- END RULES FROM PLUGIN: {plugin_name} -->"
    
    block = f"\n\n{marker_start}\n# SHARED RULES FROM {plugin_name}\n"
    block += constitution
    block += rules_body
    block += f"\n{marker_end}\n"
    
    return block

def append_monolithic_rules(target_file: Path, block: str, header: str):
    """Safely appends a rule block to a monolithic instructions file."""
    if not block:
        return
        
    if target_file.exists():
        content = target_file.read_text(encoding='utf-8')
    else:
        content = header
        
    # Overwrite if block block from the same plugin exists
    # Simple strategy: just append for now, but a robust version would Regex replace between markers.
    content += block
    target_file.write_text(content, encoding='utf-8')

# --- Installers ---

def install_antigravity(plugin_path: Path, root: Path, metadata: dict):
    print("  [Antigravity] Installing...")
    target_wf = root / TARGET_MAPPINGS["antigravity"]["workflows"]
    target_skills = root / TARGET_MAPPINGS["antigravity"]["skills"]
    target_tools = root / TARGET_MAPPINGS["antigravity"]["tools"]

    target_wf.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)
    target_tools.mkdir(parents=True, exist_ok=True)

    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Workflows (Commands)
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        commands_dir = plugin_path / "workflows"
        
    if commands_dir.exists():
        plugin_wf_dir = target_wf / plugin_name
        plugin_wf_dir.mkdir(parents=True, exist_ok=True)
        for f in commands_dir.rglob("*.md"):  # rglob: pick up nested subdirs
            content = f.read_text(encoding='utf-8')
            content = transform_content(content, "antigravity")
            stem = command_output_stem(commands_dir, f, plugin_name)
            dest = plugin_wf_dir / f"{stem}.md"
            dest.write_text(content, encoding='utf-8')
            print(f"    -> Workflow: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as progressive disclosure skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            agent_name = f.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"
            agent_dir = target_skills / final_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, agent_dir / "SKILL.md")
        print(f"    -> Agents (as Skills): {target_skills.relative_to(root)}")

    # 4. Rules (Antigravity natively supports .agent/rules/ directories)
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules = root / TARGET_MAPPINGS["antigravity"]["rules"]
        target_rules.mkdir(parents=True, exist_ok=True)
        for f in rules_dir.glob("*"):
            if f.is_file():
                content = f.read_text(encoding='utf-8')
                content = transform_rule(content)
                # Ensure it saves as .md
                dest = target_rules / (f.stem + ".md")
                dest.write_text(content, encoding='utf-8')
        print(f"    -> Rules: {target_rules.relative_to(root)}")

def install_github(plugin_path: Path, root: Path, metadata: dict):
    print("  [GitHub] Installing...")
    target_prompts = root / TARGET_MAPPINGS["github"]["workflows"]
    target_prompts.mkdir(parents=True, exist_ok=True)

    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Workflows -> Prompts
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        commands_dir = plugin_path / "workflows"
        
    if commands_dir.exists():
        import yaml
        for f in commands_dir.rglob("*.md"):  # rglob: pick up nested subdirs
            raw_content = f.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(raw_content)
            
            # STRICT OPT-IN FOR GITHUB MODELS
            # Most IDE commands are useless in GitHub CI/CD, so we drop them by default.
            export_flag = fm.get('github-model-export', 'false')
            if str(export_flag).lower() not in ['true', 'yes', '1']:
                print(f"    -> Prompt: Skipped {f.relative_to(root)} (Missing 'github-model-export: true' in frontmatter)")
                continue

            content = transform_content(body, "github")
            stem = command_output_stem(commands_dir, f, plugin_name)
            
            # Construct GitHub Models Prompt Structure (.prompt.yml)
            prompt_data = {
                "name": fm.get("name", stem).replace('_', ' ').title(),
                "description": fm.get("description", f"Command generated from {plugin_name}"),
                "model": fm.get("model", "openai/gpt-4o"),
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a specialized AI agent executing a workflow. Follow the instructions precisely."
                    },
                    {
                        "role": "user",
                        "content": content.strip()
                    }
                ]
            }
            
            dest = target_prompts / f"{stem}.prompt.yml"
            dest.write_text(yaml.dump(prompt_data, sort_keys=False), encoding='utf-8')
            print(f"    -> Prompt: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        target_skills = root / TARGET_MAPPINGS["github"]["skills"]
        target_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as progressive disclosure skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_skills_dir = root / TARGET_MAPPINGS["github"]["skills"]
        target_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            agent_name = f.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"
            agent_dir = target_skills_dir / final_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, agent_dir / "SKILL.md")
        print(f"    -> Agents (as Skills): {target_skills_dir.relative_to(root)}")

    # 4. GitHub Workflows -> .github/workflows/ (CI/CD YAML runners)
    github_wf_dir = plugin_path / "github_workflows"
    if github_wf_dir.exists():
        target_wf_dir = root / TARGET_MAPPINGS["github"]["github_workflows"]
        target_wf_dir.mkdir(parents=True, exist_ok=True)
        for f in github_wf_dir.glob("*.yml"):
            shutil.copy2(f, target_wf_dir / f.name)
            print(f"    -> Workflow: {(target_wf_dir / f.name).relative_to(root)}")

    # 5. Monolithic Rules (copilot-instructions.md)
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules_file = root / TARGET_MAPPINGS["github"]["instructions"]
        target_rules_file.parent.mkdir(parents=True, exist_ok=True)
        block = build_rule_block(rules_dir, plugin_name)
        append_monolithic_rules(target_rules_file, block, "# Copilot Instructions\n> Auto-generated by Agent Bridge Plugin Mapper.\n\n")
        print(f"    -> Rules: Appended to {target_rules_file.relative_to(root)}")

def install_gemini(plugin_path: Path, root: Path, metadata: dict):
    print("  [Gemini] Installing...")
    target_cmds = root / TARGET_MAPPINGS["gemini"]["workflows"]
    target_cmds.mkdir(parents=True, exist_ok=True)

    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Workflows -> TOML Commands
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        commands_dir = plugin_path / "workflows"
        
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):  # rglob: pick up nested subdirs
            raw_content = f.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(raw_content)  # Extract frontmatter
            description = fm.get('description', 'Imported from plugin')
            body = transform_content(body, "gemini")
            stem = command_output_stem(commands_dir, f, plugin_name)
            cmd_name = stem.replace(plugin_name + '_', '', 1).replace('_', ':')
            toml_content = f'command = "{plugin_name}:{cmd_name}"\ndescription = "{description}"\nprompt = """\n{body}\n"""'
            dest = target_cmds / f"{stem}.toml"
            dest.write_text(toml_content, encoding='utf-8')
            print(f"    -> Command: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        target_skills = root / TARGET_MAPPINGS["gemini"]["skills"]
        target_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as sub-agent skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_skills_dir = root / TARGET_MAPPINGS["gemini"]["skills"]
        agent_skills_dir = target_skills_dir / plugin_name / "agents"
        agent_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, agent_skills_dir / f.name)
        print(f"    -> Agents: {agent_skills_dir.relative_to(root)}")

    # 4. Monolithic Rules (GEMINI.md)
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules_file = root / "GEMINI.md"
        block = build_rule_block(rules_dir, plugin_name)
        append_monolithic_rules(target_rules_file, block, "# Gemini CLI Instructions\n> Auto-generated by Agent Bridge Plugin Mapper.\n\n")
        print(f"    -> Rules: Appended to {target_rules_file.relative_to(root)}")

def install_claude(plugin_path: Path, root: Path, metadata: dict):
    print("  [Claude] Installing...")
    target_cmds = root / TARGET_MAPPINGS["claude"]["commands"]
    target_cmds.mkdir(parents=True, exist_ok=True)

    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Workflows (Commands)
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        commands_dir = plugin_path / "workflows"
        
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):  # rglob: pick up nested subdirs
            content = f.read_text(encoding='utf-8')
            content = transform_content(content, "claude")
            stem = command_output_stem(commands_dir, f, plugin_name)
            dest = target_cmds / f"{stem}.md"
            dest.write_text(content, encoding='utf-8')
            print(f"    -> Command: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        target_skills = root / TARGET_MAPPINGS["claude"]["skills"]
        target_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as progressive disclosure skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_skills_dir = root / TARGET_MAPPINGS["claude"]["skills"]
        target_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            agent_name = f.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"
            agent_dir = target_skills_dir / final_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, agent_dir / "SKILL.md")
        print(f"    -> Agents (as Skills): {target_skills_dir.relative_to(root)}")

    # 4. Monolithic Rules (CLAUDE.md)
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules_file = root / "CLAUDE.md"
        block = build_rule_block(rules_dir, plugin_name)
        append_monolithic_rules(target_rules_file, block, "# Claude Assistant Instructions\n> Auto-generated by Agent Bridge Plugin Mapper.\n\n")
        print(f"    -> Rules: Appended to {target_rules_file.relative_to(root)}")

    # 5. Hooks (Claude-specific)
    install_hooks(plugin_path, root, plugin_name)

def install_azure(plugin_path: Path, root: Path, metadata: dict):
    print("  [Azure] Installing...")
    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        target_skills = root / TARGET_MAPPINGS["azure"]["skills"]
        target_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 2. Agents
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_agents_dir = root / TARGET_MAPPINGS["azure"]["agents"]
        target_agents_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, target_agents_dir / f.name)
        print(f"    -> Agents: {target_agents_dir.relative_to(root)}")

def install_generic(plugin_path: Path, root: Path, metadata: dict, target_name: str):
    print(f"  [{target_name.capitalize()}] Installing generic mapped target...")
    
    # Generic target directories map to standard markdown workflows/skills logic
    target_dir = root / f".{target_name}"
    target_wf = target_dir / "commands"
    target_skills = target_dir / "skills"
    target_rules = target_dir / "rules"

    target_wf.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)
    target_rules.mkdir(parents=True, exist_ok=True)

    plugin_name = metadata.get("name", plugin_path.name)

    # 1. Workflows (Commands)
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        commands_dir = plugin_path / "workflows"
        
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):
            content = f.read_text(encoding='utf-8')
            content = transform_content(content, target_name)
            stem = command_output_stem(commands_dir, f, plugin_name)
            dest = target_wf / f"{stem}.md"
            dest.write_text(content, encoding='utf-8')
            print(f"    -> Command: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as progressive disclosure skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            agent_name = f.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"
            agent_dir = target_skills / final_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, agent_dir / "SKILL.md")
        print(f"    -> Agents (as Skills): {target_skills.relative_to(root)}")

    # 4. Rules
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        for f in rules_dir.glob("*"):
            if f.is_file():
                content = f.read_text(encoding='utf-8')
                content = transform_rule(content)
                dest = target_rules / (f.stem + ".md")
                dest.write_text(content, encoding='utf-8')
        print(f"    -> Rules: {target_rules.relative_to(root)}")

def main():
    parser = argparse.ArgumentParser(description="Plugin Bridge Installer")
    parser.add_argument("--plugin", required=True, help="Path to plugin directory")
    parser.add_argument("--target", default="auto", help="Target environment (e.g., auto, antigravity, claude, cursor, roo, OpenHands)")
    args = parser.parse_args()

    plugin_path = Path(args.plugin).resolve()
    if not plugin_path.exists():
        print(f"Error: Plugin path not found: {plugin_path}")
        sys.exit(1)

    # Read Metadata
    manifest = plugin_path / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        metadata = json.loads(manifest.read_text(encoding='utf-8'))
    else:
        metadata = {"name": plugin_path.name}

    root = Path.cwd()
    targets = []
    
    if args.target == "auto":
        targets = detect_targets(root)
        if not targets:
            print("Error: No compatible environments detected.")
            print("Create one or more target directories first:")
            print("  mkdir .agent .github .gemini .claude")
            print("Then re-run the bridge installer.")
            sys.exit(1)
    else:
        targets = [args.target]

    print(f"Installing plugin '{metadata['name']}' to: {', '.join(targets)}")

    for t in targets:
        # Standard complex parsers
        if t == "antigravity":
            install_antigravity(plugin_path, root, metadata)
        elif t == "github":
            install_github(plugin_path, root, metadata)
        elif t == "gemini":
            install_gemini(plugin_path, root, metadata)
        elif t == "claude":
            install_claude(plugin_path, root, metadata)
        elif t == "azure" or t == "azure-foundry":
            install_azure(plugin_path, root, metadata)
        else:
            # Universal Generic fallback block
            install_generic(plugin_path, root, metadata, t.lower())

    # MCP config merge (always, affects all targets)
    merge_mcp_config(plugin_path, root, metadata.get('name', plugin_path.name))

    print("Installation complete.")

if __name__ == "__main__":
    main()
