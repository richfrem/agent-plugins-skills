---
name: create-apm-package
description: >-
  Activate when the user wants to create a new APM-native package from scratch 
  for reusable agent skills, agents, commands, hooks, MCP configuration, 
  prompts, or governance-managed agent assets. Do not use this for existing 
  plugin migration; use convert-plugin-to-apm instead.
allowed-tools: Bash, Read, Write
---

# Create APM Package (`create-apm-package`)

Scaffolds a greenfield APM-native package with source primitives isolated under `.apm/` and standard governance documentation.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Source in .apm/**: Greenfield primitives (skills, agents, prompts, hooks, mcp) must be authored inside `.apm/`.
2. **Kebab-Case Naming**: Package names must be lowercase alphanumeric with hyphens.
3. **No Overwrites**: Never overwrite existing directories without explicit user confirmation.
4. **Mandatory Governance Docs**: Every generated package must include `docs/governance.md`.

## Quick start

Scaffold a new APM package structure:

```bash
python3 scripts/scaffold_apm.py --name <package-name>
```

## Workflow

1. **Pre-Check Qualification**: Verify this is a new package from scratch (if migrating an existing plugin, redirect to `convert-plugin-to-apm`).
2. **Scaffold Package**: Run `scaffold_apm.py` to create the standard folder hierarchy (`apm.yml`, `.apm/`, `docs/`).
3. **Author Governance**: Populate `docs/governance.md`, `README.md`, and license attribution.
4. **Compile Initial Lockfile**: Run `apm install --dry-run` to generate initial dependency lockfile.

## Verification

Validate the scaffolded package structure and manifest compliance:

```bash
python3 scripts/validate_apm_package.py --path ./<package-name>
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and structural requirements for APM packages.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution when scaffolding or validation fails.
