---
description: Clean stale and orphan entries from the RLM cache (offline)
argument-hint: "[--type legacy|tool] [--apply] [--prune-orphans] [--prune-failed]"
---

# Clean RLM Cache

Remove stale entries (deleted files) and orphans (files outside manifest scope).

## Usage
```bash
# Dry run — see what would be removed
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile project

# Actually remove stale entries
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile project --cleanup

# Also prune orphans (entries not matching manifest scope)
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile tools --cleanup

# Remove failed distillation entries
python3 plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile project --cleanup
```

## Safety
- **Dry run by default** — nothing is deleted without `--apply`
- Verbose mode with `--v`
