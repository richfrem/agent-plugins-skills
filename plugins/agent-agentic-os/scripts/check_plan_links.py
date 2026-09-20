#!/usr/bin/env python3
"""
check_plan_links.py
===================
Validates local Markdown link targets in planning documents.

Usage:
    python3 check_plan_links.py <path-to-markdown-file>
"""

import re
import sys
from pathlib import Path

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def check_links(file_path: Path) -> int:
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        return 1

    content = file_path.read_text(encoding="utf-8")
    base_dir = file_path.parent
    broken = []
    total = 0

    for match in LINK_PATTERN.finditer(content):
        _, target = match.groups()
        target = target.strip()

        # Skip external URLs, email, anchors
        if (
            target.startswith("http://")
            or target.startswith("https://")
            or target.startswith("mailto:")
            or target.startswith("#")
        ):
            continue

        # Strip anchor from target if present
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            continue

        total += 1
        resolved = (base_dir / clean_target).resolve()
        if not resolved.exists():
            broken.append((target, resolved))

    if broken:
        print(f"FAILED: Found {len(broken)} broken links in {file_path}:", file=sys.stderr)
        for original, res_path in broken:
            print(f"  - '{original}' (resolved: {res_path})", file=sys.stderr)
        return 1

    print(f"All local links valid ({total} checked) in {file_path}")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: check_plan_links.py <markdown-file>", file=sys.stderr)
        sys.exit(2)

    target_file = Path(sys.argv[1]).resolve()
    sys.exit(check_links(target_file))


if __name__ == "__main__":
    main()
