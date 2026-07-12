#!/usr/bin/env python
"""
update_memory.py — Memory Update Hook
======================================================

Purpose:
    Called via PostToolUse and SessionStart hooks.
    Creates or appends to a dated session log in context/memory/YYYY-MM-DD.md
    on file writes, unless the file is volatile (MEMORY.md, status.md).

Layer: 
    Hooks / Lifecycle

Usage Examples:
    Called automatically by agent runner hooks interface with sys.argv[1] JSON payload

Supported Object Types:
    - Event payloads (SessionStart, PostToolUse)

CLI Arguments:
    sys.argv[1]             JSON payload describing tool triggers or start contexts

Input Files:
    - context/os-state.json

Output:
    - Routes events through kernel.py (fail-closed if kernel.py is absent or errors)
    - context/events.jsonl is written by kernel.py, not by this hook

Key Functions:
    _check_execution_gate() Determines lightweight vs heavy mode execution paths
    main()                  Main controller multiplexing hooks into audit items

Script Dependencies:
    - None (Uses standard python imports)

Consumed by:
    - SessionStart or PostToolUse hook dispatch wrappers
"""
import os
import sys
import json
import collections
from datetime import datetime
from pathlib import Path

def _check_execution_gate() -> bool:
    """Return True if the hook should proceed, False if it should be skipped.
    Reads execution_mode and hook_sample_rate from os-state.json.
    - execution_mode=lightweight: always skip
    - hook_sample_rate=N: run 1 in every N calls (counter stored in os-state.json)
    """
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        state_file = Path(project_dir) / "context" / "os-state.json"
        if not state_file.exists():
            return True  # No state file: proceed normally

        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        if state.get("execution_mode") == "lightweight":
            return False

        rate = int(state.get("hook_sample_rate", 1))
        if rate > 1:
            count = int(state.get("hook_call_count", 0)) + 1
            state["hook_call_count"] = count
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            if count % rate != 0:
                return False
    except Exception:
        pass  # If state is unreadable, proceed normally
    return True


def _parse_hook_payload() -> dict:
    """Parse sys.argv[1] as JSON, falling back to {} on missing/invalid payload."""
    if len(sys.argv) > 1:
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            return {}
    return {}


def _build_file_write_event(payload: dict) -> dict | None:
    """Build a file_write event_doc for a PostToolUse payload, or None if it should be skipped."""
    tool_name = payload.get("toolName", "")
    if tool_name not in ["Write", "Replace", "write_to_file", "multi_replace_file_content"]:
        return None

    tool_input = payload.get("toolInput", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            tool_input = {}

    if not isinstance(tool_input, dict):
        return None

    # Try to figure out the target file from common arguments
    raw_target = tool_input.get("TargetFile") or tool_input.get("file_path") or tool_input.get("path", "")
    if not raw_target:
        return None

    # Cross-Platform Normalization
    target_path = Path(raw_target)

    # Skip volatile memory files
    volatile_files = ["MEMORY.md", "status.md", "CLAUDE.md", "os-state.json", "events.jsonl"]
    if target_path.name in volatile_files:
        return None

    # Skip noisy directories via pure pathlib parts inspection
    noisy_dirs = {"node_modules", "dist", "build", ".git", ".venv", "coverage", "__pycache__"}
    if any(part in noisy_dirs for part in target_path.parts):
        return None

    # Emit as "legacy-hook" so agents.json permit lists don't need a "system" entry.
    # "system" was the prior value but caused silent failures when "system" was not
    # in the permitted_agents list.
    return {
        "time": datetime.now().isoformat() + "Z",
        "agent": "legacy-hook",
        "type": "result",
        "action": "file_write",
        "file": target_path.as_posix(),
        "status": "success"
    }


def _build_event_doc(payload: dict) -> dict | None:
    """Build the kernel event_doc for a hook payload, or None if the event should be skipped."""
    event_type = payload.get("event", "SessionStart")

    # We only care about file modifications for PostToolUse
    if event_type == "PostToolUse":
        return _build_file_write_event(payload)
    elif event_type == "SessionStart":
        return {
            "time": datetime.now().isoformat() + "Z",
            "agent": "legacy-hook",
            "type": "agent_start",
            "action": "session_start",
            "status": "success"
        }
    return None


def _emit_event_via_kernel(project_dir: str, event_doc: dict) -> None:
    """Ensure the memory dir exists, then route event_doc through kernel.py (fail closed if absent)."""
    memory_dir = Path(project_dir) / "context" / "memory"

    # Silently create directory if it doesn't exist
    os.makedirs(memory_dir, exist_ok=True)

    # Route event through kernel.py — fail closed if kernel absent (C-3 fix)
    kernel_script = Path(project_dir) / "context" / "kernel.py"
    if not kernel_script.exists():
        return  # Fail closed — no fallback writes
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


def _log_hook_error(e: Exception) -> None:
    """Write a hook error to context/memory/hook-errors.log with 1MB rotation, never raising."""
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
        pass  # Total failure fallback


def main() -> None:
    """Entry point for PostToolUse/SessionStart hooks: gate, build event doc, emit via kernel."""
    if not _check_execution_gate():
        return

    try:
        payload = _parse_hook_payload()
        event_doc = _build_event_doc(payload)
        if event_doc is None:
            return

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        _emit_event_via_kernel(project_dir, event_doc)
    except Exception as e:
        _log_hook_error(e)

if __name__ == "__main__":
    main()
