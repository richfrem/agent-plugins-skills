---
description: Remove stale chunks from deleted or renamed files in the vector database
---

# /vector-db:cleanup

Remove orphaned chunks from the vector store for files that no longer exist on disk.

> **For detailed execution protocol, see agent:** `vector-db-cleanup`

## Quick Reference

```bash
# Dry run -- see what would be removed
python3 ./scripts/cleanup.py --profile knowledge --dry-run

# Apply
python3 ./scripts/cleanup.py --profile knowledge --apply
```

**Dry run by default.** Nothing is deleted without `--apply`.
Prevents deleted files from returning false positives in semantic search.
