#!/usr/bin/env python3
"""
create_task.py (CLI)
=====================================
Purpose:
    Determines the next sequential Kanban task number by scanning all
    lanes (backlog, todo, in-progress, done), reads the generic task
    template, and scaffolds the new task in the specified target lane.

Usage Examples:
    python3 create_task.py --title "Fix login bug" --dir tasks/ --lane todo
"""
import argparse
import os
import re
import sys
from pathlib import Path


def get_next_task_number(root_dir: str) -> int:
    path = Path(root_dir)
    if not path.exists() or not path.is_dir():
        return 1

    highest = 0
    pattern = re.compile(r"^(\d{4})-.*\.md$")
    
    # Check all subdirectories
    for root, dirs, files in os.walk(path):
        for filename in files:
            match = pattern.match(filename)
            if match:
                num = int(match.group(1))
                if num > highest:
                    highest = num
                
    return highest + 1


def sanitize_title(title: str) -> str:
    # Convert to lowercase and replace non-alphanumeric with hyphens
    clean = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return clean


def create_task(title: str, root_dir: str, lane: str):
    script_dir = Path(__file__).parent.resolve()
    # The template is located at plugins/task-manager/templates/task-template.md
    template_path = script_dir.parent.parent.parent / "templates" / "task-template.md"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    target_dir = Path(root_dir) / lane
    target_dir.mkdir(parents=True, exist_ok=True)

    next_num = get_next_task_number(root_dir)
    num_str = f"{next_num:04d}"
    
    safe_title = sanitize_title(title)
    filename = f"{num_str}-{safe_title}.md"
    filepath = target_dir / filename
    
    # Read template and replace placeholders
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("NNNN", num_str)
    content = content.replace("[Title]", title)
    
    filepath.write_text(content, encoding="utf-8")
    
    # Output the created filepath so the agent can capture it
    print(str(filepath))


def main():
    parser = argparse.ArgumentParser(description="Create a new task from a template.")
    parser.add_argument("--title", required=True, help="The title of the task")
    parser.add_argument("--dir", default="tasks", help="Root directory of the kanban board. Defaults to 'tasks/'.")
    parser.add_argument("--lane", default="todo", help="Target lane folder (e.g., backlog, todo). Defaults to 'todo'.")
    args = parser.parse_args()
    
    create_task(args.title, args.dir, args.lane)


if __name__ == "__main__":
    main()
