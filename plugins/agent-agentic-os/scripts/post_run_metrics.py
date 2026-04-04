#!/usr/bin/env python3
"""
post_run_metrics.py — Automated Metric Collection Hook
======================================================

Purpose:
    Automated Post-Run Metric Collection. Scans events.jsonl to count friction,
    intervention, and error events, then emits a 'type: metric' event to the Event Bus.

Layer: 
    Hooks / Operations

Usage Examples:
    python3 post_run_metrics.py --correlation-id abc-123

Supported Object Types:
    - JSONL Event Logs
    - Terminal Metrics

CLI Arguments:
    --correlation-id       Scope counting to a single cycle only

Input Files:
    - context/events.jsonl
    - context/memory/hook-errors.log

Output:
    - Emits a 'type: metric' event via kernel.py

Key Functions:
    _count_events()
    count_hook_errors()
    emit_event()

Script Dependencies:
    - None

Consumed by:
    - Stop hook (hooks.json)
"""

import json
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def emit_event(project_root: Path, event_data: dict) -> None:
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



def _count_events(events_log: Path, correlation_id: "str | None" = None) -> dict:
    """
    Count metrics from events.jsonl.

    When correlation_id is provided, only events matching that cycle are counted
    (prevents double-counting when multiple loop cycles run in the same session).
    When absent, all events are counted (Stop hook context).

    Friction subtypes mapped from action field:
      human_rescue       -> human_interventions
      uncertainty        -> workflow_uncertainty
      missed_step        -> missed_steps
      wrong_cli / error  -> cli_errors
    """
    counts = {
        "human_interventions": 0,
        "workflow_uncertainty": 0,
        "missed_steps": 0,
        "cli_errors": 0,
        "friction_events_total": 0,
    }
    if not events_log.exists():
        return counts

    try:
        with open(events_log, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Scope to cycle when correlation_id provided
                if correlation_id and event.get("correlation_id") != correlation_id:
                    continue

                # Count status=error events (CLI errors from any agent)
                if event.get("status") == "error":
                    counts["cli_errors"] += 1

                evt_type = event.get("type", "")
                evt_action = event.get("action", "")

                if evt_type == "friction":
                    counts["friction_events_total"] += 1
                    action_lower = evt_action.lower()
                    if "human_rescue" in action_lower or "rescue" in action_lower:
                        counts["human_interventions"] += 1
                    elif "uncertainty" in action_lower or "unknown" in action_lower:
                        counts["workflow_uncertainty"] += 1
                    elif "missed_step" in action_lower or "skipped" in action_lower:
                        counts["missed_steps"] += 1
                    elif "wrong_cli" in action_lower or "cli_error" in action_lower:
                        counts["cli_errors"] += 1
    except Exception:
        pass  # Never crash the hook - return what we have

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agentic OS: Post-Run Metric Collection"
    )
    parser.add_argument(
        "--correlation-id",
        default=None,
        help="Scope event counting to this CYCLE_ID only. "
             "Prevents double-counting when multiple loop cycles run in one session."
    )
    args = parser.parse_args()

    target_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    project_root = Path(target_dir).resolve()
    events_log = project_root / "context" / "events.jsonl"

    counts = _count_events(events_log, correlation_id=args.correlation_id)
    hook_errors = count_hook_errors(project_root)

    # NOTE: North star regression check (_check_north_star_regression) is intentionally NOT
    # called here. The Stop hook fires before ORCHESTRATOR writes Section 3 of the ledger,
    # so checking here would always read the prior session's data (fires one session late).
    # Instead, emit a pending event that ORCHESTRATOR reads during Triple-Loop completion.
    kernel_path = project_root / "context" / "kernel.py"
    if kernel_path.exists():
        try:
            subprocess.run([
                "python3", str(kernel_path), "emit_event",
                "--agent", "post_run_hook",
                "--type", "metric",
                "--action", "north_star_check_pending",
                "--status", "success",
                "--summary", "ORCHESTRATOR must run _check_north_star_regression during Triple-Loop completion checks"
            ], capture_output=True)
        except Exception:
            pass

    metrics = {
        "time": datetime.now(tz=timezone.utc).isoformat(),
        "agent": "post_run_hook",
        "type": "metric",
        "action": "session_summary",
        "status": "success",
        "results": {
            "human_interventions": counts["human_interventions"],
            "workflow_uncertainty": counts["workflow_uncertainty"],
            "missed_steps": counts["missed_steps"],
            "cli_errors": counts["cli_errors"],
            "friction_events_total": counts["friction_events_total"],
            "hook_errors": hook_errors,
            "correlation_id": args.correlation_id or "session",
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")
        }
    }

    emit_event(project_root, metrics)

    scope = f"cycle:{args.correlation_id}" if args.correlation_id else "full session"
    summary = (
        f"--- AGENTIC OS: SESSION METRICS CAPTURED ({scope}) "
        f"human_interventions:{counts['human_interventions']} "
        f"friction:{counts['friction_events_total']} "
        f"cli_errors:{counts['cli_errors']}"
    )
    if hook_errors > 0:
        summary += f" HOOK_FAILURES:{hook_errors} (check context/memory/hook-errors.log)"
    summary += " ---"
    print(summary)


if __name__ == "__main__":
    main()
