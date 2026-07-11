#!/usr/bin/env python3
"""
Purpose:
    Validates that every plugin entry in .claude-plugin/marketplace.json points to a
    directory that actually exists. Missing source paths cause silent install failures
    in the Claude Code /plugin UI with no actionable error message.

Key Input Dependencies:
    - .claude-plugin/marketplace.json (plugin registry with source paths)
    - Project root directory structure

Key Functions:
    - audit(): Validate marketplace.json source paths and return exit code
    - main(): CLI entry point

Usage:
    python audit_marketplace_sources.py [repo_root]
    python audit_marketplace_sources.py .
"""
import json
import sys
from pathlib import Path


def audit(repo_root: Path) -> int:
    """Validate all marketplace.json plugin entries have valid source paths; return exit code."""
    marketplace = repo_root / ".claude-plugin" / "marketplace.json"
    if not marketplace.exists():
        print(f"No marketplace.json found at {marketplace}")
        return 0

    try:
        with marketplace.open() as f:
            m = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: marketplace.json is invalid JSON: {e}")
        return 1

    plugins = m.get("plugins", [])
    failures = []

    for p in plugins:
        name = p.get("name", "<unnamed>")
        source = p.get("source")
        if not isinstance(source, str) or not source.startswith("./"):
            continue  # non-relative sources (github, npm, url) can't be checked locally
        path = repo_root / source[2:]  # strip leading ./
        if not path.is_dir():
            failures.append((name, str(source), str(path)))

    if failures:
        print(f"Broken marketplace source paths ({len(failures)} of {len(plugins)}):\n")
        for name, source, path in failures:
            print(f"  MISS  {name:<40s}  {source}")
            print(f"        resolved to: {path}")
        print(
            "\nFix: update 'source' in marketplace.json to match the real directory name, "
            "or remove the entry."
        )
        return 1

    print(f"✓ All {len(plugins)} marketplace entries have valid source paths.")
    return 0


def main() -> None:
    """Parse CLI argument and audit marketplace.json source paths."""
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not repo_root.is_dir():
        print(f"ERROR: Not a directory: {repo_root}")
        sys.exit(1)
    sys.exit(audit(repo_root.resolve()))


if __name__ == "__main__":
    main()
