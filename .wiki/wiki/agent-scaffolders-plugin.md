---
concept: agent-scaffolders-plugin
source: plugin-code
source_file: agent-scaffolders/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.302785+00:00
cluster: skill
content_hash: 2c1c0415696cf1ea
---

# Agent Scaffolders Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Scaffolders Plugin

Interactive scaffolding system for creating and optimising Claude Code plugins, skills,
hooks, sub-agents, commands, GitHub Actions, MCP integrations, and agentic workflows.

## Skills

| Skill | Trigger | What it builds |
|---|---|---|
| `create-skill` | "create a skill", "scaffold a skill", "run evals on a skill" | Full skill directory with SKILL.md, references/, evals/ |
| `create-plugin` | "create a plugin", "build a new plugin" | Complete plugin with plugin.json, skills/, commands/, agents/, hooks/ |
| `create-sub-agent` | "create an agent", "add an agent to my plugin" | Agent .md file with frontmatter, system prompt, permission grants |
| `create-command` | "create a command", "add a slash command" | Slash command .md with frontmatter, argument handling |
| `create-hook` | "create a hook", "add a PreToolUse hook", "validate tool use" | hooks.json entries or skill-scoped hook frontmatter |
| `create-mcp-integration` | "add an MCP", "setup mcp server" | .mcp.json or plugin.json mcpServers block |
| `create-github-action` | "create a github action", "scaffold CI workflow" | GitHub Actions YAML |
| `create-agentic-workflow` | "create a github agent", "convert skill to copilot agent" | GitHub Agentic Workflow files (IDE or CI/CD) |
| `create-docker-skill` | "containerise this skill", "docker skill" | Dockerfile, pre-flight checker, security override |
| `create-azure-agent` | "create an azure agent", "azure ai foundry agent" | Azure AI Foundry agent boilerplate |
| `create-stateful-skill` | "stateful skill", "skill with state management" | L4-pattern skill with epistemic trust, artifact lifecycle, escalation |
| `continuous-skill-optimizer` | "optimise my skill description", "run the eval loop" | Iterative description improvement via eval loop |
| `manage-marketplace` | "create a marketplace", "publish my plugins" | marketplace.json, distribution guidance |

---

## Hook Support (13 events, 3 handler types)

`create-hook` covers all currently documented Claude Code hook lifecycle events:

| Event | Primary Use |
|---|---|
| `PreToolUse` | Approve, deny, or modify tool calls before execution |
| `PostToolUse` | React to successful tool output; inject `additionalContext` |
| `PostToolUseFailure` | Handle failed tool calls; retry logic, alerting |
| `PermissionRequest` | Auto-approve specific permissions so users aren't prompted repeatedly |
| `UserPromptSubmit` | Add context, validate, or block user prompts |
| `Stop` / `SubagentStop` | Completeness check before agent/subagent stops |
| `SubagentStart` | Inject context or enforce policies at subagent spin-up |
| `SessionStart` / `SessionEnd` | Load/save environment state |
| `PreCompact` | Preserve critical context before compaction |
| `Notification` | Logging and reactions to notifications |
| `ConfigChange` | React to dynamic configuration updates |

Handler types: `command` (bash), `prompt` (LLM-driven), `agent` (spawns subagent with Read/Grep/Glob).

Skill-scoped hooks (declared in SKILL.md frontmatter) are also supported for enforcement
scoped to a skill's active lifetime.

---

## Sub-Agent Frontmatter (current spec)

`create-sub-agent` generates agents using the full current frontmatter schema:

```yaml
---
name: my-agent
description: Use this agent when...
model: inherit            # or pinned: claude-sonnet-4-20250514
maxTokens: 4096
color: green
tools: ["Read", "Write"]
permissions:
  allowedTools:
    - "Read"
    - "Write"
  deny:
    - "Read(./.env)"
    - "Read(./secrets/**)"
hooks:
  Stop:
    - matcher: "*"
      type: prompt
      prompt: "Verify task completion before stopping."
---
```

---

## Agentic Workflow Patterns

`create-agentic-workflow` includes a mandatory complexity gate (Phase 0) that asks whether
an agentic approach is warranted, then supports five patterns:

- **Prompt Chaining** — sequential steps, each passing output to the next
- **Routing** — classify input and dispatch to a specialist sub-agent
- **Parallelisat

*(content truncated)*

## See Also

- [[agent-scaffolders-create-plugin]]
- [[agent-scaffolders-create-plugin]]
- [[agent-plugin-analyzer]]
- [[agent-plugin-analyzer---architecture]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]
- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/README.md`
- **Indexed:** 2026-04-17T06:42:09.302785+00:00
