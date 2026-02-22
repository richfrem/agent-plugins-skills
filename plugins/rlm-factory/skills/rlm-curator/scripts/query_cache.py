#!/usr/bin/env python3
"""
query_cache.py (CLI)
=====================================

Purpose:
    RLM Search: Instant O(1) semantic search of the ledger.
"""

import json
import argparse
import sys
from pathlib import Path

# Paths standardization
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache
except ImportError as e:
    print(f"❌ Could not import local RLMConfig from {SCRIPT_DIR}: {e}")
    sys.exit(1)


def search_cache(term: str, config: RLMConfig, show_summary: bool = True, output_json: bool = False):
    """Search the RLM cache for entries matching the term."""
    data = load_cache(config.cache_path)
    
    if not output_json:
        print(f"🔍 Searching RLM Cache [{config.profile_name.upper()}] for: '{term}'...")
    
    matches = []
    for rel_path, entry in data.items():
        if term.lower() in rel_path.lower() or term.lower() in entry.get('summary', '').lower():
            matches.append({"path": rel_path, "entry": entry})
    
    matches.sort(key=lambda x: x['path'])

    if output_json:
        print(json.dumps(matches, indent=2))
        return

    if not matches:
        print("No matches found.")
        return

    print(f"✅ Found {len(matches)} matches:\n")
    for match in matches:
        path = match['path']
        entry = match['entry']
        timestamp = entry.get('summarized_at', 'Unknown Time')
        print(f"📄 {path}")
        print(f"   🕒 Indexed: {timestamp}")
        if show_summary:
            summary = entry.get('summary', 'No summary available.')
            preview = summary[:300] + "..." if len(summary) > 300 else summary
            print(f"   📝 {preview}")
        print("-" * 50)


def list_cache(config: RLMConfig):
    """List all entries in the RLM cache."""
    data = load_cache(config.cache_path)
    print(f"📚 RLM Cache [{config.profile_name.upper()}] — {len(data)} entries:\n")
    for rel_path in sorted(data.keys()):
        print(f"   - {rel_path}")


def main():
    parser = argparse.ArgumentParser(description="Query RLM Cache")
    parser.add_argument("term", nargs="?", help="Search term (filename or content keyword)")
    parser.add_argument("--profile", required=True, help="RLM Profile name (from rlm_profiles.json)")
    parser.add_argument("--list", action="store_true", help="List all cached files")
    parser.add_argument("--no-summary", action="store_true", help="Hide summary text")
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
