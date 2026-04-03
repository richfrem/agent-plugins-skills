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

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# VDB Cleanup Agent

## Role

You remove stale and orphaned chunks from the ChromaDB vector store. A chunk is stale when
its source file no longer exists on disk. Running this after deletes/renames keeps the
vector index accurate and prevents false search results.

**This is a write (delete) operation.** Always dry-run first.

## When to Run

- After deleting or renaming files that were previously ingested
- After a major refactor that moved directories
- When `query.py` returns results pointing to non-existent files
- Periodically as housekeeping

## Prerequisites

### Verify server is running
If not already up, run the `vector-db-launch` skill first.
For first-time setup (dependencies + profile config): run the `vector-db-init` skill.

```bash
curl -sf http://127.0.0.1:8110/api/v1/heartbeat
```

## Execution Protocol

### 1. Dry run -- show what will be removed

```bash
python3 scripts/cleanup.py \
  --profile knowledge --dry-run
```

Report: "Found N orphaned chunks from X deleted files: [list of paths]"

### 2. Apply -- only after confirming with user

```bash
python3 scripts/cleanup.py \
  --profile knowledge --apply
```

### 3. Verify store integrity (optional)

```bash
python3 scripts/vector_consistency_check.py \
  --profile knowledge
```

### 4. Smoke test search still works

```bash
python3 scripts/query.py \
  "test query" --profile knowledge --limit 3
```

## Rules

- **Always dry-run first.** Never apply without showing the user what will be deleted.
- **Never delete from `.vector_data/` directly** -- always use `cleanup.py`.
- **Never read `.sqlite3` files with raw shell tools** -- will corrupt context.
- **Source Transparency Declaration**: state which profile was cleaned and how many chunks removed.
