---
concept: vdb-cleanup-agent
source: plugin-code
source_file: vector-db/skills/vector-db-cleanup/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.426794+00:00
cluster: vector
content_hash: af5c34d95aa5994c
---

# VDB Cleanup Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: vector-db-cleanup
description: |
  Removes stale and orphaned chunks from the ChromaDB vector store for files that have been deleted or renamed.
  Use after files are removed or moved to keep the vector index in sync with the filesystem.

  <example>
  user: "Clean up the vector store after I deleted some files"
  assistant: "I'll use vector-db-cleanup to remove orphaned chunks."
  </example>
  <example>
  user: "The vector database has chunks for files that no longer exist"
  assistant: "I'll run vector-db-cleanup to prune them."
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires the `chromadb` and `langchain` packages defined in the plugin root.

---

# VDB Cleanup Agent

## Role

You remove stale and orphaned chunks from the ChromaDB vector store. A chunk is stale when its source file no longer exists on disk. Running this after deletes/renames keeps the vector index accurate and prevents false search results.

**This is a write (delete) operation.**

## When to Run

- After deleting or renaming files that were previously ingested.
- After a major refactor that moved directories.
- When `query.py` returns results pointing to non-existent files.
- Periodically as housekeeping to maintain index health.

## Execution Mode

This skill defaults to **In-Process mode** for zero-latency direct disk access. No background server is required.

## Execution Protocol

### 1. Identify Search Profile
Verify available profiles in `.agent/learning/vector_profiles.json`. The default profile is usually `wiki`.

### 2. Run Cleanup
Note: The `--profile` flag is mandatory to ensure the correct collection and disk paths are loaded.

```bash
python ./scripts/cleanup.py --profile wiki
```

### 3. Verify Store Integrity (Optional)
Run the consistency check to verify that remaining facts are still supported.
```bash
python ./scripts/vector_consistency_check.py --profile wiki --topic .agent/learning/
```

## Rules

- **Profile Sovereignty**: Always pass `--profile` to ensure the correct semantic space is pruned.
- **API Integrity**: NEVER attempt to delete chunks from the database SQLite files directly. Always use `cleanup.py`.
- **Transparency**: State which profile was cleaned and how many chunks were removed.


## See Also

- [[rlm-cleanup-agent]]
- [[rlm-cleanup-agent]]
- [[rlm-cleanup-agent]]
- [[vdb-ingest-agent]]
- [[rlm-cleanup-agent]]
- [[vdb-ingest-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-cleanup/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.426794+00:00
