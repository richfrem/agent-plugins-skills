---
concept: using-mcp-tools-in-commands-and-agents
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-mcp-integration/references/tool-usage.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.922462+00:00
cluster: tool
content_hash: 8dd0005d7ba6cd2d
---

# Using MCP Tools in Commands and Agents

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Using MCP Tools in Commands and Agents

Complete guide to using MCP tools effectively in Claude Code plugin commands and agents.

## Overview

Once an MCP server is configured, its tools become available with the prefix `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. Use these tools in commands and agents just like built-in Claude Code tools.

## Tool Naming Convention

### Format

```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
```

### Examples

**Asana plugin with asana server:**
- `mcp__plugin_asana_asana__asana_create_task`
- `mcp__plugin_asana_asana__asana_search_tasks`
- `mcp__plugin_asana_asana__asana_get_project`

**Custom plugin with database server:**
- `mcp__plugin_myplug_database__query`
- `mcp__plugin_myplug_database__execute`
- `mcp__plugin_myplug_database__list_tables`

### Discovering Tool Names

**Use `/mcp` command:**
```bash
/mcp
```

This shows:
- All available MCP servers
- Tools provided by each server
- Tool schemas and descriptions
- Full tool names for use in configuration

## Using Tools in Commands

### Pre-Allowing Tools

Specify MCP tools in command frontmatter:

```markdown
---
description: Create a new Asana task
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task"
]
---

# Create Task Command

To create a task:
1. Gather task details from user
2. Use mcp__plugin_asana_asana__asana_create_task with the details
3. Confirm creation to user
```

### Multiple Tools

```markdown
---
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task",
  "mcp__plugin_asana_asana__asana_search_tasks",
  "mcp__plugin_asana_asana__asana_get_project"
]
---
```

### Wildcard (Use Sparingly)

```markdown
---
allowed-tools: ["mcp__plugin_asana_asana__*"]
---
```

**Caution:** Only use wildcards if the command truly needs access to all tools from a server.

### Tool Usage in Command Instructions

**Example command:**
```markdown
---
description: Search and create Asana tasks
allowed-tools: [
  "mcp__plugin_asana_asana__asana_search_tasks",
  "mcp__plugin_asana_asana__asana_create_task"
]
---

# Asana Task Management

## Searching Tasks

To search for tasks:
1. Use mcp__plugin_asana_asana__asana_search_tasks
2. Provide search filters (assignee, project, etc.)
3. Display results to user

## Creating Tasks

To create a task:
1. Gather task details:
   - Title (required)
   - Description
   - Project
   - Assignee
   - Due date
2. Use mcp__plugin_asana_asana__asana_create_task
3. Show confirmation with task link
```

## Using Tools in Agents

### Agent Configuration

Agents can use MCP tools autonomously without pre-allowing them:

```markdown
---
name: asana-status-updater
description: This agent should be used when the user asks to "update Asana status", "generate project report", or "sync Asana tasks"
model: inherit
color: blue
---

## Role

Autonomous agent for generating Asana project status reports.

## Process

1. **Query tasks**: Use mcp__plugin_asana_asana__asana_search_tasks to get all tasks
2. **Analyze progress**: Calculate completion rates and identify blockers
3. **Generate report**: Create formatted status update
4. **Update Asana**: Use mcp__plugin_asana_asana__asana_create_comment to post report

## Available Tools

The agent has access to all Asana MCP tools without pre-approval.
```

### Agent Tool Access

Agents have broader tool access than commands:
- Can use any tool Claude determines is necessary
- Don't need pre-allowed lists
- Should document which tools they typically use

## Tool Call Patterns

### Pattern 1: Simple Tool Call

Single tool call with validation:

```markdown
Steps:
1. Validate user provided required fields
2. Call mcp__plugin_api_server__create_item with validated data
3. Check for errors
4. Display confirmation
```

### Pattern 2: Sequential Tools

Chain multiple tool calls:

```markdown
Steps:
1. Search for existing items: mcp__plugin_api_server__search
2. If not found, create new: mcp__plugin_api_server__create
3. Add metadata: mcp__plugin_api

*(content truncated)*

## See Also

- [[sub-agents-hooks-and-commands]]
- [[sub-agents-hooks-and-commands]]
- [[sub-agents-hooks-and-commands]]
- [[sub-agents-and-hooks]]
- [[sub-agents-and-hooks]]
- [[claudemd-hierarchy-and-scope-rules]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-mcp-integration/references/tool-usage.md`
- **Indexed:** 2026-04-17T06:42:09.922462+00:00
