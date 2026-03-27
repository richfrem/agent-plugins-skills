#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/config_manager.py (CLI)
=====================================

Purpose:
    Manages shared configuration settings.

Layer: Curate / Utilities

Usage Examples:
    python [SKILL_ROOT]/scripts/config_manager.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    target          : Form ID or App Code (e.g. FORM0000 or AppFour)
    item            : Item ID (e.g. BUTTON1)
    target          : Form ID or App Code
    item            : Item ID
    --visible       : Comma-sep roles, or *
    --enabled       : Comma-sep roles, or *

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - locate_rule_file(): Locates the TypeScript rule file for a given target ID.
    - query_item(): Queries current visibility and enablement roles for a specific UI item.
    - update_item(): Updates the visibility and/or enablement roles for a UI item in its TypeScript rule file.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import sys
import argparse
import json
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from tools.investigate.utils.path_resolver import resolve_path

# Configuration
RULES_DIR = Path(resolve_path("sandbox/ui/src/rules"))

def locate_rule_file(target_id: str) -> tuple[Optional[str], Optional[str]]:
    """
    Locates the TypeScript rule file for a given target ID.
    
    Args:
        target_id: The ID of the form or application (e.g., 'FORM0000' or 'AppFour').
        
    Returns:
        A tuple of (file_path, file_type), or (None, None) if not found.
    """
    # Target can be "AppFour" (App Menu) or "FORM0000" (Form Rules)
    # Check for Form Rules first
    path = RULES_DIR / f"{target_id}_Rules.ts"
    if path.exists():
        return str(path), "FORM"
    
    # Check for App Menu
    path = RULES_DIR / f"{target_id}_Menu.ts"
    if path.exists():
        return str(path), "MENU"
        
    return None, None


def query_item(target_id: str, item_id: str) -> Dict[str, Any]:
    """
    Queries current visibility and enablement roles for a specific UI item.
    
    Args:
        target_id: The ID of the form or application.
        item_id: The ID of the UI element (e.g., 'BUTTON1').
        
    Returns:
        Dictionary containing item ID, file path, and role arrays.
    """
    from typing import Dict, Any, Optional
    file_path, file_type = locate_rule_file(target_id)
    if not file_path:
        return {"error": f"Rule file for {target_id} not found."}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the item block
    # Pattern: "ITEM_ID": { ... }
    # We look for the ID and then capture the visible/enabled arrays
    
    # Simple regex for visible/enabled
    # This assumes standard formatting from generator
    
    # Locate the item block start
    item_pattern = re.compile(rf"['\"]?{re.escape(item_id)}['\"]?:\s*{{", re.MULTILINE)
    match = item_pattern.search(content)
    
    if not match:
        return {"error": f"Item {item_id} not found in {target_id}"}
        
    start_idx = match.start()
    
    # Extract a chunk after start to parse
    chunk = content[start_idx:start_idx+1000] # Safe buffer
    
    # Extract visible array
    vis_match = re.search(r"visible:\s*(\[[^\]]*\])", chunk)
    en_match = re.search(r"enabled:\s*(\[[^\]]*\])", chunk)
    
    result = {
        "id": item_id,
        "file": file_path,
        "visible": json.loads(vis_match.group(1).replace("'", '"')) if vis_match else [],
        "enabled": json.loads(en_match.group(1).replace("'", '"')) if en_match else []
    }
    return result


def update_item(target_id: str, item_id: str, visible: Optional[List[str]] = None, enabled: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Updates the visibility and/or enablement roles for a UI item in its TypeScript rule file.
    
    Args:
        target_id: The ID of the form or application.
        item_id: The ID of the UI element.
        visible: List of roles that can see the item, or None to skip update.
        enabled: List of roles that can interact with the item, or None to skip update.
        
    Returns:
        Status dictionary with updated values.
    """
    from typing import List, Optional
    file_path, file_type = locate_rule_file(target_id)
    if not file_path:
        return {"error": f"Rule file for {target_id} not found."}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Locate item
    item_pattern = re.compile(rf"(['\"]?{re.escape(item_id)}['\"]?:\s*{{)", re.MULTILINE)
    match = item_pattern.search(content)
    if not match:
        return {"error": f"Item {item_id} not found in {target_id}"}

    # Helper replacement function using regex sub (safer than blind search/replace)
    # We find the block, then within that block find visible/enabled matching
    
    # LIMITATION: We need to be careful not to replace visible/enabled of OTHER items.
    # We'll locate the item index, then search for the *next* visible/enabled property from there.
    
    start_pos = match.start()
    
    new_content = content
    
    if visible:
        # Convert list to string format: ["A", "B"] or ["*"]
        vis_str = json.dumps(visible).replace('"', "'") 
        # Regex to match 'visible: [...]' starting after start_pos
        # We use a pattern that matches the first occurrence after our index
        
        # We split the string to isolate the part after our item starts
        pre = new_content[:start_pos]
        post = new_content[start_pos:]
        
        # Replace ONLY the first occurrence in 'post'
        post = re.sub(r"(visible:\s*)\[[^\]]*\]", f"\\1{vis_str}", post, count=1)
        
        new_content = pre + post
        
    if enabled:
        # Recalculate split because visible might have changed length
        # Or simpler: parse again? No, regex sub on the dirty content is acceptable if distinct
        # Logic repeated for enabled
        
        start_pos = item_pattern.search(new_content).start() # Find it again in modified text
        en_str = json.dumps(enabled).replace('"', "'")
        
        pre = new_content[:start_pos]
        post = new_content[start_pos:]
        
        post = re.sub(r"(enabled:\s*)\[[^\]]*\]", f"\\1{en_str}", post, count=1)
        
        new_content = pre + post

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return {"status": "Updated", "id": item_id, "visible": visible, "enabled": enabled}

def main():
    parser = argparse.ArgumentParser(description="Manage UI Rules Configuration")
    subparsers = parser.add_subparsers(dest="command")
    
    # Query Command
    q_parser = subparsers.add_parser("query", help="Get rules for an item")
    q_parser.add_argument("target", help="Form ID or App Code (e.g. FORM0000 or AppFour)")
    q_parser.add_argument("item", help="Item ID (e.g. BUTTON1)")
    
    # Update Command
    u_parser = subparsers.add_parser("update", help="Update rules for an item")
    u_parser.add_argument("target", help="Form ID or App Code")
    u_parser.add_argument("item", help="Item ID")
    u_parser.add_argument("--visible", help="Comma-sep roles, or *")
    u_parser.add_argument("--enabled", help="Comma-sep roles, or *")
    
    args = parser.parse_args()
    
    if args.command == "query":
        res = query_item(args.target, args.item)
        print(json.dumps(res, indent=2))
        
    elif args.command == "update":
        vis_list = args.visible.split(",") if args.visible else None
        en_list = args.enabled.split(",") if args.enabled else None
        
        # Handle wildcards cleanly
        if vis_list and "*" in vis_list: vis_list = ["*"]
        if en_list and "*" in en_list: en_list = ["*"]
        
        res = update_item(args.target, args.item, vis_list, en_list)
        print(json.dumps(res, indent=2))
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
