#!/usr/bin/env python3
"""
run_codex.py (CLI)
=====================================

Purpose:
    Launches any OpenAI-compatible command-line client (e.g. Aider, Goose, etc.)
    routed through the local proxy.
    Injects OpenAI configuration environment variables.

Layer: Infrastructure / Execution

Usage Examples:
    python3 run_codex.py aider --model openai/gemma-4-12b
    python3 run_codex.py goose run

CLI Arguments:
    The target command and arguments to run under the configured environment.
"""

import os
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_codex.py <command> [args...]")
        print("Example: python3 run_codex.py aider --model openai/gemma-4-12b")
        sys.exit(1)
        
    cmd = sys.argv[1:]
    
    print(f"[session-codex] Launching command: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env.setdefault("OPENAI_API_BASE", "http://localhost:4000/v1")
    env.setdefault("OPENAI_BASE_URL", "http://localhost:4000/v1")
    env.setdefault("OPENAI_API_KEY", "dummy")
    env.setdefault("OPENAI_MODEL", "gemma-4-12b")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print(f"ERROR: Command '{cmd[0]}' not found in PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
