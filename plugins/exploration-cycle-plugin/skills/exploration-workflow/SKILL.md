---
name: exploration-workflow
description: >
  SME-facing orchestrator for the Business Exploration Loop. Supports 4 session
  types (greenfield, brownfield, discovery-only, spike) with adaptive phase
  selection. Manages state via exploration-dashboard.md, enforces phase gates,
  and routes to child skills in sequence. Phases can be skipped based on session
  type. Single canonical entry point — invoke at the start of any exploration
  session or to resume an in-progress session.
  Trigger phrases: "start an exploration", "let's explore this idea",
  "resume my exploration", "where did we leave off", "start discovery".
allowed-tools: Read, Write
---

<example>
<commentary>SME starts a brand-new exploration session from scratch.</commentary>
user: "Let's explore this idea I have for a staff scheduling tool."
agent: [invokes exploration-workflow, bootstraps dashboard, asks for session type, begins Phase 1 discovery-planning]
</example>

<example>
<commentary>SME resumes an in-progress session after prior work.</commentary>
user: "Where did we leave off with the customer portal exploration?"
agent: [invokes exploration-workflow, reads dashboard, presents status summary, routes to active phase]
</example>

<example>
<commentary>Negative — user wants to start a new discovery plan only, not the full workflow.</commentary>
user: "Run a discovery planning session for my onboarding redesign."
agent: [invokes discovery-planning directly, NOT exploration-workflow]
</example>

# Exploration Workflow — SME Orchestrator

This skill is the single canonical entry point for the Business Exploration Loop. It manages all session state via `exploration-dashboard.md`, enforces phase gates, and routes work to the correct child skill at each phase. The SME never needs to invoke any other skill directly.

## Session Types

The workflow adapts to four session types, each with different phase requirements:

| Type | When to use | Active Phases |
|------|-------------|---------------|
| **Greenfield** | Building a new app or system from scratch | All 4 phases |
| **Brownfield** | Adding a feature to an existing codebase | Phase 1 required, Phases 2 & 4 optional, Phase 3 builds into real codebase |
| **Analysis/Docs** | Non-software output: requirements, process maps, legacy code analysis, policy, strategy, workflow design | Phases 1 & 4 required, Phase 2 optional (structure not layout), Phase 3 skipped |
| **Spike** | Investigating a question or technology | Phase 1 required (may repeat), all others flexible |

---

## Execution Disciplines (powered by orba/superpowers)

> **Required dependency:** The `orba/superpowers` plugin MUST be installed alongside this
> plugin. See the plugin README for installation instructions.

When Phase 3 is active, read `references/phase3-execution-discipline.md` for the full
execution discipline protocol (superpowers availability check, worktree isolation,
build delegation, TDD validation, branch finishing).

**Summary:** The orchestrator sets up isolation (worktrees), then delegates all build
work to `subagent-driven-prototyping`. That skill owns component decomposition, dispatch,
two-stage review, and TDD. When it signals complete, the orchestrator invokes
`finishing-a-development-branch` for merge/PR options.

---

## Block 0 — Pre-Flight & Dispatch Strategy (ask once during bootstrap)

> Dispatch strategy details: `references/dispatch-strategies.md`
> Environment check: `references/environment-check.md`

**Run the environment check silently first** (see `references/environment-check.md`). Only surface results if something is missing or needs a fallback. Do not mention the check to the SME unless action is needed.

**For Analysis/Docs sessions:** Skip the dispatch strategy question. Default to `direct`.

### Token Efficiency — Claude-only sessions

If the SME has no Copilot or Gemini CLI (strategy = `claude-subagents` or `direct`), apply these practices throughout:
- **Simple capture passes** (template filling, document extraction, format conversion): use the `Agent` tool with `model: "haiku"` (currently `haiku-4.5`) to keep the main context light.
- **Q&A clarification**: batch 3–5 questions, dispatch `haiku` to collect structured answers, write to `exploration/captures/clarifications-[topic].md`, read back once. Never run clarification loops inline in the main orchestrator turn.
- **Compact before topic switches**: if the session moves from one major phase to the next and earlier content is no longer needed, use `/compact` to reduce carry-forward context debt.
- Full details and Claude Code dispatch examples: `references/dispatch-strategies.md`.

