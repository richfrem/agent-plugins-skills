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
> plugin. The exploration-cycle-plugin does not replace superpowers — it **invokes
> superpowers skills directly** during Phase 3 to enforce build discipline.
> See the plugin README for installation instructions.

When the session reaches Phase 3 (Build), the orchestrator invokes superpowers skills
to enforce execution discipline. The exploration-cycle-plugin owns the discovery
workflow (Phases 1, 2, 4); superpowers owns the build discipline (Phase 3 execution).

### Superpowers Availability Check

Before invoking any superpowers skill, silently check whether it is available (e.g.,
try to resolve `superpowers:using-git-worktrees`). If superpowers is **not installed**:

- **Greenfield sessions:** Warn the SME: *"I recommend installing the superpowers plugin
  for isolated workspaces and build discipline. For now, I'll proceed without it, but
  the build won't be isolated from your main branch."* Then proceed with `direct` build
  mode — no worktrees, no TDD, no two-stage review. The prototype still gets built, but
  without execution discipline guardrails.
- **Brownfield sessions:** Halt. Announce: *"Building directly into an existing codebase
  without an isolated workspace is risky. Please install the superpowers plugin first."*
  Provide the install command from the README.

If superpowers IS available, proceed with the steps below.

### Step 1 — Isolation: Invoke `superpowers:using-git-worktrees`

Before Phase 3 begins, **invoke the `using-git-worktrees` skill**:

```
Skill invocation: superpowers:using-git-worktrees
Context: "Starting Phase 3 of exploration session '[session name]'.
Create a feature branch and worktree for the build work."
```

- All build work happens in the worktree, not on the main branch
- If worktrees are not available (no git repo, or discovery-only session), skip this step
- When speaking to the SME, say "isolated workspace" or "feature branch" — not "git worktree"

### Step 2 — Build: Follow `superpowers:subagent-driven-development` pattern

For each component in Phase 3, follow the sub-agent dispatch cycle from superpowers:

1. **Dispatch implementer** — fresh sub-agent per component (via dispatch strategy from Block 0)
2. **Self-review** — implementer checks its own work against the Discovery Plan
3. **Plan alignment check** — invoke `superpowers:requesting-code-review` with the Discovery Plan as the spec. A reviewer sub-agent verifies the component matches requirements.
4. **Quality check** — same review skill, second pass for code quality and conventions

If either review finds issues → implementer fixes, then re-review before next component.

**SME-friendly language adaptation:**

| Superpowers term | We say instead |
|---|---|
| "spec reviewer" | "plan alignment check" |
| "code quality reviewer" | "quality check" |
| "TDD" | "validation check" |
| "git worktree" | "isolated workspace" |
| "spec" | "Discovery Plan" |

### Step 3 — Validation: Invoke `superpowers:test-driven-development` (when applicable)

> **Why validate prototypes?** The prototype is the *evidence* that the exploration
> captured the right thing. If the prototype doesn't match the Discovery Plan, the
> SME reviews the wrong thing, the handoff describes the wrong behavior, and the
> engineering team builds from a flawed spec. Validation isn't about code quality —
> it's about **exploration accuracy**.

For code-producing sessions (greenfield, brownfield), **invoke the `test-driven-development`
skill** for each component:
- Write a failing test that verifies the component meets a Discovery Plan requirement
- Verify it fails for the right reason
- Implement minimal code to pass
- Refactor

For non-code sessions (discovery-only):
- Validate outputs against the Discovery Plan requirements
- Check for completeness, contradictions, and gaps

The validation bar is not "production code quality" but "does this accurately represent
what we discovered?" Even a prototype that will be thrown away after handoff must be
verified against the plan — otherwise it's unverified evidence.

### Step 4 — Finishing: Invoke `superpowers:finishing-a-development-branch`

When Phase 3 is complete, **invoke the `finishing-a-development-branch` skill**:
1. Verify all tests/evals pass
2. Present options to the SME: merge locally, create PR, keep branch, or discard
3. Clean up worktree if appropriate

For discovery-only sessions, this step is skipped (no code branch to finish).

---

## Block 0 — Sub-Agent Dispatch Strategy (ask once during bootstrap)

The exploration workflow can dispatch implementation work to sub-agents for cost efficiency.
Ask the SME during session setup (after session type selection):

> "One more thing — how should I handle the heavy lifting when we get to building?
>
> 1. **I have GitHub Copilot Pro** — I'll use Copilot CLI to dispatch work. Simple tasks go to `gpt-5-mini` (free tier). Complex tasks go to `claude-sonnet-4-6` (1 premium request per task — charged per request, not per token, so big dense prompts are cost-efficient).
> 2. **No Copilot subscription** — I'll dispatch sub-agents using the Claude model family. Implementation work goes to `haiku-4.5` (cheapest). Complex reasoning goes to `sonnet-4.6`.
> 3. **I'll handle it myself** — Do all work in this session directly (simplest, uses current model for everything)."

Record the choice in the dashboard as `**Dispatch Strategy:**` (one of: `copilot-cli`, `claude-subagents`, `direct`).

### Dispatch Strategy Details

**Copilot CLI (`copilot-cli`):**
- Uses the `copilot-cli-agent` skill pattern (`scripts/run_agent.py`)
- Simple/mechanical tasks → `gpt-5-mini` (free, unlimited)
- Complex reasoning/multi-file generation → `claude-sonnet-4-6` (1 premium request; batch everything into one dense prompt)
- Key advantage: premium model is charged per REQUEST not per token — one big prompt with 7 file specs costs the same as one small prompt

**Claude Sub-agents (`claude-subagents`):**
- Uses the `Agent` tool with `model` parameter
- Mechanical tasks → `model: "haiku"` (cheapest Claude model)
- Complex tasks → `model: "sonnet"` (mid-tier)
- Follows the pattern from orba/superpowers: orchestrator stays on the primary model, dispatches implementation to cheaper models

**Direct (`direct`):**
- All work done in the current session by the current model
- Simplest approach, no dispatch overhead
- Best when the session is interactive and the SME wants to see everything happen live

### Dispatch Decision Tree (for the orchestrator, not the SME)

When dispatching a task during Phase 3, use this logic to pick the right model:

```
Is the task mechanical / single-file / boilerplate?
  → copilot-cli: gpt-5-mini (free, unlimited)
  → claude-subagents: model: "haiku" (cheapest)
  → direct: do it inline

Is the task complex / multi-file / requires reasoning?
  → copilot-cli: claude-sonnet-4-6 (batch into ONE dense request — 
    charged per request not per token, so include all file specs in 
    a single prompt for maximum value)
  → claude-subagents: model: "sonnet"
  → direct: do it inline

Is the task orchestration / planning / decision-making?
  → Always keep in the current session (orchestrator model)
  → Never delegate planning or routing decisions to cheap models
```

The orchestrator (this skill) always stays on the primary model. It delegates
**implementation** to cheaper/free models. It never delegates **judgment**.

### Discovery-Only Sessions

If the session type is **discovery-only**, skip the dispatch strategy question entirely.
Default to `direct` and announce: *"Since this is a documentation session with no code
phase, I'll handle all the work directly."*

### Dispatch Fallback

If the chosen dispatch strategy becomes unavailable during Phase 3 (e.g., Copilot CLI
is not installed, or the `copilot-cli-agent` skill is not found), fall back to `direct`
mode and announce: *"The [strategy] dispatch isn't available right now, so I'll build
this directly in this session."* Do not ask the SME to reconfigure — just proceed.

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
