---
concept: 1-parse-the-hook-payload
source: plugin-code
source_file: agent-agentic-os/hooks/update_memory.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.691722+00:00
cluster: json
content_hash: 103ba541c1483520
---

# 1. Parse the hook payload

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
update_memory.py — Memory Update Hook
======================================================

Purpose:
    Called via PostToolUse and SessionStart hooks.
    Creates or appends to a dated session log in context/memory/YYYY-MM-DD.md
    on file writes, unless the file is volatile (MEMORY.md, status.md).

Layer: 
    Hooks / Lifecycle

Usage Examples:
    Called automatically by agent runner hooks interface with sys.argv[1] JSON payload

Supported Object Types:
    - Event payloads (SessionStart, PostToolUse)

CLI Arguments:
    sys.argv[1]             JSON payload describing tool triggers or start contexts

Input Files:
    - context/os-state.json
    - context/events.jsonl

Output:
    - Appends events inside context/events.jsonl via direct lock appends

Key Functions:
    _check_execution_gate() Determines lightweight vs heavy mode execution paths
    main()                  Main controller multiplexing hooks into audit items

Script Dependencies:
    - None (Uses standard python imports)

Consumed by:
    - SessionStart or PostToolUse hook dispatch wrappers
"""
import os
import sys
import json
import collections
from datetime import datetime
from pathlib import Path

def _check_execution_gate() -> bool:
    """Return True if the hook should proceed, False if it should be skipped.
    Reads execution_mode and hook_sample_rate from os-state.json.
    - execution_mode=lightweight: always skip
    - hook_sample_rate=N: run 1 in every N calls (counter stored in os-state.json)
    """
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        state_file = Path(project_dir) / "context" / "os-state.json"
        if not state_file.exists():
            return True  # No state file: proceed normally

        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        if state.get("execution_mode") == "lightweight":
            return False

        rate = int(state.get("hook_sample_rate", 1))
        if rate > 1:
            count = int(state.get("hook_call_count", 0)) + 1
            state["hook_call_count"] = count
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            if count % rate != 0:
                return False
    except Exception:
        pass  # If state is unreadable, proceed normally
    return True


def main() -> None:
    if not _check_execution_gate():
        return

    try:
        # 1. Parse the hook payload
        if len(sys.argv) > 1:
            try:
                payload = json.loads(sys.argv[1])
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}

        event_type = payload.get("event", "SessionStart")
        
        # We only care about file modifications for PostToolUse
        if event_type == "PostToolUse":
            tool_name = payload.get("toolName", "")
            if tool_name not in ["Write", "Replace", "write_to_file", "multi_replace_file_content"]:
                return
            
            tool_input = payload.get("toolInput", {})
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    tool_input = {}
                    
            if not isinstance(tool_input, dict):
                return
                
            # Try to figure out the target file from common arguments
            raw_target = tool_input.get("TargetFile") or tool_input.get("file_path") or tool_input.get("path", "")
            if not raw_target:
                return
                
            # Cross-Platform Normalization
            target_path = Path(raw_target)
                
            # Skip volatile memory files
            volatile_files = ["MEMORY.md", "status.md", "CLAUDE.md", "os-state.json", "events.jsonl"]
            if target_path.name in volatile_f

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[result-type-tells-downstream-tools-how-to-parse-the-entry]]
- [[1-basic-summarize-all-documents]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/hooks/update_memory.py`
- **Indexed:** 2026-04-27T05:21:03.691722+00:00
