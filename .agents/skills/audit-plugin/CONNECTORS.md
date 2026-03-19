# Connectors

Declares cross-plugin dependencies for the `audit-plugin` skill.

## Required: plugin-validator Agent

| Dependency | Type | Source Plugin | Status |
|------------|------|---------------|--------|
| `plugin-validator` | Sub-agent | `agent-scaffolders` | Required for Step 2 |

### What it does

The `plugin-validator` agent (defined in `agent-scaffolders`) performs comprehensive
10-category plugin validation. `audit-plugin` invokes it in Step 2 as the primary
validation engine.

### Installation

The `agent-scaffolders` plugin must be installed alongside this plugin:
```
npx skills add agent-scaffolders
```

### Fallback (if plugin-validator is unavailable)

If `agent-scaffolders` is not installed, skip Step 2 and rely solely on:
- Step 3 component-specific scripts (validate-agent.sh, validate-hook-schema.sh)
- Step 4 manual checks

The audit will be less comprehensive but still structurally valid. Document the
limitation in the audit report: `plugin-validator unavailable — manual checks only`.
