---
concept: agent-scaffolders-create-mcp-integration
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-mcp-integration.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.318403+00:00
cluster: server
content_hash: dbd410ee47c268b6
---

# Agent Scaffolders Create Mcp Integration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-mcp-integration
description: Add an MCP server integration to a plugin
argument-hint: "[mcp-server-name or service]"
allowed-tools: Bash, Read, Write
---

Follow the `create-mcp-integration` skill workflow to scaffold a new MCP server
integration for a Claude Code plugin.

## Inputs

- `$ARGUMENTS` — optional MCP server name or service description (e.g. `postgres`,
  `github`, `slack`). Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` names a server or service, use it to seed Phase 1 discovery
2. Follow the create-mcp-integration phased workflow: confirm server type
   (stdio / SSE / streamable-http), authentication method, which tools to expose,
   configuration fields, then generate the `.mcp.json` entry and any supporting config
3. Report the generated configuration and setup instructions

## Output

`.mcp.json` server entry with full configuration (command/url, env vars, allowed tools)
and instructions for obtaining credentials and verifying the connection with `/mcp`.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with server type selection
- If the service requires OAuth: document the auth flow steps explicitly
- Prefer `streamable-http` transport for new hosted integrations over SSE
- All MCP server URLs must use HTTPS/WSS — never HTTP/WS


## See Also

- [[acceptance-criteria-create-mcp-integration]]
- [[procedural-fallback-tree-create-mcp-integration]]
- [[acceptance-criteria-create-mcp-integration]]
- [[procedural-fallback-tree-create-mcp-integration]]
- [[acceptance-criteria-create-mcp-integration]]
- [[procedural-fallback-tree-create-mcp-integration]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-mcp-integration.md`
- **Indexed:** 2026-04-17T06:42:10.318403+00:00
