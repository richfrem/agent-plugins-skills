---
concept: claudemd-hierarchy-and-scope-rules
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-memory-manager/references/architecture/claude-md-hierarchy.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.181043+00:00
cluster: claude
content_hash: 422463d1c4e3c769
---

# CLAUDE.md Hierarchy and Scope Rules

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# CLAUDE.md Hierarchy and Scope Rules

## The Five Scopes

CLAUDE.md files are discovered and merged in this order (most specific wins):

| Scope | Location | Load Condition |
|-------|----------|---------------|
| Global | `~/.claude/CLAUDE.md` | Every Claude Code session |
| Organization | `~/org-name/CLAUDE.md` | When working in org directory |
| Project | `{project-root}/CLAUDE.md` | When inside the project |
| Local | `{project-root}/CLAUDE.local.md` | Same as project, gitignored |
| Subdirectory | `{any-subdir}/CLAUDE.md` | When working in that subdir |

**Precedence rule**: More specific overrides less specific. A subdirectory `CLAUDE.md` wins over the project root `CLAUDE.md` for files in that subdirectory.

## What Each Scope Is For

### Global (`~/.claude/CLAUDE.md`)
- Your identity, working style preferences, tool defaults
- Rules that apply everywhere (never commit to main, always use pip-compile, etc.)
- This is the kernel - loaded every single session

### Project (`{project-root}/CLAUDE.md`)
- Project architecture overview and key decisions
- Build commands, test commands, lint commands
- Team conventions, PR review process
- Links to important docs and files
- @imports for soul.md, user.md if desired

### Local (`CLAUDE.local.md`)
- Personal overrides not for the team
- Gitignored by convention
- Your local paths, personal shortcuts, dev machine specifics

### Subdirectory (`src/CLAUDE.md`, `tests/CLAUDE.md`)
- Subsystem-specific rules
- "Never edit generated files in this folder"
- Specialized agent instructions for that domain

## The @import Pattern

Use `@import` to load files on demand rather than always inlining them:

```markdown
# CLAUDE.md (project root)

@import context/soul.md
@import context/user.md

## Project Overview
...
```

This keeps the kernel lean while making deep context available.

## Size Constraint

> Every line in CLAUDE.md competes for attention with actual work.

**Hard limit**: Keep any single CLAUDE.md under 300 lines.
**Strategy**: Move deep knowledge into `@import`ed files in `context/` or `references/`.

## Common Anti-Patterns

| Anti-Pattern | Better Alternative |
|---|---|
| Pasting entire codebase docs into CLAUDE.md | @import a `context/architecture.md` |
| Listing every rule ever | Focus on what Claude gets WRONG without the rule |
| Duplicating content across scopes | Put it in the most specific scope only |
| Including debug logs or temp notes | Use CLAUDE.local.md or a dated memory log |


## See Also

- [[sub-agents-hooks-and-commands]]
- [[memory-hygiene-when-to-write-promote-and-archive]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[claude-md-hierarchy]]
- [[sub-agents-and-hooks]]
- [[claude-md-hierarchy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-memory-manager/references/architecture/claude-md-hierarchy.md`
- **Indexed:** 2026-04-17T06:42:10.181043+00:00
