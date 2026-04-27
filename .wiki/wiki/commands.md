---
concept: commands
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/task-agent/scripts/task_manager.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.426356+00:00
cluster: task
content_hash: 1ab6c80a1e2dd949
---

# ─── Commands ────────────────────────────────────────

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/task-agent/scripts/task_manager.py -->
"""
Lightweight Kanban Task Manager
==================================================

Purpose:
    Markdown-backed task board with lane directories: backlog, todo, in-progress, done.
    Each task is a Markdown file (NNNN-title.md) stored in its lane directory.
    Centralized CLI for all task management and kanban board operations.

Layer: Plugin / Task-Manager

Usage Examples:
    python3 ./scripts/task_manager.py create "Fix login bug" --lane todo
    python3 ./scripts/task_manager.py list
    python3 ./scripts/task_manager.py board

Supported Object Types:
    - None (Kanban operations)

CLI Arguments:
    create Title: Create task.
    list: List tasks.
    move ID Lane: Move task.
    get ID: View task.
    search Query: Search task.
    board: View kanban board.

Input Files:
    - templates/task-template.md (Template)

Output:
    - Prints lists, boards, and create responses.

Key Functions:
    cmd_create(): Creates task file in lane.
    cmd_move(): Moves task file to new lane dir.

Script Dependencies:
    os, sys, re, argparse, pathlib

Consumed by:
    - Manual workflow execution
Related:
    - scripts/next_number.py
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

SCRIPT_DIR = Path(__file__).parent.resolve()
PLUGIN_ROOT = SCRIPT_DIR.parents[2]

VALID_LANES = ["backlog", "todo", "in-progress", "done"]
LANE_ICONS = {
    "backlog": "📋",
    "todo": "📝",
    "in-progress": "🔨",
    "done": "✅",
}
TASK_PATTERN = re.compile(r"^(\d{4})-(.*?)\.md$")


def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[4]

PROJECT_ROOT = _find_project_root(Path(__file__))
TEMPLATE_PATH = PLUGIN_ROOT / "templates" / "task-template.md"


def _sanitize_title(title: str) -> str:
    """Convert title to kebab-case filename segment."""
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def _get_next_number(tasks_dir: Path) -> int:
    """Scan all lanes for the highest task number."""
    highest = 0
    for lane in VALID_LANES:
        lane_dir = tasks_dir / lane
        if not lane_dir.exists():
            continue
        for f in lane_dir.iterdir():
            match = TASK_PATTERN.match(f.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def _find_task(tasks_dir: Path, task_number: int) -> Optional[Tuple[Path, str]]:
    """Find a task file across all lanes. Returns (filepath, lane) or None."""
    num_str = f"{task_number:04d}"
    for lane in VALID_LANES:
        lane_dir = tasks_dir / lane
        if not lane_dir.exists():
            continue
        for f in lane_dir.iterdir():
            if f.name.startswith(num_str) and f.suffix == '.md':
                return (f, lane)
    return None


def _get_all_tasks(tasks_dir: Path, lane_filter: Optional[str] = None) -> List[Tuple[Path, str, int, str]]:
    """Get all tasks as (filepath, lane, number, title). Optionally filter by lane."""
    tasks = []
    lanes = [lane_filter] if lane_filter else VALID_LANES
    for lane in lanes:
        lane_dir = tasks_dir / lane
        if not lane_dir.exists():
            continue
        for f in sorted(lane_dir.iterdir()):
            match = TASK_PATTERN.match(f.name)
            if match:
                num = int(match.group(1))
                title = match.group(2).replace("-", " ").title()
                tasks.append((f, lane, num, title))
    tasks.sort(key=lambda t: t[2])
    return tasks


# ─── Commands ────────────────────────────────────────

def cmd_create(tasks_dir: Path, title: str, lane: str = "todo",
               objective: str = "", acceptance: str = "") -> None:
    """Create a new task in the specified lane."""
    if lane not in VALID_LANES:
        print(f"❌ Invalid lane '{lane}'. Must be: {', '.joi

*(content truncated)*

<!-- Source: plugin-code/task-manager/scripts/task_manager.py -->
"""
Lightweight Kanban Task Manager
==================================================

Purpose:
    Markdown-backed task board with lane directories: backlog, todo, in-progress, done.
    Each task is a Markdown file (NNNN-title.md) stored in its lane directory.
    Centralized CLI for all task management and kanban board operations.

Layer: Plugin / Task-Manager

Usage Examples:
    python ./scripts/task_manager.py create "Fix login bug" --lane todo
    python ./scripts/task_manager.py list
    python ./scripts/task_manager.py board

Supported Object Types:
    - None (Kanban operations)

CLI Arguments:
    create Title: Create task.
    list: List tasks.
    move ID Lane: Move task.
    get ID: View task.
    search Query: Search task.
    board: View kanban board.

Input Files:
    - templates/tas

*(combined content truncated)*

## See Also

- [[commands-that-are-unconditionally-safe-and-bypass-further-checks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/task-agent/scripts/task_manager.py`
- **Indexed:** 2026-04-27T05:21:04.426356+00:00
