---
concept: run-after-ingestpy
source: plugin-code
source_file: obsidian-wiki-engine/scripts/wiki_builder.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.018790+00:00
cluster: concept
content_hash: f96190860e71cbf0
---

# Run after ingest.py

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
wiki_builder.py
=====================================

Purpose:
    Karpathy-style wiki node formatter and linker.
    Reads ParsedRecord JSON (from ingest.py), formats each record into a
    Karpathy wiki node markdown file, generates cluster pages, and writes/
    updates _index.md and _toc.md.

Layer: Build / Wiki

Usage:
    # Run after ingest.py
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root

    # Build from a pre-existing records JSON
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --records /tmp/records.json

    # Dry run
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - ingest.py       (produces ParsedRecord input)
    - raw_manifest.py (WikiSourceConfig for path resolution)
    - distill_wiki.py (populates rlm/ summaries used in node frontmatter)
"""
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import now_iso

TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "templates" / "wiki-node.template.md"


def _load_template() -> str:
    """Load the wiki node template, falling back to inline default."""
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        "---\n"
        "concept: {concept_name}\nsource: {source_label}\n"
        "source_file: {source_file}\nwiki_root: {wiki_root}\n"
        "generated_at: {generated_at}\ncluster: {cluster_name}\n"
        "content_hash: {content_hash}\n---\n\n"
        "# {concept_title}\n\n> {rlm_summary}\n\n"
        "## Key Ideas\n\n{bullets}\n\n## Details\n\n{content_excerpt}\n\n"
        "## See Also\n\n{wikilinks}\n\n## Raw Source\n\n"
        "- **Source:** `{source_label}`\n- **File:** `{source_file}`\n"
        "- **Indexed:** {generated_at}\n"
    )


def _resolve_rlm_cache_dir(wiki_root: Path, rlm_cache_dir: Optional[Path] = None) -> Path:
    """Return the RLM cache directory, defaulting to {wiki_root}/rlm/."""
    if rlm_cache_dir:
        return Path(rlm_cache_dir).resolve()
    return wiki_root / "rlm"


def _load_rlm_summary(rlm_cache_dir: Path, concept: str) -> Optional[str]:
    """
    Load the 1-sentence RLM summary for a concept if it already exists.

    Returns None if distillation has not run yet for this concept.
    """
    summary_path = rlm_cache_dir / concept / "summary.md"
    if not summary_path.exists():
        return None
    text = summary_path.read_text(encoding="utf-8").strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()
    if text.startswith("# Summary"):
        text = text[len("# Summary"):].strip()
    return text or None


def _load_rlm_bullets(rlm_cache_dir: Path, concept: str) -> Optional[str]:
    """Load bullets.md for a concept if it exists."""
    bullets_path = rlm_cache_dir / concept / "bullets.md"
    if not bullets_path.exists():
        return None
    text = bullets_path.read_text(encoding="utf-8").strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()
    return text or None


def _find_related_concepts(
    concept: str, all_concepts: List[str], max_links: int = 6
) -> List[str]:
    """
    Find related concepts to wikilink by shared word-token overlap.

    Args:
        concept:      The concept being built.
        all_concepts: All concept slugs known at build time.
        max_links:    Maximum number of wikilinks to generate.

    Returns:
        List of concept slugs to wikilink (sorted by token overlap descending).
    """
    tokens = set(concept.split("-"))
    scored: List[tuple] = []
    for other in all_concepts:
        if other == concept:
            continue
      

*(content truncated)*

## See Also

- [[after-os-evolution-verifier-run]]
- [[dry-run-preview-stale-entries]]
- [[get-whats-after-description]]
- [[pipe-from-ingestpy]]
- [[run-bulk-md-to-docx]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/wiki_builder.py`
- **Indexed:** 2026-04-27T05:21:04.018790+00:00
