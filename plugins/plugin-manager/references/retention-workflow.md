# Component Retention Workflow

This document outlines the lifecycle of component retention across installation, post-sync enforcement, and selective pruning.

```mermaid
flowchart TD
    A["Install Plugin: plugin_add.py"] --> B["Seed plugin-retention.json"]
    B --> C["Central Store .agents/ & IDE symlinks"]
    D["Inventory Sync: sync_with_inventory.py"] --> E["Update Registries"]
    E --> F{"plugin-retention.json exists?"}
    F -- Yes --> G["Enforce Retention: prune_installed_skills.py"]
    F -- No --> C
    H["User Prune: prune_installed_skills.py --interactive"] --> I["Toggle Skills/Rules/Agents"]
    I --> J["Dependency Check & Warning"]
    J --> K["Update Retention Manifest"]
    K --> L["Prune Artifacts with CONFIRM_TOKEN"]
```

## Retention Stages

1. **Seeding (Day 1)**:
   - `plugin_add.py` or `plugin_installer.py` records newly installed components in `plugin-retention.json`.
   - Granular toggles during install allow selecting a subset of skills.
2. **Maintenance (Day 2+)**:
   - `prune_installed_skills.py --interactive` allows reviewing installed components per plugin.
   - Space toggles components; `a` toggles all; `/` searches; `q` exits.
   - Inline dependency advisory alerts if a retained skill references an unselected skill or rule.
3. **Automated Enforcement (Post-Sync)**:
   - `sync_with_inventory.py` automatically applies pruning based on `plugin-retention.json` unless `--no-prune` is passed.
