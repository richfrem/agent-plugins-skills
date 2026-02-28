#!/usr/bin/env python3
"""
query_cache.py
=====================================

Purpose:
    RLM Search: Instant keyword-based lookup against the semantic ledger.
    Searches entry paths and summary text to surface relevant cached records.

Layer: Curate / Rlm

Usage:
    python plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile plugins "rlm"
    python plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile tools --list
    python plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile plugins "factory" --json

Related:
    - rlm_config.py (configuration & cache utilities)
    - distiller.py (cache population)
"""
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# ============================================================
# PATHS
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache
except ImportError as e:
    print(f"❌ Could not import RLMConfig from {SCRIPT_DIR}: {e}")
    sys.exit(1)


# ----------------------------------------------------------
# search_cache — keyword search across paths and summaries
# ----------------------------------------------------------
def search_cache(
    term: str,
    config: RLMConfig,
    show_summary: bool = True,
    output_json: bool = False
) -> None:
    """
    Search the RLM cache for entries matching the given term.

    Matches against both the file path and the summary text. Results are
    sorted by path and printed to stdout (or serialized as JSON).

    Args:
        term: Keyword to search for (case-insensitive).
        config: Active RLMConfig providing the cache path.
        show_summary: If True, print a preview of the summary text.
        output_json: If True, serialize results as JSON instead of formatted text.
    """
    data = load_cache(config.cache_path)
    term_lower = term.lower()

    if not output_json:
        print(f"🔍 Searching [{config.profile_name.upper()}] for: '{term}'...")

    matches: List[Dict[str, Any]] = []
    for rel_path, entry in data.items():
        summary_str = str(entry.get("summary", ""))
        if term_lower in rel_path.lower() or term_lower in summary_str.lower():
            matches.append({"path": rel_path, "entry": entry})

    matches.sort(key=lambda x: x["path"])

    if output_json:
        print(json.dumps(matches, indent=2))
        return

    if not matches:
        print("   No matches found.")
        return

    print(f"✅ Found {len(matches)} match(es):\n")
    for match in matches:
        path = match["path"]
        entry = match["entry"]
        print(f"📄 {path}")
        print(f"   🕒 Indexed: {entry.get('summarized_at', 'Unknown')}")
        if show_summary:
            summary_str = str(entry.get("summary", "No summary."))
            preview = (summary_str[:300] + "...") if len(summary_str) > 300 else summary_str
            print(f"   📝 {preview}")
        print("-" * 50)


# ----------------------------------------------------------
# list_cache — enumerate all entries in a cache
# ----------------------------------------------------------
def list_cache(config: RLMConfig) -> None:
    """
    List all file paths currently indexed in the cache.

    Args:
        config: Active RLMConfig providing the cache path.
    """
    data = load_cache(config.cache_path)
    print(f"📚 [{config.profile_name.upper()}] — {len(data)} entries:\n")
    for rel_path in sorted(data.keys()):
        print(f"   - {rel_path}")


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main() -> None:
    """Parse CLI arguments and dispatch to search_cache() or list_cache()."""
    parser = argparse.ArgumentParser(description="RLM Cache — keyword search and listing")
    parser.add_argument("term", nargs="?", help="Search term (filename fragment or content keyword)")
    parser.add_argument("--profile", required=True, help="RLM profile name (from rlm_profiles.json)")
    parser.add_argument("--list", action="store_true", help="List all cached file paths")
    parser.add_argument("--no-summary", action="store_true", help="Hide summary text in results")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()
    config = RLMConfig(profile_name=args.profile)

    if args.list:
        list_cache(config)
    elif args.term:
        search_cache(args.term, config, show_summary=not args.no_summary, output_json=args.json)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
