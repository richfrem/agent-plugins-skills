#!/usr/bin/env python
"""
utils.py (Module)
=====================================

Purpose:
    Shared utilities for skill-creator and analyzer scripts. 
    Provides functions for parsing SKILL.md and metadata structures in plugins.

Layer: Investigate / Core / Support

Usage Examples:
    from utils import parse_skill_md
    name, desc, content = parse_skill_md(Path("path/to/skill_dir"))

Supported Object Types:
    Parsed SKILL.md data structures.

CLI Arguments:
    None (Module Import)

Input Files:
    - SKILL.md (Via function call)

Output:
    Tuple constants extracted from file contents.

Key Functions:
    - parse_skill_md()

Script Dependencies:
    None

Consumed by:
    run_eval.py, audit_plugin_structure.py, trigger evaluation benchmarks.
"""

from pathlib import Path



def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content
