# Sub-Agents, Hooks, and Commands

## Sub-Agents (`.claude/agents/`)

Sub-agents are isolated Claude instances with their own tool sets and context boundaries.
They are defined as markdown files in `.claude/agents/`.

### When to Use Sub-Agents

- Tasks that need to read many files (avoids polluting the main context)
- Specialized focus areas (security reviewer, test writer, docs updater)
- Long-running analysis that should not interfere with interactive work

### Sub-Agent Definition Format

```markdown
---
name: security-reviewer
description: >
  Specialized security audit agent. Reviews code changes for injection,
  authentication flaws, and data exposure risks. Invoke for PR reviews,
  dependency checks, or security audits.
allowed-tools: Read, Bash
---
# Security Reviewer

You are a security-focused code reviewer. Your role is to...

## Review Checklist
1. Check for SQL injection vectors
2. Review authentication flows
3. Audit sensitive data handling
...
```

### Mapping to Agent Skills Open Standard

Sub-agents defined in `.claude/agents/` are structurally equivalent to Skills in
`.agents/skills/` (the open standard). The same SKILL.md conventions apply:
- YAML frontmatter with `name`, `description`, `allowed-tools`
- Specific trigger descriptions in third person
- Progressive disclosure for deep content

## Hooks (`.claude/hooks/`)

Hooks are lifecycle integrations triggered by Claude Code events.

### Hook Types

| Event | When It Fires |
|-------|--------------|
| `PreToolUse` | Before any tool is called |
| `PostToolUse` | After a tool completes |
| `SessionStart` | When a new session begins |
| `SessionEnd` | When a session closes |

### Auto-Memory Hook Pattern

The community convention for auto-updating memory uses a `PostToolUse` hook:

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "tool": "Write",
      "command": "python .claude/hooks/update_memory.py"
    }
  ]
}
```

`update_memory.py` scans what was written and appends relevant facts to the dated session log.

### hooks.json Location

```
.claude/
  hooks/
    hooks.json       <- Hook registration
    update_memory.py <- The hook script
```

## Commands (`.claude/commands/`)

Commands are slash commands available in Claude Code chat.
They are markdown files that agents execute when invoked.

### Example Command

```markdown
# .claude/commands/summarize-session.md

Summarize what was accomplished this session:
1. Read context/memory/ for today's date
2. List key decisions made
3. List any skills or tools created
4. Write a brief summary to context/status.md
```

Invoke with: `/project:summarize-session`

### Global vs Project Commands

| Location | Scope | Invocation prefix |
|----------|-------|-------------------|
| `~/.claude/commands/` | All projects | `/user:command-name` |
| `{project}/.claude/commands/` | This project | `/project:command-name` |

## Putting It Together

```
.claude/
  agents/
    security-reviewer.md    <- Isolated security audit agent
    test-writer.md          <- Isolated test generation agent
  commands/
    summarize-session.md    <- /project:summarize-session
    update-memory.md        <- /project:update-memory
  hooks/
    hooks.json              <- Hook registrations
    update_memory.py        <- PostToolUse auto-memory script
```