For all other session types, ask the SME after session type selection:

> "One more thing — how should I handle the heavy lifting when we get to building?
>
> 1. **I have GitHub Copilot Pro** — I'll use Copilot CLI. Simple tasks use `gpt-5-mini` (free). Complex tasks use `claude-sonnet-4.6` or `claude-opus-4.6` (1 premium request — all related tasks batched into one dense call).
> 2. **I have Gemini CLI** — Simple tasks use `gemini-3.1-flash-lite-preview` (cheap). Complex tasks use `gemini-3.1-pro-preview`.
> 3. **Claude only** — I'll use Claude sub-agents. Simple tasks use `haiku-4.5` (cheapest). Complex tasks use `sonnet`.
> 4. **I'll handle it myself** — Everything happens directly in this session."

Record the choice in the dashboard as `**Dispatch Strategy:**` (`copilot-cli`, `claude-subagents`, or `direct`).

**Fallback:** If the chosen strategy becomes unavailable during Phase 3, silently fall
back to `direct` mode and inform the SME.

---

## Early Exit — Kill Session

At any point during the exploration, if the SME says something like "this isn't going to
work", "kill it", "let's stop", or "the idea is bad", the workflow should exit cleanly:

1. Ask: *"Got it — should I close the session? I'll save what we learned so it's not lost."*
2. On confirmation, write a brief `exploration/handoffs/handoff-package.md` with:
   - What was explored
   - What was learned
   - Why the session was stopped
   - A `## Risk Assessment` section containing:
     `**Outcome:** Throwaway (Fail Fast)` / `**Reason:** [one sentence from SME]` /
     `**Delivery Path:** Session closed — learning preserved.`
3. Mark all remaining phases as `[~]` (skipped) with note: `(Session killed — fail fast)`
4. Update `**Status:**` to `Complete`
5. Announce: *"Session closed. The learning is saved in `exploration/handoffs/`. Failing fast and cheap is a valid outcome — you saved weeks of wasted effort."*

This is the "Throwaway Prototype" outcome from the TierGate — it can happen at any phase,
not just at handoff. The earlier it happens, the more valuable it is.

---

## Block 1 — Bootstrap (run silently before speaking to the SME)

1. Check for `exploration/exploration-dashboard.md`.
2. **If the file does NOT exist:**
   - Create the `exploration/` directory if it does not already exist.
   - **Beat 1 — Name and goal:** Ask:
     > "What are we exploring today? Give it a short name so we can track it — and in a sentence or two, what are you hoping to achieve or solve?"
   - When the SME responds, immediately write a provisional dashboard with `**Session:**` set and `**Session Type:** TBD`. This anchors the session name before classification.
   - **Beat 2 — Session type:** Using the Scenario Routing Guide below, suggest a type with a one-sentence rationale:
     > "That sounds like [Type X] — [why]. Does that fit, or would you describe it differently?"
   - If the SME confirms: proceed with that type.
   - If the SME corrects or says "not quite": take their word for it. Always defer to SME judgment.
   - If the SME says "I'm not sure" or "you tell me": present the **full type menu** (see below) with examples.
   - Update `**Session Type:**` in the dashboard to the confirmed type.
   - **Immediately pre-mark non-applicable phases as `- [~]`** based on the confirmed session type. Use the Active Phases table in the Session Types section above to determine which phases to skip. Add a parenthetical reason: `(Skipped — [reason])`. Do this before finalizing the dashboard — the SME should never see a phase as "upcoming" if this session type will never use it.
   - Write the final dashboard, then proceed to Block 3.
3. **If the file EXISTS:** Proceed to Block 2.

---

### Scenario Routing Guide (for agent use — do NOT recite to SME)

