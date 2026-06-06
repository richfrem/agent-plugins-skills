#!/usr/bin/env python3
"""
run_claude.py (CLI)
=====================================

Purpose:
    Launches Claude Code routed through a session-scoped local Gemma 4 proxy.
    Automatically disables telemetry and attribution to protect prompt cache.

Layer: Infrastructure / Execution

Usage Examples:
    python3 run_claude.py
    python3 run_claude.py --help

Supported Object Types:
    None

CLI Arguments:
    Passed through directly to the "claude" CLI command.

Input Files:
    ~/.claude/settings.json (reads and patches)

Output:
    Foreground execution of Claude Code session, console logs

Key Functions:
    patch_claude_settings(): Configure Claude settings for cache compatibility
    port_is_open(): Check if a port is actively bound
    get_proxy_path(): Search and resolve local routing_proxy.py path

Script Dependencies:
    json, os, socket, subprocess, sys, time

Consumed by:
    local-llm-bridge skill workflows
"""

import json
import os
import socket
import subprocess
import sys
import time

def patch_claude_settings():
    home = os.path.expanduser("~")
    settings_path = os.path.join(home, ".claude/settings.json")
    
    data = {}
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, 'r') as f:
                data = json.load(f)
        except Exception:
            pass
            
    if 'env' not in data:
        data['env'] = {}
    data['env']['CLAUDE_CODE_ATTRIBUTION_HEADER'] = '0'
    data['env']['DISABLE_TELEMETRY'] = '1'
    
    try:
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("✓ Patched ~/.claude/settings.json to disable telemetry and attribution.")
    except Exception as e:
        print(f"WARNING: Could not patch Claude Code settings: {e}")

def port_is_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_proxy_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "routing_proxy.py"),                          # same scripts/ dir (installed)
        os.path.join(script_dir, "../../../local-llm-bench/routing_proxy.py"), # dev repo sibling layout
    ]
    for c in candidates:
        if os.path.isfile(os.path.abspath(c)):
            return os.path.abspath(c)
    return None

def main():
    port = 4000
    patch_claude_settings()

    proxy_proc = None
    if port_is_open(port):
        print(f"[session-proxy] Global proxy already running on port {port} — using it.")
    else:
        print(f"[session-proxy] No proxy found on port {port} — starting session proxy...")
        proxy_path = get_proxy_path()
        if not proxy_path:
            print("ERROR: Could not find routing_proxy.py to start.")
            sys.exit(1)
            
        proxy_proc = subprocess.Popen(
            [sys.executable, proxy_path, "--port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait briefly
        time.sleep(0.8)
        if not port_is_open(port):
            print(f"[session-proxy] ERROR: Proxy failed to start on port {port}.")
            if proxy_proc:
                proxy_proc.terminate()
            sys.exit(1)
        print(f"[session-proxy] Proxy started (PID {proxy_proc.pid}).")

    # Set up environment variables
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = f"http://localhost:{port}"
    env["CLAUDE_CODE_MAX_CONTEXT"] = "32768"

    # Gather any extra arguments passed to the script
    claude_args = ["claude", "--model", "gemma-4-12b"] + sys.argv[1:]
    
    try:
        # Run Claude Code in the foreground
        subprocess.run(claude_args, env=env)
    except KeyboardInterrupt:
        pass
    finally:
        if proxy_proc:
            print(f"\n[session-proxy] Stopping session proxy (PID {proxy_proc.pid})...")
            proxy_proc.terminate()
            proxy_proc.wait()

if __name__ == "__main__":
    main()
