---
name: vector-db-search
description: "Semantic search skill for retrieving code and documentation from the ChromaDB vector store. Use when you need concept-based search across the repository (Phase 2 of the 3-phase search protocol). V2 includes L4/L5 retrieval constraints."
allowed-tools: Bash, Read
---

## Dependencies

This skill requires the `chromadb` and `langchain` packages defined in the plugin root.

---

# Vector DB Search

Semantic (meaning-based) search against the ChromaDB vector store using a high-precision Parent-Child architecture. Use for Phase 2 of the 3-phase search protocol (RLM -> Vector -> Grep).

## Scripts

| Script | Role |
|:-------|:-----|
| `scripts/query.py` | Semantic search CLI -- recovers context-rich parent chunks. |
| `scripts/operations.py` | Core domain logic for retrieval. |
| `scripts/vector_config.py` | Unified profile-based configuration loader. |

## Execution Mode

This skill defaults to **In-Process mode** for zero-latency direct disk access. No background server is required. This ensures maximum stability in isolated project environments.

## When to Use

- Phase 1 (RLM Summary Ledger) returned no match or insufficient detail.
- User asks "how does X work?" / "find code that does Y".
- You need specific high-context snippets (Parent chunks) for reasoning.

## Execution Protocol

### 1. Identify Search Profile
Verify available profiles in `.agent/learning/vector_profiles.json`. The default profile is usually `wiki`.

### 2. Run Query
Note: The `--profile` flag is mandatory to ensure the correct model and collection are loaded.

```bash
python3 ./scripts/query.py "your natural language question" --profile wiki --limit 5
```

Results include ranked parent chunks (2,000 chars) that provide broad context to the LLM for reasoning.

## Rules

- **Profile Sovereignty**: Always pass `--profile` to ensure the correct semantic space is searched.
- **API Integrity**: NEVER attempt to read the database SQLite or parquet files directly. Always use `query.py`.
- **Transparency**: When search returns empty results, state which profile and scope were searched.
