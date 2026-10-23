#!/usr/bin/env python3
"""
convert_symlinks_to_manifest.py (CLI)
=====================================

Purpose:
    Converts a plugin's file-level symlinks into copy-manifest entries (APM migration plan,
    Section 10.3; plugin architecture policy Section 5). For each symlink: the link is
    removed from the working tree and `symlinks.json` records the same pair with
    `strategy: "copy"`, so the build pipeline creates the physical copy in staging and the
    packed bundle carries it. The link is also untracked (`git rm --cached`), so the copy that
    materialize_copies.py later writes in its place stays out of git. Dry-run by default.

    Left alone (reported): symlinks under tests/ (tests run from source and are not packaged),
    and links whose target is missing, a directory, another symlink, or outside the plugin.
    Manifest entries with strategy "symlink" whose destination is now a real file are removed
    as stale.

Usage:
    python3 convert_symlinks_to_manifest.py --path <repo-root>                       # all plugins, dry-run
    python3 convert_symlinks_to_manifest.py --path <repo-root> --plugins dev-utils --apply

Exit codes: 0 success, 2 usage error.

Key Input Dependencies:
    - git (symlinks are read from the index, as in apm_build_pipeline.py)
    - <repo-root>/symlinks.json ({"version": ..., "links": [{src, dst, strategy, description}]})

Function Index:
    - plugin_links(root, plugin_rel) -> list[dict]
    - classify(root, plugin_rel, link) -> tuple[str, str]
    - update_manifest(links, converted, root) -> tuple[list, dict]
    - convert(root, plugins, apply) -> dict
    - main() -> None
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apm_build_pipeline import git_symlink_entries  # noqa: E402

SKIP_PARTS = ("/tests/",)


# All current symlinks of one plugin, from the git index.
def plugin_links(root: Path, plugin_rel: str) -> list[dict]:
    """Return [{path, link_text}] for the plugin's symlinks still present as links."""
    return git_symlink_entries(root, plugin_rel)


# Decide what to do with one link: convert it, or report why not.
def classify(root: Path, plugin_rel: str, link: dict) -> tuple[str, str]:
    """Return (action, detail): ('convert', target_rel) or ('skip', reason)."""
    if any(part in "/" + link["path"] for part in SKIP_PARTS):
        return "skip", "under tests/ (not packaged; tests run from source)"
    target = Path(os.path.normpath(root / Path(link["path"]).parent / link["link_text"]))
    target_rel = os.path.relpath(target, root).replace(os.sep, "/")
    if not target_rel.startswith(plugin_rel.rstrip("/") + "/"):
        return "skip", f"target outside the plugin: {target_rel}"
    if target.is_symlink():
        return "skip", f"target is itself a symlink: {target_rel}"
    if not target.is_file():
        return "skip", f"target missing or a directory: {target_rel}"
    return "convert", target_rel


# Merge converted pairs into the manifest; drop stale symlink entries.
def update_manifest(links: list, converted: list[dict], root: Path) -> tuple[list, dict]:
    """Return (new_links, stats). Existing entries for a dst are updated, not duplicated."""
    by_dst = {entry.get("dst"): entry for entry in links}
    stats = {"updated": 0, "added": 0, "stale_removed": 0}
    for pair in converted:
        entry = by_dst.get(pair["dst"])
        if entry:
            entry.update(src=pair["src"], strategy="copy")
            stats["updated"] += 1
        else:
            entry = {"src": pair["src"], "dst": pair["dst"], "strategy": "copy",
                     "description": "converted from symlink (APM migration)"}
            links.append(entry)
            by_dst[pair["dst"]] = entry
            stats["added"] += 1
    converted_dsts = {pair["dst"] for pair in converted}
    kept = []
    for entry in links:
        dst = root / entry.get("dst", "")
        stale = (entry.get("strategy") == "symlink" and entry.get("dst") not in converted_dsts
                 and dst.is_file() and not dst.is_symlink())
        if stale:
            stats["stale_removed"] += 1
        else:
            kept.append(entry)
    return kept, stats


# Convert the selected plugins; write changes only with apply=True.
def convert(root: Path, plugins: list[str], apply: bool) -> dict:
    """Return {converted, skipped, manifest} for the run."""
    converted, skipped = [], []
    for plugin in plugins:
        plugin_rel = f"plugins/{plugin}"
        for link in plugin_links(root, plugin_rel):
            action, detail = classify(root, plugin_rel, link)
            if action == "convert":
                converted.append({"src": detail, "dst": link["path"]})
            else:
                skipped.append({"path": link["path"], "reason": detail})
    manifest_path = root / "symlinks.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {"version": 1, "links": []}
    new_links, stats = update_manifest(data.get("links", []), converted, root)
    if apply:
        for pair in converted:
            (root / pair["dst"]).unlink()
        # Untrack the links so the materialized copies (materialize_copies.py) stay ignored.
        dsts = [pair["dst"] for pair in converted]
        for start in range(0, len(dsts), 500):
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", "--", *dsts[start:start + 500]], check=True)
        data["links"] = new_links
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"applied": apply, "converted": converted, "skipped": skipped, "manifest": stats}


# CLI entry point.
def main() -> None:
    """Parse arguments, convert, print a summary."""
    parser = argparse.ArgumentParser(description="Convert plugin symlinks to copy-manifest entries")
    parser.add_argument("--path", default=".", help="Repository root (default: .)")
    parser.add_argument("--plugins", help="Comma-separated plugin names (default: every plugin)")
    parser.add_argument("--apply", action="store_true", help="Remove the links and write symlinks.json")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    plugins = ([p.strip() for p in args.plugins.split(",") if p.strip()] if args.plugins
               else sorted(d.name for d in (root / "plugins").iterdir() if d.is_dir()))
    result = convert(root, plugins, args.apply)
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"{mode}: {len(result['converted'])} symlinks -> copy entries; manifest {result['manifest']}; "
          f"{len(result['skipped'])} skipped")
    for item in result["skipped"]:
        print(f"  [SKIP] {item['path']}: {item['reason']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
