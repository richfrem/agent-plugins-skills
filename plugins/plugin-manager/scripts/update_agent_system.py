#!/usr/bin/env python3
"""
Update Agent System (Master Sync)
=================================

This is the SINGLE command to synchronize the entire Agent System.
It orchestrates the Kernel, Core Workflows, and Plugin Capabilities.

Architecture:
  1. Kernel Sync: Rules & Monolithic Context (CLAUDE.md, etc.)
  2. Core Sync:   Spec Kitty Workflows (.windsurf -> Plugins)
  3. Extensions:  Install all Plugins (Capabilities -> Agents)
  4. Distribute:  Sync Skills to non-native agents

Usage:
  python3 plugins/plugin-manager/skills/plugin-manager/scripts/update_agent_system.py
"""

import sys
import subprocess
from pathlib import Path

# Paths to the subprocess scripts
# Use relative paths from potential run locations, but assume running from root
ROOT = Path.cwd()
KERNEL_SCRIPT = ROOT / "plugins/spec-kitty/skills/spec-kitty-agent/scripts/speckit_system_bridge.py"
CORE_SYNC_SCRIPT = ROOT / "plugins/spec-kitty/skills/spec-kitty-agent/scripts/sync_workflows.py"
# install_all_plugins.py is provided by plugin-mapper (canonical)
# plugin-manager's copy has been removed — this is the new authoritative path.
PLUGIN_INSTALLER = ROOT / "plugins/plugin-mapper/skills/agent-bridge/scripts/install_all_plugins.py"
SKILL_SYNC_SCRIPT = ROOT / "plugins/spec-kitty/skills/spec-kitty-agent/scripts/sync_skills.py"

def run_step(name, script_path, args=[]):
    print(f"\n📦 [STEP] {name}")
    
    if not script_path.exists():
        print(f"⚠️  Skipped: Script not found: {script_path}")
        return

    print(f"   Executing: {script_path.name}...")
    try:
        # Pass current environment to subprocess
        cmd = [sys.executable, str(script_path)] + args
        subprocess.run(cmd, check=True)
        print(f"✅ {name} Complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {name} Failed with exit code {e.returncode}")
        # Fail fast
        sys.exit(e.returncode)

def main():
    print("🚀 Starting Full Agent System Update...")
    print("=======================================")

    # 1. Kernel Sync (Rules, Config, Context Gen)
    # This prepares the groundwork (CLAUDE.md, etc.)
    run_step("Kernel Sync (Rules)", KERNEL_SCRIPT)

    # 2. Core Workflow Sync (Windsurf -> Plugins)
    # This grabs the latest Spec Kitty workflows
    run_step("Core Workflow Sync", CORE_SYNC_SCRIPT)

    # 3. Plugin Installation (Capabilities -> Agents)
    # This deploys all plugins (including Spec Kitty workflows)
    run_step("Plugin Installation (Capabilities)", PLUGIN_INSTALLER)

    # 4. Skill Distribution (Final Mile)
    # This copies skills from .agent/skills to .claude/.github
    run_step("Skill Distribution", SKILL_SYNC_SCRIPT, ["--all"])

    print("\n🎉 SYSTEM UPDATE COMPLETE")
    print("   - Rules: Synced")
    print("   - Context: Generated (CLAUDE.md, etc.)")
    print("   - Workflows: Installed")
    print("   - Skills: Distributed")
    print("\n👉 Please Restart your IDE / Agent to load the new configuration.")

if __name__ == "__main__":
    main()
