#!/usr/bin/env python3
"""
init.py (CLI)
=====================================

Purpose:
    Installs required Python dependencies for the Vector DB plugin and 
    interactively configures the user's .env file based on their deployment choice.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent

def install_dependencies():
    print("📦 Installing Vector DB Dependencies...")
    packages = [
        "chromadb",
        "langchain-chroma",
        "langchain-huggingface",
        "sentence-transformers"
    ]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ Dependencies installed successfully.\\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def configure_env():
    env_path = PROJECT_ROOT / ".env"
    print(f"⚙️ Configuring {env_path}...")
    
    existing_content = ""
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            existing_content = str(f.read())

    print("\\n🚀 Deployment Architecture Selection")
    print("1) In-Process PersistentClient (Easiest, No background server required, blocks concurrent agents)")
    print("2) Python Native Server (Recommended, requires running `vector-db-launch` in background, allows concurrency)")
    print("3) Skip .env configuration\\n")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    lines_to_append = []
    
    # Base Collections (Always needed for Parent-Child)
    base_vars = {
        "CHROMA_DATA_PATH": ".vector_data",
        "CHROMA_CHILD_COLLECTION": "child_chunks_v5",
        "CHROMA_PARENT_STORE": "parent_documents_v5"
    }

    if choice == "3":
        print("⏭️ Skipping .env configuration.")
        return

    # Add the base variables
    for key, val in base_vars.items():
        if f"{key}=" not in existing_content:
            lines_to_append.append(f"{key}={val}")

    if choice == "2":
        # Native Server configuration
        if "# --- CHROMA CONNECTION ---" not in existing_content:
            lines_to_append.append("\\n# --- CHROMA CONNECTION ---")
            lines_to_append.append("# Used to connect to the Python `chroma run` background server")
        
        server_vars = {"CHROMA_HOST": "127.0.0.1", "CHROMA_PORT": "8110"}
        for key, val in server_vars.items():
            if f"{key}=" not in existing_content:
                lines_to_append.append(f"{key}={val}")
                print(f"   [+] Added {key}={val}")
            else:
                print(f"   [-] Skipped {key} (Already exists)")
    elif choice == "1":
        # In-Process configuration
        print("   [+] Selected In-Process mode (No CHROMA_HOST required).")
    else:
        print("❌ Invalid choice. Skipping .env configuration.")
        return

    if lines_to_append:
        with open(env_path, "a") as f:
            f.write("\\n".join(lines_to_append) + "\\n")
        print("✅ Environment configuration updated.")
    else:
        print("✅ Environment already configured perfectly.")

def configure_manifest():
    manifest_path = PROJECT_ROOT / "plugins" / "vector-db" / "ingest_manifest.json"
    print(f"\\n📋 Configuring Ingestion Manifest ({manifest_path})")
    
    # Ensure directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    existing_dirs = ["src", "docs"]
    if manifest_path.exists():
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
                existing_dirs = data.get("include", existing_dirs)
        except Exception:
            pass
            
    print(f"Current target directories: {', '.join(existing_dirs)}")
    print("Enter the top-level directories you want the Vector DB to ingest (comma-separated).")
    print("Press Enter to keep current targets, or type 'none' to clear.")
    
    choice = input("Directories: ").strip()
    
    if choice.lower() == "none":
        new_dirs = []
    elif choice:
        new_dirs = [d.strip() for d in choice.split(",") if d.strip()]
    else:
        new_dirs = existing_dirs
        
    manifest = {
        "include": new_dirs,
        "exclude": ["/archive/", "/.git/", "/node_modules/", "/.venv/", "/__pycache__/"]
    }
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"✅ Manifest saved with {len(new_dirs)} target directories.")

def main():
    print("🚀 Initializing Vector DB Environment\\n")
    install_dependencies()
    configure_env()
    configure_manifest()
    print("\\n🎉 Initialization Complete!")

if __name__ == "__main__":
    main()
