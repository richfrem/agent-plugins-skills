#!/usr/bin/env python3
"""
audit.py
=====================================

Purpose:
    Wiki health audit. Checks for orphan nodes, missing RLM summaries,
    stale source files, and broken wikilinks. Prints a human-readable
    report and exits non-zero if critical issues are found.

Layer: Audit / Wiki

Usage:
    python ./scripts/audit.py --wiki-root /path/to/wiki-root
    python ./scripts/audit.py --wiki-root /path/to/wiki-root --fix-stale
    python ./scripts/audit.py --wiki-root /path/to/wiki-root --json

Related:
    - raw_manifest.py  (WikiSourceConfig, agent-memory.json)
    - distill_wiki.py  (fixes missing summaries)
    - ingest.py        (fixes stale nodes)
"""
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import (
    WikiSourceConfig, load_agent_memory, save_agent_memory,
    compute_hash, now_iso
)

LAYERS = ["summary", "bullets", "deep"]


def audit_missing_summaries(wiki_root: Path) -> List[str]:
    """
    List concept slugs with a wiki node but no summary.md RLM layer.

    Returns:
        List of concept slugs missing at least one RLM layer.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []
    missing = []
    for node_file in sorted(wiki_dir.glob("*.md")):
        if node_file.name.startswith("_"):
            continue
        concept = node_file.stem
        if not (wiki_root / "rlm" / concept / "summary.md").exists():
            missing.append(concept)
    return missing


def audit_stale_nodes(wiki_root: Path) -> List[Dict[str, str]]:
    """
    Find wiki nodes whose source file content has changed since last ingest.

    Returns:
        List of dicts with 'key' and 'reason' fields.
    """
    memory = load_agent_memory(wiki_root)
    stale = []
    for key, entry in memory.items():
        parts = key.split("/", 1)
        if len(parts) < 2:
            continue
        source_name, rel_path = parts

        try:
            cfg = WikiSourceConfig(source_name, wiki_root=wiki_root)
        except SystemExit:
            stale.append({"key": key, "reason": f"Source '{source_name}' no longer registered"})
            continue

        file_path = cfg.source_path / rel_path
        if not file_path.exists():
            stale.append({"key": key, "reason": "Source file deleted"})
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            stale.append({"key": key, "reason": "Unreadable"})
            continue

        if compute_hash(content) != entry.get("hash", ""):
            stale.append({"key": key, "reason": "Content changed since last ingest"})

    return stale


def audit_orphan_nodes(wiki_root: Path) -> List[str]:
    """
    Find wiki nodes whose source file no longer exists.

    A node is orphaned when the 'source_file' frontmatter path resolves to a
    file that is no longer on disk.

    Returns:
        List of concept slugs that are orphaned.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []

    memory = load_agent_memory(wiki_root)
    indexed_concepts = {v.get("concept") for v in memory.values() if v.get("concept")}

    orphans = []
    for node_file in sorted(wiki_dir.glob("*.md")):
        if node_file.name.startswith("_"):
            continue
        concept = node_file.stem
        if concept not in indexed_concepts:
            orphans.append(concept)
    return orphans


