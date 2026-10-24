#!/usr/bin/env python
"""
scaffold_plugin.py
=====================================

Purpose:
    Creates a new plugin directory: .claude-plugin/plugin.json, skills/, README.md and (optionally)
    hooks/hooks.json and .mcp.json. Skills are self-contained; the plugin root holds no shared
    scripts, references or tests.

Layer: Meta-Execution

Usage:
    python scaffold_plugin.py --name <plugin-name> --path plugins [--with-hooks] [--with-mcp]

Key Input Dependencies:
    - ../assets/templates/README.md.jinja (str.format placeholders {name} and {description})
    - argparse, json, pathlib, re (standard library)
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "templates" / "README.md.jinja"


def scaffold(name: str, parent: Path, description: str, author_name: str, author_email: str, with_hooks: bool, with_mcp: bool) -> Path:
    """Write the plugin tree and return its root."""
    root = parent / name
    (root / ".claude-plugin").mkdir(parents=True)
    (root / "skills").mkdir()
    author = {"name": author_name}
    if author_email:
        author["email"] = author_email
    manifest = {"name": name, "version": "0.1.0", "description": description, "author": author, "license": "MIT", "keywords": [name]}
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / "README.md").write_text(TEMPLATE.read_text(encoding="utf-8").format(name=name, description=description), encoding="utf-8")
    if with_hooks:
        (root / "hooks").mkdir()
        (root / "hooks" / "hooks.json").write_text(json.dumps({"hooks": {}}, indent=2) + "\n", encoding="utf-8")
    if with_mcp:
        (root / ".mcp.json").write_text(json.dumps({"mcpServers": {}}, indent=2) + "\n", encoding="utf-8")
    return root


def main() -> int:
    """CLI entry point; non-zero on invalid names or an existing directory."""
    parser = argparse.ArgumentParser(description="Scaffold a plugin directory.")
    parser.add_argument("--name", required=True, help="1-64 lowercase letters, digits or hyphens")
    parser.add_argument("--path", default="plugins", help="Parent directory (default: plugins)")
    parser.add_argument("--description", default="Define the purpose of this plugin here.")
    parser.add_argument("--author-name", default="Your Name")
    parser.add_argument("--author-email", default="")
    parser.add_argument("--with-hooks", action="store_true", help="Also create hooks/hooks.json")
    parser.add_argument("--with-mcp", action="store_true", help="Also create .mcp.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]{1,64}", args.name):
        print(f"Error: name '{args.name}' must be 1-64 lowercase letters, digits or hyphens.", file=sys.stderr)
        return 2
    if (Path(args.path) / args.name).exists():
        print(f"Error: {Path(args.path) / args.name} already exists.", file=sys.stderr)
        return 1
    root = scaffold(args.name, Path(args.path), args.description, args.author_name, args.author_email, args.with_hooks, args.with_mcp)
    print(f"Success: plugin '{args.name}' scaffolded at {root}")
    print("Next: add skills with authoring-skills, then run audit_plugin_structure.py and audit.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
