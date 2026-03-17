#!/usr/bin/env python3
"""
Purpose: Automated Post-Run Metric Collection.
This script is triggered by the Claude Code 'SessionEnd' or 'PostToolUse' hook.
It prompts the agent to record session metrics into the Event Bus.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    # Identify the project root relative to this script
    # Expected location: CLAUDE_PLUGIN_ROOT/hooks/scripts/post_run_metrics.py
    # Project root is 3 levels up if executed from a .claude/hooks copy, 
    # but we should use environment variables if available.
    
    target_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not target_dir:
        # Fallback to current directory
        target_dir = os.getcwd()

    project_root = Path(target_dir).resolve()
    events_log = project_root / "context" / "events.jsonl"
    
    # We don't block the user, we just emit a template for the agent to fill
    # if it's running in an interactive session.
    
    metrics_template = {
        "time": datetime.utcnow().isoformat() + "Z",
        "agent": "self",
        "type": "metric",
        "action": "self_assessment",
        "status": "pending",
        "results": {
            "human_interventions": 0,
            "workflow_uncertainty": 0,
            "missed_steps": 0,
            "cli_errors": 0,
            "friction_events_total": 0,
            "one_change_to_test_next": "N/A"
        }
    }

    print("\n--- AGENTIC OS: SESSION METRICS REQUIRED ---")
    print("Please update 'context/events.jsonl' with your self-assessment metrics.")
    print("Use the following JSON structure as your 'type: metric' event:")
    print(json.dumps(metrics_template, indent=2))
    print("\n--- END METRICS REQUEST ---")

if __name__ == "__main__":
    main()