Match on **intent**, not keywords. When uncertain, default to the type with more phases (easier to skip phases than to add them back).

| What the SME describes | Suggested type | Key signal |
|---|---|---|
| Net-new app, portal, tool, system from scratch | Type 1 (Greenfield) | Nothing exists yet |
| New website (product site, marketing site, customer portal) | Type 1 (Greenfield) | Treat as greenfield even if using a CMS |
| Automated workflow, approval bot, notification system, integration | Type 1 (Greenfield) | New software, but ask: "Is the current manual process documented?" — if not, open with Analysis/Docs first |
| Add a feature or fix something in an existing app/codebase | Type 2 (Brownfield — feature addition) | Working codebase exists |
| Understand, document, or analyse an existing/legacy system | Type 2 (Brownfield — legacy analysis) | See Legacy Analysis sub-type below |
| Modernise, replatform, or migrate a legacy system | Type 2 (Brownfield — legacy analysis) → handoff to engineering | Start with analysis to understand what exists before planning the rebuild |
| Fix a broken business process, improve a workflow | Type 3 (Analysis/Docs — process) — but run Intervention Check first | Often NOT a software problem |
| Requirements gathering or documenting for an upcoming project | Type 3 (Analysis/Docs — requirements) | Deliverable is documents |
| Strategic planning, market entry, go-to-market, business decision | Type 3 (Analysis/Docs — strategic) | No code output |
| Policy, compliance, regulatory, risk assessment | Type 3 (Analysis/Docs — risk/compliance) | Deliverable is policy or risk doc |
| Should we build vs. buy? What are our options? | Type 4 (Spike) | Decision support, may not lead to building |
| I'm not sure if we even need software | Type 4 (Spike) or start Phase 1 directly — the Intervention Check will clarify | Do not force a type prematurely |
| Research a technology, validate a hypothesis | Type 4 (Spike) | Exploratory, outcome open |

**"Not sure if software is the answer" path:**
> "That's actually the most important question — let's not assume software is the answer yet. Let's start with Phase 1 and figure out what kind of solution actually fits. I'll ask a specific question about that during our planning conversation."
Use Type 4 (Spike). The Intervention Check in Phase 1 will resolve this cleanly.

---

### Session Type Templates

**Type 1 — Greenfield (new app, system, or website):**
All 4 phases enabled.

Phase notes:
- Phase 2 (Visual Blueprinting): always run for software and websites. For websites: present page structure and layout options, not just UI widgets.
- Phase 3: builds a working prototype. For websites: focus on content structure, navigation, and one representative page before building all pages.
- Phase 4: required — produces handoff package with risk assessment.

**Type 2 — Brownfield:**
Two distinct sub-types with different phase configurations:

*Sub-type A — Feature addition or improvement:*
- Phase 1: enabled
- Phase 2: optional — ask: *"Does this feature need a layout discussion, or is the design straightforward enough to skip?"*
- Phase 3: enabled — builds into the existing codebase directly (not a throwaway prototype)
- Phase 4: optional — ask: *"Are you handing this off to someone else, or building it yourself?"*

*Sub-type B — Legacy analysis / modernisation / replatforming:*
- Phase 1: enabled — problem framing focuses on "what does the current system do?" rather than "what do we want to build?"
- Phase 2: optional — use for architecture diagrams or migration maps if helpful
- Phase 3: **disabled** — this is an analysis session, not a build session. Output is documentation and a modernisation plan.
- Phase 4: enabled and required — the handoff IS the deliverable, typically a modernisation spec for a formal engineering team.

Record the sub-type in the dashboard under `**Session Type:**` (e.g., `Brownfield — legacy analysis`).

**Type 3 — Analysis or documentation:**
Phase 1: enabled.
Phase 2: optional — reframed as **Structure Mapping** (not "Visual Blueprinting"). Offer it proactively: *"Before we start capturing, would it help to sketch out what the final document should look like? I can show you a few structure options."* If yes, invoke `visual-companion` in document-structure mode (process flow diagrams, document outlines, decision trees, swimlanes). Output goes to `exploration/captures/document-structure.md`.
Phase 3: **disabled**.
Phase 4: enabled — the handoff IS the primary output.

