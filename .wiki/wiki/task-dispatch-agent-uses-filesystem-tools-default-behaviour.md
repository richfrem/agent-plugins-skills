---
concept: task-dispatch-agent-uses-filesystem-tools-default-behaviour
source: plugin-code
source_file: copilot-cli/scripts/run_agent.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.963427+00:00
cluster: instruction
content_hash: 68bf71571276f2aa
---

# Task dispatch (agent uses filesystem tools — default behaviour):

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
copilot-run-agent (CLI)
=====================================

Purpose:
    Orchestrates a Copilot CLI sub-agent execution by assembling a persona,
    input context, and instruction for specific model invocation.

Layer: Codify

Usage Examples:
    # Task dispatch (agent uses filesystem tools — default behaviour):
    python scripts/run_agent.py /dev/null tasks/todo/my_prompt.md temp/out.md \
        "Implement all changes." claude-sonnet-4.6

    # Analysis only (isolated, no tools):
    python scripts/run_agent.py agents/security-auditor.md target.py output.md \
        "Review this." gpt-5-mini false

    # Heartbeat check:
    python scripts/run_agent.py /dev/null /dev/null temp/hb.md \
        "HEARTBEAT CHECK: Respond with HEARTBEAT_OK only."

Prompt assembly rules:
    - persona present + input present  → persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
    - input present, no persona        → input / ---INSTRUCTION--- instruction  (task-dispatch mode)
    - instruction only (both /dev/null)→ instruction only
    - isolated=true appends:          "You are operating as an isolated sub-agent. Do NOT use tools."

CLI Arguments:
    persona_file  Path to agent persona markdown, or /dev/null to skip.
    input_file    Path to task prompt or source file, or /dev/null to skip.
    output_file   Path where output is saved (streamed live to stdout as well).
    instruction   Specific task instruction string.
    model         AI model identifier (default: gpt-5-mini).
    isolated      "true" to block tool use; default "false". Pass explicitly when
                  running analysis-only tasks where filesystem writes are unsafe.

Script Dependencies:
    subprocess, os, sys, tempfile

Consumed by:
    - Antigravity AI Agent
    - CLI users in the agent-plugins-skills ecosystem
"""

import sys
import os
import subprocess
import tempfile


def resolve_path(provided_path: str) -> str:
    """Resolve path against CWD then plugin root, return as-is if neither exists."""
    if os.path.exists(provided_path):
        return provided_path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.dirname(script_dir)
    fallback = os.path.join(plugin_root, provided_path)
    return fallback if os.path.exists(fallback) else provided_path


def read_file_or_empty(path: str) -> str:
    """Read file content; return empty string for /dev/null or missing files."""
    if path in ("/dev/null", "nul", "") or not os.path.exists(path):
        return ""
    try:
        with open(path, 'r') as f:
            return f.read()
    except (OSError, IOError):
        return ""


def build_prompt(persona_content: str, input_content: str, instruction: str, isolated: bool) -> str:
    """
    Assemble the final prompt from available parts.

    Three modes:
      - Full (persona + input): persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
      - Task dispatch (input only): input / ---INSTRUCTION--- instruction
      - Instruction only (heartbeat etc.): instruction
    """
    parts = []

    has_persona = bool(persona_content.strip())
    has_input = bool(input_content.strip())
    has_instruction = bool(instruction.strip())

    if has_persona:
        parts.append(persona_content)

    if has_input:
        # Wrap in SOURCE block only when a persona is also present
        parts.append(f"---SOURCE---\n{input_content}" if has_persona else input_content)

    if has_instruction:
        label = "---INSTRUCTION---\n" if (has_persona or has_input) else ""
        parts.append(f"{label}{instruction}")

    if isolated:
        parts.append(
            "You are operating as an isolated sub-agent. "
            "Do NOT use tools. Do NOT access filesystem. Only use the provided input."
        )

    # Leading newline prevents CLI from misinterpreting a prompt starting with '---' as a flag
    return "\n\n".join(["\n"] + parts)


def run_agent(
    persona_file: str,
    input_file

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[agent-agentic-os-hooks]]
- [[agent-bridge]]
- [[agent-harness-learning-layer]]
- [[agent-loops-execution-primitives]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `copilot-cli/scripts/run_agent.py`
- **Indexed:** 2026-04-27T05:21:03.963427+00:00
