---
concept: gemini-cli-plugin
source: plugin-code
source_file: gemini-cli/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.608903+00:00
cluster: analysis
content_hash: 988b31b90563f42d
---

# Gemini CLI Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Gemini CLI Plugin

Google Gemini CLI sub-agent system for persona-based analysis. Pipes large contexts to Gemini models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to Gemini CLI. The skill manages prompt construction, persona injection, and output handling for headless Gemini CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **gemini-cli-agent** | Dispatch persona-based analysis tasks to Gemini CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Gemini model context. Supports model selection via the `-m` flag (e.g., `gemini-3.1-flash-lite-preview`, `gemini-3-flash-preview`).

## Structure

```
gemini-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- gemini-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `gemini-cli-agent`

### Prerequisites
- `gemini` CLI installed and authenticated


## See Also

- [[claude-cli-plugin]]
- [[copilot-cli-plugin]]
- [[gemini-cli-command-reference-workflows]]
- [[acceptance-criteria-gemini-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]
- [[optimization-program-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `gemini-cli/README.md`
- **Indexed:** 2026-04-17T06:42:09.608903+00:00