Sub-types (record in dashboard):
- **Process**: Fix or improve a business workflow. Deliverable: process documentation + change recommendations.
- **Requirements**: Capture requirements for an upcoming project. Deliverable: BRD / user stories / acceptance criteria.
- **Strategic**: Plans, decisions, market analysis. Deliverable: strategic recommendation document.
- **Risk/Compliance**: Policy, regulatory, or security requirements. Deliverable: risk assessment or policy document.
- **Legacy analysis**: Document an existing system from the outside (no code access). Deliverable: system analysis report.

Note: for **Process** sub-type, flag to discovery-planning that the Intervention Check is especially important — this is the scenario most likely to reveal that software is NOT the right answer.

**Type 4 — Spike or investigation:**
Phase 1: enabled, may repeat.
Phases 2–4: flexible — the SME decides as the investigation unfolds.
Use when the outcome is unclear, when decision support is needed, or when "I'm not sure if we need software."

For skipped phases, mark them `- [~]` in the dashboard and add a note: `(Skipped — [reason])`.

---

## Block 2 — Read State (run silently)

1. Read `exploration/exploration-dashboard.md`.
2. **Check session status first:** If the dashboard contains `**Status:** Complete`, skip directly
   to the Completion Block. The session is already finished.
3. Identify the **active phase** using these explicit parsing rules:
   - `- [x]` or `- [X]` (case-insensitive) → phase is **complete**
   - `- [~]` → phase is **intentionally skipped** (treat as complete for routing purposes, but do not verify outcome files)
   - `- [ ]` (exactly one space between brackets) → phase is **incomplete**
   - The **active phase** is the first incomplete phase in the numbered list (skipping over `[~]` phases).
   - **Malformed checkboxes** (e.g., `-[x]` with no leading space, `* [x]` with asterisk,
     `–[ ]` with an em-dash) must NOT be silently mis-routed. If you encounter one, pause
     and tell the user:
     > "The session dashboard has a formatting issue on one of the phase checkboxes.
     > Let me show you so we can quickly confirm where we are."
     Display the raw affected line(s) and ask: "Is this phase complete or still in progress?"
     Correct the checkbox before continuing.
4. For every complete phase (excluding skipped `[~]` phases), verify that its listed Outcome file exists on disk.
   - If an Outcome file is missing for a completed phase, stop and say:
     > "It looks like [Phase N] was marked complete but I can't find the expected output
     > file at [path]. Let's take a quick look before continuing."
   - Do not advance to Block 3 until this is resolved.
5. Proceed to Block 3.

---

## Block 3 — Orientation Summary (always shown to the SME)

Present a brief, friendly status message based on the dashboard state.

**For a brand-new session (just bootstrapped):**
> "Great — we're all set up. We'll work through [N active phases] together, starting with Problem Framing.
> Ready to begin?"

If any phases were skipped during bootstrap, mention it naturally:
> "We've skipped [Phase N] since [reason]. If that changes, we can always add it back."

**For a mid-session resume (at least one phase complete):**
> "Welcome back! Here's where we are:
> [List each phase with ✅ if `[x]` complete, ⏭️ if `[~]` skipped, or 🔵 if it is the active phase]
>
> Ready to pick up where we left off with [active phase name]?"

Wait for a soft confirmation before proceeding. Any clear affirmation counts: "Yes", "Let's go", "Go ahead", "Ready", "Sure". Do not proceed until received.

---

## Block 4 — Phase Routing

Identify the active phase (first incomplete phase that is not skipped).

**Skipped phases** (`- [~]`) are not active — skip over them when finding the next phase to route to.

Route to the child skill for the active phase:

