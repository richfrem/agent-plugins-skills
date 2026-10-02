---
name: vector-db-search
plugin: agent-memory
description: "Semantic search skill for retrieving code and documentation from the ChromaDB vector store. Use when you need concept-based search across the repository (Phase 2 of the 3-phase search protocol). V2 includes L4/L5 retrieval constraints."
allowed-tools: Bash, Read
---

# Vector DB Search (`vector-db-search`)

Semantic concept-based search against ChromaDB using Parent-Child chunk retrieval for Phase 2 of the 3-phase search protocol (RLM -> Vector -> Grep).

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Profile Sovereignty**: The `--profile` parameter is mandatory to ensure queries target the correct collection and embedding space.
2. **API Integrity**: Never read SQLite or Parquet backing files directly. Queries must execute through `scripts/query.py`.
3. **Search Protocol Placement**: Use as Phase 2 when RLM summaries return insufficient detail, before falling back to raw regex grep.

## Quick start

Execute a natural-language semantic query against the default profile:

```bash
python3 scripts/query.py "how does session memory persist" --profile wiki --limit 5
```

## Workflow

1. **Identify Target Profile**: Verify configured profile collections (`wiki`, `codebase`) in `.agent/learning/vector_profiles.json`.
2. **Execute Query**: Run `scripts/query.py` with the natural language query, specifying `--profile` and result limit.
3. **Ingest Parent Chunks**: Extract returned high-context parent chunks (up to 2,000 chars) for downstream reasoning.
4. **Transparent Reporting**: If no results match, report the exact profile and query string evaluated before falling back to grep.

## Verification

Verify ChromaDB index responsiveness and consistency:

```bash
python3 scripts/vector_consistency_check.py --profile wiki
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Retrieval accuracy criteria and ranking constraints.
- [cheapest_models.md](references/cheapest_models.md) — Embedding model tiers and pricing guidance.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when vector collections are unavailable or return zero hits.
