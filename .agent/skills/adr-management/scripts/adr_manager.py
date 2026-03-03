#!/usr/bin/env python3
"""
adr_manager.py — Architecture Decision Record Manager
======================================================

Purpose:
    Create, list, search, and view ADRs. Uses next_number.py for
    auto-incrementing IDs and the ADR template for scaffolding.

Layer: Plugin / ADR-Manager

Usage:
    python3 plugins/adr-manager/skills/adr-management/scripts/adr_manager.py create "Title" --context "..." --decision "..." --consequences "..."
    python3 plugins/adr-manager/skills/adr-management/scripts/adr_manager.py list [--limit N]
    python3 plugins/adr-manager/skills/adr-management/scripts/adr_manager.py get N
    python3 plugins/adr-manager/skills/adr-management/scripts/adr_manager.py search "query"
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
# scripts/ → adr-management/ → skills/ → adr-manager/
PLUGIN_ROOT = SCRIPT_DIR.parents[2]

# Import next_number from sibling script
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from next_number import get_next_number, ARTIFACT_TYPES
except ImportError:
    print("❌ next_number.py not found in plugin scripts/")
    sys.exit(1)


def _find_project_root() -> Path:
    """Walk up from PLUGIN_ROOT to find the project root."""
    p = PLUGIN_ROOT
    for _ in range(10):
        if (p / ".git").exists() or (p / ".agent").exists():
            return p
        p = p.parent
    return Path.cwd()

PROJECT_ROOT = _find_project_root()
# Matches next_number.py ARTIFACT_TYPES["adr"]["directory"]
ADR_DIR = PROJECT_ROOT / "ADRs"
TEMPLATE_PATH = PLUGIN_ROOT / "templates" / "adr-template.md"


def create_adr(title: str, context: str = "", decision: str = "", 
               consequences: str = "", alternatives: str = "", status: str = "Proposed"):
    """Create a new ADR from template."""
    ADR_DIR.mkdir(parents=True, exist_ok=True)

    next_num = get_next_number("adr", PROJECT_ROOT)
    filename = f"{next_num}_{title.lower().replace(' ', '_').replace('-', '_')}.md"
    filepath = ADR_DIR / filename

    # Load template
    if TEMPLATE_PATH.exists():
        content = TEMPLATE_PATH.read_text(encoding='utf-8')
    else:
        content = "# ADR-NNNN: [Title]\n\n## Status\n[Status]\n\n## Context\n[Context]\n\n## Decision\n[Decision]\n\n## Consequences\n[Consequences]\n\n## Alternatives Considered\n[Alternatives]\n"

    # Fill template
    content = content.replace("NNNN", next_num)
    content = content.replace("[Title]", title)
    content = content.replace("[Proposed | Accepted | Deprecated | Superseded]", status)
    content = content.replace("[What is the issue or situation that needs to be addressed?]", context or "TBD")
    content = content.replace("[What is the change that we're proposing and/or doing?]", decision or "TBD")
    content = content.replace("[What becomes easier or harder as a result of this decision?]", consequences or "TBD")
    content = content.replace("[What other options were evaluated?]", alternatives or "N/A")

    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created ADR-{next_num}: {title}")
    print(f"   Path: {filepath}")
    return filepath


def list_adrs(limit: int = None):
    """List ADRs sorted by number."""
    if not ADR_DIR.exists():
        print("📂 No ADRs directory found.")
        return

    adrs = sorted([f for f in ADR_DIR.iterdir() if f.suffix == '.md'], key=lambda f: f.name)
    if limit:
        adrs = adrs[-limit:]

    if not adrs:
        print("📂 No ADRs found.")
        return

    print(f"\n📋 Architecture Decision Records ({len(adrs)}):\n")
    for adr in adrs:
        # Extract title from first line
        try:
            first_line = adr.read_text(encoding='utf-8').split('\n')[0]
            title = first_line.lstrip('# ').strip()
        except:
            title = adr.stem
        print(f"  {adr.name:40} {title}")


def get_adr(number: int):
    """Get a specific ADR by number."""
    if not ADR_DIR.exists():
        print("❌ No ADRs directory.")
        return

    pattern = re.compile(rf"^{number:03d}")
    for f in ADR_DIR.iterdir():
        if f.suffix == '.md' and pattern.match(f.name):
            print(f.read_text(encoding='utf-8'))
            return
    print(f"❌ ADR-{number:03d} not found.")


def search_adrs(query: str):
    """Search ADRs by keyword."""
    if not ADR_DIR.exists():
        print("📂 No ADRs directory.")
        return

    query_lower = query.lower()
    results = []
    for f in sorted(ADR_DIR.iterdir()):
        if f.suffix != '.md':
            continue
        try:
            content = f.read_text(encoding='utf-8')
            if query_lower in content.lower():
                first_line = content.split('\n')[0].lstrip('# ').strip()
                results.append((f.name, first_line))
        except:
            continue

    if not results:
        print(f"❌ No ADRs matching '{query}'")
    else:
        print(f"\n🔍 {len(results)} ADR(s) matching '{query}':\n")
        for name, title in results:
            print(f"  {name:40} {title}")


def main():
    parser = argparse.ArgumentParser(description="Architecture Decision Record Manager")
    subparsers = parser.add_subparsers(dest="command")

    create_p = subparsers.add_parser("create", help="Create new ADR")
    create_p.add_argument("title", help="ADR title")
    create_p.add_argument("--context", default="", help="Context/problem statement")
    create_p.add_argument("--decision", default="", help="Decision made")
    create_p.add_argument("--consequences", default="", help="Consequences")
    create_p.add_argument("--alternatives", default="", help="Alternatives considered")
    create_p.add_argument("--status", default="Proposed", help="Status (default: Proposed)")

    list_p = subparsers.add_parser("list", help="List ADRs")
    list_p.add_argument("--limit", type=int, help="Show only last N ADRs")

    get_p = subparsers.add_parser("get", help="View specific ADR")
    get_p.add_argument("number", type=int, help="ADR number")

    search_p = subparsers.add_parser("search", help="Search ADRs by keyword")
    search_p.add_argument("query", help="Search query")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "create":
        create_adr(args.title, args.context, args.decision, args.consequences, args.alternatives, args.status)
    elif args.command == "list":
        list_adrs(args.limit)
    elif args.command == "get":
        get_adr(args.number)
    elif args.command == "search":
        search_adrs(args.query)


if __name__ == "__main__":
    main()