| Active Phase | Child Skill to Invoke |
|---|---|
| Phase 1 — Problem Framing | `discovery-planning` |
| Phase 2 — Visual Blueprinting | `visual-companion` |
| Phase 3 — Build | `subagent-driven-prototyping` |
| Phase 4 — Handoff & Specs (Auto-runs User Stories & Specs) | `exploration-handoff` |
| All phases complete or skipped | → Completion Block |

When invoking a child skill, pass this structured context block — do NOT bury it in prose:

```
## Session Context (from orchestrator — read and act on before proceeding)
- Session type: [exact value from **Session Type:** in dashboard]
- Active phase: Phase [N] — [phase name]
- Discovery Plan: [path to most recent discovery-plan-*.md, or "not yet written"]
- Dispatch strategy: [value from **Dispatch Strategy:** in dashboard]
- Return signal: When this phase is complete, announce "PHASE [N] COMPLETE" then invoke the exploration-workflow skill to continue.
```

Child skills must read `Session type` and adapt their question tracks and outputs accordingly before doing anything else.

---

## Mid-Session Revision Protocol

If the SME asks to go back and change something in a completed phase (e.g., "Can we revisit the discovery plan?", "I want to change who the users are"), follow this protocol:

1. **Identify what changed.** Ask one clarifying question: *"What specifically needs to change — the problem statement, the users, the constraints, or something else?"*

2. **Assess downstream impact.** Before reopening anything, tell the SME what would need to be redone:
   > "If we change [X], it affects [Y]. Here's what we'd need to redo: [list affected phases/outputs]."

3. **Get confirmation.** *"Should I go ahead and reopen Phase [N], knowing that [downstream impact]?"* Wait for a clear yes.

4. **On confirmation:**
   - In the dashboard, change the affected phase's `- [x]` back to `- [↩]` (marks it as revised, not just incomplete).
   - Clear the Outcome file path note for that phase (set to `TBD`).
   - Re-invoke the child skill with the existing context as starting point, not a blank restart. Pass the prior output as: *"Here's what we had — the SME wants to change [specific thing]. Update accordingly."*

5. **After revision is approved**, restore the dashboard to `- [x]`, update the Outcome file path, and log the revision in the Session Log with a note: `(revised — [one-sentence reason)`.

**The `↩` marker** signals that this phase was completed, revised, and re-completed. It is distinct from `[x]` (complete), `[ ]` (not started), and `[~]` (skipped). If your dashboard template does not include this marker, add it manually.

---

## Block 5 — HARD-GATE (phase completion approval)

`<HARD-GATE>` — This block runs when the child skill signals its phase is done.

1. Present a plain-language summary of what was produced (1–3 bullets).
2. Show the SME the Outcome file path.
3. Ask for explicit approval:
   > "Does everything look right? If you're happy with it, just say the word and I'll mark Phase [N] complete."
4. **Do NOT update the dashboard until the SME gives a clear affirmation.** Accepted responses: "Yes", "Looks good", "Approved", "Go ahead", "That's right", or any equivalent clear confirmation.
5. If the SME requests changes: return control to the child skill, apply changes, then re-present for approval. Repeat until satisfied.

---

## Block 6 — Dashboard Write (runs after HARD-GATE approval)

Using the Write tool, update `exploration/exploration-dashboard.md`:
1. Change `- [ ]` to `- [x]` for the now-completed phase.
2. Update `**Current Phase:**` to the name of the next phase, or to `Complete` if Phase 4 was just finished.
3. Update `**Status:**` to `In Progress` (or `Complete` if all phases are done).
4. In the Session Log table, fill in the completed phase row with today's date and a one-sentence note describing what was produced.

Then loop back to **Block 3** to orient the SME for the next phase.

---

## Gotchas

