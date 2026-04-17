---
concept: agent-scaffolders-create-plugin
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-plugin.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.318608+00:00
cluster: name
content_hash: fb2b5137485e7d60
---

# Agent Scaffolders Create Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[agent-scaffolders-plugin]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-azure-agent]]
- [[agent-scaffolders-create-docker-skill]]
- [[agent-scaffolders-create-github-action]]
- [[agent-scaffolders-create-hook]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-plugin.md`
- **Indexed:** 2026-04-17T06:42:10.318608+00:00
