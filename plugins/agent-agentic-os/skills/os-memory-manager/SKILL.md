---
name: os-memory-manager
description: >
  Trigger with "remember this", "update memory", "what should we record from this session", 
  "capture learnings", "write a session log", or when closing a session and summarizing 
  what was accomplished. Guides agents on managing memory hygiene across sessions, deciding 
  what to write to dated memory logs, what to promote to long-term memory.md, and when to archive.

  <example>
  <commentary>User requested explicit session close.</commentary>
  User: I'm done for the day, can you write up a session log?
  Agent:
  <Bash>
  python3 context/kernel.py emit_event --agent os-memory-manager --type intent --action promote_memory
  python3 context/kernel.py state_update active_agent os-memory-manager
  </Bash>
  </example>

  <example>
  <commentary>User implicitly closed the session.</commentary>
  User: That's all, logging off now.
  Agent:
  <Bash>
  python3 context/kernel.py acquire_lock memory
  </Bash>
  </example>

  <example>
  <commentary>User is mid-task and asks a question. Do not invoke.</commentary>
  User: How does the memory system work?
  Agent:
  <Read>
  ./references/context-folder-patterns.md
  </Read>
  <commentary>Reads documentation instead of trying to lock the memory manager.</commentary>
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
   Verify it exists and the latest cycle row is CLOSED before proceeding.
2. **Closed scenario files** (`context/memory/tests/[CYCLE_ID]_*.md`) — preserve in place
   for 90 days, then move to `context/memory/tests/archive/`. Never delete.
3. **Confirmed findings from test scenarios** — if the scenario file has a "Confirmed"
   hypothesis, check whether the finding is already in `context/memory.md`. If not,
   promote it as a fact with the cycle ID as evidence source.
4. **Falsified hypotheses** — check `context/memory.md` for a "DO NOT RE-TEST" entry.
   If missing, add it now to prevent future wasted cycles.

### Phase 4: Promote to Long-Term Memory

For each item in the session log, apply the **promote/skip decision**:

- Ephemeral state (e.g., "Tried running tests, they failed") -> **SKIP** (Archive with log)
- Open tasks (e.g., "Need to fix the auth module") -> **SKIP** (Leave in session log for tomorrow)
- System facts, new commands, style rules, or architectural decisions -> **PROMOTE**

If a fact is selected for promotion, you **MUST first read `context/memory.md` AND the last 10 entries of `MEMORY.md`**:
1. Search for the topic or conceptually similar topics.
2. **THE DEMENTIA DEFENSE**: If the topic, or *any* overlapping topic exists, you must flag it as a potential **Conflict** even if the wording differs. LLMs are bad at detecting semantic equivalence. Err toward false positives. 
3. **Deduplication IDs**: Assign a sequential unique ID based on the current highest ID in `context/memory.md` (e.g., if the highest is `[#042]`, assign `[#043]`) to prevent syntactic duplication. Ensure this ID prefix `[#ID]` is stored with the fact. Let the user know the generated ID. Use `grep -c "^\[#"` via `Bash` if you need help finding the count.
4. **Cross-Skill Conflict Detection**: Run `grep -ri "[Fact Keywords]" ./skills/` using the `Bash` tool to ensure promoted memory doesn't break or contradict existing procedural skills.
5. **Semantic Deduplication**: If ANY semantic overlap exists, explicitly output `<CONFLICT>` before any Write. Ask the user if the new proposed fact *supersedes* the existing fact (to replace the old hash) or if it's a conflict to resolve. If superseding, you MUST output a `<SUPERSEDE old_id=NNN>` marker (e.g., `<SUPERSEDE old_id=042>`) so the next learning loop can locate and prune the old fact. Never silently overwrite — the marker is required for audit trail continuity.
6. **Safe Write Protocol**: Wrap every `Write` in a `git stash` + diff preview (use `Bash` tool). If the user rejects the preview, run `git stash pop` to rollback.
7. If there is absolutely no conflict (or the user resolves it), append the numbered/hashed fact cleanly.
8. **Post-Write Verification**: After writing, use the `Read` tool on the exact file. If the expected diff is not present, output `<WRITE_FAILED>` and run `git stash pop`.

Format facts in `context/memory.md` like this (choose one format and stick to it):

**Option A — Markdown (default, human-readable):**
```markdown
## [YYYY-MM-DD] [Topic]
[The fact, decision, or convention in 1-3 sentences]
```

**Option B — Structured JSON entries (recommended for projects with high fact volume or automated tooling):**
```json
{"id": "build_cmd_001", "type": "command", "topic": "build", "value": "npm run build", "source": "session-2026-03-19", "supersedes": null}
```
Append one JSON object per line to a `context/memory.jsonl` file. Reference it from `context/memory.md` with a note: `<!-- structured facts in context/memory.jsonl -->`. Benefits: unambiguous deduplication by `id`, machine-queryable, easier `<SUPERSEDE>` enforcement.

### Phase 4: Enforce Memory.md Size Limits

You MUST verify the size of the curated memory file to prevent context degradation.
1. Run `wc -c context/memory.md` using the `Bash` tool to check the exact byte size.
   (Line count is unreliable on Windows due to CRLF line endings; byte size is platform-neutral.)
2. If the byte size is strictly greater than 50000 bytes, you must condense it:
   - **Merge & Prune**: Look for redundant, outdated, or supersedable facts and merge them.
   - **Archive**: If still too large, create the archive directory: `mkdir -p context/memory/archive/`
   - Move the oldest (top-most) ~200 lines to `context/memory/archive/YYYY-MM.md` using `Write`.
   - Remove these archived lines from `context/memory.md` using `Write`.
   - Ensure an archive reference log (e.g., `<!-- Archived data -> context/memory/archive/ -->`) exists at the top of `context/memory.md`.

### Phase 5: Self-Assessment Survey (MANDATORY)

Before releasing the lock, complete the Post-Run Self-Assessment Survey
(`references/post_run_survey.md`). The memory manager must reflect on its own runs
to improve the quality of what gets promoted and what gets skipped.

**Count-Based Signals**: How many times were you uncertain whether to promote or skip?
How many potential conflicts did you flag? How many dedup IDs did you assign?

**Qualitative Friction**:
1. Which promotion decision felt most uncertain?
2. Was any fact promoted that probably should have been skipped (or vice versa)?
3. Which part of the deduplication protocol felt most ambiguous?
4. What one change to the session log template would improve the next run?

**Improvement Recommendation**: What one change to this skill should be tested next run?

Save to: `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-memory-manager.md`

Emit survey completion:
```bash
python3 context/kernel.py emit_event --agent os-memory-manager \
  --type learning --action survey_completed \
  --summary "retrospectives/survey_[DATE]_[TIME]_os-memory-manager.md"
```

### Phase 6: Confirm with User and Release Lock

After writing and survey saved, show a summary:
```
[x] Session log written: context/memory/YYYY-MM-DD.md
[x] Promoted N facts to context/memory.md
[x] Survey saved: retrospectives/survey_[DATE]_[TIME]_os-memory-manager.md
[ ] No archive needed (current count: N facts)
```

**Event Bus Publish**: Use `Bash` to emit your success result:
`python3 context/kernel.py emit_event --agent os-memory-manager --type result --action promote_memory --status success`

Finally, **Lock Release Protocol**: Execute `python3 context/kernel.py release_lock memory` to release the acquired loop lock.

## Next Actions

- To understand the full memory layer architecture -> read `os-guide` skill
- To set up CLAUDE.md @imports for memory -> read `references/claude-md-hierarchy.md` in `os-guide`
