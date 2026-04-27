---
concept: http-server
source: plugin-code
source_file: agent-scaffolders/references/examples/http-server.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.153697+00:00
cluster: example
content_hash: 7a11adaea5ac1bb7
---

# Http Server

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/references/examples/http-server.json -->
{
  "_comment": "Example HTTP MCP server configuration for REST APIs",
  "rest-api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "Content-Type": "application/json",
      "X-API-Version": "2024-01-01"
    }
  },
  "internal-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Service-Name": "claude-plugin"
    }
  }
}


<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-mcp-integration/references/examples/http-server.json -->
{
  "_comment": "Example HTTP MCP server configuration for REST APIs",
  "rest-api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "Content-Type": "application/json",
      "X-API-Version": "2024-01-01"
    }
  },
  "internal-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Service-Name": "claude-plugin"
    }
  }
}


## See Also

- [[sse-server]]
- [[stdio-server]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/examples/http-server.json`
- **Indexed:** 2026-04-27T05:21:04.153697+00:00
