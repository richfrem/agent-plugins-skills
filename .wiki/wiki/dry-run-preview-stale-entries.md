---
concept: dry-run-preview-stale-entries
source: plugin-code
source_file: rlm-factory/scripts/cleanup_cache.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.339259+00:00
cluster: cache
content_hash: 5f53a5128f7f4190
---

# Dry run — preview stale entries

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/rlm-factory/scripts/cleanup_cache.py -->
#!/usr/bin/env python
"""
cleanup_cache.py
=====================================

Purpose:
    RLM Cleanup: Removes stale and orphan entries from the RLM semantic ledger.
    Supports dry-run mode by default; requires --apply to commit changes.

Layer: Curate / Rlm

Usage:
    # Dry run — preview stale entries
    python ./scripts/cleanup_cache.py --profile plugins

    # Remove files whose source no longer exists
    python ./scripts/cleanup_cache.py --profile plugins --apply

    # Remove entries outside the manifest + failed distillations
    python ./scripts/cleanup_cache.py --profile tools --prune-orphans --prune-failed --apply

Related:
    - rlm_config.py (configuration & utilities)
    - inventory.py (coverage audit)
    - distiller.py (cache population)
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Set

# ============================================================
# PATHS
# File is at: ./scripts/cleanup_cache.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[3]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache, save_cache, collect_files
except ImportError as e:
    print(f"[ERROR] Could not import local rlm_config from {SCRIPT_DIR}: {e}")
    sys.exit(1)


# ----------------------------------------------------------
# run_cleanup — entry-by-entry sweep of the cache
# ----------------------------------------------------------
def run_cleanup(
    config: RLMConfig,
    apply: bool,
    prune_orphans: bool,
    prune_failed: bool,
    verbose: bool
) -> int:
    """
    Scan the cache for stale, orphan, and failed entries, then optionally remove them.

    Three removal criteria (controlled by flags):
    1. **Stale**: Source file no longer exists on disk (always checked).
    2. **Failed**: Summary is the sentinel string `[DISTILLATION FAILED]`.
    3. **Orphan**: File exists but is not covered by the profile's manifest.

    Args:
        config: Active RLMConfig defining the cache and manifest.
        apply: If True, write the pruned cache to disk. If False, dry-run only.
        prune_orphans: Include orphan entries (not in manifest) in removals.
        prune_failed: Include entries with failed distillations in removals.
        verbose: Print per-entry status during the scan.

    Returns:
        Number of entries removed (or that would be removed in dry-run mode).
    """
    print(f"[CLEAN] Checking cache [{config.profile_name.upper()}]: {config.cache_path.name}")

    if not config.cache_path.exists() and not config.cache_path.with_suffix('').exists():
        print("   Cache not found. Nothing to clean.")
        return 0

    cache: Dict = load_cache(config.cache_path)
    print(f"   Entries in cache: {len(cache)}")

    entries_to_remove = []
    authorized_files: Optional[Set[str]] = None

    for rel_path, entry in list(cache.items()):
        full_path = PROJECT_ROOT / rel_path

        # 1. Failed distillation check
        if prune_failed and entry.get("summary") == "[DISTILLATION FAILED]":
            entries_to_remove.append(rel_path)
            if verbose:
                print(f"   [FAILED]  {rel_path}")
            continue

        # 2. Stale check — source file missing from disk
        if not full_path.exists():
            entries_to_remove.append(rel_path)
            if verbose:
                print(f"   [MISSING] {rel_path}")
            continue

        # 3. Orphan check — file exists but is not in manifest
        if prune_orphans:
            if au

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-cleanup-agent/scripts/cleanup_cache.py -->
#!/usr/bin/env python3
"""
cleanup_cache.py
=====================================

Purpose:
    RLM Cleanup: Removes stale and orphan entries from the RLM semantic ledger.
    Supports dry-run mode by default; requires --apply to commit changes.

Layer: Curate / Rlm

Usage:
    # Dry run — preview stale entries
    python ./scripts/cleanup_cache.py --profile plugins

    # Remove files whose source no longer exists
    python ./scripts/cleanup_cache.py --profile plugins --apply

    # Remove entries outside the manifest + failed distillations
    python ./scripts/cleanup_cache.py --profile tools --prune-orphans --prune-failed --apply

Related:
    - rlm_config.py (configuration & utilities)
    - inventory.py (coverage audit)
    - distiller.py (cache population)
"""
import sys
import argparse

*(combined content truncated)*

## See Also

- [[after-os-evolution-verifier-run]]
- [[data-is-a-dict-of-id-iso-timestamp-prune-entries-outside-dedup-window]]
- [[run-after-ingestpy]]
- [[run-bulk-md-to-docx]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `rlm-factory/scripts/cleanup_cache.py`
- **Indexed:** 2026-04-27T05:21:04.339259+00:00
