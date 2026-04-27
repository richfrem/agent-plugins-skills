---
concept: audit
source: plugin-code
source_file: obsidian-wiki-engine/scripts/audit.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.008665+00:00
cluster: wiki
content_hash: 4fce6e813bca4916
---

# Audit

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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

    existing = {f.st

*(content truncated)*

## See Also

- [[audit-a-single-file]]
- [[business-rule-audit-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/audit.py`
- **Indexed:** 2026-04-27T05:21:04.008665+00:00
