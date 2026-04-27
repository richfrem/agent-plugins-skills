---
concept: sample-payloads-keyed-by-claude-code-event-type-name
source: plugin-code
source_file: agent-scaffolders/scripts/test_hook.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.840025+00:00
cluster: test
content_hash: c0ca9317f47237ba
---

# Sample payloads keyed by Claude Code event type name

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
test_hook.py
=====================================

Purpose:
    Test runner for Claude Code hook scripts. Accepts a hook script path and
    a JSON input file, pipes the input to the hook via subprocess, and reports
    the exit code, duration, stdout/stderr output, and parsed JSON decision.
    Also supports generating sample input payloads via --create-sample.

Layer: Investigate

Usage:
    python test_hook.py [options] <hook-script> <test-input.json>
    python test_hook.py --create-sample PreToolUse
    python test_hook.py -v -t 30 validate_write.py write-input.json
"""
import sys
import os
import json
import argparse
import subprocess
import time

_SEPARATOR = "━" * 40

# Sample payloads keyed by Claude Code event type name
_SAMPLES: dict = {
    "PreToolUse": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/test.txt", "content": "Test content"},
    },
    "PostToolUse": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_result": "Command executed successfully",
    },
    "Stop": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "Stop",
        "reason": "Task appears complete",
    },
    "UserPromptSubmit": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "UserPromptSubmit",
        "user_prompt": "Test user prompt",
    },
    "SessionStart": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "SessionStart",
    },
}
_SAMPLES["SubagentStop"] = {**_SAMPLES["Stop"], "hook_event_name": "SubagentStop"}
_SAMPLES["SessionEnd"] = {**_SAMPLES["SessionStart"], "hook_event_name": "SessionEnd"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Print a sample JSON payload for the requested event type and exit
def _create_sample(event_type: str) -> None:
    """
    Print a JSON sample payload for the given event type.

    Args:
        event_type: One of the valid Claude Code hook event names.

    Raises:
        SystemExit: Code 1 if the event type is unknown; code 0 on success.
    """
    if event_type not in _SAMPLES:
        print(f"Unknown event type: {event_type}")
        print(f"Valid types: {', '.join(_SAMPLES)}")
        sys.exit(1)
    print(json.dumps(_SAMPLES[event_type], indent=2))
    sys.exit(0)


# Build the subprocess command list to run the hook script
def _build_cmd(hook_script: str) -> list:
    """
    Determine the execution command for a hook script.

    Python scripts are run via `python`; others are tried directly, falling
    back to `bash` if not executable.

    Args:
        hook_script: Path to the hook script file.

    Returns:
        List of command components suitable for subprocess.run().
    """
    if hook_script.endswith(".py"):
        return ["python", hook_script]
    if os.access(hook_script, os.X_OK):
        return [hook_script]
    print("⚠️  Warning: Hook script is not executable. Attempting to run with bash...")
    return ["bash", hook_script]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# E

*(content truncated)*

## See Also

- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[extract-module-name]]
- [[file-type-classification]]
- [[file-type-handlers]]
- [[ordered-list-of-marker-files-label-env-vars-for-project-type-detection]]
- [[patterns-to-find-file-references-in-code]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/test_hook.py`
- **Indexed:** 2026-04-27T05:21:03.840025+00:00
