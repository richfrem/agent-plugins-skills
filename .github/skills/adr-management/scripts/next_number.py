#!/usr/bin/env python3
"""
next_number.py (CLI)
=====================================

Purpose:
    Sequential Identifier Generator.
    Scans artifact directories (Specs, Tasks, ADRs, Chronicles, BRs, BWs) to find
    the next available sequence number. Prevents ID collisions.

Layer: Investigate / Utils

Usage Examples:
    python plugins/adr-manager/scripts/next_number.py --type spec
    python plugins/adr-manager/scripts/next_number.py --type task
    python plugins/adr-manager/scripts/next_number.py --type br
    python plugins/adr-manager/scripts/next_number.py --type all

CLI Arguments:
    --type          : Artifact type (spec, task, adr, chronicle, br, bw, all)

Input Files:
    - kitty-specs/
    - tasks/
    - ADRs/
    - legacy-system/business-rules/
    - legacy-system/business-workflows/

Output:
    - Next available ID (e.g. "0045") to stdout
    
Key Functions:
    - main(): Scans directories using regex patterns defined in ARTIFACT_TYPES.

Consumed by:
    - scripts/domain_cli.py (indirectly logic reference)
    - Manual workflow execution
"""
import os
import re
import sys
import argparse
from pathlib import Path

# Configuration: artifact types and their locations/patterns
ARTIFACT_TYPES = {
    "br": {
        "name": "Business Rule",
        "directory": "legacy-system/business-rules",
        "pattern": r"^BR-(\d{3})",
        "format": "BR-{:03d}",
        "prefix": "BR-"
    },
    "bw": {
        "name": "Business Workflow",
        "directory": "legacy-system/business-workflows",
        "pattern": r"^BW-(\d{3})",
        "format": "BW-{:03d}",
        "prefix": "BW-"
    },
    "task": {
        "name": "Maintenance Task",
        "directory": "tasks",
        "pattern": r"^(\d{3})",
        "format": "{:03d}",
        "prefix": "",
        "search_subdirs": True  # Search backlog, in-progress, done, superseded
    },
    "spec": {
        "name": "Specification",
        "directory": "specs",
        "pattern": r"^(\d{3})",
        "format": "{:03d}",
        "prefix": "",
        "scan_type": "directory"
    },
    "adr": {
        "name": "Architecture Decision Record",
        "directory": "docs/ADRs",
        "pattern": r"^(\d{3})",
        "format": "{:03d}",
        "prefix": ""
    }
}


def find_max_number(artifact_type: str, project_root: Path) -> int:
    """Find the maximum existing number for an artifact type."""
    config = ARTIFACT_TYPES.get(artifact_type)
    if not config:
        return 0
    
    base_dir = project_root / config["directory"]
    pattern = re.compile(config["pattern"])
    max_num = 0
    
    if config.get("search_subdirs"):
        dirs_to_search = [base_dir / "backlog", base_dir / "todo", base_dir / "in-progress", base_dir / "done", base_dir / "superseded"]
    else:
        dirs_to_search = [base_dir]
    
    scan_dirs = config.get("scan_type") == "directory"

    for search_dir in dirs_to_search:
        if not search_dir.exists():
            continue
        for item in search_dir.iterdir():
            # Check for directory or file based on config
            if scan_dirs:
                is_valid = item.is_dir()
            else:
                is_valid = item.is_file() and item.suffix == ".md"

            if is_valid:
                match = pattern.match(item.name)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)
    
    return max_num


def get_next_number(artifact_type: str, project_root: Path) -> str:
    """
    Get the next available number, filling gaps if they exist.
    """
    config = ARTIFACT_TYPES.get(artifact_type)
    if not config:
        raise ValueError(f"Unknown artifact type: {artifact_type}")
    
    base_dir = project_root / config["directory"]
    pattern = re.compile(config["pattern"])
    
    existing_numbers = set()
    
    if config.get("search_subdirs"):
        dirs_to_search = [base_dir / "backlog", base_dir / "todo", base_dir / "in-progress", base_dir / "done", base_dir / "superseded"]
    else:
        dirs_to_search = [base_dir]
    
    scan_dirs = config.get("scan_type") == "directory"

    for search_dir in dirs_to_search:
        if not search_dir.exists():
            continue
        for item in search_dir.iterdir():
             # Check for directory or file based on config
            if scan_dirs:
                is_valid = item.is_dir()
            else:
                is_valid = item.is_file() and item.suffix == ".md"

            if is_valid:
                match = pattern.match(item.name)
                if match:
                    existing_numbers.add(int(match.group(1)))
    
    # Find first unused number (gap filling)
    next_num = 1
    while next_num in existing_numbers:
        next_num += 1
    
    return config["format"].format(next_num)


def find_max_in_directory(directory: Path, pattern: str = r'(\d{3})', recursive: bool = True) -> int:
    """Find the maximum number in an arbitrary directory using a regex pattern."""
    if not directory.exists():
        return 0
    
    regex = re.compile(pattern)
    max_num = 0
    
    iterator = directory.rglob("*") if recursive else directory.iterdir()
    
    for file in iterator:
        if file.is_file():
            match = regex.search(file.name)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
    
    return max_num


def show_all(project_root: Path):
    """Show next numbers for all artifact types."""
    print("=" * 50)
    print("NEXT AVAILABLE NUMBERS")
    print("=" * 50)
    
    for type_key, config in ARTIFACT_TYPES.items():
        next_id = get_next_number(type_key, project_root)
        max_num = find_max_number(type_key, project_root)
        existing = max_num if max_num > 0 else "none"
        print(f"  {config['name']:30} : {next_id} (existing max: {existing})")


def main():
    parser = argparse.ArgumentParser(
        description='Get next available number for artifact types or arbitrary directories.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--type', '-t', 
                        choices=list(ARTIFACT_TYPES.keys()) + ['all'],
                        help='Artifact type')
    group.add_argument('--dir', '-d', help='Ad-hoc directory to scan for 4-digit numbers')
    
    parser.add_argument('--pattern', help=r'Regex pattern for --dir (default: (\d{3}))', default=r'(\d{3})')
    parser.add_argument('--recursive', action='store_true', help='Recursive scan for --dir')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Find project root
    # plugins/adr-manager/skills/adr-management/scripts/next_number.py -> scripts -> adr-management -> skills -> adr-manager -> plugins -> root
    script_path = Path(__file__).resolve()
    # Go up 5 levels to reach project root
    project_root = script_path.parents[4]

    if args.type == 'all':
        show_all(project_root)
    elif args.type:
        next_num = get_next_number(args.type, project_root)
        if args.json:
            import json
            print(json.dumps({"type": args.type, "next": next_num}))
        else:
            print(next_num)
    elif args.dir:
        max_num = find_max_in_directory(Path(args.dir), args.pattern, args.recursive)
        next_num = f"{max_num + 1:04d}"
        if args.json:
            import json
            print(json.dumps({"directory": args.dir, "next": next_num}))
        else:
            print(next_num)


if __name__ == "__main__":
    main()