---
description: Remove stale chunks from deleted or renamed files in the vector database
---

# /vector-db:cleanup

Remove orphaned chunks from the vector store for files that no longer exist on disk.

> **For detailed execution protocol, see agent:** `vector-db-cleanup`

## Quick Reference

```bash
# Dry run -- see what would be removed
python ./scripts/cleanup.py --profile wiki--dry-run

# Apply
python ./scripts/cleanup.py --profile wiki--apply
```

**Dry run by default.** Nothing is deleted without `--apply`.
Prevents deleted files from returning false positives in semantic search.
