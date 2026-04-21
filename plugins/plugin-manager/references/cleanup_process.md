# Plugin Synchronization & Cleanup Process

This document explains the logic used by `../scripts/sync_with_inventory.py` to manage plugin lifecycles in consuming repositories. It is invoked via the **[plugin-syncer](../skills/plugin-syncer/SKILL.md)** skill (Sync operation).

## Key Concepts

### 1. `plugin-sources.json` (The Source of Truth)
Unlike previous iterations that dynamically scanned local target directories to infer what was installed, the system now exclusively relies on `plugin-sources.json` stored at the root of the user's workspace. If a plugin is not registered inside a mapped `"source"}` ledger key, it effectively does not exist.

### 2. Idempotent Redeployment
When `/plugin-manager:sync` is triggered, the sync script loops over the `sources` manifest. It invokes `plugin_add.py <source> --plugins <list> --yes` natively via subprocess. Because the installer engine guarantees perfect overwrite idempotency, the sync script requires absolutely no difference-checking logic.

## The Cleanup Rules

The script sweeps for orphaned artifacts automatically:
1. It loads all valid plugins currently recorded in `plugin-sources.json`.
2. It systematically recursively walks `.agents/skills`, `.agents/workflows` and `.agents/agents`.
3. If it finds a file or directory that maps to a plugin prefix not listed in the canonical JSON registry, it violently unlinks and purges it to prevent ghostly context bleed.

This single unified operation replaces legacy python scripts like `clean_orphans.py` entirely.
