---
concept: project-root
source: plugin-code
source_file: obsidian-wiki-engine/scripts/query_wiki.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.016397+00:00
cluster: wiki
content_hash: 456f2fbe63228d74
---

# ─── PROJECT ROOT ─────────────────────────────────────────────────────────────

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
query_wiki.py
=====================================

Purpose:
    Progressive-disclosure query engine for the Obsidian LLM wiki.
    Returns the cheapest useful answer first — a 1-sentence RLM summary —
    and expands to bullets or full wiki node only on demand.

    Search strategy (3-phase):
        1. Exact slug + token match against wiki/_index.md
        2. Vector DB semantic search (via vector-db plugin's query.py)
           Resolved from .agent/learning/vector_profiles.json automatically.
        3. Full-text keyword scan of wiki/*.md as final fallback

    The --save-as flag files query results back into the wiki as a new node,
    implementing Karpathy's "outputs always add back to the knowledge base" loop.

Layer: Query / Wiki

Usage:
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow"
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "api design" --level bullets
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "Oracle Forms" --level full
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root --list
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth" --json
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth flow" --save-as auth-flow
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "rlm design" --vdb-profile wiki

Related:
    - raw_manifest.py   (WikiSourceConfig for wiki root resolution)
    - distill_wiki.py   (populates the rlm/ summaries)
    - wiki_builder.py   (populates wiki/ nodes)
    - concept_extractor (infer_cluster_from_content for saved nodes)
"""
import sys
import json
import argparse
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import WikiSourceConfig, now_iso, _find_project_root

DISCLOSURE_LEVELS = ["summary", "bullets", "full", "raw"]

# ─── PROJECT ROOT ─────────────────────────────────────────────────────────────
_PROJECT_ROOT = _find_project_root(SCRIPT_DIR)


def _slug(text: str) -> str:
    """Convert a search term to a concept slug for exact matching."""
    s = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


# ─── VECTOR DB PHASE 2 ────────────────────────────────────────────────────────

def _find_vdb_query_script() -> Optional[Path]:
    """
    Discover the vector-db query.py script.

    Resolution order (mirrors how rlm-distill-agent is discovered):
        1. .agent/learning/ sibling to vector_profiles.json (installed skills)
        2. .agents/skills/vector-db-search/scripts/query.py
        3. plugins/vector-db/scripts/query.py (dev tree)

    Returns:
        Resolved Path to query.py, or None if not found.
    """
    candidates = [
        _PROJECT_ROOT / ".agents" / "skills" / "vector-db-search" / "scripts" / "query.py",
        _PROJECT_ROOT / "plugins" / "vector-db" / "scripts" / "query.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _vector_phase2_search(
    term: str,
    wiki_root: Path,
    vdb_profile: str,
    limit: int = 5,
) -> List[str]:
    """
    Run vector DB semantic search and map results back to concept slugs.

    Calls the vector-db query.py as a subprocess, parses 'Source:' lines
    from the output, and reverse-maps file paths to concept slugs via
    agent-memory.json.

    Args:
        term:        Raw search term.
        wiki_root:   Wiki root (for agent-memory.json lookup).
        vdb_profile: Vector DB profile name (default: "wiki").
        limit:       Max results to request.

    Returns:
        Ordered list of concept slugs matching the semantic query.
        Empty list if vector-db is not available.
    """
    query_script = _find_vdb_query_script()
    if not query_script:
        return []

 

*(content truncated)*

## See Also

- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[robustly-discover-the-project-root]]
- [[1-check-root-structure]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/query_wiki.py`
- **Indexed:** 2026-04-27T05:21:04.016397+00:00
