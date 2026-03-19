# Canonical Agentic OS File Structure

The full reference layout for an Agentic OS environment.
Anthropic-native components are marked [A]; community conventions marked [C].

```
~/my-agent-os/                        <- Root of the OS
|
|-- CLAUDE.md                         <- [A] KERNEL: global rules, @imports, tool index
|                                        Loaded every session. Keep under 300 lines.
|
|-- MEMORY.md                         <- [A] AUTO-MEMORY: written by Claude, not you
|                                        Build commands, code patterns, decisions discovered
|
|-- START_HERE.md                     <- [C] BOOTSTRAP: onboarding prompt for new sessions
|                                        Loads context, memory, active tasks on start
|
|-- heartbeat.md                      <- [C] CRON DEFINITION: what to do on /loop runs
|                                        Hourly: scan PRs. Daily: promote memory. etc.
|
|-- context/                          <- [C] PERSISTENT RAM
|   |-- soul.md                       <- Identity, values, personality, tone
|   |-- user.md                       <- User preferences, working style
|   |-- memory.md                     <- Long-term facts / decisions (you curate)
|   |-- status.md                     <- Current state (what is in progress)
|   `-- memory/                       <- Dated session logs
|       |-- 2026-03-15.md             <- Today's session log
|       |-- 2026-03-14.md
|       `-- archive/
|           `-- 2026-02.md            <- Archived older sessions
|
|-- skills/                           <- [A] STANDARD LIBRARY: procedural knowledge bundles
|   `-- my-skill/
|       `-- SKILL.md                  <- Skill definition (YAML frontmatter + instructions)
|
|-- .claude/                          <- [A] AGENT RUNTIME
|   |-- agents/                       <- [A] Sub-agents with isolated context + tool sets
|   |   |-- security-reviewer.md
|   |   `-- test-writer.md
|   |-- commands/                     <- [A] Slash commands (/project:command-name)
|   |   |-- summarize-session.md
|   |   `-- update-memory.md
|   `-- hooks/                        <- [A] Lifecycle event integrations
|       |-- hooks.json                <- Hook registrations (PostToolUse, SessionStart, etc.)
|       `-- update_memory.py          <- Auto-memory update script
|
`-- projects/                         <- [C] PROJECT-SCOPED CONTEXTS
    `-- my-project/
        |-- CLAUDE.md                 <- [A] Project kernel: arch, commands, conventions
        |                                Inherits from root CLAUDE.md. Project-specific only.
        `-- CLAUDE.local.md           <- [A] Personal overrides (gitignored)
```

## Minimal Starter Setup

If setting up from scratch, implement in this order:

1. **Global CLAUDE.md** (`~/.claude/CLAUDE.md`): Your identity, universal rules
2. **context/soul.md**: Agent identity and values
3. **context/user.md**: Your working style preferences
4. **Project CLAUDE.md**: Architecture, build commands, conventions for each project
5. **START_HERE.md**: Bootstrap prompt to load context at session start
6. **First session log**: After first meaningful session, write `context/memory/YYYY-MM-DD.md`

Add as needed:
- **MEMORY.md**: Appears automatically as Claude works
- **heartbeat.md + /loop**: Add when you want scheduled background tasks
- **Sub-agents**: Add for specialized recurring tasks (security review, test writing)
- **Hooks**: Add when you want automatic post-tool-use memory updates

## Key Design Principles

1. **CLAUDE.md is the kernel** - Keep it lean. It loads every session. Every line costs attention.
2. **context/ is RAM** - It is fast, accessible, and cleared/rebuilt per session via @import.
3. **skills/ is stdlib** - Reusable patterns that any session can pull in.
4. **Dated logs are the disk** - Slow, durable, loaded on demand when you need history.
5. **Agents compete for context** - If documents conflict or are obsolete, agents get "dementia". Keep your context clean.
