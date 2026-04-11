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

## Block 0 — Sub-Agent Dispatch Strategy (ask once during bootstrap)

> Full details: `references/dispatch-strategies.md`

**For Analysis/Docs sessions:** Skip this question. Default to `direct`.

For all other session types, ask the SME after session type selection:

> "One more thing — how should I handle the heavy lifting when we get to building?
>
> 1. **I have GitHub Copilot Pro** — I'll use Copilot CLI. Simple tasks use `gpt-5-mini` (free). Complex tasks use `claude-sonnet` (1 premium request — batched dense for value).
> 2. **No Copilot** — I'll use Claude sub-agents. Simple tasks use `haiku` (cheapest). Complex tasks use `sonnet`.
> 3. **I'll handle it myself** — Everything happens directly in this session."

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
   - Ask the SME: *"What are we exploring today? Give it a short name so we can track it."*
   - After receiving the session name, ask the SME to choose a **session type**:
     > "What kind of session is this?
     > 1. **New app or system** — building a software prototype from scratch (all 4 phases)
     > 2. **Feature for an existing app** — adding to or modifying a codebase you already have (Phase 2 is optional, Phase 3 builds into the real codebase, Phase 4 is optional)
     > 3. **Analysis or documentation** — no code output. Could be: requirements gathering, business process mapping, legacy code analysis, policy drafting, strategic planning, workflow design, or any non-software deliverable (Phases 1 & 4, Phase 2 optional, Phase 3 skipped)
     > 4. **Spike or investigation** — exploring a question or technology, may loop back to Phase 1 multiple times (flexible phases)"
   - Based on their selection, scaffold the dashboard from the appropriate template (see Session Type Templates below).
   - Replace `[to be filled in]` in the `**Session:**` field with their session name.
   - Write the updated file, then proceed to Block 3.
3. **If the file EXISTS:** Proceed to Block 2.

### Session Type Templates

**Type 1 — New app (Greenfield):** All 4 phases enabled. Use the full template from `assets/templates/exploration-dashboard.md`.

**Type 2 — Feature for existing app (Brownfield):**
- Phase 1 (Problem Framing): enabled
- Phase 2 (Visual Blueprinting): optional — ask the SME: *"Does this feature need a layout discussion, or is the design straightforward enough to skip?"*
- Phase 3 (Implementation): enabled — builds directly into the existing codebase (not a throwaway prototype)
- Phase 4 (Handoff): optional — ask the SME: *"Are you handing this off to another team, or building it yourself? If building it yourself, we can skip the formal handoff."*

**Type 3 — Analysis or documentation:**
- Phase 1 (Problem Framing): enabled
- Phase 2 (Visual Blueprinting): optional — only if the work involves visual outputs (UI concepts, process diagrams, workflow maps). For pure analysis or text deliverables, skip.
- Phase 3: disabled (no code output)
- Phase 4 (Handoff): enabled — the handoff IS the primary output

This type covers a wide range of non-software work:
- Business requirements gathering and documentation
- Business process mapping and workflow design
- Legacy application or codebase analysis (reading and documenting, not modifying)
- Policy drafting, strategic planning, or operational procedures
- Any exploration where the deliverable is documents, not running code

**Type 4 — Spike:**
- Phase 1 (Problem Framing): enabled, may repeat
- Phases 2–4: flexible — the SME decides which phases are relevant as the investigation unfolds

For skipped phases, mark them `- [~]` in the dashboard (tilde = intentionally skipped) and add a note: `(Skipped — [reason])`.

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

When invoking a child skill, include this context:
> "You are operating as part of an active Exploration Session. The session type is [type from dashboard]. When your phase is complete, return here so we can update the session dashboard."

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

When all phases are either marked `[x]` (complete) or `[~]` (skipped):

**Spike re-entry check:** For spike sessions, before declaring completion, ask the SME:
*"You've completed this round of investigation. Would you like to loop back to Phase 1
with what you've learned, or are we done?"* If they want to loop, reset Phase 1 to `[ ]`
and return to Block 3. If they're done, proceed with completion below.

> "Congratulations — your Exploration Session is complete!
> All phases are finished and your outputs are ready.
> Your exploration outputs are in the `exploration/` folder."

**If Phase 4 was skipped** (brownfield self-build):
> "Since you built this directly, you're already in Engineering mode.
> Your build documentation is at `exploration/prototype/README.md`."

**If Phase 4 produced a handoff package**, the completion message depends on the
**Risk Tier** recorded in the handoff (from Stage 1.5 — Risk & Rigor Assessment):

| Tier | Completion Message |
|---|---|
| **Tier 1 (Low Risk)** | "Your handoff assessed this as low risk. You're clear to deploy directly — no formal engineering cycle needed. Your build documentation and handoff are in `exploration/`." |
| **Tier 2 (Moderate Risk)** | "Your handoff assessed this as moderate risk. Before deploying, this needs a security review and red team assessment. Hand the file at `exploration/handoffs/handoff-package.md` to your security team." |
| **Tier 3 (High Risk)** | "Your handoff assessed this as high risk. The next step is formal Engineering (Opportunity 4). Hand the file at `exploration/handoffs/handoff-package.md` to the engineering team to begin the spec-driven build." |
| **Throwaway / Fail Fast** | "The exploration revealed this idea isn't viable — and that's a valuable outcome. You discovered this at near-zero cost instead of months into a build. The session artifacts are preserved in `exploration/` for reference." |

If no tier is recorded in the handoff, default to the Tier 3 message (safest path).

Update `**Status:**` to `Complete` in the dashboard.
