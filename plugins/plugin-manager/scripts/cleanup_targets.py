"""
Cleanup Target Directories
==========================

Purpose:
    Cleans up flattened command/workflow files from agent directories
    to prevent stale remnants during sync operations.

Layer: Plugin Manager / Maintenance

Usage Examples:
    python plugins/plugin-manager/scripts/cleanup_targets.py

Supported Object Types:
    - None (Filesystem cleanup)

CLI Arguments:
    None.

Input Files:
    - None (Scans targeted directories)

Output:
    - Deletes items in targeted directories.

Key Functions:
    clean_dir(): Cleans a directory.

Script Dependencies:
    shutil, os, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/clean_orphans.py
"""

import shutil
import os
from pathlib import Path

def clean_dir(target_dir: str) -> None:
    path = Path.cwd() / target_dir
    if not path.exists():
        print(f"Skipping {target_dir} (not found)")
        return

    print(f"Cleaning {target_dir}...")
    for item in path.iterdir():
        if item.is_dir():
            print(f"  - Removing directory: {item.name}")
            shutil.rmtree(item)

if __name__ == "__main__":
    clean_dir(".claude/commands")
    clean_dir(".gemini/commands")
    clean_dir(".github/prompts") 
