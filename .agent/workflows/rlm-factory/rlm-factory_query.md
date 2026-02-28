---
description: Search the RLM cache for file summaries by keyword (offline — no Ollama needed)
argument-hint: "\"search term\" [--type legacy|tool] [--list] [--json]"
---

# Query RLM Cache

Instant O(1) search of the semantic ledger. **No Ollama required** — reads JSON only.

## Usage
```bash
# Search for a topic
python3 plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile project "bail"

# Search tool cache
python3 plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile tools "distiller"

# List all cached entries
python3 plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile project --list

# JSON output for programmatic use
python3 plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py --profile project "config" --json
```

## Matches Against
- File path (substring)
- Summary content (substring)
- Content hash
