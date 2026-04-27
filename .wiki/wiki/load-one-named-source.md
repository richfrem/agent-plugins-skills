---
concept: load-one-named-source
source: plugin-code
source_file: obsidian-wiki-engine/scripts/raw_manifest.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.017227+00:00
cluster: path
content_hash: fda74614d89eef03
---

# Load one named source

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
raw_manifest.py
=====================================

Purpose:
    WikiSourceConfig — centralized configuration loader for the Obsidian Wiki
    Engine. Mirrors the RLMConfig pattern from rlm-factory: loads named source
    entries from the raw sources manifest, giving every wiki script a single
    configuration entry point.

    Canonical manifest location: .agent/learning/rlm_wiki_raw_sources_manifest.json
    This mirrors the rlm-factory pattern of storing all learning config under
    .agent/learning/. Override via WIKI_SOURCES_PATH env var.

Layer: Config / Wiki

Usage:
    from raw_manifest import WikiSourceConfig, load_wiki_sources, save_wiki_sources

    # Load one named source
    cfg = WikiSourceConfig(source_name="arch-docs", wiki_root=Path("/path/to/root"))

    # Load all sources
    for name, cfg in WikiSourceConfig.all_sources(wiki_root).items():
        print(cfg.source_path, cfg.label)

    # Collect eligible files from a source
    files = cfg.collect_files()

Related:
    - ingest.py       (raw file parsing)
    - wiki_builder.py (node generation)
    - distill_wiki.py (RLM distillation)
    - query_wiki.py   (progressive query)
    - audit.py        (health checks)
"""
import os
import sys
import json
import fnmatch
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


# ─── PROJECT ROOT ─────────────────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    """Walk up from start to find the .git root (or .agents root), or fall back to 4 levels up."""
    # Use .absolute() instead of .resolve() to prevent symlink traversal
    # which breaks when the script is symlinked from a plugin repository.
    absolute_start = start.absolute()
    for p in [absolute_start] + list(absolute_start.parents):
        if (p / ".git").is_dir() or (p / ".agents").is_dir():
            return p
    return absolute_start.parents[3]


PROJECT_ROOT = _find_project_root(Path(__file__))


# Canonical manifest filename under .agent/learning/
_CANONICAL_MANIFEST_NAME = "rlm_wiki_raw_sources_manifest.json"
# Legacy fallback filename (wiki-root local)
_LEGACY_MANIFEST_NAME = "wiki_sources.json"


# ─── SOURCES FILE DISCOVERY ───────────────────────────────────────────────────
def _get_sources_path(wiki_root: Optional[Path] = None) -> Path:
    """
    Resolve the raw sources manifest path.

    Priority:
        1. WIKI_SOURCES_PATH env var
        2. {project_root}/.agent/learning/rlm_wiki_raw_sources_manifest.json  (canonical)
        3. {project_root}/.agents/learning/rlm_wiki_raw_sources_manifest.json (alt install)
        4. {wiki_root}/meta/raw-sources.json                                  (local override)
        5. {wiki_root}/meta/wiki_sources.json                                 (legacy)

    The canonical location mirrors rlm-factory's convention of keeping all
    learning config under .agent/learning/ for consistent discovery.
    """
    env_path = os.getenv("WIKI_SOURCES_PATH")
    if env_path:
        p = Path(env_path)
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    # Canonical: .agent/learning/ (mirrors rlm_profiles.json location)
    for learning_dir in (".agent/learning", ".agents/learning"):
        candidate = PROJECT_ROOT / learning_dir / _CANONICAL_MANIFEST_NAME
        if candidate.exists():
            return candidate

    # Local wiki-root override
    if wiki_root:
        for name in ("raw-sources.json", _LEGACY_MANIFEST_NAME):
            candidate = Path(wiki_root) / "meta" / name
            if candidate.exists():
                return candidate

    # Return canonical default even if not yet created (init will create it)
    return PROJECT_ROOT / ".agent" / "learning" / _CANONICAL_MANIFEST_NAME


def get_default_save_path(wiki_root: Optional[Path] = None) -> Path:
    """
    Return the preferred path for writing the raw sources manifest

*(content truncated)*

## See Also

- [[load-and-validate-eval-results-data-from-tsv]]
- [[load-input-from-files-or-stdin]]
- [[no-session-in-progress-suggest-starting-one]]
- [[phase-1-ensure-vendor-source]]
- [[schema-validation-every-entry-must-use-the-new-flat-source-key]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/raw_manifest.py`
- **Indexed:** 2026-04-27T05:21:04.017227+00:00
