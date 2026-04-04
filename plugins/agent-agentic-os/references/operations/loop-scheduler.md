# Loop Scheduler and Heartbeat Pattern

The `/loop` command turns Claude Code into a cron daemon - a background worker that runs
scheduled tasks at fixed intervals while a session is active.

## Native /loop Command

```bash
# Start an hourly loop task
/loop "Scan open PRs and write a summary to context/memory/pr-digest.md" --interval 1h

# Start a daily task
/loop "Review context/memory/ and promote any recurring patterns to memory.md" --interval 24h
```

**Constraints (Anthropic-enforced):**
- Up to **50 concurrent scheduled tasks** per session
- Tasks auto-expire after **3 days** to prevent unbounded operation
- Each task runs in its own isolated context window

## heartbeat.md Pattern

`heartbeat.md` is a community convention: a markdown file that describes what Claude
should do on a scheduled basis. It is referenced from a `/loop` invocation.

### Example heartbeat.md

```markdown
# Heartbeat Tasks

## Every Hour
- Check `context/memory/` for new dated logs
- Scan project/TODO.md for new items
- Write a brief status update to `context/status.md`

## Every 24 Hours
- Review open GitHub issues via GitHub MCP
- Promote durable facts from today's session log to `context/memory.md`
- Summarize the day to `context/memory/YYYY-MM-DD.md`

## On Session Start
- Load `START_HERE.md`
- Read `context/memory.md` for recent decisions
- Check `context/status.md` for open items
```

### Connecting heartbeat.md to /loop

```bash
# Run the heartbeat every hour
/loop "Read heartbeat.md and execute the items listed under 'Every Hour'" --interval 1h
```

## START_HERE.md - Bootstrap Prompt

`START_HERE.md` is the onboarding prompt for new sessions.
It bootstraps context loading so Claude starts each session aware.

```markdown
# Session Bootstrap

## Load Context
1. @import context/soul.md
2. @import context/user.md
3. @import context/memory.md (last 20 entries)
4. @import context/status.md

## Check Open Items
Look for `[ ]` items in context/memory/ logs from the last 7 days.

## Confirm Readiness
Say: "I'm ready. Here is what I know: [summary of loaded context]"
```

## MEMORY.md - Auto-Memory (Anthropic Native)

`MEMORY.md` is written **by Claude**, not by you.
Claude silently maintains this file as it works, noting:
- Build commands discovered
- Code style patterns observed
- Architecture decisions encountered
- Tricky bugs solved

This is the Anthropic-native layer; no manual configuration required.
You can read it anytime to see what Claude has learned about your project.

## Common Loop Patterns

| Pattern | Interval | Purpose |
|---------|----------|---------|
| PR digest | 1h | Summarize open PRs |
| Memory promotion | 24h | Curate session logs into memory.md |
| Status report | 4h | Write status.md with current work state |
| Skill update | On session close | Codify new learnings into skills |
