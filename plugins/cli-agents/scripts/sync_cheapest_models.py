#!/usr/bin/env python3
"""sync_cheapest_models.py

Treats plugins/cli-agents/references/cheapest_models.{json,md} as the master
copies and propagates them to every other copy found in the repo.

Purpose:
    Keeps every duplicate copy of cheapest_models.json/md in sync with the
    canonical master, so cheapest-model routing tables never silently drift.

Key Input Dependencies:
    - plugins/cli-agents/references/cheapest_models.json, cheapest_models.md (masters)

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


def find_copies(filename: str, master: Path, repository: Path | None = None) -> list[Path]:
    """Return all non-master, non-symlink copies of filename under plugins/."""
    plugins_root = (repository or REPO_ROOT) / "plugins"
    return [
        p for p in plugins_root.rglob(filename)
        if p.resolve() != master.resolve() and not p.is_symlink()
    ]


def sync(dry_run: bool = False, repository: Path | None = None) -> None:
    """Copy the master cheapest_models.{json,md} over every other copy found in the repo."""
    repository = (repository or REPO_ROOT).resolve()
    masters = {name: repository / "plugins/cli-agents/references" / name for name in MASTERS}
    total_updated = 0
    for filename, master in masters.items():
        if not master.exists():
            print(f"ERROR: master not found: {master}", file=sys.stderr)
            sys.exit(1)

        copies = find_copies(filename, master, repository)
        print(f"\n{filename}: {len(copies)} copies to sync")
        for copy in sorted(copies):
            rel = copy.relative_to(repository)
            if dry_run:
                print(f"  [dry-run] would update: {rel}")
            else:
                shutil.copy2(master, copy)
                print(f"  updated: {rel}")
            total_updated += 1

    action = "would update" if dry_run else "updated"
    print(f"\nDone — {action} {total_updated} files.")


def main() -> None:
    """CLI entry point: parse --dry-run and run sync()."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--repository", type=Path, help="Caller-supplied repository containing canonical CLI catalogs")
    args = parser.parse_args()
    repository = args.repository
    if repository is None:
        # Backward compatibility applies only to the canonical source checkout.
        canonical_script = REPO_ROOT / "plugins/cli-agents/scripts/sync_cheapest_models.py"
        if canonical_script.resolve() != Path(__file__).resolve() or not canonical_script.is_file():
            parser.error("Installed execution requires --repository; no source checkout is inferred")
        repository = REPO_ROOT
    if not (repository / "plugins/cli-agents/references").is_dir():
        parser.error("--repository must contain plugins/cli-agents/references")
    sync(dry_run=args.dry_run, repository=repository)


if __name__ == "__main__":
    main()
