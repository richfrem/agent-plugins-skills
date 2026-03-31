#!/usr/bin/env python3
"""
Update Agent System (Master Sync)
=================================

Orchestrates the full agent system synchronization in 2 steps:

  1. Core Sync:    Spec Kitty Workflows (.windsurf -> Plugin -> Agent Envs)
  2. Extensions:  Install all Plugins (Capabilities -> Agent Environments)

Architecture Notes:
  - Step 1 runs sync_configuration.py which converts .windsurf/workflows ->
    plugins/spec-kitty-plugin/commands/ (the auto-generated layer).
  - Step 2 runs install_all_plugins.py which deploys ALL plugins (including
    the freshly synced spec-kitty-plugin) to .agents/, .claude/, .gemini/, .github/.
  - The old Kernel/Skill-sync scripts (speckit_system_bridge.py, sync_skills.py)
    have been superseded by the plugin bridge architecture.

Usage:
  python3 plugins/plugin-manager/scripts/update_agent_system.py
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path.cwd()

SPEC_KITTY_SYNC = ROOT / "plugins/spec-kitty-plugin/skills/spec-kitty-agent/scripts/sync_configuration.py"
PLUGIN_INSTALLER = ROOT / "plugins/plugin-manager/scripts/install_all_plugins.py"


def run_step(name: str, script_path: Path, args: list = []) -> None:
    """Run a subprocess step, skipping gracefully if the script is missing."""
    print(f"\n📦 [STEP] {name}")

    if not script_path.exists():
        print(f"⚠️  Skipped: Script not found: {script_path}")
        return

    print(f"   Executing: {script_path.name}...")
    try:
        cmd = [sys.executable, str(script_path)] + args
        subprocess.run(cmd, check=True)
        print(f"✅ {name} Complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {name} Failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def main() -> None:
    print("\n" + "="*80)
    print("⚠️  DEPRECATION NOTICE: This script is partially superseded by `uvx`.")
    print("For standard syncing to agents, use: `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add . --all -y`")
    print("This script remains for legacy custom syncing and structural audits.")
    print("="*80 + "\n")

    print("🚀 Starting Full Agent System Update...")
    print("=======================================")

    # Step 1: Sync Spec-Kitty Workflows (.windsurf -> Plugin Commands)
    # Converts fresh .windsurf/workflows/*.md into plugins/spec-kitty-plugin/commands/
    run_step("Spec-Kitty Workflow Sync", SPEC_KITTY_SYNC)

    # Step 2: Install All Plugins (Plugin Commands/Skills/Rules -> Agent Envs)
    # Deploys all plugins/ to .agents/, .claude/, .gemini/, .github/
    run_step("Plugin Installation (All Targets)", PLUGIN_INSTALLER)

    print("\n🎉 SYSTEM UPDATE COMPLETE")
    print("   - Spec-Kitty workflows: Synced to plugin")
    print("   - All plugins: Deployed to agent environments")
    print("\n👉 Restart your IDE / Agent to load the new configuration.")


if __name__ == "__main__":
    main()
