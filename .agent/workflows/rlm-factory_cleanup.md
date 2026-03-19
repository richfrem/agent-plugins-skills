---
description: Remove stale and orphaned entries from the RLM Summary Ledger (offline)
argument-hint: "[--profile project|tools] [--apply]"
---

# /rlm-factory:cleanup

Remove stale entries (deleted files) and orphans (files outside manifest scope) from the ledger.

> **For detailed execution protocol, see agent:** [`rlm-cleanup`](../agents/rlm-cleanup.md)

## Quick Reference

```bash
# Dry run -- see what would be removed (safe, no changes)
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile project

# Apply -- actually remove stale entries
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile project --apply

# Both profiles
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile tools --apply
```

**Dry run by default.** Nothing is deleted without `--apply`.
