# Acceptance Criteria: Plugin Manager Lifecycle Tools

## 1. Plugin Installer (`plugin_add.py`)
- **Deterministic Deployment**: Successfully extracts and deploys plugin components (skills, rules, commands, workflows, hooks, MCP) to the central store (`.agents/`).
- **Multi-Environment Symlinking**: Automatically bridges components into client environment folders (`.claude/`, `.azure/`, etc.) using valid file-level symlinks.
- **Source Ledger Integrity**: Updates or registers entries in `plugin-sources.json` without duplicate keys or syntax errors.
- **Non-Interactive Execution**: When passed `-y` or `--all -y`, executes without blocking or prompting for stdin.
- **Skill Customization**: `--select-skills` correctly filters which skills are installed and registered.
- **Conflict & Preservation**: Never overwrites existing user modifications to rules or configs without confirmation or flags.

## 2. Component Retention Pruner (`prune_installed_skills.py`)
- **Safety First**: Dry-run by default unless explicitly invoked with `--execute` and `--confirm-token PRUNE-INSTALLED-SKILLS`.
- **Dependency Awareness**: Validates dependencies across installed skills, subagents, and rules before deletion; surfaces warnings if retained components depend on pruned targets.
- **Protected Core**: Preserves core infrastructure components (e.g. `plugin-manager`, `agent-orchestration`, core bootstrap rules) from accidental pruning.
- **Manifest Synchronization**: Accurately reflects retained states in `plugin-retention.json` and prunes untracked files from `.agents/skills/`.
- **Interactive TUI**: Supports keyboard-driven multiselect TUI via ANSI codes (`--interactive`) with space toggling and real-time dependency warnings.

## 3. Inventory Syncer (`sync_with_inventory.py`)
- **Single Command Reconciliation**: Idempotently reconciles installed `.agents/` components against sources declared in `plugin-sources.json`.
- **Automated Retention Enforcement**: Seamlessly triggers pruning if `plugin-retention.json` defines component exclusions.
- **Headless First**: Fully automated for CI/CD or agent-driven self-healing without requiring GUI interactions.

## 4. Plugin Remover (`plugin_remove.py`)
- **Complete Teardown**: Removes target plugin files from `.agents/` and breaks/removes all associated client symlinks (`.claude/`, etc.).
- **Clean Ledger Pruning**: Cleans up deleted plugin entries from `plugin-sources.json` and removes unreferenced skill locks from `skills-lock.json`.
- **Non-Interactive Batching**: Supports headless removal via `--plugins <name1> <name2> -y` or `--all -y`.
- **Clean State Exit**: When all plugins are removed, `.agents/skills/` is left clean without orphaned dangling files.