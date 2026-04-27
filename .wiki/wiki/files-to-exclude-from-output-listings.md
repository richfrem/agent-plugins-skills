---
concept: files-to-exclude-from-output-listings
source: plugin-code
source_file: agent-scaffolders/scripts/eval-viewer/generate_review.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.209676+00:00
cluster: workspace
content_hash: dc59c1018d9d5b5a
---

# Files to exclude from output listings

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/eval-viewer/generate_review.py -->
#!/usr/bin/env python
"""
generate_review.py (CLI/Dashboard)
=====================================

Purpose:
    Generate and serve a standalone review page for evaluation workspaces.
    Discovers run outputs, embeds all data into an HTML template, and serves via tiny HTTP server.
    Feedback auto-saves to feedback.json inside the workspace.

Layer: User Interface/Dashboard

Usage Examples:
    python generate_review.py <workspace-path> [--port PORT] [--skill-name NAME]

Supported Object Types:
    - Eval workspace directories containing outputs/ Subdirectories

CLI Arguments:
    workspace: Path to review workspace
    --port, -p: Server port override (default 3117)
    --skill-name, -n: Name override for dashboard header
    --previous-workspace: Show comparisons against previous iterations
    --benchmark: Path to benchmark.json results
    --static, -s: Write standalone HTML file instead of serving

Input Files:
    - Workspace directories
    - feedback.json (read/write)
    - benchmark.json

Output:
    - HTML standalone review dashboard
    - feedback.json append commits

Key Functions:
    - find_runs(): Scans nested directories for evaluation artifacts.
    - generate_html(): Binds variables into viewer.html scripts.

Script Dependencies:
    - http.server, base64, mimetypes, webbrowser, functools

Consumed by:
    - User (Browser)
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import time
import webbrowser
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Files to exclude from output listings
METADATA_FILES = {"transcript.md", "user_notes.md", "metrics.json"}

# Extensions we render as inline text
TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".yaml", ".yml", ".xml", ".html", ".css", ".sh", ".rb", ".go", ".rs",
    ".java", ".c", ".cpp", ".h", ".hpp", ".sql", ".r", ".toml",
}

# Extensions we render as inline images
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

# MIME type overrides for common types
MIME_OVERRIDES = {
    ".svg": "image/svg+xml",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def get_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def find_runs(workspace: Path) -> list[dict]:
    """Recursively find directories that contain an outputs/ subdirectory."""
    runs: list[dict] = []
    _find_runs_recursive(workspace, workspace, runs)
    runs.sort(key=lambda r: (r.get("eval_id", float("inf")), r["id"]))
    return runs


def _find_runs_recursive(root: Path, current: Path, runs: list[dict]) -> None:
    if not current.is_dir():
        return

    outputs_dir = current / "outputs"
    if outputs_dir.is_dir():
        run = build_run(root, current)
        if run:
            runs.append(run)
        return

    skip = {"node_modules", ".git", "__pycache__", "skill", "inputs"}
    for child in sorted(current.iterdir()):
        if child.is_dir() and child.name not in skip:
            _find_runs_recursive(root, child, runs)


def build_run(root: Path, run_dir: Path) -> dict | None:
    """Build a run dict with prompt, outputs, and grading data."""
    prompt = ""
    eval_id = None

    # Try eval_metadata.json
    for candidate in [run_dir / "eval_metadata.json", run_dir.parent / "eval_metadata.json"]:
        if candidate.exists():
            try:
                metadata = json.loads(candidate.read_text())
                prompt = metadata.get("prompt", "")
                eval_id = metadata.get("eval

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/generate_review.py -->
#!/usr/bin/env python
"""
generate_review.py
=====================================

Purpose:
    Generates and serves a standalone self-contained review page dashboard 
    using embeds of evaluation runs outputs and dynamic HTTP saves for local audits.

Layer: Investigate / Synthesis

Usage Examples:
    pythongenerate_review.py path/to/workspace --port 3117
    pythongenerate_review.py path/to/workspace --static report_viewer.html

Supported Object Types:
    Workspace execution bundles containing iterative output artifacts.

CLI Arguments:
    workspace: Workspace directory index.
    --port|-p: Port to bind dashboard daemon on (default: 3117)
    --skill-name|-n: Label prefix displayed on header items.
    --previous-workspace: Show prior loops feedback comparison metadata.
    --benchmark: Include b

*(combined content truncated)*

## See Also

- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[load-input-from-files-or-stdin]]
- [[prefer-remaining-broken-linksjson-post-fix-output-from-step-4-if-present-and]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/eval-viewer/generate_review.py`
- **Indexed:** 2026-04-27T05:21:04.209676+00:00
