#!/usr/bin/env python
"""
scaffold_subagent.py
=====================================

Purpose:
    Writes a new sub-agent definition (<path>/<name>.md) from assets/templates/agent.md.jinja.
    Sub-agents are for isolated contexts, sandboxed tools or adversarial personas only.

Layer: Meta-Execution

Usage:
    python scaffold_subagent.py --name <agent-name> --path plugins/<plugin>/agents --desc "<use-case>"

Key Input Dependencies:
    - ../assets/templates/agent.md.jinja (str.format placeholders {name} and {description})
    - argparse, pathlib, re (standard library)
"""

import argparse
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "templates" / "agent.md.jinja"


def main() -> int:
    """CLI entry point; returns a non-zero exit code on invalid names or existing files."""
    parser = argparse.ArgumentParser(description="Scaffold a sub-agent definition.")
    parser.add_argument("--name", required=True, help="Lowercase letters, digits and hyphens, at most 64 characters")
    parser.add_argument("--path", required=True, help="Destination agents directory")
    parser.add_argument("--desc", required=True, help="Short use-case description")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing file")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9-]{1,64}", args.name):
        print(f"Error: name '{args.name}' must be 1-64 lowercase letters, digits or hyphens.", file=sys.stderr)
        return 2
    target = Path(args.path) / f"{args.name}.md"
    if target.exists() and not args.force:
        print(f"Error: {target} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE.read_text(encoding="utf-8").format(name=args.name, description=args.desc), encoding="utf-8")
    print(f"Success: sub-agent saved to {target}")
    print("Next: customise the system prompt, then run validate_agent.py and audit_sub_agent.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
