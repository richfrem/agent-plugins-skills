---
description: "Remove stale chunks from deleted or renamed files in the vector database"
---

# /vector-db:cleanup

Maintain the vector database by removing orphaned chunks (from deleted/renamed files).

## Usage

### Dry Run (See what would be removed)
```bash
python3 plugins/vector-db/scripts/cleanup.py --dry-run
```

### Apply Cleanup
```bash
python3 plugins/vector-db/scripts/cleanup.py --apply
```

## Steps
1. Run `--dry-run` first to see what stale chunks exist.
2. Review the list of orphaned files.
3. Run `--apply` to remove them.
4. Verify with `python3 plugins/vector-db/scripts/query.py --stats`.

## Notes
- Prevents hallucinations from deleted code appearing in search results.
- Safe to run frequently — only removes chunks whose source files no longer exist.
