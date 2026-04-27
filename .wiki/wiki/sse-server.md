---
concept: sse-server
source: plugin-code
source_file: agent-scaffolders/references/examples/sse-server.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.153850+00:00
cluster: type
content_hash: 9b0be023f74e12c8
---

# Sse Server

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/references/examples/sse-server.json -->
{
  "_comment": "Example SSE MCP server configuration for hosted cloud services",
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  },
  "github": {
    "type": "sse",
    "url": "https://mcp.github.com/sse"
  },
  "custom-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-API-Version": "v1",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}


<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-mcp-integration/references/examples/sse-server.json -->
{
  "_comment": "Example SSE MCP server configuration for hosted cloud services",
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  },
  "github": {
    "type": "sse",
    "url": "https://mcp.github.com/sse"
  },
  "custom-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-API-Version": "v1",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}


## See Also

- [[http-server]]
- [[stdio-server]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/examples/sse-server.json`
- **Indexed:** 2026-04-27T05:21:04.153850+00:00
