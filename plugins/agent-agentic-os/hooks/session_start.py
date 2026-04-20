#!/usr/bin/env python
"""
SessionStart hook wrapper for agent-agentic-os

Purpose:
  Cross-platform (Windows & macOS/Linux) Python wrap that applies a --resume guard 
  to avoid double-injection on resumed sessions, then invokes update_memory.py.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def main():
    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    
    # Prefer CLAUDE_PLUGIN_ROOT / CURSOR_PLUGIN_ROOT from env if set
    resolved_root_str = os.environ.get("CURSOR_PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT") or str(plugin_root)
    resolved_root = Path(resolved_root_str)
    
    # Detect project dir
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    
    # --resume guard: If events.jsonl was modified in the last 60 seconds, skip
    events_file = project_dir / "context" / "events.jsonl"
    if events_file.exists():
        try:
            mtime = events_file.stat().st_mtime
            if time.time() - mtime < 60:
                print(json.dumps({"continue": True}))
                sys.exit(0)
        except Exception:
            pass
            
    # Read stdin payload
    try:
        if not sys.stdin.isatty():
            hook_payload = sys.stdin.read()
        else:
            hook_payload = "{}"
    except Exception:
        hook_payload = "{}"
        
    # Platform context
    if os.environ.get("CURSOR_PLUGIN_ROOT"):
        os.environ["AGENTIC_OS_PLATFORM"] = "cursor"
    elif os.environ.get("CLAUDE_PLUGIN_ROOT"):
        os.environ["AGENTIC_OS_PLATFORM"] = "claude"
    else:
        os.environ["AGENTIC_OS_PLATFORM"] = "unknown"
        
    # Invoke update_memory.py
    update_memory_py = resolved_root / "hooks" / "update_memory.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(update_memory_py), hook_payload],
            input=hook_payload,
            text=True,
            capture_output=True
        )
        python_out = proc.stdout.strip()
    except Exception as e:
        python_out = ""
        
    # Both Cursor and Claude code receive valid JSON dict
    if python_out:
        print(python_out)
    else:
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
