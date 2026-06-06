#!/usr/bin/env python3
"""
run_agy.py (CLI)
=====================================

Purpose:
    Ensures that the Antigravity (agy) config.toml contains the local model definition,
    and launches the agy CLI tool mapped to the local proxy endpoint.

Layer: Infrastructure / Execution

Usage Examples:
    python3 run_agy.py
    python3 run_agy.py chat "Explain quantum computing"

Supported Object Types:
    None

CLI Arguments:
    Passed directly to the underlying "agy" command.

Input Files:
    ~/.config/antigravity/config.toml (reads and registers local model)

Output:
    Foreground execution of Antigravity CLI session, logs

Key Functions:
    patch_agy_config(): Safely add local model block to Agy config.toml
    main(): Execute configuration patches and launch agy binary

Script Dependencies:
    os, subprocess, sys

Consumed by:
    local-llm-bridge-agy skill workflows
"""

import os
import subprocess
import sys

def patch_agy_config():
    home = os.environ.get("HOME") or os.path.expanduser("~")
    config_dir = os.path.join(home, ".config/antigravity")
    config_path = os.path.join(config_dir, "config.toml")
    
    os.makedirs(config_dir, exist_ok=True)
    
    local_block = """
[[models]]
name = "Gemma 4 Local"
model = "gemma-4-12b"
base_url = "http://localhost:4000/v1"
env_key = "LOCAL_PASSTHROUGH"
"""
    
    content = ""
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as f:
                content = f.read()
        except Exception as e:
            print(f"WARNING: Could not read existing config.toml: {e}")
            
    blocks = content.split("[[models]]")
    configured = False
    for block in blocks[1:]:
        lines = [line.strip() for line in block.splitlines() if line.strip() and not line.strip().startswith("#")]
        attrs = {}
        for line in lines:
            if "=" in line:
                k, v = line.split("=", 1)
                attrs[k.strip()] = v.strip().strip('"').strip("'")
        if attrs.get("model") == "gemma-4-12b" and attrs.get("base_url") == "http://localhost:4000/v1":
            configured = True
            break
            
    if not configured:
        print("[session-agy] Patching config.toml to add/update local Gemma 4 model entry...")
        header = blocks[0]
        new_blocks = []
        for block in blocks[1:]:
            lines = [line.strip() for line in block.splitlines() if line.strip() and not line.strip().startswith("#")]
            attrs = {}
            for line in lines:
                if "=" in line:
                    k, v = line.split("=", 1)
                    attrs[k.strip()] = v.strip().strip('"').strip("'")
            if attrs.get("model") != "gemma-4-12b":
                new_blocks.append("[[models]]" + block)
        
        new_content = header + "".join(new_blocks)
        if not new_content.endswith("\n"):
            new_content += "\n"
        new_content += local_block
        
        try:
            with open(config_path, "w") as f:
                f.write(new_content)
            print("✓ Config patched successfully (added/updated Gemma 4 Local).")
        except Exception as e:
            print(f"WARNING: Could not write to config.toml: {e}")
    else:
        print("[session-agy] Local Gemma 4 entry already configured in config.toml.")

def main():
    patch_agy_config()
    
    print("[session-agy] Starting Antigravity CLI...")
    agy_args = ["agy"] + sys.argv[1:]
    
    env = os.environ.copy()
    env.setdefault("LOCAL_PASSTHROUGH", "dummy_token")
    
    try:
        subprocess.run(agy_args, env=env)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print("ERROR: Antigravity CLI binary ('agy') not found in PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
