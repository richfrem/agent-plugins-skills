---
description: Add APM governance to an existing plugin or convert it to an APM-native package using overlay-first migration.
argument-hint: "[source-plugin-path] [--mode overlay|hybrid|full] [--output ./converted] [--governance experimental|team|enterprise]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# convert-plugin-to-apm

Analyze an existing Claude plugin and choose the least disruptive APM integration path. This command prioritizes preserving the original plugin primitives.

## Usage

```bash
/convert-plugin-to-apm ./plugins/my-plugin --mode overlay --governance enterprise
```

## Migration Modes

- **overlay (Default)**: Keeps existing plugin structure. Adds `apm.yml` and governance docs. Primitives stay in `skills/`, `agents/`, etc.
- **hybrid**: Keeps plugin structure but adds `.apm/` for new governance assets or shared metadata.
- **full**: Creates a new output directory and migrates all primitives into the `.apm/` source tree. Original plugin remains untouched.

## Workflow

1. **Inspection**: Analyzes the source plugin's `plugin.json` and directory layout.
2. **Strategy**: Proposes a migration plan based on the selected mode.
3. **Execution**: Invokes `scripts/migrate_to_apm.py` to apply the overlay or conversion.
4. **Validation**: Runs `scripts/validate_apm_package.py` to ensure the resulting package is valid.
5. **Report**: Outputs a migration report with warnings (e.g., dual-manifest risks).

> [!TIP]
> Use **overlay mode** whenever possible to maintain compatibility with existing plugin tools while adding APM governance.
