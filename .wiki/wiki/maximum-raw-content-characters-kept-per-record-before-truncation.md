---
concept: maximum-raw-content-characters-kept-per-record-before-truncation
source: plugin-code
source_file: obsidian-wiki-engine/scripts/ingest.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.013269+00:00
cluster: wiki
content_hash: dbf3a4195c210275
---

# Maximum raw content characters kept per record before truncation

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
ingest.py
=====================================

Purpose:
    Raw file ingestion pipeline. Reads all files from sources registered in
    wiki_sources.json, normalizes content, and produces ParsedRecord dicts
    ready for wiki_builder.py. Also updates agent-memory.json with fresh hashes.

Layer: Ingest / Wiki

Usage:
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root --source arch-docs
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - raw_manifest.py  (WikiSourceConfig loader)
    - wiki_builder.py  (consumes ParsedRecord output)
    - audit.py         (stale detection via agent-memory.json)
"""
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import (
    WikiSourceConfig, load_agent_memory, save_agent_memory,
    compute_hash, is_stale, now_iso
)
from concept_extractor import infer_cluster_from_content

# Maximum raw content characters kept per record before truncation
MAX_CONTENT_CHARS = 4000


def extract_title(content: str, fallback: str) -> str:
    """
    Extract the first H1 heading from markdown, or use filename fallback.

    Args:
        content:  Raw file content.
        fallback: Filename stem to use if no H1 found.

    Returns:
        Title string.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback.replace("-", " ").replace("_", " ").title()


def extract_concept_name(title: str) -> str:
    """
    Convert a title into a slug-style concept name for wiki node filenames.

    Args:
        title: Human-readable title.

    Returns:
        Lowercase kebab-case concept name.
    """
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug


def infer_cluster(source_label: str, concept: str, content: str = "") -> str:
    """
    Infer a semantic cluster name from content keywords.

    Delegates to concept_extractor.infer_cluster_from_content for keyword-
    based cluster assignment. Falls back to source_label if extraction fails.

    Args:
        source_label: The label of the source (e.g. 'arch-docs').
        concept:      The concept slug.
        content:      Raw file content for keyword extraction.

    Returns:
        Kebab-case cluster name derived from dominant content keywords.
    """
    return infer_cluster_from_content(source_label, concept, content)


def parse_file(
    file_path: Path,
    source_cfg: WikiSourceConfig,
) -> Optional[Dict[str, Any]]:
    """
    Read and normalize one source file into a ParsedRecord dict.

    Returns None if the file cannot be read or is below min size.

    Args:
        file_path:   Absolute path to the source file.
        source_cfg:  WikiSourceConfig for this source.

    Returns:
        ParsedRecord dict or None.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Cannot read {file_path}: {e}", file=sys.stderr)
        return None

    if len(content.strip()) < 50:
        return None

    rel_path = source_cfg.relative_path(file_path)
    title = extract_title(content, file_path.stem)
    concept = extract_concept_name(title)
    cluster = infer_cluster(source_cfg.label, concept, content)
    content_hash = compute_hash(content)

    # Truncate for wiki node storage
    excerpt = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS:
        excerpt += "\n\n*(content truncated)*"

    return {
        "source_name":   source_cfg.source_name,
        "source_label":  source_cfg.label,
        "source_path":   str(source_cfg

*(content truncated)*

## See Also

- [[expected-minimums-per-fixture]]
- [[parse-frontmatter-and-content]]
- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]
- [[premium-dispatch-claude-sonnet-46-for-complex-multi-file-generation-charged-per-request-batch-everything]]
- [[strip-yaml-frontmatter-from-skillmd-before-using-it-as-an-agent-prompt]]
- [[track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/ingest.py`
- **Indexed:** 2026-04-27T05:21:04.013269+00:00
