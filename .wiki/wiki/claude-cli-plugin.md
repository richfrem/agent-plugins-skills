---
concept: claude-cli-plugin
source: plugin-code
source_file: claude-cli/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.532921+00:00
cluster: analysis
content_hash: f9de364e1249f083
---

# Claude CLI Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Claude CLI Plugin

Claude CLI sub-agent system for persona-based analysis. Pipes large contexts to Anthropic models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to Claude CLI. The skill manages prompt construction, persona injection, and output handling for headless Claude CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **claude-cli-agent** | Dispatch persona-based analysis tasks to Claude CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Claude model context. Particularly useful for large file analysis via stdin piping without loading content into the parent agent's memory.

## Structure

```
claude-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- claude-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `claude-cli-agent`

### Prerequisites
- `claude` CLI installed and authenticated (`claude login`)


## See Also

- [[acceptance-criteria-claude-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[copilot-cli-plugin]]
- [[gemini-cli-plugin]]
- [[acceptance-criteria-claude-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `claude-cli/README.md`
- **Indexed:** 2026-04-17T06:42:09.532921+00:00
