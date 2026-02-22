---
name: create-mcp-integration
description: Interactive initialization script that scaffolds a new Model Context Protocol (MCP) server integration setup. Use when adding native code tools to an agent's environment.
disable-model-invocation: false
---

# MCP Integration Scaffold Generator

You are tasked with generating the scaffolding required to integrate a new Model Context Protocol (MCP) server.

## Execution Steps:

1. **Gather Requirements:**
   Ask the user for:
   - The name of the MCP server.
   - The command/executable required to run it (e.g. `npx -y @modelcontextprotocol/server-postgres`).
   - Any required environment variables (e.g. database URLs, API Keys).

2. **Scaffold the Integration:**
   Using bash file creation tools:
   - If this is going into a Claude Code environment, update the `claude.json` configuration file to include the new server definition under the `mcpServers` object.
   - Ensure you properly map any provided environment variables in the configuration.
   - Create a basic testing script or prompt (perhaps leveraging `create-skill`) that the agent can use to test the new MCP tools once attached.

3. **Confirmation:**
   Print a success message showing the modified configuration. Instruct the user that they may need to restart their agent environment to pick up the new MCP handles.
