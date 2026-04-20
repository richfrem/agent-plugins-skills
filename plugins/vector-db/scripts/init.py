#!/usr/bin/env python
"""
init.py
=====================================

Purpose:
    Installs required Python dependencies for the Vector DB plugin and
    interactively configures the user's vector_profiles.json with the 
    new architectural and performance parameters.

Layer: Codify / Retrieve

Usage:
    python init.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))


def install_dependencies() -> None:
    """Installs required Python packages from the repository lockfile."""
    print("[INIT] Installing Vector DB Dependencies from lockfile...")
    req_txt = PROJECT_ROOT / "plugins" / "vector-db" / "requirements.txt"
        
    if not req_txt.exists():
        req_txt = PROJECT_ROOT / ".agents" / "skills" / "vector-db-init" / "requirements.txt"
        if not req_txt.exists():
             print(f"[ERROR] Lockfile not found.")
             return
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_txt)])
        print("[OK] Dependencies installed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")


def configure_profile() -> None:
    """
    Scaffolds the configurable Vector DB Profile in .agent/learning/vector_profiles.json.
    Defaults to High-Performance In-Process mode (No server needed).
    """
    learning_dir = PROJECT_ROOT / ".agent" / "learning"
    profiles_path = learning_dir / "vector_profiles.json"
    manifest_path = learning_dir / "vector_wiki_manifest.json"
    
    print(f"\n[CONFIG] Scaffolding High-Performance Vector DB Profile...")
    learning_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load existing profiles or start fresh
    profiles_data: Dict[str, Any] = {"version": 2, "profiles": {}}
    if profiles_path.exists():
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    profiles_data = loaded
        except Exception:
            pass
            
    KNOWLEDGE_PROFILE = "wiki"
    profile = profiles_data.get("profiles", {}).get(KNOWLEDGE_PROFILE, {})
    
    # 2. Apply Mandatory Architectural Settings (In-Process Default)
    print("[ARCH] Defaulting to In-Process Persistence (Direct disk access).")
    
    # Core Identity
    profile["description"] = profile.get("description", "High-performance semantic index for code and documentation.")
    profile["manifest"] = profile.get("manifest", ".agent/learning/vector_wiki_manifest.json")
    profile["child_collection"] = profile.get("child_collection", "vector_child_v1")
    profile["parent_collection"] = profile.get("parent_collection", "vector_parent_v1")
    profile["chroma_data_path"] = profile.get("chroma_data_path", ".agent/learning/vector_db")
    
    # Connection (Empty Host = In-Process)
    profile["chroma_host"] = "" 
    profile["chroma_port"] = 8110
    
    # High-Performance Defaults
    profile["batch_size"] = profile.get("batch_size", 1000)
    profile["embedding_model"] = profile.get("embedding_model", "nomic-ai/nomic-embed-text-v1.5")
    
    # Optimized Parent-Child Chunking
    profile["parent_chunk_size"] = profile.get("parent_chunk_size", 2000)
    profile["parent_chunk_overlap"] = profile.get("parent_chunk_overlap", 200)
    profile["child_chunk_size"] = profile.get("child_chunk_size", 400)
    profile["child_chunk_overlap"] = profile.get("child_chunk_overlap", 50)
    profile["device"] = profile.get("device", "cpu")

    # Save Profile
    profiles_data["profiles"][KNOWLEDGE_PROFILE] = profile
    profiles_data["default_profile"] = KNOWLEDGE_PROFILE
        
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles_data, f, indent=4)
        f.write("\n")
        
    print(f"[OK] Dynamic profile '{KNOWLEDGE_PROFILE}' is ready.")
    
    # 3. Scaffold Blank Manifest if missing
    if not manifest_path.exists():
        manifest_data = {
            "description": "Project analysis manifest",
            "include": ["./"],
            "exclude": [".git/", ".agent/", "__pycache__/", "node_modules/"],
            "extensions": [".md", ".py", ".js", ".ts", ".xml", ".sql", ".json"],
            "recursive": True
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
        print(f"[OK] Created initial manifest at {manifest_path}.")


def main() -> None:
    """Main execution sequence."""
    print("--- Initializing Dynamic Vector DB Environment ---")
    configure_profile()
    print("--- Initialization Complete ---")


if __name__ == "__main__":
    main()
