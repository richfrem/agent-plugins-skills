---
concept: memory-hygiene-when-to-write-promote-and-archive
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-guide/references/memory-hygiene.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.156666+00:00
cluster: plugin-code
content_hash: 31a52a87661d321b
---

# Memory Hygiene: When to Write, Promote, and Archive

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Memory Hygiene: When to Write, Promote, and Archive

## The Three-Tier Model

```
MEMORY.md (auto)  <--  Claude writes this constantly, without prompting
context/memory.md <--  You curate this. Only durable facts.
context/memory/   <--  Session logs. Dated. One per significant session.
```

## Tier 1: MEMORY.md (Auto-Memory)

Claude writes this automatically. Do NOT manually edit it often.
It is a fast-write cache for things Claude discovers during work.

Contents will include:
- `npm run dev` starts the dev server
- "This project uses snake_case for database columns"
- "The auth module requires JWT_SECRET in .env"

**Your job**: Periodically read it and promote durable facts to `context/memory.md`.

## Tier 2: context/memory.md (Curated Long-Term)

**Promote to here when:**
- An architectural decision was made that will affect future work
- A gotcha or bug was discovered that could bite someone again
- A team convention was established
- A tool configuration quirk was resolved

**Do NOT promote:**
- One-off debugging steps
- Temporary state ("currently working on auth refactor")
- Facts that will be stale in a week
- Duplicates of what is already in MEMORY.md

### Promotion Format

```markdown
## [YYYY-MM-DD] Gotcha: Docker Volume Permissions
On Mac with Apple Silicon, Docker volumes default to 777. Use explicit chmod 755 in Dockerfile.

## [YYYY-MM-DD] Convention: API Error Format
All API errors use `{error: string, code: string, details?: object}`. Never raw exception messages.

## [YYYY-MM-DD] Decision: Monorepo Structure
Chose monorepo over polyrepo for shared type safety. Services in services/, shared code in packages/.
```

## Tier 3: Session Logs (context/memory/YYYY-MM-DD.md)

Write one per significant session. Use `os-memory-manager` skill.

**Write a session log when:**
- Something meaningful was accomplished (a feature shipped, a bug fixed, a decision made)
- A session ran longer than 20 minutes
- Multiple topics were discussed

**Skip the session log when:**
- It was a quick 2-minute question
- Nothing new was decided or built
- All relevant facts already got promoted to `context/memory.md`

## Archive Policy

Trigger archiving when `context/memory.md` exceeds 500 lines or becomes hard to scan:

1. Group the oldest 3-6 months of entries
2. Copy them to `context/memory/archive/YYYY-MM.md`
3. Remove those entries from `context/memory.md`
4. Add a note at the top of `context/memory.md`:
   ```
   <!-- Entries before YYYY-MM archived to context/memory/archive/YYYY-MM.md -->
   ```

## Quick Decision Table

| Situation | Action |
|-----------|--------|
| Found a tricky bug and fixed it | Promote to `context/memory.md` |
| Discussed options, chose architecture | Promote to `context/memory.md` |
| Wrote 10 files for a feature | Write session log |
| Updated a skill | Record in session log |
| Had a quick chat to clarify a concept | Skip (no log needed) |
| context/memory.md > 500 lines | Archive oldest block |
| MEMORY.md has durable facts mixed in | Promote to context/memory.md + clean up |


## See Also

- [[long-term-memory]]
- [[os-memory-command]]
- [[claudemd-hierarchy-and-scope-rules]]
- [[sub-agents-hooks-and-commands]]
- [[memory-promotion-decision-guide]]
- [[loop-scheduler-and-heartbeat-pattern]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-guide/references/memory-hygiene.md`
- **Indexed:** 2026-04-17T06:42:10.156666+00:00
