#!/usr/bin/env python3
"""sync_cheapest_models.py

Treats plugins/cli-agents/references/cheapest_models.{json,md} as the master
copies and propagates them to every other copy found in the repo.

Usage:
    python3 plugins/cli-agents/scripts/sync_cheapest_models.py [--dry-run]
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MASTERS = {
    "cheapest_models.json": REPO_ROOT / "plugins/cli-agents/references/cheapest_models.json",
    "cheapest_models.md": REPO_ROOT / "plugins/cli-agents/references/cheapest_models.md",
}


def find_copies(filename: str, master: Path) -> list[Path]:
    """Return all non-master, non-symlink copies of filename under plugins/."""
    plugins_root = REPO_ROOT / "plugins"
    return [
        p for p in plugins_root.rglob(filename)
        if p.resolve() != master.resolve() and not p.is_symlink()
    ]


def sync(dry_run: bool = False) -> None:
    total_updated = 0
    for filename, master in MASTERS.items():
        if not master.exists():
            print(f"ERROR: master not found: {master}", file=sys.stderr)
            sys.exit(1)

        copies = find_copies(filename, master)
        print(f"\n{filename}: {len(copies)} copies to sync")
        for copy in sorted(copies):
            rel = copy.relative_to(REPO_ROOT)
            if dry_run:
                print(f"  [dry-run] would update: {rel}")
            else:
                shutil.copy2(master, copy)
                print(f"  updated: {rel}")
            total_updated += 1

    action = "would update" if dry_run else "updated"
    print(f"\nDone — {action} {total_updated} files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()
    sync(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
