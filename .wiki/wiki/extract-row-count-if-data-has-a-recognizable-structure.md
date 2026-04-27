---
concept: extract-row-count-if-data-has-a-recognizable-structure
source: plugin-code
source_file: obsidian-wiki-engine/scripts/bases_ops.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.258427+00:00
cluster: base
content_hash: 35adea5cfb48caec
---

# Extract row count if data has a recognizable structure

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/obsidian-wiki-engine/scripts/bases_ops.py -->
"""
bases_ops.py (CLI)
=====================================

Purpose:
    Read and manipulate Obsidian Bases (.base) files.
    These YAML-based files define database-like views (tables, cards, grids) over vault notes.
    This module handles row appending, cell updates, and view config preservation.

Layer: Core Operations

Usage Examples:
    pythonbases_ops.py read --file example.base
    pythonbases_ops.py append-row --file example.base --data key1=value1 key2=value2
    pythonbases_ops.py update-cell --file example.base --row-index 0 --column Title --value "New Title"

Supported Object Types:
    - .base (YAML layouts)

CLI Arguments:
    Subcommands: read, append-row, update-cell. Run with --help for details.

Input Files:
    - .base files.

Output:
    - JSON results or modified .base files.

Key Functions:
    read_base(): Read and parse a .base file.
    append_row(): Append a new row to a .base file.
    update_cell(): Update a specific cell in a .base file.

Script Dependencies:
    sys, json, argparse, pathlib, ruamel.yaml

Consumed by:
    - obsidian-bases-manager skill
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from ruamel.yaml import YAML
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    print("WARNING: ruamel.yaml required. Install: pip install ruamel.yaml", file=sys.stderr)


class BasesError(Exception):
    """Non-fatal error for bases operations. Reports cleanly instead of crashing."""
    pass


def read_base(filepath: Path) -> Dict[str, Any]:
    """Read and parse a .base file. Returns the parsed YAML structure."""
    if not HAS_RUAMEL:
        return {"error": "ruamel.yaml not installed"}

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    if not str(filepath).endswith('.base'):
        return {"error": f"Not a .base file: {filepath}"}

    try:
        from io import StringIO
        content = filepath.read_text(encoding='utf-8')
        data = _yaml.load(StringIO(content))

        if data is None:
            return {"error": "Empty or invalid .base file", "file": str(filepath)}

        result = {
            "file": str(filepath),
            "data": dict(data) if data else {},
        }

        # Extract row count if data has a recognizable structure
        if isinstance(data, dict):
            for key in ['rows', 'data', 'entries', 'items']:
                if key in data and isinstance(data[key], list):
                    result["row_count"] = len(data[key])
                    break

        return result

    except Exception as e:
        return {"error": f"YAML_PARSE_ERROR: {str(e)}", "file": str(filepath)}


def append_row(filepath: Path, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """Append a new row to a .base file's data array."""
    if not HAS_RUAMEL:
        return {"error": "ruamel.yaml not installed"}

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        from io import StringIO
        content = filepath.read_text(encoding='utf-8')
        data = _yaml.load(StringIO(content))

        if data is None:
            return {"error": "Empty or invalid .base file"}

        # Find the data array (try common keys)
        data_key = None
        for key in ['rows', 'data', 'entries', 'items']:
            if key in data and isinstance(data[key], list):
                data_key = key
                break

        if data_key is None:
            # Create a 'rows' array if none exists
            data['rows'] = []
            data_key = 'rows'

        data[data_key].append(row_data)

        # Write back atomically
        stream = StringIO()
        _yaml.dump(data, stream)
        new_content = stream.getvalue()

        # Use atomic write from vault_ops
        tmp_path = filepath.parent / f"{filepath.

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/obsidian-bases-manager/scripts/bases_ops.py -->
"""
bases_ops.py (CLI)
=====================================

Purpose:
    Read and manipulate Obsidian Bases (.base) files.
    These YAML-based files define database-like views (tables, cards, grids) over vault notes.
    This module handles row appending, cell updates, and view config preservation.

Layer: Core Operations

Usage Examples:
    python3 bases_ops.py read --file example.base
    python3 bases_ops.py append-row --file example.base --data key1=value1 key2=value2
    python3 bases_ops.py update-cell --file example.base --row-index 0 --column Title --value "New Title"

Supported Object Types:
    - .base (YAML layouts)

CLI Arguments:
    Subcommands: read, append-row, update-cell. Run with --help for details.

Input Files:
    - .base files.

Output:
    - JSON results or mo

*(combined content truncated)*

## See Also

- [[data-is-a-dict-of-id-iso-timestamp-prune-entries-outside-dedup-window]]
- [[1-check-root-structure]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[as-a-library]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/bases_ops.py`
- **Indexed:** 2026-04-27T05:21:04.258427+00:00
