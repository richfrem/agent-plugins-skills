#!/usr/bin/env python3
"""
install_all_plugins.py (CLI)
=====================================

Purpose:
    Iterates through all directories in `plugins/` and runs the `bridge_installer.py` for each one 
    to orchestrate a bulk repository update, strictly using the new .agents centralized symlink pattern.

Usage Examples:
    python3 install_all_plugins.py

Script Dependencies:
    - bridge_installer.py
"""
import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

print("\n" + "="*80)
print("⚠️  DEPRECATION NOTICE: For standard consumer pipelines, use `npx skills`.")
print("To install all plugins natively from remote: `npx skills add richfrem/agent-plugins-skills`")
print("This local Python script is retained for bulk rebuilding local source plugins.")
print("="*80 + "\n")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent 
PLUGINS_ROOT = PROJECT_ROOT / "plugins"

INSTALLER_SCRIPT = SCRIPT_DIR / "bridge_installer.py"

def main():
    if not INSTALLER_SCRIPT.exists():
        print(f"❌ Error: Installer script not found at {INSTALLER_SCRIPT}")
        sys.exit(1)

    print(f"🚀 Starting Local Batch Installation mimicking `npx skills add ./plugins/`...")
    print("Flushing old .agents/ source block to ensure a clean central repo before symlinking...")
    target_agents_repo = PROJECT_ROOT / ".agents"
    if target_agents_repo.exists():
        shutil.rmtree(target_agents_repo, ignore_errors=True)
    
    plugins_processed = 0
    plugins_failed = 0
    
    # Iterate over all directories in plugins/
    for plugin_dir in sorted(PLUGINS_ROOT.iterdir()):
        if not plugin_dir.is_dir():
            continue
            
        # Skip special directories
        if plugin_dir.name.startswith(".") or plugin_dir.name.startswith("__"):
            continue
        if plugin_dir.name in ["node_modules", "venv", "env"]:
            continue
            
        print(f"\n📦 Installing Component: {plugin_dir.name}")
        
        try:
            # We use subprocess to isolate execution and ensure clean state per plugin
            cmd = [
                sys.executable, 
                str(INSTALLER_SCRIPT),
                "--plugin", str(plugin_dir)
            ]
            
            subprocess.run(cmd, check=True, text=True)
            plugins_processed += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {plugin_dir.name}")
            plugins_failed += 1
        except Exception as e:
            print(f"❌ Unexpected error installing {plugin_dir.name}: {e}")
            plugins_failed += 1

    print("\n" + "="*50)
    print(f"Batch Installation into .agents/ Complete")
    print(f"✅ Success: {plugins_processed}")
    if plugins_failed > 0:
        print(f"❌ Failed:  {plugins_failed}")
    print("="*50)

if __name__ == "__main__":
    main()
