---
name: rlm-search
plugin: agent-memory
description: 3-Phase Knowledge Search strategy enforcing optimal lookup order - RLM Summary Scan -> Vector DB Semantic Search -> Grep/Exact Match.
allowed-tools: Bash, Read, Write
---

# RLM Knowledge Search (`rlm-search`)

Enforces the 3-phase knowledge search protocol to locate repository context with minimal token overhead.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Search Order Protocol](#search-order-protocol)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Start at Phase 1**: Never skip directly to full-repo grep or read files cold without checking summary cache first.
2. **Scope Grep Searches**: Restrict regex or grep searches to files identified in Phase 1 or Phase 2.
3. **Never Edit Ledgers**: Reading summaries is purely non-destructive.

## Quick start

Execute a Phase 1 scan across pre-computed summary caches:

```bash
python3 scripts/query_cache.py "session memory persistence" --profile wiki
```

## Search Order Protocol

```
Phase 1: RLM Summary Scan    -> O(1), ~1ms       -> Table of Contents
Phase 2: Vector DB Semantic  -> O(log N), 1-5s   -> Back-of-book Index
Phase 3: Scoped Exact Grep   -> O(N), scoped     -> Ctrl+F
```

## Workflow

1. **Phase 1 (RLM Scan)**: Scan summaries using `scripts/query_cache.py` or `grep_search .agent/learning/*_cache/`. Stop if answered.
2. **Phase 2 (Vector Search)**: If ranked similarity across chunks is needed, query `scripts/query.py "query" --profile wiki`. Stop if answered.
3. **Phase 3 (Scoped Grep)**: If exact symbol or function names are required, run targeted `rg "pattern" <scoped-dir>`.
4. **Transparent Citations**: State which search phase resolved the target and provide exact file links.

## Verification

Confirm query tool responsiveness and cache availability:

```bash
python3 scripts/query_cache.py "health" --profile wiki
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for 3-phase search retrieval accuracy.
- [cheapest_models.md](references/cheapest_models.md) — Model tiers and pricing guidance for semantic query engines.
- [RLM_ARCHITECTURE.md](references/RLM_ARCHITECTURE.md) — Architectural overview of the 3-phase lookup design.
