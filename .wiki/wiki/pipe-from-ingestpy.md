---
concept: pipe-from-ingestpy
source: plugin-code
source_file: obsidian-wiki-engine/scripts/concept_extractor.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.011331+00:00
cluster: text
content_hash: e6b5c6b1f16b3d07
---

# Pipe from ingest.py

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
concept_extractor.py
=====================================

Purpose:
    Cross-source concept synthesis for the Obsidian Wiki Engine.
    Implements the "compile" step from Karpathy's LLM wiki vision:
    multiple raw source files about the same concept are merged into
    one authoritative wiki node instead of producing N separate pages.

    Reads ParsedRecord JSON from stdin (or --input file), groups records by
    concept slug, merges multi-source records into a single synthetic record,
    improves cluster assignment using keyword extraction, and writes the
    deduplicated record list to stdout (or --output file).

    Called by wiki_builder.py between ingest.py and node generation.

Layer: Extract / Wiki

Usage:
    # Pipe from ingest.py
    python ingest.py --wiki-root /path/to/wiki-root | python concept_extractor.py --json

    # From file
    python concept_extractor.py --input /tmp/records.json --output /tmp/merged.json

Related:
    - ingest.py       (produces ParsedRecord input)
    - wiki_builder.py (consumes merged output)
"""
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ─── STOPWORDS ────────────────────────────────────────────────────────────────
# Common English words that don't carry cluster-level meaning
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "this",
    "that", "these", "those", "it", "its", "i", "we", "you", "they",
    "he", "she", "not", "no", "all", "also", "more", "over", "into",
    "about", "up", "out", "if", "then", "than", "so", "yet", "both",
    "each", "when", "there", "here", "how", "what", "which", "who",
    "any", "one", "two", "new", "use", "used", "using", "s",
})


def _extract_keywords(text: str, top_n: int = 3) -> List[str]:
    """
    Extract the top N keyword tokens from text by term frequency.

    Strips markdown syntax, splits on whitespace/punctuation, removes
    stopwords, and returns the most frequent remaining tokens.

    Args:
        text:  Raw content string (markdown).
        top_n: Number of top keywords to return.

    Returns:
        List of keyword strings (lowercase, deduplicated, frequency-sorted).
    """
    # Strip markdown: remove code fences, links, wikilinks, headings syntax
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", " ", text)
    text = re.sub(r"[^\w\s]", " ", text.lower())

    tokens = text.split()
    freq: Dict[str, int] = {}
    for tok in tokens:
        if len(tok) >= 4 and tok not in _STOPWORDS:
            freq[tok] = freq.get(tok, 0) + 1

    sorted_tokens = sorted(freq.keys(), key=lambda t: -freq[t])
    return sorted_tokens[:top_n]


def infer_cluster_from_content(source_label: str, concept: str, content: str) -> str:
    """
    Infer a semantic cluster name from content keywords.

    Uses top keyword(s) extracted from the content as the cluster name,
    falling back to source_label if extraction yields nothing useful.

    The cluster name is kebab-case and represents the dominant topic of
    the concept, not just its source origin.

    Args:
        source_label: The source label (used as fallback cluster).
        concept:      The concept slug.
        content:      Raw source content for keyword extraction.

    Returns:
        Kebab-case cluster name.
    """
    keywords = _extract_keywords(content, top_n=2)

    # If top keyword is too similar to concept itself, use the se

*(content truncated)*

## See Also

- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[files-to-exclude-from-output-listings]]
- [[generates-evaluation-instructions-from-a-template]]
- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/concept_extractor.py`
- **Indexed:** 2026-04-27T05:21:04.011331+00:00
