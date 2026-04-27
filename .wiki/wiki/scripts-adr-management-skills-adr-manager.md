---
concept: scripts-adr-management-skills-adr-manager
source: plugin-code
source_file: adr-manager/scripts/adr_manager.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.054594+00:00
cluster: content
content_hash: a4b86cb4c418b25b
---

# scripts/ → adr-management/ → skills/ → adr-manager/

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/adr-manager/scripts/adr_manager.py -->
#!/usr/bin/env python
"""
adr_manager.py — Architecture Decision Record Manager
======================================================

Purpose:
    Create, list, search, and view ADRs. Uses next_number.py for
    auto-incrementing IDs and the ADR template for scaffolding.

Layer: 
    Plugin / ADR-Manager

Usage Examples:
    python./scripts/adr_manager.py create "Title" --context "..." --decision "..." --consequences "..."
    python./scripts/adr_manager.py list [--limit N]
    python./scripts/adr_manager.py get N
    python./scripts/adr_manager.py search "query"

Supported Object Types:
    - Architecture Decision Records (ADR)

CLI Arguments:
    create <title>          Create a new ADR with specified metadata fields
    list [--limit <N>]      List existing ADRs with optional result count limit
    get <number>            View a specific ADR fully by its numeric ID
    search <query>          Search ADR bodies using exact matching keywords

Input Files:
    - templates/adr-template.md

Output:
    - ADRs/<NNN>_<title>.md

Key Functions:
    create_adr(title, ...)  Scaffolds a new decision log using auto-increment IDs
    list_adrs()             Renders index list ordered ascending by serial ID
    get_adr(n)              Loads detailed record for exact matched record ID

Script Dependencies:
    - next_number.py (sibling script helper indexer)

Consumed by:
    - ADR Management Skill orchestration workflows
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
               consequences: str = "", alternatives: str = "", status: str = "Proposed") -> Path:
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


def list_adrs(limit: int | None = None) -> None:
    """List ADRs sorted by number."""

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/adr-management/scripts/adr_manager.py -->
#!/usr/bin/env python3
"""
adr_manager.py — Architecture Decision Record Manager
======================================================

Purpose:
    Create, list, search, and view ADRs. Uses next_number.py for
    auto-incrementing IDs and the ADR template for scaffolding.

Layer: 
    Plugin / ADR-Manager

Usage Examples:
    python3 ./scripts/adr_manager.py create "Title" --context "..." --decision "..." --consequences "..."
    python3 ./scripts/adr_manager.py list [--limit N]
    python3 ./scripts/adr_manager.py get N
    python3 ./scripts/adr_manager.py search "query"

Supported Object Types:
    - Architecture Decision Records (ADR)

CLI Arguments:
    create <title>          Create a new ADR with specified metadata fields
    list [--limit <N>]      List existing ADRs with optional result cou

*(combined content truncated)*

## See Also

- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[dependency-management]]
- [[domain-patterns-routing-skills]]
- [[handle-nested-skills-eg-skillsdeferredskill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `adr-manager/scripts/adr_manager.py`
- **Indexed:** 2026-04-27T05:21:04.054594+00:00
