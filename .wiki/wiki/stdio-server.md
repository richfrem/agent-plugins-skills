---
concept: stdio-server
source: plugin-code
source_file: agent-scaffolders/references/examples/stdio-server.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.154016+00:00
cluster: command
content_hash: 46148a5dc7fc5e63
---

# Stdio Server

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/references/examples/stdio-server.json -->
{
  "_comment": "Example stdio MCP server configuration for local file system access",
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "${CLAUDE_PROJECT_DIR}"],
    "env": {
      "LOG_LEVEL": "info"
    }
  },
  "database": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server.js",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config/db.json"],
    "env": {
      "DATABASE_URL": "${DATABASE_URL}",
      "DB_POOL_SIZE": "10"
    }
  },
  "custom-tools": {
    "command": "python",
    "args": ["-m", "my_mcp_server", "--port", "8080"],
    "env": {
      "API_KEY": "${CUSTOM_API_KEY}",
      "DEBUG": "false"
    }
  }
}


<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-mcp-integration/references/examples/stdio-server.json -->
{
  "_comment": "Example stdio MCP server configuration for local file system access",
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "${CLAUDE_PROJECT_DIR}"],
    "env": {
      "LOG_LEVEL": "info"
    }
  },
  "database": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server.js",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config/db.json"],
    "env": {
      "DATABASE_URL": "${DATABASE_URL}",
      "DB_POOL_SIZE": "10"
    }
  },
  "custom-tools": {
    "command": "python",
    "args": ["-m", "my_mcp_server", "--port", "8080"],
    "env": {
      "API_KEY": "${CUSTOM_API_KEY}",
      "DEBUG": "false"
    }
  }
}


## See Also

- [[http-server]]
- [[sse-server]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/examples/stdio-server.json`
- **Indexed:** 2026-04-27T05:21:04.154016+00:00
