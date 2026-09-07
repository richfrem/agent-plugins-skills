---
name: os-memory-manager
plugin: agent-agentic-os
description: >
  Trigger with "remember this", "update memory", "what should we record from this session",
  "capture learnings", "write a session log", or when closing a session. Guides agents on
  managing memory hygiene across sessions, deciding what to write to dated memory logs, what
  to promote to long-term memory.md, and when to archive.
allowed-tools: Bash, Read, Write
---

# Session Memory Manager

Manages the three tiers of agent memory in an Agentic OS environment.

Prerequisites, dependencies, and trigger examples are in `references/detailed-reference.md` —
this skill requires the Agentic OS to be initialized first (`os-init`).

## Memory Tiers

| Tier | File | Written By | When Loaded |
|------|------|-----------|-------------|
| Auto-memory | `MEMORY.md` | Claude automatically | Every session (Anthropic native) |
| Long-term facts | `context/memory.md` | You (curated) | @imported in CLAUDE.md |
| Session logs | `context/memory/YYYY-MM-DD.md` | Agent at session close | On demand |

## Execution Flow

Execute these phases in order. Do not skip phases. Full detail (templates, dedup protocol,
size-limit enforcement, survey questions) for each phase is in `references/detailed-reference.md`.

### Phase 0: Intent Emission (Event Bus)

Before taking any actions, publish your intent:
`python context/kernel.py emit_event --agent os-memory-manager --type intent --action promote_memory`

### Phase 1: Acquire OS State and Lock

1. Update OS state: `active_agent os-memory-manager`, `mode memory-gc`, `memory_gc_due false`.
2. Acquire the lock: `python context/kernel.py acquire_lock memory`. If it fails, abort.
3. Ask the user to confirm session scope: main task/goal, architectural decisions, tricky bugs
   solved, skills updated, open next steps.

### Phase 2: Write the Dated Session Log

Write to `context/memory/YYYY-MM-DD.md` using today's date, per the template in
`references/detailed-reference.md`.

### Phase 3: Preserve Test Registry Artifacts

Never archive/skip `context/memory/tests/registry.md`; preserve closed scenario files for 90
days before archiving; promote confirmed test findings not already in `context/memory.md`; add
"DO NOT RE-TEST" entries for falsified hypotheses. Full protocol in `references/detailed-reference.md`.

### Phase 4: Promote to Long-Term Memory

Apply the promote/skip decision (ephemeral state and open tasks → skip; system facts, commands,
style rules, architectural decisions → promote). Before promoting, read `context/memory.md` and
the last 10 `MEMORY.md` entries, run dedup/conflict detection, and follow the Safe Write Protocol
(git stash + diff preview + post-write verification). Full dedup/conflict/ID protocol and both
fact-format options are in `references/detailed-reference.md`.

### Phase 4b: Enforce Memory.md Size Limits

Check `wc -c context/memory.md`; if over 50000 bytes, merge/prune redundant facts or archive the
oldest ~200 lines to `context/memory/archive/YYYY-MM.md`. Full steps in `references/detailed-reference.md`.

### Phase 5: Self-Assessment Survey (MANDATORY)

Before releasing the lock, complete the Post-Run Self-Assessment Survey
(`references/memory/post_run_survey.md`) and save to
`context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-memory-manager.md`. Emit
`--type learning --action survey_completed` on completion. Full survey questions in
`references/detailed-reference.md`.

### Phase 6: Confirm with User and Release Lock

Show a completion summary, emit the success result event, then run
`python context/kernel.py release_lock memory`. Full format in `references/detailed-reference.md`.

## Next Actions

- To understand the full memory layer architecture -> read `os-guide` skill
- To set up CLAUDE.md @imports for memory -> read `references/architecture/claude-md-hierarchy.md` in `os-guide`
