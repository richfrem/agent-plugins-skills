#!/usr/bin/env python3
"""
manage_missing_objects.py
=========================
Purpose: Manages the inventory of missing legacy objects (Forms, Reports, Tables, etc.) 
         that are referenced in code/configuration but missing source artifacts.

Usage:
    python manage_missing_objects.py add --id FORM0000 --type FORM --artifacts XML FMB --notes " Referenced in APP1_INQ_RPT"
    python manage_missing_objects.py search "FORM0000"
    python manage_missing_objects.py list

Location: plugins/inventory-manager/scripts/manage_missing_objects.py
"""
import argparse
import json
import os
import sys
from datetime import datetime

INVENTORY_FILE = "legacy-system/reference-data/missing_objects.json"

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return []
    try:
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {INVENTORY_FILE} is corrupted. Returning empty list.")
        return []

def save_inventory(data):
    os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Inventory saved to {INVENTORY_FILE}")

MAX_INVENTORY_FILE = "legacy-system/reference-data/master_object_collection.json"

def check_master_inventory(obj_id):
    """Returns True if object exists in Master Inventory."""
    if not os.path.exists(MAX_INVENTORY_FILE):
        return False
    try:
        with open(MAX_INVENTORY_FILE, 'r') as f:
            full_inventory = json.load(f)
            # Master inventory structure: list of objects. Check 'id' key.
            for item in full_inventory:
                 if item.get('id', '').upper() == obj_id.upper():
                     return True
            return False
    except Exception as e:
        print(f"⚠️ Warning: Could not read Master Inventory: {e}")
        return False

def add_entry(args):
    # 1. Verification: Check if it exists in Master Inventory first
    if check_master_inventory(args.id):
        print(f"❌ Error: Object '{args.id.upper()}' found in Master Object Collection.")
        print("   It cannot be added to the 'Missing Objects' inventory.")
        return

    data = load_inventory()
    
    # Check for duplicate in local missing inventory
    for entry in data:
        if entry['id'].upper() == args.id.upper() and entry['type'].upper() == args.type.upper():
            print(f"⚠️  Entry {args.id} ({args.type}) already exists in Missing Inventory.")
            return

    new_entry = {
        "id": args.id.upper(),
        "type": args.type.upper(),
        "missing_artifacts": args.artifacts,
        "notes": args.notes,
        "detected_at": datetime.now().isoformat(),
        "status": "MISSING"
    }
    
    data.append(new_entry)
    save_inventory(data)
    print(f"✅ Added {args.id} to missing objects.")

def search_entry(args):
    data = load_inventory()
    term = args.term.lower()
    
    matches = [
        e for e in data 
        if term in e['id'].lower() 
        or term in e['notes'].lower()
        or term in str(e['missing_artifacts']).lower()
    ]
    
    if not matches:
        print(f"No matches found for '{args.term}'")
        return

    print(f"Found {len(matches)} matches:")
    print("-" * 60)
    for m in matches:
        print(f"ID: {m['id']} ({m['type']})")
        print(f"Missing: {', '.join(m['missing_artifacts'])}")
        print(f"Notes: {m['notes']}")
        print(f"Status: {m['status']}")
        print("-" * 60)

def list_entries(args):
    data = load_inventory()
    if not data:
        print("Inventory is empty.")
        return
        
    print(f"Total Missing Objects: {len(data)}")
    print("-" * 60)
    print(f"{'ID':<15} | {'Type':<10} | {'Missing Artifacts'}")
    print("-" * 60)
    for m in data:
        artifacts = ", ".join(m['missing_artifacts'])
        print(f"{m['id']:<15} | {m['type']:<10} | {artifacts}")

def main():
    parser = argparse.ArgumentParser(description="Manage Missing Objects Inventory")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ADD
    add_parser = subparsers.add_parser("add", help="Add a new missing object")
    add_parser.add_argument("--id", required=True, help="Object ID (e.g. FORM0000)")
    add_parser.add_argument("--type", required=True, help="Object Type (FORM, REPORT, TABLE, etc.)")
    add_parser.add_argument("--artifacts", nargs="+", required=True, help="List of missing artifacts (XML, FMB, SQL)")
    add_parser.add_argument("--notes", default="", help="Context/Reason")
    
    # SEARCH
    search_parser = subparsers.add_parser("search", help="Search the inventory")
    search_parser.add_argument("term", help="Search term")
    
    # LIST
    list_parser = subparsers.add_parser("list", help="List all entries")

    args = parser.parse_args()
    
    if args.command == "add":
        add_entry(args)
    elif args.command == "search":
        search_entry(args)
    elif args.command == "list":
        list_entries(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
