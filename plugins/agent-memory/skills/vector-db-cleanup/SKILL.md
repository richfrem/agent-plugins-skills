---
name: vector-db-cleanup
plugin: agent-memory
description: Removes stale and orphaned chunks from the ChromaDB vector store when source files have been deleted or renamed.
allowed-tools: Bash, Read, Write
---

# Vector DB Cleanup (`vector-db-cleanup`)

Removes stale and orphaned chunks from the ChromaDB vector store when source files no longer exist on disk.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Write Operation**: Always specify the target `--profile` to prune the intended semantic space.
2. **API Integrity**: NEVER manipulate SQLite files directly; always execute `scripts/cleanup.py`.
3. **Transparency**: Report which profile was pruned and the total number of chunks removed.

## Quick start

Execute in-process cleanup for the default wiki profile:

```bash
python3 scripts/cleanup.py --profile wiki
```

## Workflow

1. **Identify Profile**: Verify active profiles in `.agent/learning/vector_profiles.json` (default: `wiki`).
2. **Execute Cleanup**: Run `scripts/cleanup.py` with the mandatory `--profile` flag.
3. **Report Output**: State the target profile and total chunks removed.

## Verification

Verify store integrity and index consistency after cleanup:

```bash
python3 scripts/vector_consistency_check.py --profile wiki --topic .agent/learning/
```
