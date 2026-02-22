#!/usr/bin/env python3
"""
board.py (CLI)
=====================================
Purpose:
    Prints an ASCII Kanban board by reading the markdown files from
    the various lane directories.

Usage Examples:
    python3 board.py --dir tasks/
"""
import argparse
import os
import re
from pathlib import Path

LANES = ["backlog", "todo", "in-progress", "done"]
LANE_ICONS = {
    "backlog": "📋",
    "todo": "📝",
    "in-progress": "🔨",
    "done": "✅",
}

def print_board(root_dir: str):
    root = Path(root_dir)
    pattern = re.compile(r"^(\d{4})-(.*)\.md$")
    
    print(f"\n{'='*60}")
    print(f"  📋 KANBAN BOARD")
    print(f"{'='*60}")
    
    total = 0
    done = 0
    
    for lane in LANES:
        lane_dir = root / lane
        tasks = []
        
        if lane_dir.exists() and lane_dir.is_dir():
            for filename in os.listdir(lane_dir):
                match = pattern.match(filename)
                if match:
                    num = match.group(1)
                    title = match.group(2).replace("-", " ").title()
                    tasks.append((num, title))
        
        tasks.sort()  # Sort by task number
        icon = LANE_ICONS.get(lane, "📌")
        print(f"\n{icon} {lane.upper()} ({len(tasks)})")
        print(f"{'─'*40}")
        
        if not tasks:
            print(f"   (empty)")
        else:
            for num, title in tasks:
                print(f"   #{num} {title}")
                
        total += len(tasks)
        if lane == "done":
            done += len(tasks)
            
    print(f"\n{'='*60}")
    print(f"  Total: {total}  |  Done: {done}/{total}")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="Print the markdown kanban board.")
    parser.add_argument("--dir", default="tasks", help="Root directory of the kanban board. Defaults to 'tasks/'.")
    args = parser.parse_args()
    
    print_board(args.dir)

if __name__ == "__main__":
    main()
