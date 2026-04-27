---
concept: phase-1-ensure-vendor-source
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/plugin_bootstrap.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.249984+00:00
cluster: plugin
content_hash: 1e92cb63570655c3
---

# Phase 1: Ensure Vendor Source

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Plugin Bootstrap (CLI)
======================

Purpose:
    Automates the synchronization of the local plugin ecosystem with the central vendor repository.
    Handles cloning/updating the vendor source and syncing agent configurations.

Layer: Plugin Manager / Initialization

Usage Examples:
    python3 plugins/plugin-manager/scripts/plugin_bootstrap.py

Supported Object Types:
    - None (Automation script)

CLI Arguments:
    --repo: Git repository URL (default: https://github.com/richfrem/agent-plugins-skills.git).
    --vendor-dir: Local vendor directory (default: .vendor/agent-plugins-skills).

Input Files:
    - sync_with_inventory.py (Subprocess script)

Output:
    - Clones/Updates vendor repository and triggers sync.

Key Functions:
    ensure_vendor_source(): Clones or pulls the latest vendor repository.
    sync_agent_configs(): Runs sync_with_inventory.py to update agent environments.

Script Dependencies:
    os, sys, argparse, subprocess, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/sync_with_inventory.py
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """Utility to run a shell command and print output."""
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Command failed with exit code {e.returncode}")
        return False

def ensure_vendor_source(repo_url: str, vendor_dir: str) -> bool:
    """Ensures the vendor repository exists and is up to date."""
    vendor_path = Path(vendor_dir).resolve()
    
    if not vendor_path.exists():
        print(f"📦 Cloning vendor repository to {vendor_dir}...")
        vendor_path.parent.mkdir(parents=True, exist_ok=True)
        return run_command(["git", "clone", repo_url, str(vendor_path)])
    else:
        print(f"🔄 Updating vendor repository at {vendor_dir}...")
        return run_command(["git", "pull"], cwd=str(vendor_path))

def sync_agent_configs(script_path: Path) -> bool:
    """Runs the sync_with_inventory script."""
    print("🔗 Synchronizing agent configurations...")
    if not script_path.exists():
        print(f"❌ Error: sync_with_inventory.py not found at {script_path}")
        return False
    return run_command([sys.executable, str(script_path)])

def main() -> None:
    parser = argparse.ArgumentParser(description="Plugin Bootstrap Automation")
    parser.add_argument("--repo", default="https://github.com/richfrem/agent-plugins-skills.git", help="Vendor Git repository URL")
    parser.add_argument("--vendor-dir", default=".vendor/agent-plugins-skills", help="Local vendor directory")
    args = parser.parse_args()

    project_root = Path.cwd()
    pm_scripts = project_root / "plugins" / "plugin-manager" / "scripts"
    sync_script = pm_scripts / "sync_with_inventory.py"

    # Phase 1: Ensure Vendor Source
    if not ensure_vendor_source(args.repo, args.vendor_dir):
        sys.exit(1)

    # Phase 2: Sync Plugins + Agent Configs
    if not sync_agent_configs(sync_script):
        sys.exit(1)

    print("\n✅ Plugin bootstrap complete! Your ecosystem is up to date.")
    print("👉 Next steps: Use 'plugin-replicator' or 'plugin-maintenance' to manage specific plugins.")

if __name__ == "__main__":
    main()


## See Also

- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-copilot-gpt-5-mini]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/plugin_bootstrap.py`
- **Indexed:** 2026-04-27T05:21:04.249984+00:00
