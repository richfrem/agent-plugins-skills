#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/standardize_manifests.py (CLI)
=====================================

Purpose:
    Ensures all base context-bundler manifests have a consistent structure by inserting the Context Bundler System Prompt as the first file entry. Iterates through base-*-file-manifest.json files and reorders entries as needed.

Layer: Curate / Curate

Usage Examples:
    python [SKILL_ROOT]/scripts/standardize_manifests.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - update_manifests(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
MANIFEST_DIR = PROJECT_ROOT / "plugins" / "context-bundler" / "resources" / "base-manifests"
PROMPT_ENTRY = {
    "path": "plugins/ai-resources/prompts/extraction/Context_Bundler_System_Prompt.md",
    "note": "Context Bundler Instructions (System Prompt)"
}

def update_manifests():
    for manifest_path in MANIFEST_DIR.glob("base-*-file-manifest.json"):
        if manifest_path.name == "base-generic-file-manifest.json":
            continue # Already done
        
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if prompt entry already exists
            exists = False
            for f in data.get("files", []):
                if f["path"] == PROMPT_ENTRY["path"]:
                    exists = True
                    break
            
            if not exists:
                # Insert at index 0
                data["files"].insert(0, PROMPT_ENTRY)
                print(f"Updated {manifest_path.name}")
                
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            else:
                 # Ensure it is at index 0?
                 # If it exists but not at 0, move it?
                 # ideally yes for consistency
                 if data["files"][0]["path"] != PROMPT_ENTRY["path"]:
                     # Remove and insert at 0
                     data["files"] = [f for f in data["files"] if f["path"] != PROMPT_ENTRY["path"]]
                     data["files"].insert(0, PROMPT_ENTRY)
                     print(f"Reordered {manifest_path.name}")
                     with open(manifest_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error processing {manifest_path.name}: {e}")

if __name__ == "__main__":
    update_manifests()
