---
concept: obsidian-query-agent
source: plugin-code
source_file: obsidian-wiki-engine/skills/obsidian-query-agent/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.654712+00:00
cluster: wiki
content_hash: 92899ea79b6dc0f6
---

# Obsidian Query Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: obsidian-query-agent
description: "Progressive-disclosure query against the Obsidian LLM wiki. Returns RLM summary first, expands to bullets, then full wiki node on demand. Use when looking up concepts, searching the wiki, or getting instant context from the knowledge graph."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ and pyyaml.

```bash
pip install -r requirements.txt
```

---
# Obsidian Query Agent

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Wiki Engine

## Purpose

Progressive-disclosure query interface for the Obsidian LLM wiki. Returns the
**cheapest useful answer first**: a 1-5 sentence RLM summary. The caller can
then request bullets, then the full wiki node — expanding context only as needed.

## Progressive Disclosure Levels

| Level | Content | Cost |
|:------|:--------|:-----|
| `summary` | 1-5 sentence distilled answer | ~50 tokens |
| `bullets` | 6-10 key idea bullets | ~150 tokens |
| `full` | Complete wiki node + wikilinks | ~800 tokens |
| `raw` | Original source file content | variable |

## Usage

### Quick summary (default)
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow"
```

### Bullet-level detail
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow" --level bullets
```

### Full wiki node
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow" --level full
```

### File result back into wiki (Karpathy's "outputs always add back" loop)
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "rlm design" \
    --level full --save-as my-rlm-research
```

### Use specific vector DB profile for Phase 2
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "attention mechanism" \
    --vdb-profile research
```

### Use shared .agent/learning/ RLM cache
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth flow" \
    --rlm-cache-dir /path/to/project/.agent/learning/rlm_wiki_cache
```

### List all indexed concepts
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root --list
```

### JSON output (for programmatic use / agent pipelines)
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "api design" --json
```

## Search Strategy (3-Phase)

**Phase 1 — Slug/token match (O(1), always runs):**
1. Exact concept slug match
2. Slug is a prefix/substring of a concept name
3. Shared word-token overlap (e.g. "auth" matches "authentication-flow")

**Phase 2 — Vector DB semantic search (O(log N), requires vector-db installed):**
- Calls `vector-db` plugin's `query.py` as a subprocess
- Resolves vector DB config from `.agent/learning/vector_profiles.json`
- Default profile: `wiki` (override with `--vdb-profile`)
- Maps semantic results back to concept slugs via `meta/agent-memory.json`
- Gracefully skipped if vector-db is not installed

**Phase 3 — Full-text keyword scan (O(N), always available):**
- Grep-style scan of `wiki/*.md` content as final fallback

## --save-as: Filing Results Back Into the Wiki

Karpathy's key insight: *"I end up filing the outputs back into the wiki to enhance it."*

The `--save-as` flag writes the query result as a new wiki node:
```
wiki/{concept-slug}.md  ← new concept page derived from the query result
```

The saved node includes:
- YAML frontmatter with `query_derived: true` and `derived_from` attribution
- Original content at the requested disclosure level
- `## See Also` link back to the source concept

This means every query session can grow the wiki, not just read from it.

## When to Use

- Any time you need fast context about a concept in the wiki
- Before reading a full raw source file (use summary first)
- When `/wiki-ingest` has been run and nodes are populated
- As a pre-flight check before expensive agent operations

## Related Scripts

- `query_wiki.py` — progressive-disclosure query engine
- `raw_manifest.

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[template-post-run-agent-self-assessment]]
- [[research-summary-agent-operating-systems-agent-os]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/skills/obsidian-query-agent/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.654712+00:00
