---
concept: 1-read-the-agent-instructions-and-strip-yaml-frontmatter
source: plugin-code
source_file: exploration-cycle-plugin/scripts/dispatch.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.235915+00:00
cluster: file
content_hash: d1d7ebc22acec401
---

# 1. Read the agent instructions and strip YAML frontmatter.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/exploration-cycle-plugin/scripts/dispatch.py -->
#!/usr/bin/env python
"""
dispatch.py (CLI)
=====================================

Purpose:
    Safely dispatches multi-file context to a CLI backend (claude, gh copilot, or copilot)
    using embedded prompting. Replaces brittle Bash string concatenation.
    Default backend: claude (--cli claude). Override with --cli copilot or --cli gh-copilot.

Layer: Infrastructure / Tooling

Usage Examples:
    pythondispatch.py --agent agent.md --context brief.md captures.md --instruction "Mode: run" --output out.md
    pythondispatch.py --agent agent.md --context brief.md --optional-context prototype-notes.md --instruction "Mode: run" --output out.md

Supported Object Types:
    Any text-based plugin artifacts

CLI Arguments:
    --agent: path to the agent markdown file
    --context: one or more paths to required context files (missing = fatal)
    --optional-context: one or more paths to optional context files (missing = silently skipped)
    --instruction: the explicit prompt command for the agent
    --output: file path to save the generated output
    --timeout: subprocess timeout in seconds (default: 120)

Input Files:
    - Agent instructions (.md)
    - Context payload files (.md, .txt)

Output:
    - Target rendered artifact file

Key Functions:
    read_file(): Safe UTF-8 file reading with missing file handling
    read_optional_file(): Reads file if it exists, returns None if missing
    write_file(): Safe target directory creation and UTF-8 file writing
    validate_output(): Checks output is non-empty, has headers, meets minimum length
    main(): Argument parsing and subprocess Copilot orchestration

Script Dependencies:
    subprocess
    os
    sys
    argparse

Consumed by:
    exploration-cycle-orchestrator-agent.md
    exploration-workflow/SKILL.md
"""

import argparse
import re
import subprocess
import os
import sys

MIN_OUTPUT_CHARS = 500


def read_file(filepath: str) -> str:
    """Reads a required file. Exits non-zero if missing."""
    if not os.path.exists(filepath):
        print(f"Error: Could not find required file at '{filepath}'", file=sys.stderr)
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def read_optional_file(filepath: str) -> str | None:
    """Reads an optional file. Returns None silently if missing."""
    if not os.path.exists(filepath):
        print(f"Info: Optional file not found, skipping: '{filepath}'")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def write_file(filepath: str, content: str) -> None:
    """Safely writes content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')


def strip_leading_prose(content: str) -> str:
    """Strips conversational preamble before the first markdown section header.

    Claude CLI responses sometimes prepend a natural-language opener
    (e.g. "Here is the audit report:") before the structured document body.
    This trims everything before the first line starting with '#' so that
    validate_output() and the written artifact both start at the document root.

    If no '#' header is found, the original content is returned unchanged so
    that the header-presence check in validate_output() still fires correctly.
    """
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith('#'):
            stripped = ''.join(lines[i:])
            if i > 0:
                print(f"Info: Stripped {i} line(s) of leading prose before first section header.")
            return stripped
    return content


def validate_output(content: str, output_path: str) -> str | None:
    """Validates CLI output before writing to disk.

    Strips leading prose first (conversational openers before t

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/exploration-workflow/scripts/dispatch.py -->
#!/usr/bin/env python3
"""
dispatch.py (CLI)
=====================================

Purpose:
    Safely dispatches multi-file context to a CLI backend (claude, gh copilot, or copilot)
    using embedded prompting. Replaces brittle Bash string concatenation.
    Default backend: claude (--cli claude). Override with --cli copilot or --cli gh-copilot.

Layer: Infrastructure / Tooling

Usage Examples:
    python3 dispatch.py --agent agent.md --context brief.md captures.md --instruction "Mode: run" --output out.md
    python3 dispatch.py --agent agent.md --context brief.md --optional-context prototype-notes.md --instruction "Mode: run" --output out.md

Supported Object Types:
    Any text-based plugin artifacts

CLI Arguments:
    --agent: path to the agent markdown file
    --context: one or

*(combined content truncated)*

## See Also

- [[strip-yaml-frontmatter-from-skillmd-before-using-it-as-an-agent-prompt]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-parse-the-hook-payload]]
- [[optimize-agent-instructions]]
- [[parse-frontmatter-and-content]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/scripts/dispatch.py`
- **Indexed:** 2026-04-27T05:21:04.235915+00:00
