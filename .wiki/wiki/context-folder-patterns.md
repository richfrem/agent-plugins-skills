---
concept: context-folder-patterns
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-memory-manager/references/architecture/context-folder-patterns.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.181366+00:00
cluster: user
content_hash: bd36f91b3794c9f8
---

# Context Folder Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Context Folder Patterns

The `context/` folder is the persistent RAM of the Agentic OS.
It stores identity, preferences, and memory that survive across sessions.

## Standard File Layout

```
context/
  soul.md              <- Identity, values, tone, personality
  user.md              <- User preferences, working style, communication prefs
  memory.md            <- Long-term facts, decisions, project conventions (you curate)
  memory/
    2026-03-15.md      <- Session log: what happened, lessons learned, skills updated
    2026-03-14.md
    archive/
      2026-02.md       <- Archived older sessions
```

## soul.md - Identity and Values

Defines WHO the agent is. Written once, rarely updated.

```markdown
# Soul

## Identity
I am [agent name/persona]. My purpose is [mission].

## Values
- [Core principle 1]
- [Core principle 2]

## Tone
- [Communication style]
- [What I avoid]

## Strengths
- [Area of expertise]
```

**When to update**: Only when the agent's fundamental identity or purpose changes.

## user.md - User Preferences

Defines how to work WITH the specific user. Evolves over time.

```markdown
# User Preferences

## Name
[User's preferred name]

## Working Style
- Prefers [concise/detailed] responses
- Timezone: [timezone]
- [Other style notes]

## Communication
- Uses [platform] for questions
- Prefers [format] for code reviews

## Technical Context
- Primary language: [language]
- Stack: [tech stack]
- Editor: [editor]
```

**When to update**: When user expresses a preference, or you notice a consistent pattern.

## memory.md - Long-Term Curated Facts

The "permanent storage" layer. You (the human) curate this.
Only promote facts that are durable and reusable.

```markdown
# Long-Term Memory

## [YYYY-MM-DD] Architecture Decision: [Topic]
[Fact or decision in 1-3 sentences]

## [YYYY-MM-DD] Gotcha: [Short label]
[Bug, quirk, or edge case that bit us]

## [YYYY-MM-DD] Convention: [Topic]
[Team or project convention established]
```

**Size limit**: Keep under 500 lines total. Archive older entries to `memory/archive/`.

## Dated Session Logs - `memory/YYYY-MM-DD.md`

Written at the end of each significant session.
Use the `os-memory-manager` skill to create these.

```markdown
# Session Log: 2026-03-15

## Summary
Fixed the authentication bug and updated the login skill.

## Key Decisions
- Chose JWT over session cookies for stateless scaling

## Lessons Learned
- The auth middleware runs BEFORE the skill router

## Open Items
- [ ] Write unit tests for new JWT handler
```

## @import Strategy

Reference `context/` files from CLAUDE.md selectively:

```markdown
# CLAUDE.md
@import context/soul.md          <- Always import: identity is always relevant
@import context/user.md          <- Always import: working style is always relevant

<!-- memory.md imported on demand, not always -->
```

Do NOT always @import `memory.md` — it grows large. Load it only when you need historical context.


## See Also

- [[context-status-specification-contextstatusmd]]
- [[optimizer-engine-patterns-reference-design]]
- [[quick-start-zero-context-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns]]
- [[testing-anti-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-memory-manager/references/architecture/context-folder-patterns.md`
- **Indexed:** 2026-04-17T06:42:10.181366+00:00