- **Malformed checkbox silently mis-routes**: A `- [x]` with no leading space or an asterisk instead of dash will match the wrong phase. Block 2 now explicitly stops on malformed checkboxes — don't skip that check.
- **Skipping dispatch strategy question for Analysis/Docs sessions**: Block 0 correctly skips the dispatch question for Analysis/Docs, but if the session type pivots mid-session (Q4 Intervention Check reveals a software problem was actually a process problem), the dispatch strategy default (`direct`) may not be what the SME wants. Re-ask if the session type changes.
- **Phase routing after kill-session**: Early-exit writes `[~]` to remaining phases but if the write is incomplete (crash, context loss), Block 2 may re-route to a killed phase. Always confirm `**Status:** Complete` is written before announcing completion.
- **Mid-session revision back-pointer**: When a phase is reopened with `- [↩]`, the Outcome file path is cleared to TBD. If the SME later asks "where are my files", they may not find them. Always log the prior file path in the Session Log revision note even when clearing the Outcome field.
- **Tier message mismatch**: If Phase 4 is skipped but a prototype exists, the Completion Block may default to "Tier 3" message. Read the dashboard `**Session Type:**` field first — brownfield self-build completions use the brownfield message, not the tier message.

## Completion Block

When all phases are either marked `[x]` (complete) or `[~]` (skipped):

**Spike re-entry check:** For spike sessions, before declaring completion, ask the SME:
*"You've completed this round of investigation. Would you like to loop back to Phase 1 with what you've learned, or are we done?"*

If they want to loop:
1. Archive the current discovery plan: rename `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md` to `discovery-plan-YYYY-MM-DD-v[N].md` where N is the iteration number.
2. Clear the Phase 1 Outcome file path in the dashboard (set to `TBD`).
3. Reset Phase 1 to `- [ ]` in the dashboard.
4. Add a note in the Session Log: `(Spike re-entry — iteration [N] — prior plan archived as [filename])`.
5. Return to Block 3.

If they're done, proceed with completion below.

> "Congratulations — your Exploration Session is complete!
> All phases are finished and your outputs are ready.
> Your exploration outputs are in the `exploration/` folder."

**If Phase 4 was skipped** (brownfield self-build):
> "Since you built this directly, you're already in Engineering mode.
> Your build documentation is at `exploration/prototype/README.md`."

**If Phase 4 produced a handoff package**, the completion message depends on the
**Risk Tier** and **session type** recorded in the handoff:

| Tier | Completion Message |
|---|---|
| **Tier 1 (Low Risk)** | "Your handoff assessed this as low risk. You're clear to deploy directly — no formal engineering cycle needed. Your build documentation and handoff are in `exploration/`." |
| **Tier 2 (Moderate Risk)** | "Your handoff assessed this as moderate risk. Before deploying, this needs a security review and red team assessment. Hand the file at `exploration/handoffs/handoff-package.md` to your security team." |
| **Tier 3 (High Risk)** | "Your handoff assessed this as high risk. The next step is a formal engineering cycle. Hand the package at `exploration/handoffs/handoff-package.md` to your development team — it includes the requirements, user stories, business rules, prototype notes, and risk assessment they need to begin a spec-driven build." |
| **Non-software outcome** | "The exploration concluded that the right solution here isn't a new system — it's a [process change / policy update / strategic recommendation]. Your recommendation document is at `exploration/handoffs/handoff-package.md`. Hand it to the team or person responsible for [implementing the change]." |
| **Legacy analysis complete** | "The analysis is done. Your modernisation plan is at `exploration/handoffs/handoff-package.md`. This is the input your engineering team needs to scope the replatforming project — hand it to them to begin formal planning." |
| **Throwaway / Fail Fast** | "The exploration revealed this idea isn't viable — and that's a valuable outcome. You discovered this at near-zero cost instead of months into a build. The session artifacts are preserved in `exploration/` for reference." |

If no tier is recorded in the handoff, default to the Tier 3 message (safest path).

**Non-software and legacy analysis sessions:** check the session type in the dashboard. If `**Session Type:**` contains "process", "strategic", "risk/compliance", or "legacy analysis", use the matching non-software or legacy analysis completion message above, regardless of tier.

Update `**Status:**` to `Complete` in the dashboard.
