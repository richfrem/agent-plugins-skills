---
concept: memory-promotion-decision-guide
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-memory-manager/references/memory-promotion-guide.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.182335+00:00
cluster: promote
content_hash: e5db977643a5288a
---

# Memory Promotion Decision Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Memory Promotion Decision Guide

Use this guide to decide what facts from a session deserve promotion to long-term memory.

## The Promotion Filter

Ask three questions before promoting any fact:

1. **Will this fact still be true in 3 months?** If no -> session log only, do not promote.
2. **Would a new team member (or fresh Claude session) need to know this?** If yes -> promote.
3. **Is this already in MEMORY.md or context/memory.md?** If yes -> update existing entry instead.

## Fact Categories and Promotion Rules

### Promote Always

| Category | Example | Where |
|----------|---------|-------|
| Architecture decisions | "Chose JWT over sessions for stateless scaling" | `context/memory.md` |
| Project conventions | "Always use snake_case for DB columns" | `context/memory.md` |
| Tool/env quirks | "Docker volumes need explicit chmod on Apple Silicon" | `context/memory.md` |
| Security constraints | "Never log the JWT payload - only the header" | `context/memory.md` |
| Team agreements | "PR review required from 2+ people before merge" | `context/memory.md` |

### Promote Conditionally

| Category | Promote If... |
|----------|--------------|
| Bug fixes | The bug could recur. The fix is non-obvious. |
| Performance findings | The optimization is reusable (not one-time) |
| External API quirks | Will interact with this API again |
| Dependency decisions | Why a specific version was pinned |

### Never Promote

| Category | Reason |
|----------|--------|
| Today's debugging steps | Too specific; will not repeat exactly |
| Temporary state ("WIP branch") | Stale next week |
| Meeting notes / chat summaries | Not actionable or architectural |
| Obvious things | If any developer would know it, skip it |
| Duplicates | If already in MEMORY.md, do not duplicate |

## Promotion Entry Format

```markdown
## [YYYY-MM-DD] [Category]: [Short Label]
[The fact in 1-3 sentences. Be specific enough to be actionable.]
```

Examples:

```markdown
## [2026-03-15] Decision: Auth Strategy
Chose stateless JWT over server-side sessions. Reason: horizontal scaling requirement.
Tokens expire in 1h; refresh tokens in 30d stored in httpOnly cookies.

## [2026-03-14] Gotcha: Pip-Compile on M3 Mac
pip-compile generates platform-specific hashes on M3 Macs that break Linux CI.
Fix: always run pip-compile in Docker (make deps) not locally.

## [2026-03-12] Convention: Commit Message Format
All commits use imperative mood: "Add feature" not "Added feature".
Scope prefix for breaking changes: "feat!: " or "fix!: ".
```

## Demotion Rules

If a long-term fact becomes stale or superseded:
1. Add a comment noting it is superseded: `<!-- superseded: see [date] entry -->`
2. Or delete it and write a new entry with the updated fact
3. Do NOT leave contradictory facts - they cause agent confusion

## Archive Trigger

Archive old entries to `context/memory/archive/YYYY-MM.md` when:
- `context/memory.md` exceeds 500 lines
- You find yourself scrolling past dozens of outdated entries to find current ones

Archive the oldest 3-6 months, not recent entries.


## See Also

- [[memory-promotion-guide]]
- [[long-term-memory]]
- [[os-memory-command]]
- [[memory-hygiene-when-to-write-promote-and-archive]]
- [[chart-reading-guide]]
- [[os-eval-backport-phase-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-memory-manager/references/memory-promotion-guide.md`
- **Indexed:** 2026-04-17T06:42:10.182335+00:00
