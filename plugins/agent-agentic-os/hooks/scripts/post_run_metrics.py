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
            # If 'metric' type failed (likely due to choice validation), retry as 'result'
            if "choice" in result.stderr.lower():
                cmd[cmd.index("--type") + 1] = "result"
                subprocess.run(cmd, check=True, capture_output=True)
            else:
                # Other error, try direct append as final fallback
                raise Exception(result.stderr)
                
    except Exception as e:
        # Final fallback: direct append
        try:
            events_log = project_root / "context" / "events.jsonl"
            with open(events_log, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e2:
            print(f"Failed to record metrics: {e2}")

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
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")
        }
    }

    emit_event(project_root, metrics)
    print(f"--- AGENTIC OS: SESSION METRICS CAPTURED ({cli_errors} errors, {friction_events} friction events) ---")

if __name__ == "__main__":
    main()
