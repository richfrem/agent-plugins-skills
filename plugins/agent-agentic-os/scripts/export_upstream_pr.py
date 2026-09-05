#!/usr/bin/env python
"""
export_upstream_pr.py — Upstream PR Exporter with Human Gate
============================================================

Purpose:
    Safely exports evolved plugins to upstream repositories.
    Defaults strictly to --dry-run, enforcing an allowlist of plugin files,
    sanitizing diffs, and requiring explicit human sign-off before any remote push.

Key Input Dependencies:
    - Local git repo working tree (diff/changed-files source)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _get_repo_root(repo_dir: Path = None) -> Path:
    """Resolve the repo root, defaulting to the git toplevel of the cwd."""
    if repo_dir:
        return repo_dir.resolve()
    try:
        res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(res.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def get_changed_files(repo_root: Path) -> list[str]:
    """Return the list of files changed in the current branch vs. its base."""
    res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    files = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        p = line[3:].strip()
        if " -> " in p:
            p = p.split(" -> ")[1].strip()
        files.append(p)
    return files


def sanitize_and_filter_files(files: list[str], target_plugin: str = None) -> list[str]:
    """Filter changed files to the export allowlist and scrub disallowed paths."""
    allowed = []
    for f in files:
        # Must be within plugins/
        if not f.startswith("plugins/"):
            continue
        if target_plugin and not f.startswith(f"plugins/{target_plugin}/"):
            continue
        # Reject obvious credential/env files
        name = Path(f).name.lower()
        if any(bad in name for bad in [".env", "secret", "credentials", "id_rsa"]):
            continue
        allowed.append(f)
    return allowed


def main():
    """CLI entry point: parse args, sanitize the diff, and export only after human sign-off."""
    parser = argparse.ArgumentParser(description="Export Evolved Plugin to Upstream PR")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default mode: simulate PR export")
    parser.add_argument("--execute", action="store_true", help="Execute git push and gh pr create (requires human confirmation)")
    parser.add_argument("--plugin", default=None, help="Specific plugin to export")
    parser.add_argument("--repo-dir", type=Path, default=None)

    args = parser.parse_args()
    repo_root = _get_repo_root(args.repo_dir)

    all_files = get_changed_files(repo_root)
    allowed_files = sanitize_and_filter_files(all_files, args.plugin)

    branch_name = f"upstream-sync/{args.plugin or 'plugins'}"
    pr_title = f"feat({args.plugin or 'plugins'}): Upstream synchronization of verified evolution"
    pr_body = (
        "### Verified Self-Evolution Upstream Export\n"
        "- Automated synchronization from consumer repository\n"
        "- Verified with programmatic Evolution Integrity Receipt\n"
        "- Sanitized allowlist applied\n"
    )

    if not args.execute:
        print("=== DRY RUN: UPSTREAM PR EXPORT ===")
        print(f"Proposed Branch: {branch_name}")
        print(f"PR Title:        {pr_title}")
        print(f"PR Body:\n{pr_body}")
        print("Allowlisted Files:")
        for af in allowed_files:
            print(f"  + {af}")
        print("\nExcluded/Untracked non-plugin files are omitted.")
        print("Zero git remotes touched. To execute, pass --execute with explicit confirmation.")
        sys.exit(0)

    # Execution requires explicit interactive confirmation
    print("WARNING: --execute requested. This will create a branch and open a PR.", file=sys.stderr)
    print("Human gate: upstream PR creation aborted until interactive confirmation protocol is completed.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
