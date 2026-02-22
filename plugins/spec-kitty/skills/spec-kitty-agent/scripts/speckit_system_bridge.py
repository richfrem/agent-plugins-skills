#!/usr/bin/env python3
"""
speckit_system_bridge.py
=====================================
Purpose:
    The "Universal Bridge" Synchronization Engine.
    Reads Spec Kitty definitions (Windsurf + Memory) and projects them into native
    configurations for:
    1.  Antigravity (.agent/)
    2.  Claude (.claude/)
    3.  Gemini (.gemini/)
    4.  GitHub Copilot (.github/)

    Philosophy:
    "Bring Your Own Agent" (BYOA). Maintain a Single Source of Truth in Spec Kitty,
    and auto-generate the necessary config files for any supported agent.

Usage:
    python plugins/spec-kitty/speckit_system_bridge.py
"""
import os
import shutil
from pathlib import Path
import re
import sys
import toml
import yaml

# Force UTF-8 for Windows Consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
WINDSURF_DIR = PROJECT_ROOT / ".windsurf"
KITTIFY_DIR = PROJECT_ROOT / ".kittify"

# Targets
AGENT_DIR = PROJECT_ROOT / ".agent"
CLAUDE_DIR = PROJECT_ROOT / ".claude"
GEMINI_DIR = PROJECT_ROOT / ".gemini"
GITHUB_DIR = PROJECT_ROOT / ".github"

# Markers for Rule Injection
MARKER_START = "<!-- RULES_SYNC_START -->"
MARKER_END = "<!-- RULES_SYNC_END -->"


def setup_directories():
    """Ensure all target directory structures exist and are clean (Idempotency)."""
    print(f"🔧 Initializing & Cleaning Target Directories...")
    
    # 1. Antigravity
    (AGENT_DIR / "rules").mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / "workflows").mkdir(parents=True, exist_ok=True)
    
    # 2. Claude
    (CLAUDE_DIR / "commands").mkdir(parents=True, exist_ok=True)
    
    # 3. Gemini
    (GEMINI_DIR / "commands").mkdir(parents=True, exist_ok=True)
    
    # 4. Copilot
    (GITHUB_DIR / "prompts").mkdir(parents=True, exist_ok=True)


def ingest_rules():
    """Read rules from .kittify/memory (Source of Truth via Symlink)."""
    rules = {}
    memory_dir = KITTIFY_DIR / "memory"
    agent_rules_dir = AGENT_DIR / "rules"
    
    # Ensure memory dir exists
    memory_dir.mkdir(parents=True, exist_ok=True)

    # SPECIAL HANDLING: constitution.md
    # Source: .agent/rules/constitution.md
    # Target: .kittify/memory/constitution.md (Symlink/Copy)
    constitution_src = agent_rules_dir / "constitution.md"
    constitution_tgt = memory_dir / "constitution.md"

    if constitution_src.exists():
        try:
            # tailored logic: link if possible, copy if not (Windows fallback)
            if constitution_tgt.exists():
                if constitution_tgt.is_symlink() or constitution_tgt.stat().st_mtime != constitution_src.stat().st_mtime:
                    constitution_tgt.unlink()
            
            # FORCE COPY: Symlinks cause issues in GitHub Actions/CI
            shutil.copy2(constitution_src, constitution_tgt)
            print(f"📄 Copied constitution.md: .agent -> .kittify")
        except Exception as e:
            print(f"⚠️  Failed to copy constitution.md: {e}")

    if not memory_dir.exists():
        print("⚠️  No .kittify/memory directory found. Rules will be empty.")
        return rules
        
    for rule_file in sorted(memory_dir.rglob("*.md")):
        try:
            content = rule_file.read_text(encoding="utf-8")
            rules[rule_file.stem] = content
        except Exception as e:
            print(f"⚠️  Failed to read rule {rule_file.name}: {e}")
            
    return rules

def ingest_workflows():
    """Read workflows from .windsurf/workflows (Source of Truth)."""
    workflows = {}
    source_dir = WINDSURF_DIR / "workflows"
    
    if not source_dir.exists():
        print("⚠️  No .windsurf/workflows directory found. Workflows will be empty.")
        return workflows
        
    for wf_file in sorted(source_dir.rglob("*.md")):
        try:
            content = wf_file.read_text(encoding="utf-8")
            workflows[wf_file.name] = content # Key is full filename (spec-kitty.accept.md)
        except Exception as e:
            print(f"⚠️  Failed to read workflow {wf_file.name}: {e}")
            
    return workflows

def sync_antigravity(workflows, rules):
    """Sync to .agent/ (Antigravity)."""
    print("\n🔵 Syncing Antigravity (.agent)...")
    
    # Rules (e.g., constitution.md)
    # SPECIAL HANDLING: Do NOT overwrite constitution.md in .agent/rules/
    # because it is now key Source of Truth.
    for name, content in rules.items():
        if name == "constitution":
            continue # SKIP overwriting the source
        (AGENT_DIR / "rules" / f"{name}.md").write_text(content, encoding="utf-8")
        
    print(f"   ✅ Synced {len(rules)-1 if 'constitution' in rules else len(rules)} rules (skipped constitution).")
    print(f"   ℹ️  Workflows are now managed by Plugin Manager (run install_all_plugins.py).")

