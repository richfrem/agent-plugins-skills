#!/usr/bin/env python3
"""
create_adr.py (CLI)
=====================================
Purpose:
    Determines the next sequential Architecture Decision Record (ADR) number,
    reads the standard ADR template, applies the title, and scaffolds the new file.

Usage Examples:
    python3 create_adr.py --title "Use ChromaDB for Vector Storage" --dir "ADRs"
"""
import argparse
import os
import re
import sys
from pathlib import Path


def get_next_adr_number(target_dir: str) -> int:
    path = Path(target_dir)
    if not path.exists() or not path.is_dir():
        return 1

    highest = 0
    pattern = re.compile(r"^(\d{4})-.*\.md$")
    
    for filename in os.listdir(path):
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


def create_adr(title: str, target_dir: str):
    script_dir = Path(__file__).parent.resolve()
    # The template is located at plugins/adr-manager/templates/adr-template.md
    # We are in plugins/adr-manager/skills/adr-management/scripts/
    template_path = script_dir.parent.parent.parent / "templates" / "adr-template.md"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    next_num = get_next_adr_number(target_dir)
    num_str = f"{next_num:04d}"
    
    safe_title = sanitize_title(title)
    filename = f"{num_str}-{safe_title}.md"
    filepath = out_dir / filename
    
    # Read template and replace placeholders
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("NNNN", num_str)
    content = content.replace("[Title]", title)
    
    filepath.write_text(content, encoding="utf-8")
    
    # Output the created filepath so the agent can capture it
    print(str(filepath))


def main():
    parser = argparse.ArgumentParser(description="Create a new ADR from a template.")
    parser.add_argument("--title", required=True, help="The title of the ADR (e.g., 'Use PostgreSQL')")
    parser.add_argument("--dir", default="ADRs", help="Target directory to save the ADR. Defaults to 'ADRs'.")
    args = parser.parse_args()
    
    create_adr(args.title, args.dir)


if __name__ == "__main__":
    main()
