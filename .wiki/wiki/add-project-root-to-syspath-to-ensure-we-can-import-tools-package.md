---
concept: add-project-root-to-syspath-to-ensure-we-can-import-tools-package
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/references/manage_tool_inventory.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.376584+00:00
cluster: path
content_hash: 233ecb7af4c875fa
---

# Add project root to sys.path to ensure we can import tools package

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory/references/manage_tool_inventory.py -->
#!/usr/bin/env python3
"""
manage_tool_inventory.py (CLI)
=====================================

Purpose:
    Comprehensive manager for Tool Inventories. Supports list, add, update, remove, search, audit, and generate operations.

Layer: Curate / Curate

Usage Examples:
    python ./scripts/manage_tool_inventory.py --help
    python ./scripts/manage_tool_inventory.py list
    python ./scripts/manage_tool_inventory.py search "keyword"
    python ./scripts/manage_tool_inventory.py remove --path "path/to/tool_script.py"
    python ./scripts/manage_tool_inventory.py update --path "tool_script.py" --desc "New description"
    python ./scripts/manage_tool_inventory.py discover --auto-stub
    python ./scripts/manage_tool_inventory.py summarize-missing
    python ./scripts/manage_tool_inventory.py sync-from-cache
    python ./scripts/manage_tool_inventory.py reset-from-cache
    python ./scripts/manage_tool_inventory.py clear-inventory

Supported Object Types:
    - Generic

CLI Arguments:
    --inventory     : Path to JSON inventory
    --path          : Relative path to tool
    --category      : Category (e.g. curate/inventories)
    --desc          : Description (Optional, auto-extracted if empty)
    --output        : Output file path (Default: adjacent TOOL_INVENTORY.md)
    keyword         : Keyword to search in name/path/description
    --status        : Filter by compliance status
    --path          : Current path or name of the tool
    --desc          : New description
    --new-path      : New path
    --mark-compliant: Mark as compliant
    --path          : Path or name of tool to remove
    --auto-stub     : Automatically create stub entries
    --include-json  : Include JSON config files
    --json          : Output as JSON
    --path          : Single script path
    --batch         : Process all 'stub' tools
    --dry-run       : Preview changes only

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_markdown(): Generate Markdown documentation from the Inventory Manager data.
    - extract_docstring(): Read file and extract PyDoc or JSDoc.
    - main(): No description.

Script Dependencies:
    - Agent orchestration expected: 'rlm-curator' skill (for updating)
    - Agent orchestration expected: 'rlm-cleanup-agent' skill (for removals)

Consumed by:
    - rlm-factory skills
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path to ensure we can import tools package
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
import re
import json
import argparse
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import ast
import re

# Compliance status values

# Compliance status values
COMPLIANCE_STATUS = ['compliant', 'partial', 'needs_review', 'stub']
HEADER_STYLES = ['extended', 'basic', 'minimal', 'none']

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

CATEGORY_EMOJIS = {
    'miners': '⛏️',
    'search': '🔍',
    'bundler': '📦',
    'rlm': '🧠',
    'vector': '🗄️',
    'code-gen': '⚙️',
    'documentation': '📝',
    'inventories': '📊',
    'menu': '🍽️',
    'link-checker': '🔗',
    'utils': '🛠️',
    'tracking': '📋',
    'processors': '🔧',
    'elements': '📦',
    'tools': '🔨',
    'src': '📁',
    'root': '🚀',
}

# -----------------------------------------------------------------------------
# Core Classes
# -----------------------------------------------------------------------------

class InventoryManager:
    def __init__(self, inventory_path: Path) -> None:
        self.inventory_path = inventory_path.resolve()
        self.root_dir = self._determine_root()
        self.data = self._load()

    def _determine_r

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory/scripts/manage_tool_inventory.py -->
#!/usr/bin/env python3
"""
manage_tool_inventory.py (CLI)
=====================================

Purpose:
    Comprehensive manager for Tool Inventories. Supports list, add, update, remove, search, audit, and generate operations.

Layer: Curate / Curate

Usage Examples:
    python ./scripts/manage_tool_inventory.py --help
    python ./scripts/manage_tool_inventory.py list
    python ./scripts/manage_tool_inventory.py search "keyword"
    python ./scripts/manage_tool_inventory.py remove --path "path/to/tool_script.py"
    python ./scripts/manage_tool_inventory.py update --path "tool_script.py" --desc "New description"
    python ./scripts/manage_tool_inventory.py discover --auto-stub
    python ./scripts/manage_tool_inventory.py summarize-miss

*(combined content truncated)*

## See Also

- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-project-root-to-syspath]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/references/manage_tool_inventory.py`
- **Indexed:** 2026-04-27T05:21:04.376584+00:00
