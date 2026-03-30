#!/usr/bin/env python3
"""
Bulk Plugin Replicator
======================

Replicates all (or filtered) plugins from a source plugins/ directory
to a destination plugins/ directory in another project.

Usage:
    bulk_replicator.py --source <plugins-dir> --dest <plugins-dir> [--link] [--clean] [--dry-run] [--filter <glob>]

Arguments:
    --source    Source plugins directory (e.g., plugins/)
    --dest      Destination plugins directory (e.g., /path/to/other-project/plugins/)
    --link      Use symlinks instead of copying
    --clean     Remove dest files/dirs no longer in source (per plugin)
    --dry-run   Preview changes without applying them
    --filter    Glob pattern to select plugins (default: * = all)

Examples:
    # Replicate all plugins to Project Sanctuary
    python3 bulk_replicator.py \\
        --source plugins/ \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/

    # Replicate only obsidian-* plugins with clean sync
    python3 bulk_replicator.py \\
        --source plugins/ \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/ \\
        --filter "obsidian-*" --clean
"""

import sys
import argparse
from pathlib import Path

# Ensure sibling scripts are importable when run from any working directory
sys.path.insert(0, str(Path(__file__).parent))
from plugin_replicator import replicate_plugin  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk-replicate plugins from one project to another.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--source", required=True, help="Source plugins/ directory")
    parser.add_argument("--dest",   required=True, help="Destination plugins/ directory")
    parser.add_argument("--link",    action="store_true", help="Use symlinks instead of copying")
    parser.add_argument("--clean",   action="store_true", help="Remove stale files from dest (per plugin)")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Preview changes without applying them")
    parser.add_argument("--filter",  default="*", help="Glob pattern for plugin names (default: *)")

    args = parser.parse_args()
    source_dir = Path(args.source).resolve()
    dest_dir   = Path(args.dest).resolve()

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)

    # Find matching plugin directories
    matched = sorted([
        p for p in source_dir.glob(args.filter)
        if p.is_dir() and not p.name.startswith(".")
    ])

    print(f"🚀 Bulk Plugin Replicator")
    print(f"   Source : {source_dir}")
    print(f"   Dest   : {dest_dir}")
    print(f"   Filter : {args.filter}")
    print(f"   Mode   : {'symlink' if args.link else 'copy'}"
          f"{' + clean' if args.clean else ''}"
          f"{' [DRY RUN]' if args.dry_run else ''}")
    print(f"   Found  : {len(matched)} plugin(s)")
    print()

    success_count: int = 0
    fail_count: int = 0

    for src_plugin in matched:
        dest_plugin = dest_dir / src_plugin.name
        print(f"── {src_plugin.name}")
        ok = replicate_plugin(src_plugin, dest_plugin, args.link, args.clean, args.dry_run)
        if ok:
            success_count += 1
        else:
            fail_count += 1
        print()

    print(f"🏁 Done. Replicated: {success_count}, Failed: {fail_count}")
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
