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

# Project paths
# File is at: plugins/vector-db/skills/vector-db-init/scripts/init.py
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).parent


def install_dependencies():
    print("📦 Installing Vector DB Dependencies from lockfile...")
    req_txt = PROJECT_ROOT / "plugins" / "vector-db" / "requirements.txt"
        
    if not req_txt.exists():
        print(f"❌ Error: Lockfile not found at {req_txt}")
        sys.exit(1)
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_txt)])
        print("✅ Dependencies installed successfully from requirements.txt.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def configure_profile():
    """
    Interactive profile configuration.
    Writes all settings to .agent/learning/vector_profiles.json — no .env needed.
    """
    learning_dir = PROJECT_ROOT / ".agent" / "learning"
    profiles_path = learning_dir / "vector_profiles.json"
    manifest_path = learning_dir / "vector_knowledge_manifest.json"
    
    print(f"\n📋 Configuring Vector DB Profile in {profiles_path}...")
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
    
    KNOWLEDGE_PROFILE = "knowledge"
    
    # 2. Select deployment architecture
    print("\n🚀 Deployment Architecture Selection")
    print("1) In-Process PersistentClient (Easiest, no background server, blocks concurrent agents)")
    print("2) Python Native Server (Recommended, requires `chroma run` in background, allows concurrency)")
    print("3) Skip configuration\n")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "3":
        print("⏭️ Skipping profile configuration.")
    elif choice in ("1", "2"):
        profile = profiles_data["profiles"].get(KNOWLEDGE_PROFILE, {})
        
        # Base settings
        profile["description"] = profile.get("description", "General documentation and project knowledge.")
        profile["manifest"] = ".agent/learning/vector_knowledge_manifest.json"
        profile["child_collection"] = profile.get("child_collection", "knowledge_child_v5")
        profile["parent_collection"] = profile.get("parent_collection", "knowledge_parent_v5")
        profile["chroma_data_path"] = ".knowledge_vector_data"
        
        if choice == "2":
            # Native Server configuration
            profile["chroma_host"] = profile.get("chroma_host", "127.0.0.1")
            profile["chroma_port"] = profile.get("chroma_port", 8110)
            print(f"   [+] Set chroma_host={profile['chroma_host']}")
            print(f"   [+] Set chroma_port={profile['chroma_port']}")
            print("   ℹ️  Remember to start the server: chroma run --host 127.0.0.1 --port 8110 --path .knowledge_vector_data")
        elif choice == "1":
            # In-Process — no host needed (empty string triggers PersistentClient)
            profile["chroma_host"] = ""
            profile.pop("chroma_port", None)
            print("   [+] Selected In-Process mode (no background server required).")
        
        profiles_data["profiles"][KNOWLEDGE_PROFILE] = profile
    else:
        print("❌ Invalid choice. Skipping profile configuration.")
        
    if "default_profile" not in profiles_data:
        profiles_data["default_profile"] = KNOWLEDGE_PROFILE
        
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles_data, f, indent=4)
        f.write("\n")
        
    print(f"✅ Configured profile '{KNOWLEDGE_PROFILE}'.")
    
    # 3. Scaffold Manifest
    if not manifest_path.exists():
        manifest_data = {
            "description": "Globs tracking project documentation and knowledge records.",
            "include": ["plugins/"],
            "exclude": ["/archive/", "/.git/", "/node_modules/", "/.venv/", "/__pycache__/", "/tests/"]
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
            f.write("\n")
        print(f"✅ Created knowledge manifest at {manifest_path}.")
    else:
        print(f"ℹ️  Manifest already exists at {manifest_path}. Skipping.")


def main():
    print("🚀 Initializing Vector DB Environment\n")
    install_dependencies()
    configure_profile()
    print("\n🎉 Initialization Complete!")

if __name__ == "__main__":
    main()
