#!/usr/bin/env python3
"""
session_end.py
=====================================

Purpose:
    Detects when an exploration session completes (dashboard Status: Complete)
    and emits a session-complete event to context/events.jsonl for the
    exploration-optimizer to consume as friction signal input.

Layer: Hooks / Triggering

Usage Examples:
    python session_end.py

Script Dependencies:
    - context/kernel.py (for emitting events, optional)

Consumed by:
    - Exploration cycle hooks
"""
import os
import sys
from pathlib import Path


def _extract_session_name(content: str) -> str:
    """Extract the session name from the dashboard's '**Session:**' line."""
    for line in content.splitlines():
        if line.startswith("**Session:**"):
            return line.replace("**Session:**", "").strip()
    return "unknown"


def _emit_completion_event(kernel_script: Path, summary: str) -> None:
    """Invoke kernel.py emit_event for a session-complete lifecycle event, if kernel.py exists."""
    if not kernel_script.exists():
        return
    import subprocess
    cmd = [
        sys.executable, str(kernel_script), "emit_event",
        "--agent", "exploration-plugin-hook",
        "--type", "lifecycle",
        "--action", "session-complete",
        "--status", "success",
        "--summary", summary,
    ]
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    """Detect exploration session completion and emit session-complete event."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        dashboard_path = Path(project_dir) / "exploration" / "exploration-dashboard.md"
        marker_path = Path(project_dir) / "context" / ".exploration_session_end_marker"

        if not dashboard_path.exists():
            return

        content = dashboard_path.read_text(encoding="utf-8")
        if "**Status:** Complete" not in content:
            return

        # Check if we already emitted for this completion (avoid duplicate events)
        dashboard_mtime = str(int(dashboard_path.stat().st_mtime))
        if marker_path.exists() and marker_path.read_text().strip() == dashboard_mtime:
            return

        session_name = _extract_session_name(content)
        summary = f"Exploration session complete: {session_name}"
        kernel_script = Path(project_dir) / "context" / "kernel.py"
        _emit_completion_event(kernel_script, summary)

        # Write marker so we don't re-emit on next hook invocation
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text(dashboard_mtime)

        print(
            f"\n[exploration-cycle] Session complete: {session_name}\n"
            "Friction signal emitted. Run /exploration-optimizer to improve the workflow.\n"
        )

    except Exception:
        pass  # Hooks must fail silently


if __name__ == "__main__":
    main()
