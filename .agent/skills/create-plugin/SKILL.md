---
name: create-plugin
description: Scaffold a complete Claude Code plugin from scratch
argument-hint: "[plugin-name]"
allowed-tools: Bash, Read, Write
---

Follow the `create-plugin` skill workflow to scaffold a new Claude Code plugin.

## Inputs

- `$ARGUMENTS` — optional plugin name in kebab-case. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a plugin name, use it to seed Phase 1
2. Follow the create-plugin phased workflow: discover purpose and plugin type,
   plan component table (skills / commands / agents / hooks / MCP), ask clarifying
   questions per component, scaffold directory structure and `plugin.json`, implement
   each component using the appropriate sub-skill, validate, test, and document
3. Report the created plugin directory and verification checklist results

## Output

Plugin directory with `.claude-plugin/plugin.json`, component directories, `README.md`,
and a `.claude/settings.json` stub for reliable local discovery.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with Phase 1 discovery — do not pre-fill plugin name
- If similar plugin already exists: reference it as a starting point
- If MCP integrations are needed: invoke `create-mcp-integration` for each one
- After scaffolding: run `/agent-scaffolders:audit-plugin` to validate structure
