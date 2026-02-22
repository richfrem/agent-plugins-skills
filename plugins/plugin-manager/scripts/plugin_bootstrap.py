#!/usr/bin/env python3
"""
plugin_bootstrap.py (CLI)
=====================================

Purpose:
    Automates the synchronization of the local plugin ecosystem with the central vendor repository.
    Handles cloning/updating the vendor source, updating local plugins, and syncing agent configurations.

Usage Examples:
    python3 plugins/plugin-manager/scripts/plugin_bootstrap.py

CLI Arguments:
    --repo          : Git repository URL (default: https://github.com/richfrem/agent-plugins-skills.git)
    --vendor-dir    : Local vendor directory (default: .vendor/agent-plugins-skills)
    --target        : Agent target for sync (default: auto)

Key Functions:
    - ensure_vendor_source(): Clones or pulls the latest vendor repository.
    - update_local_plugins(): Runs update_from_vendor.py to refresh local plugins.
    - sync_agent_configs(): Runs sync_with_inventory.py to update agent environments.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Utility to run a shell command and print output."""
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Command failed with exit code {e.returncode}")
        return False

def ensure_vendor_source(repo_url, vendor_dir):
    """Ensures the vendor repository exists and is up to date."""
    vendor_path = Path(vendor_dir).resolve()
    
    if not vendor_path.exists():
        print(f"📦 Cloning vendor repository to {vendor_dir}...")
        vendor_path.parent.mkdir(parents=True, exist_ok=True)
        return run_command(["git", "clone", repo_url, str(vendor_path)])
    else:
        print(f"🔄 Updating vendor repository at {vendor_dir}...")
        return run_command(["git", "pull"], cwd=str(vendor_path))

def update_local_plugins(script_path):
    """Runs the update_from_vendor script."""
    print("🚀 Updating local plugins from vendor source...")
    if not script_path.exists():
        print(f"❌ Error: update_from_vendor.py not found at {script_path}")
        return False
    return run_command([sys.executable, str(script_path)])

def sync_agent_configs(script_path, target):
    """Runs the sync_with_inventory script."""
    print(f"🔗 Synchronizing agent configurations (target: {target})...")
    if not script_path.exists():
        print(f"❌ Error: sync_with_inventory.py not found at {script_path}")
        return False
    return run_command([sys.executable, str(script_path), "--target", target])

def main():
    parser = argparse.ArgumentParser(description="Plugin Bootstrap Automation")
    parser.add_argument("--repo", default="https://github.com/richfrem/agent-plugins-skills.git", help="Vendor Git repository URL")
    parser.add_argument("--vendor-dir", default=".vendor/agent-plugins-skills", help="Local vendor directory")
    parser.add_argument("--target", default="auto", help="Sync target (auto, antigravity, claude, etc.)")
    args = parser.parse_args()

    project_root = Path.cwd()
    pm_scripts = project_root / "plugins" / "plugin-manager" / "scripts"
    
    update_script = pm_scripts / "update_from_vendor.py"
    sync_script = pm_scripts / "sync_with_inventory.py"

    # Phase 1: Ensure Vendor Source
    if not ensure_vendor_source(args.repo, args.vendor_dir):
        sys.exit(1)

    # Phase 2: Execute Update
    if not update_local_plugins(update_script):
        sys.exit(1)

    # Phase 3: Finalize Sync
    if not sync_agent_configs(sync_script, args.target):
        sys.exit(1)

    print("\n✅ Plugin bootstrap complete! Your ecosystem is up to date.")
    print("👉 Next steps: Use 'plugin-replicator' or 'plugin-maintenance' to manage specific plugins.")

if __name__ == "__main__":
    main()
