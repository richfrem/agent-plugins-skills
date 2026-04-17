---
concept: plan-gap-fill-cleanup-attribution
source: plugin-code
source_file: exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.580904+00:00
cluster: before
content_hash: 35963bb51d7b9f07
---

# Plan: Gap-Fill, Cleanup & Attribution

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Plan: Gap-Fill, Cleanup & Attribution
**Plugin:** `exploration-cycle-plugin`
**Target agent:** Claude Sonnet 4.6 (GitHub Copilot)
**Date:** 2026-04-06
**Status:** Ready for execution

---

## Context

PR #209 (`feat/snr-upgrade`) was merged successfully. The infrastructure of the SMR upgrade
is in place (HARD-GATE, routing logic, SME language, Phase A/B/C gates, all evals/).

However, a post-merge audit identified four outstanding gaps:

1. **Three new skills referenced by agents do not exist** — `discovery-planning`,
   `visual-companion`, `subagent-driven-prototyping`
2. **`prototype-builder/SKILL.md` is still a stub** — 1 KiB, explicitly marked STUB
3. **`skills/deferred/` is structural garbage** — old nested orphan files, symlink stubs,
   and mis-placed agent files that belong elsewhere or should be deleted
4. **No attribution or license notice for `obra/superpowers`** — a direct architectural
   inspiration that requires proper open-source credit

---

## Working Directory

All work is done inside:
```
/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin/
```

Do NOT modify any files outside this directory.

---

## Task 1 — Create `skills/discovery-planning/SKILL.md`

**What it is:** The HARD-GATE skill. It is the first thing the orchestrator invokes when
an SME starts a new exploration session. It guides the SME through structured discovery
questions (one at a time, business language only) and produces an approved Discovery Plan
before any prototype can be built.

**Inspired by:** `obra/superpowers` `brainstorming` skill — the `<HARD-GATE>` pattern.
See attribution section below.

**Create the file:**
```
skills/discovery-planning/SKILL.md
skills/discovery-planning/evals/evals.json
```

### `SKILL.md` must contain:

**YAML frontmatter:**
```yaml
---
name: discovery-planning
description: >
  Guides an SME through a structured discovery session to produce an approved
  Discovery Plan before any prototype is built. Enforces the HARD-GATE: no prototype
  can be built until the SME has approved the plan. Trigger with "start a discovery
  session", "let's plan this out", "help me figure out what we're building", or
  "I have an idea I want to explore".
allowed-tools: Read, Write
---
```

**Core content the skill MUST implement:**

1. **Pre-Phase 0 (Silent Discovery):** Before speaking to the SME, silently check:
   - Does `exploration/session-brief.md` exist? If yes, read it for context.
   - Does `exploration/discovery-plans/` exist? If not, create it.

2. **Discovery Session Rules (enforce strictly):**
   - Ask ONE question at a time. Never ask multiple questions at once.
   - Use ONLY business language. Never say: scaffold, repo, branch, commit, worktree,
     phase, gate, spec, schema, iterate, invoke, dispatch, deploy.
   - Instead say: "Let me take a note of that", "I'll save this for us",
     "here's what I understood — does this look right?"

3. **Session flow (5 questions minimum, sequential):**
   - Q1: What problem are we trying to solve for the people we serve?
   - Q2: Who are the people involved — who uses this, who approves, who is affected?
   - Q3: What does success look like when this is working well?
   - Q4: What are the must-have requirements vs. nice-to-haves?
   - Q5: Are there any hard rules, constraints, or things we definitely cannot do?
   - After each answer: confirm back in plain language before moving to next question.

4. **Discovery Plan output:** After all questions answered, write
   `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md` with:
   - Problem statement (plain language)
   - Stakeholders
   - Success criteria
   - Must-have requirements
   - Constraints and rules
   - Open questions (if any)

5. **HARD-GATE approval:** Present the plan to the SME and ask:
   > "Here is the discovery plan we built together. Please review it.
   > When you're happy with it, reply **YES** to approve it and we'll move
   > to the next stage. If anything need

*(content truncated)*

## See Also

- [[pattern-action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[pattern-action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md`
- **Indexed:** 2026-04-17T06:42:09.580904+00:00
