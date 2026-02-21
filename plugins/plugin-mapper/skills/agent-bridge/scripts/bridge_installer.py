#!/usr/bin/env python3
"""
Plugin Bridge Installer
=======================

Installs Agent Plugins (.claude-plugin structure) into target environments.

Supported Targets:
- Antigravity (.agent/)
- GitHub Copilot (.github/)
- Gemini (.gemini/)

Usage:
  python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin <path> [--target <auto|antigravity|github|gemini>]
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

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter block from markdown. Returns (metadata_dict, body_without_frontmatter)."""
    metadata = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        fm_block = match.group(1)
        body = content[match.end():]
        # Simple key: value parse (no full YAML needed)
        for line in fm_block.splitlines():
            if ':' in line:
                key, _, value = line.partition(':')
                metadata[key.strip()] = value.strip().strip('"')
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

def detect_targets(root: Path):
    targets = []
    for name, config in TARGET_MAPPINGS.items():
        if (root / config["check"]).exists():
            targets.append(name)
    return targets

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

    # 3. Agents (bridge as sub-agent skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        agent_skills_dir = target_skills / plugin_name / "agents"
        agent_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, agent_skills_dir / f.name)
        print(f"    -> Agents: {agent_skills_dir.relative_to(root)}")

    # 4. Rules (Antigravity)
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules = root / TARGET_MAPPINGS["antigravity"]["rules"]
        target_rules.mkdir(parents=True, exist_ok=True)
        shutil.copytree(rules_dir, target_rules, dirs_exist_ok=True)
        print(f"    -> Rules: {target_rules.relative_to(root)}")

    # 3. Tools / Scripts (DEPRECATED: Direct execution from plugins/ preferred)
    # scripts_dir = plugin_path / "scripts"
    # if scripts_dir.exists():
    #     # Copy to tools/{plugin_name}/
    #     dest_tools = target_tools / plugin_name
    #     if dest_tools.exists(): shutil.rmtree(dest_tools) 
    #     # shutil.copytree(scripts_dir, dest_tools)
    #     # print(f"    -> Tools: {dest_tools.relative_to(root)} (DEPRECATED MIRROR)")

    # 4. Resources (Manifests, Prompts, Configs)
    # DEPRECATED: Resources now live in plugins/<plugin>/resources and are accessed directly.
    # No copy to tools/ needed.
    # resources_dir = plugin_path / "resources"
    # if resources_dir.exists():
    #    print(f"    -> Resources: {resources_dir.relative_to(root)} (Referenced in-place)")

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
        for f in commands_dir.rglob("*.md"):  # rglob: pick up nested subdirs
            content = f.read_text(encoding='utf-8')
            content = transform_content(content, "github")
            stem = command_output_stem(commands_dir, f, plugin_name)
            dest = target_prompts / f"{stem}.prompt.md"
            dest.write_text(content, encoding='utf-8')
            print(f"    -> Prompt: {dest.relative_to(root)}")

    # 2. Skills
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        target_skills = root / TARGET_MAPPINGS["github"]["skills"]
        target_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_dir, target_skills, dirs_exist_ok=True)
        print(f"    -> Skills: {target_skills.relative_to(root)}")

    # 3. Agents (bridge as sub-agent skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_skills_dir = root / TARGET_MAPPINGS["github"]["skills"]
        agent_skills_dir = target_skills_dir / plugin_name / "agents"
        agent_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, agent_skills_dir / f.name)
        print(f"    -> Agents: {agent_skills_dir.relative_to(root)}")

    # 4. Rules
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules = root / TARGET_MAPPINGS["github"]["rules"]
        target_rules.mkdir(parents=True, exist_ok=True)
        shutil.copytree(rules_dir, target_rules, dirs_exist_ok=True)
        print(f"    -> Rules: {target_rules.relative_to(root)}")

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

    # 4. Rules
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules = root / TARGET_MAPPINGS["gemini"]["rules"]
        target_rules.mkdir(parents=True, exist_ok=True)
        shutil.copytree(rules_dir, target_rules, dirs_exist_ok=True)
        print(f"    -> Rules: {target_rules.relative_to(root)}")


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

    # 3. Agents (bridge as sub-agent skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        target_skills_dir = root / TARGET_MAPPINGS["claude"]["skills"]
        agent_skills_dir = target_skills_dir / plugin_name / "agents"
        agent_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, agent_skills_dir / f.name)
        print(f"    -> Agents: {agent_skills_dir.relative_to(root)}")

    # 4. Rules
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        target_rules = root / TARGET_MAPPINGS["claude"]["rules"]
        target_rules.mkdir(parents=True, exist_ok=True)
        shutil.copytree(rules_dir, target_rules, dirs_exist_ok=True)
        print(f"    -> Rules: {target_rules.relative_to(root)}")

    # 5. Hooks (Claude-specific)
    install_hooks(plugin_path, root, plugin_name)

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

    # 3. Agents (bridge as sub-agent skills)
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        agent_skills_dir = target_skills / plugin_name / "agents"
        agent_skills_dir.mkdir(parents=True, exist_ok=True)
        for f in agents_dir.glob("*.md"):
            shutil.copy2(f, agent_skills_dir / f.name)
        print(f"    -> Agents: {agent_skills_dir.relative_to(root)}")

    # 4. Rules
    rules_dir = plugin_path / "rules"
    if rules_dir.exists():
        shutil.copytree(rules_dir, target_rules, dirs_exist_ok=True)
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
        else:
            # Universal Generic fallback block
            install_generic(plugin_path, root, metadata, t.lower())

    # MCP config merge (always, affects all targets)
    merge_mcp_config(plugin_path, root, metadata.get('name', plugin_path.name))

    print("Installation complete.")

if __name__ == "__main__":
    main()
