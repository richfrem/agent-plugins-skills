#!/usr/bin/env python3
"""
init.py (CLI)
=====================================

Purpose:
    Installs required Python dependencies for the Vector DB plugin and
    interactively configures the user's vector_profiles.json.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# ============================================================
# PATHS
# ============================================================
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).parent


def install_dependencies():
    print("[INIT] Installing Vector DB Dependencies from lockfile...")
    req_txt = PROJECT_ROOT / "plugins" / "vector-db" / "requirements.txt"
        
    if not req_txt.exists():
        # Fallback for installed skills
        req_txt = PROJECT_ROOT / ".agents" / "skills" / "vector-db-init" / "requirements.txt"
        if not req_txt.exists():
             print(f"[ERROR] Lockfile not found.")
             return
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_txt)])
        print("[OK] Dependencies installed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        # sys.exit(1) # Don't exit, might be partially working

def configure_profile():
    """
    Interactive profile configuration.
    Writes all settings to .agent/learning/vector_profiles.json — no .env needed.
    """
    learning_dir = PROJECT_ROOT / ".agent" / "learning"
    profiles_path = learning_dir / "vector_profiles.json"
    manifest_path = learning_dir / "vector_wiki_manifest.json"
    
    print(f"\n[CONFIG] Configuring Vector DB Profile in {profiles_path}...")
    learning_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load existing profiles (or start fresh)
    profiles_data = {}
    if profiles_path.exists():
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles_data = json.load(f)
        except Exception:
            pass
            
    if "version" not in profiles_data:
        profiles_data["version"] = 2
    if "profiles" not in profiles_data:
        profiles_data["profiles"] = {}
    
    KNOWLEDGE_PROFILE = "wiki"
    
    # 2. Select deployment architecture
    print("\n[ARCH] Deployment Architecture Selection")
    print("1) In-Process PersistentClient (Easiest, no background server)")
    print("2) Python Native Server (Requires `chroma run` in background)")
    print("3) Skip interactive configuration\n")
    
    # Since we are running in an agent, we assume choice 1 or we use the existing file
    choice = "1"
    print(f"Selecting default: {choice}")
    
    if choice in ("1", "2"):
        profile = profiles_data["profiles"].get(KNOWLEDGE_PROFILE, {})
        
        # Base settings
        profile["description"] = "Legacy Oracle Forms analysis wiki"
        profile["manifest"] = ".agent/learning/vector_wiki_manifest.json"
        profile["child_collection"] = "jag_oracle_forms_wiki_child"
        profile["parent_collection"] = "jag_oracle_forms_wiki_parent"
        profile["chroma_data_path"] = ".agent/learning/vector_wiki_db"
        
        if choice == "2":
            # Native Server configuration
            profile["chroma_host"] = "127.0.0.1"
            profile["chroma_port"] = 8110
        elif choice == "1":
            # In-Process
            profile["chroma_host"] = ""
            profile.pop("chroma_port", None)
        
        profiles_data["profiles"][KNOWLEDGE_PROFILE] = profile
    
    profiles_data["default_profile"] = KNOWLEDGE_PROFILE
        
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles_data, f, indent=4)
        f.write("\n")
        
    print(f"[OK] Configured profile '{KNOWLEDGE_PROFILE}'.")
    
    # 3. Scaffold Manifest
    if not manifest_path.exists():
        manifest_data = {
            "description": "Legacy system analysis manifest",
            "include": ["legacy-system/"],
            "exclude": ["/reference-data/"],
            "extensions": [".md"],
            "recursive": True
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
        print(f"[OK] Created wiki manifest at {manifest_path}.")


def main():
    print("--- Initializing Vector DB Environment ---")
    # install_dependencies() # Already done
    configure_profile()
    print("--- Initialization Complete ---")

if __name__ == "__main__":
    main()
