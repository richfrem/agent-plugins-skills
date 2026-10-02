---
name: update-cli-models
plugin: cli-agents
description: Updates CLI model catalogs, capability tiers and cheapest-model references from official sources. Use when asked to refresh model IDs, availability or prices for Copilot, Agy, Claude, Codex or local models.
argument-hint: "[cli-name or 'all']"
allowed-tools: Bash, Read, Write
---

# Update CLI Models

Refresh the requested catalogs and verify their consumers.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Catalog contract and sources](references/model-catalog-maintenance.md)

## Constraints

Run a refresh only when requested or needed to resolve a stale catalog.
Preserve schema version 2, existing model identities and historical entries;
mark verified withdrawals unavailable instead of deleting entries.
Source catalogs have one canonical owner; installed copies are deployment artifacts.
Do not invent prices, limits, aliases or availability; record unknowns and evidence.

## Quick start

Identify the requested providers and the caller-supplied source repository.
Read [catalog maintenance](references/model-catalog-maintenance.md) before editing.
Bundled catalogs are readable references, not authorization to dispatch any model.

## Workflow

1. Fetch official provider data and verify runtime IDs for the requested CLI.
2. Diff canonical catalogs in the selected source repository; update fields and tiers.
3. Recalculate cheapest picks only when comparable availability/pricing is verified.
4. From this skill root, preview synchronization to the explicit repository:

```bash
python3 scripts/sync_cheapest_models.py --repository <repository> --dry-run
```

5. Inspect the proposed destinations; rerun without `--dry-run` for authorized updates.
6. Delegate managed resource-link changes to symlink-manager; refresh installed copies through plugin-syncer.

## Verification

Validate catalogs using the bundled [model catalog helper](scripts/model_catalog.py).
Check [profile compatibility](references/capability-profile-contract.md), [default picks](references/cheapest_models.md), tier references,
JSON validity, unknown fields and synchronized output. Report provider-specific changes,
source evidence, unchanged cheapest picks, sync counts and any unavailable verification.
A catalog refresh neither authorizes a model call nor starts a review.
