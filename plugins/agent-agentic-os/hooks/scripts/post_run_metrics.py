#!/usr/bin/env python3
"""
Purpose: Automated Post-Run Metric Collection.
This script scans events.jsonl to auto-populate session metrics
and emits a final 'type: metric' (falling back to 'result') event to the Event Bus.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def emit_event(project_root, event_data):
    """
    Uses kernel.py to emit a structured event.
    Encodes results into --summary for maximum compatibility with older kernels.
    """
    kernel_path = project_root / "context" / "kernel.py"
    if not kernel_path.exists():
        # Fallback to appending directly if kernel is missing
        events_log = project_root / "context" / "events.jsonl"
        with open(events_log, "a") as f:
            f.write(json.dumps(event_data) + "\n")
        return

    # Use the kernel's CLI to emit the event
    # We use --summary to hold the JSON results for compatibility
    try:
        # Try 'metric' type, fallback to 'result' if the kernel is old
        event_type = event_data["type"]
        summary_payload = json.dumps(event_data["results"])
        # Truncate to prevent oversized CLI arguments. The kernel receives this
        # as a list-form subprocess arg (not shell=True), so there is no shell
        # injection risk, but we cap at 2048 chars as a defensive measure.
        if len(summary_payload) > 2048:
            summary_payload = summary_payload[:2048]

        cmd = [
            "python3", str(kernel_path), "emit_event",
            "--agent", event_data["agent"],
            "--type", event_type,
            "--action", event_data["action"],
            "--status", event_data["status"],
            "--summary", summary_payload
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # kernel.py accepts "metric" type natively; no fallback needed
            raise Exception(result.stderr)
                
    except Exception as e:
        # Final fallback: direct append
        try:
            events_log = project_root / "context" / "events.jsonl"
            with open(events_log, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e2:
            print(f"Failed to record metrics: {e2}")

def count_hook_errors(project_root: Path) -> int:
    """Count error lines written to hook-errors.log this session.
    Returns 0 if the log does not exist."""
    error_log = project_root / "context" / "memory" / "hook-errors.log"
    if not error_log.exists():
        return 0
    try:
        with open(error_log, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def main():
    target_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project_root = Path(target_dir).resolve()
    events_log = project_root / "context" / "events.jsonl"

    cli_errors = 0
    friction_events = 0

    if events_log.exists():
        with open(events_log, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("status") == "error":
                        cli_errors += 1
                    if event.get("type") == "friction":
                        friction_events += 1
                except json.JSONDecodeError:
                    continue

    hook_errors = count_hook_errors(project_root)

    metrics = {
        "time": datetime.utcnow().isoformat() + "Z",
        "agent": "post_run_hook",
        "type": "metric",
        "action": "session_summary",
        "status": "success",
        "results": {
            "human_interventions": 0,
            "workflow_uncertainty": 0,
            "missed_steps": 0,
            "cli_errors": cli_errors,
            "friction_events_total": friction_events,
            "hook_errors": hook_errors,
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")
        }
    }

    emit_event(project_root, metrics)
    summary = f"--- AGENTIC OS: SESSION METRICS CAPTURED ({cli_errors} errors, {friction_events} friction events"
    if hook_errors > 0:
        summary += f", {hook_errors} HOOK FAILURES - check context/memory/hook-errors.log"
    summary += ") ---"
    print(summary)

if __name__ == "__main__":
    main()
