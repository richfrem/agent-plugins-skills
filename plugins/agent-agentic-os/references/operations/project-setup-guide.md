# Project Setup Reference Guide

Detailed checklist and decisions reference for `os-init` users.

## What Gets Created and Why

### Root Files

| File | Purpose | Priority | Git? |
|------|---------|----------|------|
| `CLAUDE.md` | Project kernel -- read every session | Critical | YES |
| `CLAUDE.local.md` | Personal overrides (not for team) | Optional | NO |
| `START_HERE.md` | Bootstrap prompt for new sessions | High | YES |
| `heartbeat.md` | /loop scheduled task definitions | If using /loop | YES |

### context/ Folder

| File | Purpose | Priority | Git? |
|------|---------|----------|------|
| `context/soul.md` | Agent identity and tone | High (personas) | YES |
| `context/user.md` | Your working style preferences | Medium | YES |
| `context/memory.md` | Long-term curated facts | High | YES |
| `context/memory/YYYY-MM-DD.md` | Dated session logs | Auto-generated | NO |

### .claude/ Folder

| Path | Purpose | Notes |
|------|---------|-------|
| `.claude/agents/` | Sub-agent definitions (.md files) | Per-task specialists |
| `.claude/commands/` | Slash commands (`/project:name`) | Optional shortcuts |
| `.claude/hooks/hooks.json` | Lifecycle automation | Optional, restart needed |

## CLAUDE.md Writing Guide

A CLAUDE.md file has a hard practical limit around 300 lines before it becomes
counterproductive. Use the `@import` pattern to stay lean:

```markdown
# My Project

@import context/soul.md
@import context/user.md

## Build Commands
npm run dev
npm test
npm run lint

## Key Architecture
[2-3 sentences max - deep detail goes in a reference file]

## Conventions
[bullet list of must-know rules]
```

Move deep knowledge to external files -- do NOT put your entire codebase architecture
in CLAUDE.md. Claude can read individual files when it needs them.

## Scope Hierarchy (Anthropic Official)

Claude loads CLAUDE.md files in this order (later = higher precedence):

1. `~/.claude/CLAUDE.md` (global, all projects)
2. `~/.claude/projects/<project-id>/CLAUDE.md` (enterprise/organization)
3. `<project-root>/CLAUDE.md` (this repo, shared with team)
4. `<project-root>/CLAUDE.local.md` (your personal overrides, gitignored)
5. Subdirectory `CLAUDE.md` files (for specific subdirectories)

**Key insight**: You probably want files at scope 3 (shared) and 4 (personal only).
Scope 1 (global) is great for identity and personal preferences that span all projects.

Source: https://docs.anthropic.com/en/docs/claude-code/memory

## Sub-Agent Patterns by Use Case

### Legacy System Documentation

Create 3-4 specialized sub-agents in `.claude/agents/`:

**screen-analyzer.md** - Reads screenshots, extracts UI patterns and business rules
**business-rules-writer.md** - Transforms observations into formal BRD format
**workflow-documenter.md** - Maps screen flows into process diagrams (Mermaid)
**qa-reviewer.md** - Validates documentation completeness and consistency

### Software Development

**code-reviewer.md** - Code review specialist
**test-generator.md** - Test case writer
**refactor-agent.md** - Technical debt reduction

### Marketing / Content

**content-writer.md** - Writes in brand voice (reference soul.md)
**editor.md** - Reviews and improves drafts
**strategist.md** - Research and competitive analysis

## /loop Setup Guide

The `/loop` command runs a scheduled task repeatedly. It requires:
1. A `heartbeat.md` file defining what tasks to run
2. Starting the loop: `/loop "Read heartbeat.md and run the Every Hour tasks" --interval 1h`

Constraints (Anthropic official):
- Max 3-day auto-expiry per task
- Runs in a new context each iteration (stateless between ticks)
- Must write state explicitly (e.g., to `status.md`) to persist across ticks

Source: https://docs.anthropic.com/en/docs/claude-code/loop

## Settings File Pattern (.local.md)

If your agents need per-project configuration store it in `.claude/<plugin-name>.local.md`:

```markdown
---
enabled: true
mode: strict
project_type: legacy-docs
---

# Agent Configuration

Specializing in documenting the ACME Corp billing system.
Focus on screen-by-screen analysis.
```

This YAML frontmatter can be read by hooks and commands to configure behavior.
Always add `.claude/*.local.md` to `.gitignore`.

## Hooks Quick Reference

Hooks run automatically on Claude Code events. Define in `.claude/hooks/hooks.json`:

```json
{
  "SessionStart": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "cat START_HERE.md",
      "timeout": 5
    }]
  }]
}
```

**Important**: Hooks require a Claude Code restart to take effect after changes.

Available events: PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart,
SessionEnd, UserPromptSubmit, PreCompact, Notification

Source: https://docs.anthropic.com/en/docs/claude-code/hooks

## .gitignore Template

```gitignore
# Agentic OS - personal/session files (do not commit)
CLAUDE.local.md
context/memory/
context/status.md
context/os-state.json
context/events.jsonl
context/.locks/
.claude/
MEMORY.md

# Keep these (shared project kernel)
# CLAUDE.md
# context/soul.md
# context/user.md
# context/memory.md
# heartbeat.md
# START_HERE.md
# context/kernel.py
# context/agents.json
```
