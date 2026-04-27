---
concept: file-type-classification
source: plugin-code
source_file: agent-scaffolders/scripts/inventory_plugin.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.346081+00:00
cluster: plugin
content_hash: f0598170626a2f99
---

# ── File Type Classification ──────────────────────────────────────────

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/inventory_plugin.py -->
#!/usr/bin/env python
"""
inventory_plugin.py (CLI)
=====================================

Purpose:
    Deterministically inventories all files in a plugin or plugin collection,
    classifying each by type, counting lines, and detecting compliance issues.

Layer: Meta-Execution

Usage Examples:
    pythonentory_plugin.py --path <plugin-dir> --format json
    pythonentory_plugin.py --path <plugin-dir> --format markdown
    pythonentory_plugin.py --path <plugin-dir> --format checklist

CLI Arguments:
    --path: The path to the plugin or plugin collection directory.
    --format: Output format (json, markdown, checklist). Default: markdown.
    --recursive: If set, treat path as a collection and inventory each subdirectory.
    --no-security: Disable deterministic security scans (enabled by default).

Output:
    Structured inventory to stdout in the requested format.

Script Dependencies:
    None (standard library only)

Consumed by:
    - analyze-plugin (Agent Skill)
    - mine-plugins (Command)
"""
import argparse
import json
import os
import re
import sys


# ── File Type Classification ──────────────────────────────────────────

FILE_TYPE_MAP = {
    "SKILL.md": "skill",
    "README.md": "readme",
    "CONNECTORS.md": "connectors",
    "QUICKREF.md": "quickref",
    "CLAUDE.md": "claude-config",
    "plugin.json": "manifest",
    "marketplace.json": "marketplace",
    ".mcp.json": "mcp-config",
    "mcp.json": "mcp-config",
    "hooks.json": "hooks-config",
    "lsp.json": "lsp-config",
    "requirements.txt": "dependencies",
    "requirements.in": "dependencies",
}

EXT_TYPE_MAP = {
    ".md": "document",
    ".py": "script",
    ".json": "config",
    ".yaml": "config",
    ".yml": "config",
    ".html": "artifact-template",
    ".mmd": "diagram",
    ".png": "image",
    ".jpg": "image",
    ".txt": "text",
    ".jinja": "template",
}

COMMANDS_DIR = "commands"
REFERENCES_DIR = "references"
REFERENCE_DIR = "reference"
SCRIPTS_DIR = "scripts"
EXAMPLES_DIR = "examples"
TEMPLATES_DIR = "templates"
AGENTS_DIR = "agents"
SETTINGS_DIR = "settings"


def classify_file(filepath: str, relpath: str) -> str:
    """Classify a file by its type based on name, extension, and location."""
    basename = os.path.basename(filepath)
    _, ext = os.path.splitext(basename)
    parts = relpath.split(os.sep)

    # Check exact filename matches first
    if basename in FILE_TYPE_MAP:
        return FILE_TYPE_MAP[basename]

    # Check location-based classification
    if COMMANDS_DIR in parts:
        return "command"
    if AGENTS_DIR in parts:
        return "agent"
    if REFERENCES_DIR in parts or REFERENCE_DIR in parts:
        return "reference"
    if SCRIPTS_DIR in parts:
        return "script"
    if EXAMPLES_DIR in parts:
        return "example"
    if TEMPLATES_DIR in parts:
        return "template"
    if SETTINGS_DIR in parts:
        return "settings"

    # Fall back to extension
    if ext in EXT_TYPE_MAP:
        return EXT_TYPE_MAP[ext]

    return "other"


def count_lines(filepath: str) -> int:
    """Count lines in a text file. Returns -1 for binary files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="strict") as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, ValueError):
        return -1


def detect_issues(filepath: str, relpath: str, file_type: str, line_count: int) -> list[str]:
    """Detect Open Standards compliance issues."""
    issues = []
    basename = os.path.basename(filepath)

    # SKILL.md over 500 lines
    if basename == "SKILL.md" and line_count > 500:
        issues.append(f"SKILL.md exceeds 500 lines ({line_count} lines)")

    # Bash or PowerShell scripts
    if basename.endswith(".sh"):
        issues.append("Bash script detected — only Python (.py) is allowed")
    if basename.endswith(".ps1"):
        issues.append("PowerShell script detected — only Python (.py) is allowed")

    return issues


# ── Security Scanning ────────────────────────

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/analyze-plugin/references/inventory_plugin.py -->
#!/usr/bin/env python3
"""
inventory_plugin.py (CLI)
=====================================

Purpose:
    Deterministically inventories all files in a plugin or plugin collection,
    classifying each by type, counting lines, and detecting compliance issues.

Layer: Meta-Execution

Usage Examples:
    python3 inventory_plugin.py --path <plugin-dir> --format json
    python3 inventory_plugin.py --path <plugin-dir> --format markdown
    python3 inventory_plugin.py --path <plugin-dir> --format checklist

CLI Arguments:
    --path: The path to the plugin or plugin collection directory.
    --format: Output format (json, markdown, checklist). Default: markdown.
    --recursive: If set, treat path as a collection and inventory each subdirectory.
    --no-security: Disable deterministic se

*(combined content truncated)*

## See Also

- [[file-type-handlers]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[audit-a-single-file]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[file-manifest]]
- [[file-manifest-schema]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/inventory_plugin.py`
- **Indexed:** 2026-04-27T05:21:04.346081+00:00
