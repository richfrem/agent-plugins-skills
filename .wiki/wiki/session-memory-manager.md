---
concept: session-memory-manager
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-memory-manager/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.180179+00:00
cluster: plugin-code
content_hash: 642a6776535ef047
---

# Session Memory Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-memory-manager
description: >
  Trigger with "remember this", "update memory", "what should we record from this session", 
  "capture learnings", "write a session log", or when closing a session.
  Guides agents on managing memory hygiene across sessions, deciding 
  what to write to dated memory logs, what to promote to long-term memory.md, and when to archive.

  <example>
  User: I'm done for the day, can you write up a session log?
  Agent:
  <Bash>
  python3 context/kernel.py emit_event --agent os-memory-manager --type intent --action promote_memory
  python3 context/kernel.py state_update active_agent os-memory-manager
  </Bash>
  </example>

  <example>
  User: That's all, logging off now.
  Agent:
  <Bash>
  python3 context/kernel.py acquire_lock memory
  </Bash>
  </example>

  <example>
  
  User: How does the memory system work?
  Agent:
  <Read>
  ./references/architecture/context-folder-patterns.md
  </Read>
  
  </example>
allowed-tools: Bash, Read, Write
---

## Prerequisites

This skill requires the **Agentic OS to be initialized first**. It calls `context/kernel.py`, `context/memory.md`, and `context/.locks/` — files that only exist after running the `os-init` skill in your project.

If you have not yet initialized the OS, run:
```
os-init
```

---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Session Memory Manager

Manages the three tiers of agent memory in an Agentic OS environment.

## Memory Tiers

| Tier | File | Written By | When Loaded |
|------|------|-----------|-------------|
| Auto-memory | `MEMORY.md` | Claude automatically | Every session (Anthropic native) |
| Long-term facts | `context/memory.md` | You (curated) | @imported in CLAUDE.md |
| Session logs | `context/memory/YYYY-MM-DD.md` | Agent at session close | On demand |

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 0: Intent Emission (Event Bus)

Before taking any actions, you MUST publish your intent to the Event Bus.
Use the `Bash` tool to run:
`python3 context/kernel.py emit_event --agent os-memory-manager --type intent --action promote_memory`

### Phase 1: Acquire OS State and Lock

1. **Update OS State**: Run `python3 context/kernel.py state_update active_agent os-memory-manager`, `python3 context/kernel.py state_update mode memory-gc`, and `python3 context/kernel.py state_update memory_gc_due false`.
2. **Strict Lock Protocol**: Run `python3 context/kernel.py acquire_lock memory` using the `Bash` tool to acquire the lock. If it fails, abort. The kernel handles stale lock timeouts automatically.
3. **Capture What Happened**: Before writing memory files, ask the user to confirm the session scope:
- What was the main task or goal this session?
- Were any architectural decisions made? (if yes -> promote to `context/memory.md`)
- Were any bugs solved that were tricky? (if yes -> promote to `context/memory.md`)
- Were any skills updated or created? (if yes -> record in session log)
- Are there open items / next steps?

### Phase 2: Write the Dated Session Log

Write to `context/memory/YYYY-MM-DD.md`. Use today's date.

Use this template:

```markdown
# Session Log: YYYY-MM-DD

## Summary
[1-2 sentence summary of what was accomplished]

## Key Decisions
- [Decision 1 and its rationale]
- [Decision 2 and its rationale]

## Lessons Learned
- [Lesson or edge case discovered]

## Skills Updated
- [Skill name]: [what changed]

## Open Items
- [ ] [Next steps or follow-up tasks]
```

### Phase 3: Preserve Test Registry Artifacts

Before general promotion, handle test registry files specially:

1. **`context/memory/tests/registry.md`** — never archive, never skip. This is always L3.
   Verify it exists and the latest

*(content truncated)*

## See Also

- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[adr-manager-plugin]]
- [[acceptance-criteria-adr-manager]]
- [[identity-the-adr-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-memory-manager/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.180179+00:00
