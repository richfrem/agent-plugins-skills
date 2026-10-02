---
name: manage-marketplace
plugin: agent-scaffolders
description: >
  This skill should be used when the user wants to "create a marketplace", 
  "setup a marketplace catalog", "scaffold marketplace.json", "initialize 
  a plugin registry", or "configure a Gemini CLI extension".
allowed-tools: Bash, Read, Write
---

# Marketplace Manager (`manage-marketplace`)

Guidelines for authoring, validating, and distributing plugin marketplace catalogs.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Distribution Commands](#distribution-commands)
- [References](#references)

## Constraints

- **Strict invariant**: Set `"strict": true` when plugin has its own `.claude-plugin/plugin.json`.
- **Kebab-case naming**: Catalog name must be kebab-case; reserved names: `claude-code-marketplace`, `anthropic-plugins`.
- **Clean manifests**: Never declare auto-discovered `skills`, `agents`, or `hooks` arrays in `plugin.json`.
- **Author format**: Author must be an object `{"name": "...", "email": "..."}`.

## Quick start

```bash
# Audit marketplace source paths from repo root
python3 scripts/audit_marketplace_sources.py .
```

## Workflow

1. **Scaffold Catalog**: Create `.claude-plugin/marketplace.json` at repository root with name and owner object.
2. **Register Plugins**: Add entries using relative paths (`./plugins/<name>`) with `"strict": true`.
3. **Verify Schemas**: Audit source path references and manifest conformance.
4. **Distribute**: Publish catalog or configure team distribution channels.

## Verification

```bash
# Validate marketplace catalog schema
python3 scripts/audit_marketplace_sources.py .
# Verify JSON syntax
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"
```

## Distribution Commands

- **Add Marketplace**: `/plugin marketplace add owner/repo`
- **Install Plugin**: `/plugin install <plugin>@<marketplace> --scope [user|project|local]`
- **Update Catalog**: `/plugin marketplace update <name>`
- **Reload Plugins**: `/reload-plugins`

## References

- [marketplace.md](references/marketplace.md) — Comprehensive marketplace catalog guide.
- [marketplace-schema.md](references/marketplace-schema.md) — Structure definition and field types.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for marketplace management.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for catalog issues.