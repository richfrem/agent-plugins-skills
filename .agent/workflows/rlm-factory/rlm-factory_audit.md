---
description: Audit RLM cache coverage — compare ledger against filesystem (offline)
argument-hint: "[--type legacy|tool]"
---

# Audit RLM Inventory

Compare the ledger against the actual filesystem to report coverage gaps.

## Usage
```bash
# Audit legacy docs coverage
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/inventory.py

# Audit tool scripts coverage
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/inventory.py --type tool
```

## Output
- Files on disk vs entries in cache
- Coverage percentage
- Missing files (not yet distilled)
- Stale entries (files deleted but still in cache)
