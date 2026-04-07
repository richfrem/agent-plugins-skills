---
name: exploration-workflow
description: >
  SME-facing orchestrator for the 4-phase Business Exploration Loop. Manages
  state via exploration-dashboard.md, enforces phase gates, and routes to
  child skills in sequence. Single canonical entry point — invoke at the start
  of any exploration session or to resume an in-progress session.
  Trigger phrases: "start an exploration", "let's explore this idea",
  "resume my exploration", "where did we leave off", "start discovery".
allowed-tools: Read, Write
---

# Exploration Workflow — SME Orchestrator

This skill is the single canonical entry point for the Business Exploration Loop. It manages all session state via `exploration-dashboard.md`, enforces phase gates, and routes work to the correct child skill at each phase. The SME never needs to invoke any other skill directly.

---

## Block 1 — Bootstrap (run silently before speaking to the SME)

1. Check for `exploration/exploration-dashboard.md`.
2. **If the file does NOT exist:**
   - Create the `exploration/` directory if it does not already exist.
   - Scaffold a new dashboard by copying the template structure from `assets/templates/exploration-dashboard.md` to `exploration/exploration-dashboard.md`.
   - Ask the SME: *"What are we exploring today? Give it a short name so we can track it."*
   - Replace `[to be filled in]` in the `**Session:**` field with their answer.
   - Write the updated file, then proceed to Block 3.
3. **If the file EXISTS:** Proceed to Block 2.

---

## Block 2 — Read State (run silently)

1. Read `exploration/exploration-dashboard.md`.
2. **Check session status first:** If the dashboard contains `**Status:** Complete`, skip directly
   to the Completion Block. The session is already finished.
3. Identify the **active phase** using these explicit parsing rules:
   - `- [x]` or `- [X]` (case-insensitive) → phase is **complete**
   - `- [ ]` (exactly one space between brackets) → phase is **incomplete**
   - The **active phase** is the first incomplete phase in the numbered list.
   - **Malformed checkboxes** (e.g., `-[x]` with no leading space, `* [x]` with asterisk,
     `–[ ]` with an em-dash) must NOT be silently mis-routed. If you encounter one, pause
     and tell the user:
     > "The session dashboard has a formatting issue on one of the phase checkboxes.
     > Let me show you so we can quickly confirm where we are."
     Display the raw affected line(s) and ask: "Is this phase complete or still in progress?"
     Correct the checkbox before continuing.
4. For every complete phase, verify that its listed Outcome file exists on disk.
   - If an Outcome file is missing for a completed phase, stop and say:
     > "It looks like [Phase N] was marked complete but I can't find the expected output
     > file at [path]. Let's take a quick look before continuing."
   - Do not advance to Block 3 until this is resolved.
5. Proceed to Block 3.

---

## Block 3 — Orientation Summary (always shown to the SME)

Present a brief, friendly status message based on the dashboard state.

**For a brand-new session (just bootstrapped):**
> "Great — we're all set up. We'll work through 4 phases together, starting with Problem Framing.
> Ready to begin?"

**For a mid-session resume (at least one phase complete):**
> "Welcome back! Here's where we are:
> [List each phase with ✅ if `[x]` complete, or 🔵 if it is the active phase]
>
> Ready to pick up where we left off with [active phase name]?"

Wait for a soft confirmation before proceeding. Any clear affirmation counts: "Yes", "Let's go", "Go ahead", "Ready", "Sure". Do not proceed until received.

---

## Block 4 — Phase Routing

Route to the child skill for the active phase:

| Active Phase | Child Skill to Invoke |
|---|---|
| Phase 1 — Problem Framing | `discovery-planning` |
| Phase 2 — Visual Blueprinting | `visual-companion` |
| Phase 3 — Prototyping | `subagent-driven-prototyping` |
| Phase 4 — Handoff & Specs (Auto-runs User Stories & Specs) | `exploration-handoff` |
| All 4 phases complete | → Completion Block |

When invoking a child skill, include this context:
> "You are operating as part of an active Exploration Session. When your phase is complete, return here so we can update the session dashboard."

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

## Completion Block

When all 4 phases are marked `[x]`:

> "🎉 Congratulations — your Exploration Session is complete!
> All four phases are finished and your handoff package is ready.
> Your exploration outputs are in the `exploration/` folder.
> The next step is Opportunity 4: Engineering. Hand your team the file at
> `exploration/handoffs/handoff-package.md` to begin the build."

Update `**Status:**` to `Complete` in the dashboard.
