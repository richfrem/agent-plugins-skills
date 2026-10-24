#!/usr/bin/env python
"""
SessionStart hook wrapper for agent-agentic-os

Purpose:
  Cross-platform (Windows & macOS/Linux) Python wrap that applies a --resume guard
  to avoid double-injection on resumed sessions, then invokes update_memory.py.

Key Input Dependencies:
  - context/events.jsonl (resume guard mtime check)
  - hooks/update_memory.py (invoked as a subprocess)
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def _resolve_plugin_root() -> Path:
    """Resolve the plugin root: prefer CURSOR_PLUGIN_ROOT/CLAUDE_PLUGIN_ROOT env vars, else infer from this file."""
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    resolved_root_str = os.environ.get("CURSOR_PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT") or str(plugin_root)
    return Path(resolved_root_str)


def _should_skip_resume(project_dir: Path) -> bool:
    """Return True if events.jsonl was modified in the last 60 seconds (resumed-session guard)."""
    events_file = project_dir / "context" / "events.jsonl"
    if events_file.exists():
        try:
            mtime = events_file.stat().st_mtime
            if time.time() - mtime < 60:
                return True
        except Exception:
            pass
    return False


def _read_stdin_payload() -> str:
    """Read the hook payload from stdin, defaulting to '{}' if unavailable or a TTY."""
    try:
        if not sys.stdin.isatty():
            return sys.stdin.read()
        return "{}"
    except Exception:
        return "{}"


def _set_platform_env() -> None:
    """Set AGENTIC_OS_PLATFORM based on which plugin-root env var is present."""
    if os.environ.get("CURSOR_PLUGIN_ROOT"):
        os.environ["AGENTIC_OS_PLATFORM"] = "cursor"
    elif os.environ.get("CLAUDE_PLUGIN_ROOT"):
        os.environ["AGENTIC_OS_PLATFORM"] = "claude"
    else:
        os.environ["AGENTIC_OS_PLATFORM"] = "unknown"


def _invoke_update_memory(resolved_root: Path, hook_payload: str) -> str:
    """Run update_memory.py as a subprocess with the hook payload, returning its stripped stdout."""
    update_memory_py = resolved_root / "hooks" / "update_memory.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(update_memory_py), hook_payload],
            input=hook_payload,
            text=True,
            capture_output=True
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def main():
    """Entry point for the SessionStart hook: apply the resume guard, then delegate to update_memory.py."""
    resolved_root = _resolve_plugin_root()
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

    if _should_skip_resume(project_dir):
        print(json.dumps({"continue": True}))
        sys.exit(0)

    hook_payload = _read_stdin_payload()
    _set_platform_env()
    python_out = _invoke_update_memory(resolved_root, hook_payload)

    # Both Cursor and Claude code receive valid JSON dict
    if python_out:
        print(python_out)
    else:
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
