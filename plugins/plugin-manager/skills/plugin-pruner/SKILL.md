---
name: plugin-pruner
description: Selectively prunes unneeded skills, rules, and sub-agents from installed plugins while preserving dependencies and protected infrastructure.
allowed-tools: Bash, Read, Write
---

# Component Retention Pruner

Selectively prune unneeded installed skills, rules, and sub-agents from your agent environments.

## Quick Start

### 1. Interactive Review & Pruning (Recommended)
Review installed components plugin-by-plugin and toggle retention interactively:
```bash
python3 scripts/prune_installed_skills.py --interactive
```

### 2. Preview Pruning Plan (Dry Run)
Inspect what would be removed based on `plugin-retention.json` without modifying disk:
```bash
python3 scripts/prune_installed_skills.py --dry-run
```

### 3. Headless Enforcement
Execute pruning of components flagged as unneeded (`false` in manifest):
```bash
python3 scripts/prune_installed_skills.py --execute --confirm-token PRUNE-INSTALLED-SKILLS
```

## Progressive Disclosure & References

- **Architecture & Lifecycle**: See `references/retention-workflow.md` for the full lifecycle diagram and state engine rules.
- **CLI Options & TUI Controls**: See `references/pruner-cli-guide.md` for keyboard shortcuts and automation flags.
- **Verification Standards**: See `references/acceptance-criteria.md` for quality criteria and invariants.
- **Fallback Procedures**: See `references/fallback-tree.md` for fallback and recovery trees.
