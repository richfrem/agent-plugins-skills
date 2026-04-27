---
name: create-mcp-integration
plugin: agent-scaffolders
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
