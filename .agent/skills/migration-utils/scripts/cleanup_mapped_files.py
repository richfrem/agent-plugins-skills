#!/usr/bin/env python3
"""cleanup_mapped_files.py — Selectively delete migrated files."""
import json
import os
import shutil

# Load inventory
try:
    with open("migration_inventory.json") as f:
        inventory = json.load(f)
except FileNotFoundError:
    print("Error: migration_inventory.json not found.")
    exit(1)

def cleanup(dry_run=True):
    deleted_count = 0
    skipped_count = 0
    
    print(f"Cleanup Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("-" * 40)
    
    for old_path, info in inventory.items():
        if info.get("status") != "pending" and info.get("status") != "target_missing" and info.get("status") != "unmapped":
             # Wait, generate_inventory.py sets status to "pending" for mapped items
             # Let's check logic: if new_path is set, it's mapped.
             pass

        new_path = info.get("new_path")
        
        # Only delete if mapped AND new path exists
        if new_path and os.path.exists(new_path):
            if os.path.exists(old_path):
                if dry_run:
                    print(f"[Would Delete] {old_path} -> Mapped to {new_path}")
                else:
                    try:
                        os.remove(old_path)
                        print(f"[Deleted] {old_path}")
                        deleted_count += 1
                    except OSError as e:
                        print(f"[Error] Could not delete {old_path}: {e}")
            else:
                 # File already gone
                 pass
        else:
            if os.path.exists(old_path):
                skipped_count += 1
                # print(f"[Skipping] {old_path} (Unmapped or Target Missing)")
    
    # Clean up empty directories
    if not dry_run:
        print("\nCleaning up empty directories in tools/...")
        for root, dirs, files in os.walk("tools", topdown=False):
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                    print(f"[Removed Dir] {os.path.join(root, name)}")
                except OSError:
                    # Directory not empty
                    pass

    print("-" * 40)
    print(f"Files {'would be' if dry_run else ''} deleted: {deleted_count}")
    print(f"Files preserved: {skipped_count}")

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually delete files")
    args = parser.parse_args()
    
    cleanup(dry_run=not args.execute)
