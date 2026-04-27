---
concept: configuration-artifact-types-and-their-locationspatterns
source: plugin-code
source_file: adr-manager/scripts/next_number.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.425551+00:00
cluster: type
content_hash: bead94033deb5f66
---

# Configuration: artifact types and their locations/patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/adr-manager/scripts/next_number.py -->
#!/usr/bin/env python
"""
next_number.py (CLI)
=====================================

Purpose:
    Sequential Identifier Generator.
    Scans artifact directories (Specs, Tasks, ADRs, Chronicles, BRs, BWs) to find
    the next available sequence number. Prevents ID collisions.

Layer: Investigate / Utils

Usage Examples:
    python./scripts/next_number.py --type spec
    python./scripts/next_number.py --type task
    python./scripts/next_number.py --type br
    python./scripts/next_number.py --type all

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
    
    scan_dirs = config.get("scan_type") == 

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/adr-management/scripts/next_number.py -->
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
    python3 ./scripts/next_number.py --type spec
    python3 ./scripts/next_number.py --type task
    python3 ./scripts/next_number.py --type br
    python3 ./scripts/next_number.py --type all

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
    
Key 

*(combined content truncated)*

## See Also

- [[1-configuration-setup-dynamic-from-profile]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[commands-that-are-unconditionally-safe-and-bypass-further-checks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `adr-manager/scripts/next_number.py`
- **Indexed:** 2026-04-27T05:21:04.425551+00:00
