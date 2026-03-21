#!/usr/bin/env python3
"""
Exploration Cycle Plugin - Session Start Hook
Checks if an exploration session brief exists. If not, emits an event 
to suggest starting the intake process.
"""
import os
import sys
from pathlib import Path

def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        brief_path = Path(project_dir) / "exploration" / "session-brief.md"
        
        # We only trigger if the brief is missing
        if not brief_path.exists():
            kernel_script = Path(project_dir) / "context" / "kernel.py"
            if kernel_script.exists():
                import subprocess
                # Emit the event to the kernel bus (audit log)
                cmd = [
                    sys.executable, str(kernel_script), "emit_event",
                    "--agent", "exploration-plugin-hook",
                    "--type", "intent",
                    "--action", "suggest_intake",
                    "--status", "success",
                    "--summary", "No exploration brief found at exploration/session-brief.md. Suggesting intake-agent."
                ]
                subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Print to stdout — this IS the subscriber in a hook-based architecture.
            # Hook stdout is surfaced directly to the agent at session start.
            print(
                "\n[exploration-cycle] No session brief found at exploration/session-brief.md.\n"
                "Suggested action: run the intake-agent to create one before starting exploration.\n"
                "  → Use skill: exploration-session-brief  OR  invoke the intake-agent directly.\n"
            )
            
    except Exception:
        pass # Hooks must fail silently

if __name__ == "__main__":
    main()
