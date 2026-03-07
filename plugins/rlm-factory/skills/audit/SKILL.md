---
description: Audit RLM cache coverage — compare ledger against filesystem (offline)
argument-hint: "[--type legacy|tool]"
---

# Audit RLM Inventory

Compare the ledger against the actual filesystem to report coverage gaps.

## Usage
```bash
# Audit legacy docs coverage
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile project

# Audit tool scripts coverage
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile tools
```

## Output
- Files on disk vs entries in cache
- Coverage percentage
- Missing files (not yet distilled)
- Stale entries (files deleted but still in cache)
