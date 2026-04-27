---
concept: fallback-to-appending-directly-if-kernel-is-missing
source: plugin-code
source_file: agent-agentic-os/scripts/post_run_metrics.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.287525+00:00
cluster: events
content_hash: 4c9c39896284a688
---

# Fallback to appending directly if kernel is missing

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/scripts/post_run_metrics.py -->
#!/usr/bin/env python
"""
post_run_metrics.py — Automated Metric Collection Hook
======================================================

Purpose:
    Automated Post-Run Metric Collection. Scans events.jsonl to count friction,
    intervention, and error events, then emits a 'type: metric' event to the Event Bus.

Layer: 
    Hooks / Operations

Usage Examples:
    pythonpost_run_metrics.py --correlation-id abc-123

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
            "python, str(kernel_path), "emit_event",
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
      wrong

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-improvement-loop/scripts/post_run_metrics.py -->
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

Scri

*(combined content truncated)*

## See Also

- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/post_run_metrics.py`
- **Indexed:** 2026-04-27T05:21:04.287525+00:00
