#!/usr/bin/env python3
"""
run_copilot.py (CLI)
=====================================

Purpose:
    Launches GitHub Copilot CLI routed through the local proxy.
    Injects BYOK (Bring Your Own Key) settings and forces Offline Mode
    to bypass standard GitHub API authentication checkpoints.

Layer: Infrastructure / Execution

Usage Examples:
    python3 run_copilot.py
    python3 run_copilot.py explain "def hello(): pass"

Supported Object Types:
    None

CLI Arguments:
    Passed directly to the underlying "copilot" command.

Input Files:
    None

Output:
    Foreground execution of GitHub Copilot CLI session, logs

Key Functions:
    main(): Injects environment configurations and executes copilot binary

Script Dependencies:
    os, subprocess, sys

Consumed by:
    local-llm-bridge-copilot skill workflows
"""

import os
import subprocess
import sys

def main():
    if "--diagnose" in sys.argv or "--diagnose-live" in sys.argv:
        print("=== COPILOT CLI DIAGNOSTIC MODE ===")
        import shutil
        copilot_path = shutil.which("copilot")
        print(f"which copilot: {copilot_path}")
        if copilot_path:
            try:
                res = subprocess.run(["copilot", "--version"], capture_output=True, text=True, timeout=5)
                print(f"copilot --version:\n{res.stdout.strip() or res.stderr.strip()}")
            except Exception as e:
                print(f"copilot --version failed: {e}")
            try:
                res = subprocess.run(["copilot", "--help"], capture_output=True, text=True, timeout=5)
                print(f"copilot --help output snippet (first 10 lines):\n" + "\n".join(res.stdout.strip().splitlines()[:10]))
            except Exception as e:
                print(f"copilot --help failed: {e}")
        else:
            print("copilot command not found, skipping version/help checks.")
        
        # Show the effective values that will be forced into the session
        target_env = {
            "COPILOT_PROVIDER_TYPE": "openai",
            "COPILOT_PROVIDER_BASE_URL": "http://localhost:4000/v1",
            "COPILOT_PROVIDER_API_KEY": "dummy",
            "COPILOT_MODEL": "gemma-4-12b",
            "COPILOT_OFFLINE": os.environ.get("COPILOT_OFFLINE", "true"),
            "COPILOT_TELEMETRY_DISABLED": os.environ.get("COPILOT_TELEMETRY_DISABLED", "true"),
            "COPILOT_PROXY_STRICT_SSL": os.environ.get("COPILOT_PROXY_STRICT_SSL", "false"),
        }
        
        print("\nTarget Environment Injection Variables:")
        for k, v in target_env.items():
            print(f"  {k}={v}")
            
        print("\nActive Environment variables containing 'COPILOT' or 'PROXY':")
        for k, v in os.environ.items():
            if "copilot" in k.lower() or "proxy" in k.lower():
                print(f"  {k}={v}")
                
        if "--diagnose-live" in sys.argv:
            print("\nExecuting live proxy smoke check (sending test request to localhost:4000)...")
            import urllib.request
            import json
            test_data = {
                "model": "gemma-4-12b",
                "messages": [{"role": "user", "content": "hi"}]
            }
            req = urllib.request.Request(
                "http://localhost:4000/v1/chat/completions",
                data=json.dumps(test_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                # Set a short timeout
                with urllib.request.urlopen(req, timeout=3) as resp:
                    print(f"✓ Proxy response status: {resp.status}")
                    print(f"✓ Proxy response content: {resp.read().decode('utf-8')[:100]}...")
            except Exception as e:
                print(f"✗ Live proxy test failed: {e}")
                
        print("===================================")
        sys.exit(0)

    print("[session-copilot] Starting GitHub Copilot CLI with Local Gemma routing...")
    
    # Force routing vars — always override so shell env can't redirect away from local Gemma
    env = os.environ.copy()
    env["COPILOT_PROVIDER_TYPE"] = "openai"
    env["COPILOT_PROVIDER_BASE_URL"] = "http://localhost:4000/v1"
    env["COPILOT_PROVIDER_API_KEY"] = "dummy"
    env["COPILOT_MODEL"] = "gemma-4-12b"
    # Soft defaults — user can override these if needed
    env.setdefault("COPILOT_OFFLINE", "true")
    env.setdefault("COPILOT_TELEMETRY_DISABLED", "true")
    env.setdefault("COPILOT_PROXY_STRICT_SSL", "false")

    # Assemble copilot execution arguments
    copilot_args = ["copilot"] + sys.argv[1:]
    
    try:
        subprocess.run(copilot_args, env=env)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print("ERROR: GitHub Copilot CLI binary ('copilot') not found in PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
