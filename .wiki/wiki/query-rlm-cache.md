---
concept: query-rlm-cache
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_query.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.324304+00:00
cluster: search
content_hash: eec5f0828c5964f8
---

# Query RLM Cache

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Search the RLM cache for file summaries by keyword (offline — no Ollama needed)
argument-hint: "\"search term\" [--type legacy|tool] [--list] [--json]"
---

# Query RLM Cache

Instant O(1) search of the semantic ledger. **No Ollama required** — reads JSON only.

## Usage
```bash
# Search for a topic
python ./scripts/query_cache.py --profile project "bail"

# Search tool cache
python ./scripts/query_cache.py --profile tools "distiller"

# List all cached entries
python ./scripts/query_cache.py --profile project --list

# JSON output for programmatic use
python ./scripts/query_cache.py --profile project "config" --json
```

## Matches Against
- File path (substring)
- Summary content (substring)
- Content hash


## See Also

- [[rlm-init-cache-bootstrap]]
- [[recursive-language-model-rlm-the-holographic-cache-pattern]]
- [[recursive-language-model-rlm-the-holographic-cache-pattern]]
- [[recursive-language-model-rlm-the-holographic-cache-pattern]]
- [[recursive-language-model-rlm-the-holographic-cache-pattern]]
- [[rlm-init-cache-bootstrap]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_query.md`
- **Indexed:** 2026-04-17T06:42:10.324304+00:00
