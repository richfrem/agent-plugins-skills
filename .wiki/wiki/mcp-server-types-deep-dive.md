---
concept: mcp-server-types-deep-dive
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-mcp-integration/references/server-types.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.921680+00:00
cluster: servers
content_hash: 7b06c7ea92e25521
---

# MCP Server Types: Deep Dive

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# MCP Server Types: Deep Dive

Complete reference for all MCP server types supported in Claude Code plugins.

## stdio (Standard Input/Output)

### Overview

Execute local MCP servers as child processes with communication via stdin/stdout. Best choice for local tools, custom servers, and NPM packages.

### Configuration

**Basic:**
```json
{
  "my-server": {
    "command": "npx",
    "args": ["-y", "my-mcp-server"]
  }
}
```

**With environment:**
```json
{
  "my-server": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/custom-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "API_KEY": "${MY_API_KEY}",
      "LOG_LEVEL": "debug",
      "DATABASE_URL": "${DB_URL}"
    }
  }
}
```

### Process Lifecycle

1. **Startup**: Claude Code spawns process with `command` and `args`
2. **Communication**: JSON-RPC messages via stdin/stdout
3. **Lifecycle**: Process runs for entire Claude Code session
4. **Shutdown**: Process terminated when Claude Code exits

### Use Cases

**NPM Packages:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
  }
}
```

**Custom Scripts:**
```json
{
  "custom": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server.js",
    "args": ["--verbose"]
  }
}
```

**Python Servers:**
```json
{
  "python-server": {
    "command": "python",
    "args": ["-m", "my_mcp_server"],
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

### Best Practices

1. **Use absolute paths or ${CLAUDE_PLUGIN_ROOT}**
2. **Set PYTHONUNBUFFERED for Python servers**
3. **Pass configuration via args or env, not stdin**
4. **Handle server crashes gracefully**
5. **Log to stderr, not stdout (stdout is for MCP protocol)**

### Troubleshooting

**Server won't start:**
- Check command exists and is executable
- Verify file paths are correct
- Check permissions
- Review `claude --debug` logs

**Communication fails:**
- Ensure server uses stdin/stdout correctly
- Check for stray print/console.log statements
- Verify JSON-RPC format

## SSE (Server-Sent Events)

### Overview

Connect to hosted MCP servers via HTTP with server-sent events for streaming. Best for cloud services and OAuth authentication.

### Configuration

**Basic:**
```json
{
  "hosted-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

**With headers:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-API-Version": "v1",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}
```

### Connection Lifecycle

1. **Initialization**: HTTP connection established to URL
2. **Handshake**: MCP protocol negotiation
3. **Streaming**: Server sends events via SSE
4. **Requests**: Client sends HTTP POST for tool calls
5. **Reconnection**: Automatic reconnection on disconnect

### Authentication

**OAuth (Automatic):**
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

Claude Code handles OAuth flow:
1. User prompted to authenticate on first use
2. Opens browser for OAuth flow
3. Tokens stored securely
4. Automatic token refresh

**Custom Headers:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### Use Cases

**Official Services:**
- Asana: `https://mcp.asana.com/sse`
- GitHub: `https://mcp.github.com/sse`
- Other hosted MCP servers

**Custom Hosted Servers:**
Deploy your own MCP server and expose via HTTPS + SSE.

### Best Practices

1. **Always use HTTPS, never HTTP**
2. **Let OAuth handle authentication when available**
3. **Use environment variables for tokens**
4. **Handle connection failures gracefully**
5. **Document OAuth scopes required**

### Troubleshooting

**Connection refused:**
- Check URL is correct and accessible
- Verify HTTPS certificate is valid
- Check network connectivity
- Review firewall settings

**OAuth fails:*

*(content truncated)*

## See Also

- [[github-agent-types]]
- [[mcp-authentication-patterns]]
- [[using-mcp-tools-in-commands-and-agents]]
- [[acceptance-criteria-create-mcp-integration]]
- [[procedural-fallback-tree-create-mcp-integration]]
- [[rsvp-reading-protocol-referencennput-deep-context-here-so-it-is-not-loaded-into-context-implicitly]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-mcp-integration/references/server-types.md`
- **Indexed:** 2026-04-17T06:42:09.921680+00:00
