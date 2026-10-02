---
name: convert-plugin-to-apm
description: >-
  Activate when the user wants to add APM governance, lockfile/audit readiness, 
  or multi-runtime package management to an existing Claude/Copilot/agent plugin, 
  or explicitly convert a plugin into an APM-native package.
allowed-tools: Bash, Read, Write, Glob
---

# Convert Plugin to APM (`convert-plugin-to-apm`)

Applies overlay-first APM governance, lockfile reproducibility, and multi-runtime packaging to existing agent plugins without disruptive refactors.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Overlay-First Directive**: Never force `.apm/` as the source of truth or move existing files unless explicitly requested by the user.
2. **Preserve Original Layout**: Default to Overlay Mode, adding `apm.yml` and `docs/governance.md` at root without disrupting active workflows.
3. **Lossless Mapping**: When Full Conversion is requested, keep the original plugin untouched and map primitives accurately.

## Quick start

Analyze a plugin directory to determine the appropriate conversion mode:

```bash
python3 scripts/validate_apm_package.py --analyze <path-to-plugin>
```

## Workflow

1. **Select Migration Mode**:
   - **Overlay Mode (Default)**: Add `apm.yml` and `docs/governance.md` to root; zero file relocations.
   - **Hybrid Mode**: Add `.apm/` for new governance assets while keeping existing primitives in place.
   - **Full Conversion**: Migrate primitives into `.apm/` structure (`commands/*` -> `.apm/prompts/*`).
2. **Generate Manifest**: Scaffold compliant `apm.yml` capturing plugin metadata and dependencies.
3. **Compile Lockfile**: Run `apm install --dry-run` to generate initial lockfile state.

## Verification

Audit the converted plugin package for schema and lockfile validity:

```bash
python3 scripts/validate_apm_package.py --path <path-to-plugin>
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for overlay, hybrid, and full conversion modes.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for mapping errors and validation rejections.
