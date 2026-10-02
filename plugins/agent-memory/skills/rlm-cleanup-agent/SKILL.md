---
name: rlm-cleanup-agent
plugin: agent-memory
description: Removes stale and orphaned entries from the RLM Summary Ledger when files are deleted, renamed, or moved.
allowed-tools: Bash, Read, Write
---

# RLM Cleanup Agent (`rlm-cleanup-agent`)

Removes stale and orphaned entries from the RLM Summary Ledger to keep it in sync with the filesystem.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Write Operation**: Always confirm scope with the user before applying deletions.
2. **Dry-Run First**: Never apply cache prunes without showing what will be removed first.
3. **Scripted Integrity**: Never edit cache markdown files directly; always execute `scripts/cleanup_cache.py`.

## Quick start

Perform a dry-run check for stale or orphaned ledger entries:

```bash
python3 scripts/cleanup_cache.py --profile project --dry-run
```

## Workflow

1. **Confirm Profiles**: Default to all configured profiles (`project`, `tools`), or query the user if scope is ambiguous.
2. **Execute Dry-Run**: Run `cleanup_cache.py` with `--dry-run` to identify orphaned entries.
3. **User Confirmation**: Present the audit findings for explicit authorization.
4. **Apply Pruning**: Execute `cleanup_cache.py --apply` to purge verified orphans.
5. **Report Summary**: State the total number of removed entries per profile.

## Verification

Verify cache coverage and ledger consistency after cleanup:

```bash
python3 scripts/inventory.py --profile project
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for RLM cache pruning and hygiene.
- [cheapest_models.md](references/cheapest_models.md) — Model selection guidance for regeneration passes.
- [RLM_ARCHITECTURE.md](references/RLM_ARCHITECTURE.md) — Architectural overview of the RLM ledger filesystem.
