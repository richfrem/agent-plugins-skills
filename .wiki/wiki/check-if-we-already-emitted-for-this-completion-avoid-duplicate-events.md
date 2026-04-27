---
concept: check-if-we-already-emitted-for-this-completion-avoid-duplicate-events
source: plugin-code
source_file: exploration-cycle-plugin/hooks/session_end.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.975684+00:00
cluster: exploration
content_hash: 5bc5218a4ffeec9e
---

# Check if we already emitted for this completion (avoid duplicate events)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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


def main() -> None:
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

        # Extract session name from dashboard for the summary
        session_name = "unknown"
        for line in content.splitlines():
            if line.startswith("**Session:**"):
                session_name = line.replace("**Session:**", "").strip()
                break

        summary = f"Exploration session complete: {session_name}"
        kernel_script = Path(project_dir) / "context" / "kernel.py"

        if kernel_script.exists():
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


## See Also

- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[check-for-broken-symlinks]]
- [[track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/hooks/session_end.py`
- **Indexed:** 2026-04-27T05:21:03.975684+00:00
