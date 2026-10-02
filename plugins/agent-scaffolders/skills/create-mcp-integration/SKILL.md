---
name: create-mcp-integration
plugin: agent-scaffolders
description: >
  Adds an MCP server integration configuration to an existing plugin. NOT for scaffolding a brand-new plugin (use `create-plugin`) and NOT for Azure hosted agents (use `create-azure-agent`).
argument-hint: "[mcp-server-name or service]"
allowed-tools: Bash, Read, Write
---

# Create MCP Integration (create-mcp-integration)

Configures Model Context Protocol (MCP) server integrations within a plugin or workspace `.mcp.json`.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Integration Scope**: Configuration of MCP servers only. For scaffolding new plugins, use `create-plugin`. For hosted cloud agents, use `create-azure-agent`.
- **Encrypted Transports**: Remote server endpoints must use `https://` or `wss://`; unencrypted plain HTTP/WS transports are forbidden.
- **Modern Transport Priority**: Prefer `streamable-http` or `stdio` transports over deprecated SSE implementations.
- **Credential Hygiene**: Store secrets strictly in environment variables; never embed raw API tokens or credentials inside `.mcp.json`.

## Quick start

```bash
python3 plugins/agent-scaffolders/scripts/scaffold.py \
  --type mcp \
  --name postgres-mcp \
  --path plugins/<plugin>
```

## Workflow

1. **Phase 1: Transport & Security Discovery**: Establish server archetype (`stdio`, `streamable-http`, `sse`), endpoint URL or binary command, and authentication mechanism.
2. **Phase 2: Tool Surface Definition**: Select target tool subsets, resource templates, and prompt templates to expose to the agent environment.
3. **Phase 3: Configuration Scaffolding**: Generate the `.mcp.json` server definition block with required environment variable placeholders and arguments.
4. **Phase 4: Schema & Connection Audit**: Validate JSON formatting and test connectivity using the environment MCP inspector.

## Verification

```bash
# Validate JSON formatting
python3 -c "import json; json.load(open('.mcp.json'))"

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/agent-scaffolders/skills/create-mcp-integration --mode source
```

## References
- [fallback-tree.md](references/fallback-tree.md) - Fallback tree for scaffolding failures.
- [references/server-types.md](references/server-types.md) - MCP transport architecture standards.
- [references/authentication.md](references/authentication.md) - Safe credential and authentication patterns.
- [references/tool-usage.md](references/tool-usage.md) - Tool filtering and prompt exposure.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Quality checklist for MCP integrations.
