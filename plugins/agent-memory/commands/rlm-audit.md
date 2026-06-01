---
description: Audit RLM cache coverage — compare ledger against filesystem (offline)
argument-hint: "[--profile project|tools]"
---

# Audit RLM Inventory

Compare the ledger against the actual filesystem to report coverage gaps.

## Usage
```bash
# Audit legacy docs coverage
python ./scripts/inventory.py --profile project

# Audit tool scripts coverage
python ./scripts/inventory.py --profile tools
```

## Output
- Files on disk vs entries in cache
- Coverage percentage
- Missing files (not yet distilled)
- Stale entries (files deleted but still in cache)
