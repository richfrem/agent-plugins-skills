---
description: Search the RLM cache for file summaries by keyword
argument-hint: "\"search term\" [--profile project|tools] [--list] [--json]"
---

# Query RLM Cache

Instant search of the semantic ledger. Because the cache leverages pure Markdown directories, you do NOT strictly need this script. You can use native `grep_search`.

## Usage
```bash
# Preferred Method (Native):
grep_search "bail" .agent/learning/rlm_summary_cache/

# Fallback CLI Method:
python ./scripts/query_cache.py --profile project "bail"
python ./scripts/query_cache.py --profile tools "distiller"
```

## Matches Against
- File path (substring)
- Summary content (substring)
