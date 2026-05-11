---
name: convert-plugin-to-apm
description: >-
  Activate when the user wants to add APM governance, lockfile/audit readiness, 
  or multi-runtime package management to an existing Claude/Copilot/agent plugin, 
  or explicitly convert a plugin into an APM-native package.
allowed-tools: Bash, Read, Write, Glob
---

# convert-plugin-to-apm Skill 🔄

## Overview
This skill implements the **Overlay-First** migration strategy. It allows existing plugins to gain APM governance without the "repackaging tax" of moving files, unless explicitly requested.

## Migration Modes

### 1. Overlay Mode (Default)
**Use when**: The plugin is active and its current layout is preferred.
- **Action**: Add `apm.yml` and `docs/governance.md` to the root.
- **Benefit**: Zero disruption to existing `npx skills` or Claude Code workflows.

### 2. Hybrid Mode
**Use when**: You want to keep the plugin layout but start adding new APM-native assets.
- **Action**: Add `.apm/` for new governance assets; keep existing primitives in place.

### 3. Full Conversion
**Use when**: You want a clean, APM-native package structure.
- **Action**: Create a new directory and migrate all primitives into `.apm/`.
- **Note**: Always preserve the original plugin untouched.

## 🎯 Primary Directive
**Do not force .apm/ as the new source of truth unless explicitly requested.**

## Validation & Audit
After conversion, run:
```bash
python scripts/validate_apm_package.py --path <target-path>
```

## Mapping Rules (Full Mode)
- `.claude-plugin/plugin.json` -> Metadata for `apm.yml`
- `skills/*` -> `.apm/skills/*`
- `agents/*` -> `.apm/agents/*`
- `commands/*` -> `.apm/prompts/*` (APM standard)
- `hooks/hooks.json` -> `.apm/hooks/hooks.json`