def audit_broken_wikilinks(wiki_root: Path) -> List[Dict[str, str]]:
    """
    Scan all wiki nodes for [[wikilinks]] that point to non-existent concepts.

    Returns:
        List of dicts with 'node', 'broken_link' fields.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []

    existing = {f.stem for f in wiki_dir.glob("*.md") if not f.name.startswith("_")}
    broken = []
    wikilink_pattern = re.compile(r"\[\[([^\]|#]+)")

    for node_file in sorted(wiki_dir.glob("*.md")):
        if node_file.name.startswith("_"):
            continue
        try:
            content = node_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in wikilink_pattern.finditer(content):
            link_target = match.group(1).strip()
            if link_target not in existing:
                broken.append({"node": node_file.stem, "broken_link": link_target})

    return broken


def audit_source_paths(wiki_root: Path) -> List[Dict[str, str]]:
    """
    Check that all registered source paths in wiki_sources.json exist on disk.

    Returns:
        List of dicts with 'source_name' and 'path' for missing sources.
    """
    sources = WikiSourceConfig.all_sources(wiki_root=wiki_root)
    missing = []
    for name, cfg in sources.items():
        if not cfg.source_path.exists():
            missing.append({"source_name": name, "path": str(cfg.source_path)})
    return missing


def fix_stale_memory(wiki_root: Path, stale: List[Dict[str, str]]) -> None:
    """
    Remove stale entries from agent-memory.json so ingest re-processes them.

    Args:
        wiki_root: Root of the wiki output directory.
        stale:     Output of audit_stale_nodes().
    """
    memory = load_agent_memory(wiki_root)
    for entry in stale:
        key = entry["key"]
        if key in memory:
            del memory[key]
            print(f"  [FIX] Removed stale entry: {key}")
    save_agent_memory(memory, wiki_root)


def main() -> None:
    """Run the wiki audit and print a health report."""
    parser = argparse.ArgumentParser(description="Audit the Obsidian LLM wiki for health issues")
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--fix-stale", action="store_true",
                        help="Remove stale entries from agent-memory.json (triggers re-ingest on next run)")
    parser.add_argument("--json", dest="output_json", action="store_true",
                        help="Output audit results as JSON")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()

    wiki_dir = wiki_root / "wiki"
    total_nodes = len([f for f in wiki_dir.glob("*.md") if not f.name.startswith("_")]) if wiki_dir.exists() else 0

    missing_summaries = audit_missing_summaries(wiki_root)
    stale_nodes = audit_stale_nodes(wiki_root)
    orphan_nodes = audit_orphan_nodes(wiki_root)
    broken_links = audit_broken_wikilinks(wiki_root)
    missing_sources = audit_source_paths(wiki_root)

    report = {
        "wiki_root": str(wiki_root),
        "audited_at": now_iso(),
        "total_nodes": total_nodes,
        "missing_summaries": missing_summaries,
        "stale_nodes": stale_nodes,
        "orphan_nodes": orphan_nodes,
        "broken_wikilinks": broken_links,
        "missing_sources": missing_sources,
    }

    if args.output_json:
        print(json.dumps(report, indent=2))
        return

    print(f"\n[AUDIT] Wiki Root: {wiki_root}")
    print(f"[OK]    Total nodes       : {total_nodes}")

    def _status(count: int, warn_level: int = 1) -> str:
        return "[WARN] " if count >= warn_level else "[OK]   "

    print(f"{_status(len(missing_summaries))}Missing RLM summaries : {len(missing_summaries)}"
          + ("  -> run /wiki-distill" if missing_summaries else ""))
    print(f"{_status(len(stale_nodes))}Stale nodes           : {len(stale_nodes)}"
          + ("  -> run /wiki-ingest" if stale_nodes else ""))
    print(f"{_status(len(orphan_nodes), 1)}Orphan nodes          : {len(orphan_nodes)}"
          + ("  -> source files deleted" if orphan_nodes else ""))
    print(f"{_status(len(broken_links))}Broken wikilinks      : {len(broken_links)}"
          + ("  -> run /wiki-rebuild" if broken_links else ""))
    print(f"{_status(len(missing_sources))}Missing source paths  : {len(missing_sources)}"
          + ("  -> update wiki_sources.json" if missing_sources else ""))

    if args.fix_stale and stale_nodes:
        print(f"\n[FIX] Removing {len(stale_nodes)} stale entries from agent-memory.json...")
        fix_stale_memory(wiki_root, stale_nodes)
        print("      Done. Run /wiki-ingest to re-process.")

    critical = len(missing_sources) + len(orphan_nodes)
    sys.exit(1 if critical > 0 else 0)


if __name__ == "__main__":
    main()
