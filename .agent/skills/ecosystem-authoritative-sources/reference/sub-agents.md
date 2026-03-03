# Sub-Agents Research

This document captures our accumulated knowledge and definitive specifications for **Sub-agents**.

**Source:** [Create custom subagents](https://code.claude.com/docs/en/sub-agents)

## Definition
Subagents are specialized AI assistants that run in their own context window with customized system prompts, restricted tools, and independent permissions. They prevent the main conversation from drowning in exploratory actions and enforce operational boundaries.

## Creation & Structure
- Subagents are defined in Markdown files with YAML frontmatter.
- The markdown body acts as the *System Prompt* for that agent.
- During execution, the main Claude agent spawns subagents utilizing the `Task` tool.
- Subagents *cannot* spawn other subagents.

## Core Configuration (YAML Frontmatter)
The frontmatter defines the metadata and bounds of the subagent:
- `name` (required): Unique identifier (e.g., `code-reviewer`). Included in namespace if part of a plugin.
- `description` (required): Tells the main Claude agent *when* and *why* to delegate tasks to this subagent.
- `tools`: An allowlist of specific tools (e.g., `Read, Glob, Grep`).
- `disallowedTools`: A denylist of inherited tools.
- `model`: Defaults to `inherit` from parent, but can be forced (e.g., `sonnet`, `haiku`).
- `permissionMode`: Overrides permission prompts (`default`, `acceptEdits`, `bypassPermissions`, `dontAsk`, `plan`).
- `skills`: An array of Skill names to inject into the subagent's memory pre-load.
- `memory`: Persistent memory scope (`user`, `project`, `local`) forming a `$MEMORY_DIR/MEMORY.md` directory across sessions.
- `hooks`: Component-scoped [Hooks](hooks.md) running explicitly for this agent's lifecycle (e.g., `PreToolUse`, `SubagentStop`).

## Scope & Precedence
When multiple subagents share the same name, they resolve in an ordered priority:
1. **CLI Flag** (`--agents '{...json...}'`)
2. **Project** (`.claude/skills/`)
3. **User Local** (`~/.claude/skills/`)
4. **Plugin** (located in the enabled plugin's `agents/` root).

## Foreground vs. Background execution
- **Foreground:** Subagent blocks the main conversation, passing through interactive permission and `AskUserQuestion` prompts.
- **Background:** Placed in the background (concurrent). Auto-denies unapproved tool permissions and fails if it attempts to use `AskUserQuestion`. MCP tools are forbidden in background agents.
