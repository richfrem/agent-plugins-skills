---
concept: architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers
source: plugin-code
source_file: exploration-cycle-plugin/skills/discovery-planning/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.983351+00:00
cluster: session
content_hash: 05e23f7383300eee
---

# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: discovery-planning
description: >
  Guides a Subject Matter Expert through a structured discovery session to create and approve a Discovery Plan before any building begins. This is the HARD-GATE brainstorming skill — no prototype can be built until the SME explicitly approves the plan. Trigger phrases: "start a discovery session", "let's plan this out", "help me figure out what we're building", "I have an idea I want to explore", "let's start from scratch"
allowed-tools: Read, Write
---
# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers


## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:** Read it silently and check the `**Status:**` line.
  - If `**Status:** Complete` → the prior session has ended. Proceed with this skill's
    standalone flow as normal.
  - Otherwise → an active session is in progress. Stop immediately. Do not continue here.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    **Return to the orchestrator.** Use the Skill tool: `skill: "exploration-workflow"`.
    After invoking it, stop generating output from this skill — do not continue below.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

<example>
<commentary>Demonstrates a cold start where the user opens a brand new session with no prior context.</commentary>
User: I have an idea I want to explore
Agent: Welcomes the SME warmly, silently checks for any existing session brief, then asks the first discovery question: "What problem are we trying to solve for the people we serve?"
</example>

<example>
<commentary>Demonstrates re-entry after a previously incomplete attempt — the skill picks up existing context and resumes.</commentary>
User: Let's plan this out, I tried before but it didn't go anywhere
Agent: Silently reads the existing session brief if present, acknowledges the SME's prior attempt in plain language, and picks up the discovery questions from where they left off — or starts fresh if no useful context exists.
</example>

<example>
<commentary>Demonstrates the HARD-GATE redirect when the user tries to skip planning and go straight to building.</commentary>
User: Can we just skip the planning and build it?
Agent: Politely but firmly redirects: "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions." Returns to the next unanswered discovery question.
</example>

## HARD-GATE Rule

Do NOT write any prototype files. Do NOT hand off to prototype-builder or any other skill. Do NOT proceed beyond this skill until the SME replies **YES** (or an equivalent clear affirmation) approving the Discovery Plan.

If the SME asks to "just build it" or "skip to the prototype", respond:
> "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions."

Then return to the next unanswered discovery question. Never skip the gate.

## Pre-Phase 0: Silent Discovery

Before speaking to the SME, silently (without announcing to the user):

1. Check if `exploration/session-brief.md` exists. If it does, read it for any useful context about the problem domain or stakeholders.
2. Create the directory `exploration/discovery-plans/` if it does not already exist.

Do not mention these steps to the SME.

## Session Type Fork

**Read the session type before asking any questions.** Check in this order:
1. The `## Session Context` block passed by the orchestrator (look for `Session type:`)
2. `**Session Type:**` field in `exploration/exploration-dashboard.md`
3. If neither is available, ask: *"What kind of session is this — are we building something new, improving an existing system, documenting a process, or investigating a question?"*

Route to the correct track

*(content truncated)*

## See Also

- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[domain-patterns]]
- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[domain-patterns-routing-skills]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/discovery-planning/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.983351+00:00
