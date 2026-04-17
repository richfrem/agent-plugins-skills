---
concept: copilot-cli-plugin
source: plugin-code
source_file: copilot-cli/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.549543+00:00
cluster: analysis
content_hash: adc95404d4c4605b
---

# Copilot CLI Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Copilot CLI Plugin

GitHub Copilot CLI sub-agent system for persona-based analysis. Pipes large contexts to Copilot models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to GitHub Copilot CLI. The skill manages prompt construction, persona injection, and output handling for headless Copilot CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **copilot-cli-agent** | Dispatch persona-based analysis tasks to Copilot CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Copilot model context without access to agent tools or memory.

## Structure

```
copilot-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- copilot-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `copilot-cli-agent`

### Prerequisites
- `copilot` CLI installed and authenticated (`copilot login`)


## See Also

- [[claude-cli-plugin]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[optimization-program-copilot-cli-agent]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]
- [[gemini-cli-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `copilot-cli/README.md`
- **Indexed:** 2026-04-17T06:42:09.549543+00:00
