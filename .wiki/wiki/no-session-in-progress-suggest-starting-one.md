---
concept: no-session-in-progress-suggest-starting-one
source: plugin-code
source_file: exploration-cycle-plugin/hooks/session_start.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.976081+00:00
cluster: exploration
content_hash: 26ed888192d1152b
---

# No session in progress — suggest starting one

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
session_start.py
=====================================

Purpose:
    Checks if an exploration session brief exists. If not, emits an event to suggest starting the intake process.

Layer: Hooks / Triggering

Usage Examples:
    python session_start.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    - exploration/session-brief.md

Output:
    - Printed warning / suggested action to stdout.

Key Functions:
    None

Script Dependencies:
    - context/kernel.py (for emitting events)

Consumed by:
    - Exploration cycle hooks
"""
import os
import sys
from pathlib import Path

def main() -> None:
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        dashboard_path = Path(project_dir) / "exploration" / "exploration-dashboard.md"

        def emit_event(kernel_script: Path, summary: str) -> None:
            if kernel_script.exists():
                import subprocess
                cmd = [
                    sys.executable, str(kernel_script), "emit_event",
                    "--agent", "exploration-plugin-hook",
                    "--type", "intent",
                    "--action", "suggest_intake",
                    "--status", "success",
                    "--summary", summary,
                ]
                subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        kernel_script = Path(project_dir) / "context" / "kernel.py"

        if not dashboard_path.exists():
            # No session in progress — suggest starting one
            summary = "No exploration dashboard found. Suggesting exploration-workflow to start a session."
            emit_event(kernel_script, summary)
            print(
                "\n[exploration-cycle] No session found at exploration/exploration-dashboard.md.\n"
                "Suggested action: start a new exploration session.\n"
                "  → Use skill: exploration-workflow\n"
            )
        else:
            # Dashboard exists — check if the session is complete
            content = dashboard_path.read_text(encoding="utf-8")
            if "**Status:** Complete" in content:
                summary = "Prior exploration session is complete. Ready to start a new one."
                emit_event(kernel_script, summary)
                print(
                    "\n[exploration-cycle] Your last exploration session is complete.\n"
                    "Suggested action: start a new session or review your handoff.\n"
                    "  → Use skill: exploration-workflow  to start a new session.\n"
                    "  → Check: exploration/handoffs/  for prior session outputs.\n"
                )
            # else: active session in progress — no suggestion needed, orchestrator handles it

    except Exception:
        pass  # Hooks must fail silently

if __name__ == "__main__":
    main()


## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[domain-patterns-exploration-session-failures]]
- [[improvement-session-brief]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/hooks/session_start.py`
- **Indexed:** 2026-04-27T05:21:03.976081+00:00
