#!/usr/bin/env python3
"""
Agentic OS - Memory Update Hook
Called via PostToolUse and SessionStart hooks.
Creates or appends to a dated session log in context/memory/YYYY-MM-DD.md
on file writes, unless the file is volatile (MEMORY.md, status.md).
Fails silently so as not to crash the agent session.
"""
import os
import sys
import json
import collections
from datetime import datetime
from pathlib import Path

def main():
    try:
        # 1. Parse the hook payload
        if len(sys.argv) > 1:
            try:
                payload = json.loads(sys.argv[1])
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}

        event_type = payload.get("event", "SessionStart")
        
        # We only care about file modifications for PostToolUse
        if event_type == "PostToolUse":
            tool_name = payload.get("toolName", "")
            if tool_name not in ["Write", "Replace", "write_to_file", "multi_replace_file_content"]:
                return
            
            tool_input = payload.get("toolInput", {})
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    tool_input = {}
                    
            if not isinstance(tool_input, dict):
                return
                
            # Try to figure out the target file from common arguments
            raw_target = tool_input.get("TargetFile") or tool_input.get("file_path") or tool_input.get("path", "")
            if not raw_target:
                return
                
            # Cross-Platform Normalization
            target_path = Path(raw_target)
                
            # Skip volatile memory files
            volatile_files = ["MEMORY.md", "status.md", "CLAUDE.md", "os-state.json", "events.jsonl"]
            if target_path.name in volatile_files:
                return
                
            # Skip noisy directories via pure pathlib parts inspection
            noisy_dirs = {"node_modules", "dist", "build", ".git", ".venv", "coverage", "__pycache__"}
            if any(part in noisy_dirs for part in target_path.parts):
                return
                
            # It's difficult to know the exact agent name from the hook, so we default to 'system'
            # and rely on the agent itself to emit its own intent events.
            event_doc = {
                "time": datetime.now().isoformat() + "Z",
                "agent": "system",
                "type": "result",
                "action": "file_write",
                "file": target_path.as_posix(),
                "status": "success"
            }
        elif event_type == "SessionStart":
            event_doc = {
                "time": datetime.now().isoformat() + "Z",
                "agent": "system",
                "type": "agent_start",
                "action": "session_start",
                "status": "success"
            }
        else:
            return

        # 2. Get environment paths
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        memory_dir = Path(project_dir) / "context" / "memory"
        
        # 2.5 Update OS State
        os_state_file = Path(project_dir) / "context" / "os-state.json"
        if os_state_file.exists():
            try:
                with open(os_state_file, "r", encoding="utf-8") as f:
                    os_state = json.load(f)
                
                os_state["active_agent"] = "background-hook"
                os_state["mode"] = payload.get("event", "unknown")
                os_state["last_hook_execution"] = datetime.now().isoformat()
                
                with open(os_state_file, "w", encoding="utf-8") as f:
                    json.dump(os_state, f, indent=2)
            except Exception:
                pass
        
        # Silently create directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # 3. Use Kernel Controller to emit event to the bus
        kernel_script = Path(project_dir) / "context" / "kernel.py"
        if kernel_script.exists():
            import subprocess
            cmd = [
                sys.executable, str(kernel_script), "emit_event",
                "--agent", event_doc["agent"],
                "--type", event_doc["type"],
                "--action", event_doc["action"],
                "--status", event_doc.get("status", "success")
            ]
            if "summary" in event_doc:
                cmd.extend(["--summary", event_doc["summary"]])
                
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Fallback for systems that haven't fully initialized the v10 kernel yet
            events_file = Path(project_dir) / "context" / "events.jsonl"
            with open(events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_doc) + "\n")
            
            
    except Exception as e:
        # P0 Red Team Fix: Do not fail silently. Write to an error log that the OS can see,
        # but do not print to stdout/stderr so as not to pollute the LLM tool return string.
        try:
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
            error_log = Path(project_dir) / "context" / "memory" / "hook-errors.log"
            
            # Size limit / rotation: 1MB limit
            if error_log.exists() and error_log.stat().st_size > 1 * 1024 * 1024:
                try:
                    with open(error_log, "r", encoding="utf-8") as f:
                        lines = collections.deque(f, 100)
                    with open(error_log, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                except Exception:
                    open(error_log, "w").close()
                    
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(error_log, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Hook Error: {str(e)}\n")
        except Exception:
            pass # Total failure fallback

if __name__ == "__main__":
    main()
