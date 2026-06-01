---
description: Remove stale and orphaned entries from the RLM Summary Ledger (offline)
argument-hint: "[--profile project|tools] [--apply]"
---

# /rlm-factory:cleanup

Remove stale entries (deleted files) and orphans (files outside manifest scope) from the ledger.

> **For detailed execution protocol, see agent:** `rlm-cleanup`

## Quick Reference

```bash
# Dry run -- see what would be removed (safe, no changes)
python ./scripts/cleanup_cache.py --profile project

# Apply -- actually remove stale entries
python ./scripts/cleanup_cache.py --profile project --apply

# Both profiles
python ./scripts/cleanup_cache.py --profile tools --apply
```

**Dry run by default.** Nothing is deleted without `--apply`.
