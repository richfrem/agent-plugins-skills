#!/usr/bin/env python3
"""
Plugin Replicator
=================

Replicates a plugin from a source directory to a destination directory.
Supports additive-update mode (default) and clean-sync mode (--clean).

Usage:
    plugin_replicator.py --source <src-plugin-dir> --dest <dest-dir> [--link] [--clean] [--dry-run]

Arguments:
    --source    Path to the source plugin folder (e.g., plugins/rlm-factory)
    --dest      Path to the destination folder (e.g., /path/to/other-project/plugins/rlm-factory)
    --link      Create a symlink instead of copying (best for active development)
    --clean     Remove files/dirs in dest that no longer exist in source (default: additive only)
    --dry-run   Preview changes without making them

Modes:
    Default     Copies new/updated files. Does NOT delete anything from dest.
    --clean     Copies new/updated files AND removes dest files missing from source.
    --link      Creates a symlink. Implies always up-to-date (no --clean needed).

Examples:
    # Additive update: replicate rlm-factory to Project Sanctuary
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory

    # Clean sync: remove deleted skills/files too
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory \\
        --clean

    # Dev symlink (always live)
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory \\
        --link
"""

import sys
import shutil
import platform
import argparse
from pathlib import Path


def replicate_plugin(
    source: Path,
    dest: Path,
    use_link: bool = False,
    clean: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Replicate a plugin directory from source to dest.

    Args:
        source:   Absolute path to source plugin directory.
        dest:     Absolute path to destination directory (will be created if missing).
        use_link: Create a symlink instead of copying.
        clean:    Remove dest files/dirs that no longer exist in source.
        dry_run:  Print actions without applying them.

    Returns:
        True on success, False on error.
    """
    prefix = "[DRY RUN] " if dry_run else ""

    if not source.exists():
        print(f"❌ Source not found: {source}")
        return False

    # --- Symlink mode: simple and always live ---
    if use_link:
        if dest.exists() or dest.is_symlink():
            print(f"{prefix}🧹 Removing existing: {dest}")
            if not dry_run:
                dest.unlink() if dest.is_symlink() else shutil.rmtree(dest)
        print(f"{prefix}🔗 Linking: {dest} -> {source}")
        if not dry_run:
            try:
                dest.symlink_to(source, target_is_directory=True)
            except Exception as e:
                print(f"❌ Symlink failed: {e}")
                if platform.system() == "Windows":
                    print("👉 Windows tip: run as Administrator or enable Developer Mode.")
                return False
        print(f"✅ Linked.")
        return True

    # --- Copy/update mode ---
    dest.mkdir(parents=True, exist_ok=True)

    # Step 1: Copy new/updated files from source -> dest
    copied: int = 0
    skipped: int = 0
    for src_file in source.rglob("*"):
        rel = src_file.relative_to(source)
        dst_file = dest / rel
        if src_file.is_dir():
            if not dry_run:
                dst_file.mkdir(parents=True, exist_ok=True)
            continue
        # Copy if missing or source is newer
        if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
            print(f"{prefix}  copy  {rel}")
            if not dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
            copied += 1
        else:
            skipped += 1

    print(f"  {copied} files updated, {skipped} up-to-date.")

    # Step 2: If --clean, remove dest files/dirs no longer in source
    if clean:
        removed: int = 0
        for dst_item in list(dest.rglob("*")):
            rel = dst_item.relative_to(dest)
            src_item = source / rel
            if not src_item.exists():
                print(f"{prefix}  clean {rel}")
                if not dry_run:
                    if dst_item.is_dir():
                        shutil.rmtree(dst_item, ignore_errors=True)
                    else:
                        dst_item.unlink(missing_ok=True)
                removed += 1
        if removed:
            print(f"  {removed} stale items removed (--clean).")

    print(f"✅ Done: {source.name} -> {dest}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replicate a plugin from source to destination.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--source", required=True, help="Source plugin directory path")
    parser.add_argument("--dest",   required=True, help="Destination directory path")
    parser.add_argument("--link",    action="store_true", help="Symlink instead of copy")
    parser.add_argument("--clean",   action="store_true", help="Remove dest files missing from source")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Preview changes without applying them")

    args = parser.parse_args()
    source = Path(args.source).resolve()
    dest   = Path(args.dest).resolve()

    print(f"🚀 Plugin Replicator")
    print(f"   Source : {source}")
    print(f"   Dest   : {dest}")
    print(f"   Mode   : {'symlink' if args.link else 'copy'}"
          f"{' + clean' if args.clean else ''}"
          f"{' [DRY RUN]' if args.dry_run else ''}")
    print()

    success = replicate_plugin(source, dest, args.link, args.clean, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