def sync_claude(workflows, rules):
    """Sync to .claude/."""
    print("\n🟠 Syncing Claude (.claude)...")
    
    # 1. Context (CLAUDE.md)
    # 1. Context (CLAUDE.md)
    # Target Project Root for CLAUDE.md so it is auto-detected by Claude Desktop/CLI
    claude_md = PROJECT_ROOT / "CLAUDE.md"
    
    # Separate Constitution from other rules
    constitution = rules.get("constitution", "")
    other_rules = []
    for name, content in rules.items():
        if name != "constitution":
            other_rules.append(f"\n\n--- RULE: {name}.md ---\n\n{content}")
    
    rules_block = "".join(other_rules)
    
    header = "# Claude Assistant Instructions\nManaged by Spec Kitty Bridge.\n\n"
    constitution_section = f"## Constitution\n\n{constitution}\n\n---\n\n" if constitution else ""
    shared_rules_block = f"\n\n{MARKER_START}\n# SHARED RULES FROM .agent/rules/\n{rules_block}\n{MARKER_END}"
    
    # Write monolithic file
    claude_md.write_text(header + constitution_section + shared_rules_block, encoding="utf-8")
    
    print(f"   ✅ Generated CLAUDE.md.")
    print(f"   ℹ️  Commands are now managed by Plugin Manager.")

def sync_gemini(workflows, rules):
    """Sync to .gemini/."""
    print("\n✨ Syncing Gemini (.gemini)...")
    
    # 1. Context (GEMINI.md)
    root_gemini_md = PROJECT_ROOT / "GEMINI.md"
    
    # Separate Constitution from other rules
    constitution = rules.get("constitution", "")
    other_rules = []
    for name, content in rules.items():
        if name != "constitution":
            other_rules.append(f"\n\n--- RULE: {name}.md ---\n\n{content}")
    
    rules_block = "".join(other_rules)
    
    header = "# Gemini CLI Instructions\nManaged by Spec Kitty Bridge.\n\n"
    constitution_section = f"## Constitution\n\n{constitution}\n\n---\n\n" if constitution else ""
    shared_rules_block = f"\n\n{MARKER_START}\n# SHARED RULES FROM .agent/rules/\n{rules_block}\n{MARKER_END}"
    
    root_gemini_md.write_text(header + constitution_section + shared_rules_block, encoding="utf-8")
    
    print(f"   ✅ Generated GEMINI.md.")
    print(f"   ℹ️  Commands are now managed by Plugin Manager.")

def sync_copilot(workflows, rules):
    """Sync to .github/ (Copilot)."""
    print("\n🤖 Syncing Copilot (.github)...")

    # 1. Instructions (copilot-instructions.md)
    instr_file = GITHUB_DIR / "copilot-instructions.md"

    # Separate Constitution from other rules
    constitution = rules.get("constitution", "")
    other_rules = []
    for name, content in rules.items():
        if name != "constitution":
            other_rules.append(f"\n\n--- RULE: {name}.md ---\n\n{content}")
    
    rules_block = "".join(other_rules)

    header = "# Copilot Instructions\n> Managed by Spec Kitty Bridge.\n\n"
    constitution_section = f"## Constitution\n\n{constitution}\n\n---\n\n" if constitution else ""
    
    # Index Workflows
    workflow_index = "\n# Available Workflows\n"
    for filename in workflows.keys():
        stem = filename.replace(".md", "")
        workflow_index += f"- /prompts/{stem}.prompt.md\n"

    shared_rules_block = f"\n\n{MARKER_START}\n# SHARED RULES FROM .agent/rules/\n{rules_block}\n{MARKER_END}"

    instr_file.write_text(header + constitution_section + workflow_index + shared_rules_block, encoding="utf-8")

    print(f"   ✅ Generated copilot-instructions.md.")
    print(f"   ℹ️  Prompts are now managed by Plugin Manager.")

def update_kittify_config():
    """Update .kittify/config.yaml to register all synced agents."""
    print("\n⚙️  Updating .kittify/config.yaml...")

    config_file = KITTIFY_DIR / "config.yaml"

    # Define all agents that the bridge supports
    all_agents = ["windsurf", "claude", "antigravity", "gemini", "copilot"]

    try:
        # Read existing config
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        # Ensure agents section exists
        if 'agents' not in config:
            config['agents'] = {}

        # Update available agents list (preserve order, add new ones)
        current_agents = config['agents'].get('available', [])
        updated_agents = []

        # Keep existing agents in their order
        for agent in current_agents:
            if agent in all_agents:
                updated_agents.append(agent)

        # Add any missing agents
        for agent in all_agents:
            if agent not in updated_agents:
                updated_agents.append(agent)

        config['agents']['available'] = updated_agents

        # Ensure selection section exists with defaults if not present
        if 'selection' not in config['agents']:
            config['agents']['selection'] = {
                'strategy': 'preferred',
                'preferred_implementer': 'claude',
                'preferred_reviewer': 'claude'
            }

        # Write back to file
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"   ✅ Registered {len(updated_agents)} agents: {', '.join(updated_agents)}")

    except Exception as e:
        print(f"   ⚠️  Failed to update config.yaml: {e}")
        print(f"   💡 You may need to manually add agents to .kittify/config.yaml")

def main():
    print("🚀 Starting Spec Kitty Bridge Sync...")

    setup_directories()

    # 1. Ingest Source (Spec Kitty)
    rules = ingest_rules()
    workflows = ingest_workflows()

    if not workflows and not rules:
        print("❌ No source data found in .windsurf or .kittify. Run 'spec-kitty init' first.")
        return

    # 2. Project to All Agents
    sync_antigravity(workflows, rules)
    sync_claude(workflows, rules)
    sync_gemini(workflows, rules)
    sync_copilot(workflows, rules)

    # 3. Update Kittify Config to Register All Agents
    update_kittify_config()

    print("\n🎉 Bridge Sync Complete. All agents are configured.")

if __name__ == "__main__":
    main()
