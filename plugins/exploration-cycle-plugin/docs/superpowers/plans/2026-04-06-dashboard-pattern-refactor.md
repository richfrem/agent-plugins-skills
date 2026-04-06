# Dashboard Pattern Refactor (Option 1.5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the exploration-cycle-plugin to implement the Dashboard Pattern — a stateful 4-phase SME orchestrator backed by `exploration-dashboard.md` — replacing the existing narrative-only `exploration-workflow` and retiring the stub `exploration-orchestrator`.

**Architecture:** `exploration-workflow` becomes a rigid state machine with 6 ordered blocks (Bootstrap → Read State → Orientation → Route → HARD-GATE → Dashboard Write). Shared state is maintained in `exploration-dashboard.md` in the user's workspace. Child skills gain a Dashboard Intercept block (redirect if session active) and a Terminal Return block (hand back to orchestrator on completion). `exploration-handoff` absorbs the Scribe Phase as Stage 0.

**Tech Stack:** Markdown prompt engineering only. No code, no scripts, no dependencies. All changes are to `.md` files within the plugin.

**Design Doc:** `docs/superpowers/specs/2026-04-06-dashboard-pattern-refactor-design.md`

---

## File Map

| File | Action |
|---|---|
| `assets/templates/exploration-dashboard.md` | **Create** |
| `skills/exploration-workflow/SKILL.md` | **Rewrite** |
| `skills/discovery-planning/SKILL.md` | **Update** — Intercept + Terminal Return |
| `skills/visual-companion/SKILL.md` | **Update** — Intercept + Terminal Return |
| `skills/subagent-driven-prototyping/SKILL.md` | **Update** — Intercept + Orchestrator Context + Terminal Return |
| `skills/exploration-handoff/SKILL.md` | **Update** — Intercept + Stage 0 Scribe + Terminal Return |
| `skills/exploration-orchestrator/` (entire dir) | **Delete** |
| `skills/deferred/exploration-orchestrator/` (entire dir) | **Delete** |
| `README.md` | **Update** — remove orchestrator from tree |
| `references/architecture.md` | **Update** — replace orchestrator row |
| `references/post-run-survey.md` | **Update** — update title and orchestrator references |

---

## Task 1: Create the Dashboard Template

**Files:**
- Create: `assets/templates/exploration-dashboard.md`

- [ ] **Step 1: Create the `assets/templates/` directory and write the template**

  Create `assets/templates/exploration-dashboard.md` with this exact content:

  ```markdown
  # Business Exploration Dashboard

  **Session:** [to be filled in]
  **Current Phase:** Phase 1 — Problem Framing
  **Status:** In Progress

  ---

  ## The 4-Phase Exploration Loop

  - [ ] **Phase 1: Problem Framing**
    - Skill: `discovery-planning`
    - Gate: SME approval of Discovery Plan
    - Outcome: `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

  - [ ] **Phase 2: Visual Blueprinting**
    - Skill: `visual-companion`
    - Gate: SME selection and confirmation of layout direction
    - Outcome: `exploration/captures/layout-direction.md`

  - [ ] **Phase 3: Prototyping**
    - Skill: `subagent-driven-prototyping`
    - Gate: SME walkthrough and sign-off on working prototype
    - Outcome: `exploration/prototype/index.html`

  - [ ] **Phase 4: Handoff & Specs**
    - Skill: `exploration-handoff`
    - Gate: SME approval of final handoff package (includes requirements, user stories, risk tier)
    - Outcome: `exploration/handoffs/handoff-package.md`

  ---

  ## Session Log

  | Phase | Completed | Notes |
  |-------|-----------|-------|
  | Phase 1 | — | — |
  | Phase 2 | — | — |
  | Phase 3 | — | — |
  | Phase 4 | — | — |
  ```

- [ ] **Step 2: Verify the file was created correctly**

  Run: `cat plugins/exploration-cycle-plugin/assets/templates/exploration-dashboard.md`
  Expected: Full template content shown, 4 unchecked `- [ ]` phase entries, Session Log table present.

- [ ] **Step 3: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/assets/templates/exploration-dashboard.md
  git commit -m "feat(exploration-cycle): add exploration-dashboard.md template for Dashboard Pattern

  Introduces the canonical blank dashboard template that exploration-workflow
  will scaffold into the user's workspace on first session bootstrap.

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 2: Rewrite `exploration-workflow/SKILL.md`

**Files:**
- Modify: `skills/exploration-workflow/SKILL.md` (full rewrite)

- [ ] **Step 1: Read the current file to confirm baseline**

  Run: `cat plugins/exploration-cycle-plugin/skills/exploration-workflow/SKILL.md`
  Expected: The existing narrative-only Phase 0–4 description (no state machine blocks).

- [ ] **Step 2: Replace the entire file content**

  Write the following as the complete new content of `skills/exploration-workflow/SKILL.md`:

  ````markdown
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
  2. Identify the **active phase** — the first phase with an unchecked `- [ ]` box.
  3. For every phase marked `- [x]`, verify that its listed Outcome file exists on disk.
     - If an Outcome file is missing for a completed phase, stop and say:
       > "It looks like [Phase N] was marked complete but I can't find the expected output file at [path]. Let's take a quick look before continuing."
     - Do not advance to Block 3 until this is resolved.
  4. Proceed to Block 3.

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
  | Phase 4 — Handoff & Specs | `exploration-handoff` |
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
  ````

- [ ] **Step 3: Verify against spec checklist**

  Confirm all 6 blocks are present:
  - Block 1 Bootstrap: checks for dashboard, scaffolds if missing, asks for session name ✓
  - Block 2 Read State: identifies active phase, verifies outcome files ✓
  - Block 3 Orientation: friendly status summary, soft confirmation, both new/resume variants ✓
  - Block 4 Phase Routing: routing table with all 4 phases + Completion Block row ✓
  - Block 5 HARD-GATE: `<HARD-GATE>` tag present, natural language affirmations accepted, change loop ✓
  - Block 6 Dashboard Write: checkbox update, Current Phase update, Session Log update, loop back ✓

- [ ] **Step 4: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/skills/exploration-workflow/SKILL.md
  git commit -m "feat(exploration-cycle): rewrite exploration-workflow as 6-block state machine

  Replaces narrative-only phase guide with a deterministic orchestrator.
  Introduces Bootstrap, Read State, Orientation, Phase Routing, HARD-GATE,
  and Dashboard Write blocks. exploration-workflow is now the single canonical
  entry point for all SME exploration sessions.

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 3: Update `discovery-planning/SKILL.md`

**Files:**
- Modify: `skills/discovery-planning/SKILL.md`

The Dashboard Intercept block is inserted immediately after the closing `---` of the YAML frontmatter. The Terminal Return block replaces the final "On approval" section (lines starting from `On approval:`).

- [ ] **Step 1: Insert Dashboard Intercept block after the YAML frontmatter closing `---`**

  After the line `allowed-tools: Read, Write` and its closing `---`, insert this exact block before the first `<example>` tag:

  ```markdown
  ## Dashboard Intercept

  Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

  - **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    Then invoke `exploration-workflow` to resume from the correct phase.

  - **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

  ```

- [ ] **Step 2: Replace the terminal "On approval:" block**

  Find this block at the end of the file:

  ```markdown
  On approval:
  1. Write the final plan file to `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`
  2. Announce:
  > "Your plan is saved. We're all set to move forward."
  ```

  Replace it with:

  ```markdown
  On approval:
  1. Write the final plan file to `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`
  2. Announce: "Your plan is saved — Phase 1 is complete."

  ## Completion — Return to Orchestrator

  If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
  > "Returning to your session dashboard now."
  Then invoke `exploration-workflow` to trigger the Phase 1 HARD-GATE and dashboard update.

  If operating standalone (no dashboard file), the skill is complete.
  ```

- [ ] **Step 3: Verify the file has both sections**

  Run: `grep -n "Dashboard Intercept\|Return to Orchestrator" plugins/exploration-cycle-plugin/skills/discovery-planning/SKILL.md`
  Expected: Two matching lines — one for each new section.

- [ ] **Step 4: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/skills/discovery-planning/SKILL.md
  git commit -m "feat(exploration-cycle): add dashboard intercept + orchestrator return to discovery-planning

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 4: Update `visual-companion/SKILL.md`

**Files:**
- Modify: `skills/visual-companion/SKILL.md`

- [ ] **Step 1: Insert Dashboard Intercept block after the YAML frontmatter closing `---`**

  After the YAML frontmatter closing `---`, insert this exact block before the first `<example>` tag:

  ```markdown
  ## Dashboard Intercept

  Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

  - **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    Then invoke `exploration-workflow` to resume from the correct phase.

  - **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

  ```

- [ ] **Step 2: Replace Step 5 — Signal ready**

  Find this block:

  ```markdown
  ### Step 5 — Signal ready

  Announce:
  > "Layout confirmed. Ready to start building."
  ```

  Replace it with:

  ```markdown
  ### Step 5 — Signal ready

  Announce: "Layout confirmed — Phase 2 is complete."

  ## Completion — Return to Orchestrator

  If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
  > "Returning to your session dashboard now."
  Then invoke `exploration-workflow` to trigger the Phase 2 HARD-GATE and dashboard update.

  If operating standalone (no dashboard file), the skill is complete.
  ```

- [ ] **Step 3: Verify**

  Run: `grep -n "Dashboard Intercept\|Return to Orchestrator" plugins/exploration-cycle-plugin/skills/visual-companion/SKILL.md`
  Expected: Two matching lines.

- [ ] **Step 4: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/skills/visual-companion/SKILL.md
  git commit -m "feat(exploration-cycle): add dashboard intercept + orchestrator return to visual-companion

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 5: Update `subagent-driven-prototyping/SKILL.md`

**Files:**
- Modify: `skills/subagent-driven-prototyping/SKILL.md`

This skill gets three changes: Dashboard Intercept, Orchestrator Context (entry), and Terminal Return (completion).

- [ ] **Step 1: Insert Dashboard Intercept block after the YAML frontmatter closing `---`**

  After the YAML frontmatter closing `---`, insert this exact block before the first `<example>` tag:

  ```markdown
  ## Dashboard Intercept

  Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

  - **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    Then invoke `exploration-workflow` to resume from the correct phase.

  - **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

  ```

- [ ] **Step 2: Insert Orchestrator Context block before `## Required Inputs Check`**

  Find the line:

  ```markdown
  ## Required Inputs Check
  ```

  Insert this block immediately before it:

  ```markdown
  ## Orchestrator Context

  If dispatched by `exploration-workflow`, the Discovery Plan and layout direction have
  already been approved by the SME. The Required Inputs Check below is a verification
  step only — do not re-present these artifacts for re-approval. Proceed directly to
  Component Decomposition once inputs are confirmed present.

  ```

- [ ] **Step 3: Replace the Completion Report block**

  Find this block:

  ```markdown
  ## Completion Report

  Announce:
  > "Your prototype is ready. I'll hand it over now so you can walk through it."

  Report back to prototype-builder: all components are built, the entry point is at `exploration/prototype/index.html`, and the prototype is ready for the SME walkthrough.
  ```

  Replace it with:

  ```markdown
  ## Completion Report

  Announce: "Your prototype is ready — Phase 3 is complete."

  ## Completion — Return to Orchestrator

  If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
  > "Returning to your session dashboard now."
  Then invoke `exploration-workflow` to trigger the Phase 3 HARD-GATE and dashboard update.

  If operating standalone (no dashboard file), the skill is complete. Report back to
  prototype-builder: all components are built, the entry point is at
  `exploration/prototype/index.html`, and the prototype is ready for the SME walkthrough.
  ```

- [ ] **Step 4: Verify all three sections are present**

  Run: `grep -n "Dashboard Intercept\|Orchestrator Context\|Return to Orchestrator" plugins/exploration-cycle-plugin/skills/subagent-driven-prototyping/SKILL.md`
  Expected: Three matching lines.

- [ ] **Step 5: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/skills/subagent-driven-prototyping/SKILL.md
  git commit -m "feat(exploration-cycle): add dashboard intercept, orchestrator context, and return to subagent-driven-prototyping

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 6: Update `exploration-handoff/SKILL.md`

**Files:**
- Modify: `skills/exploration-handoff/SKILL.md`

This skill gets three changes: Dashboard Intercept, a new Stage 0 Scribe block prepended before Stage 1, and a Terminal Return block appended at the end.

- [ ] **Step 1: Insert Dashboard Intercept block after the YAML frontmatter closing `---`**

  The current file has a `> **Note:**` block immediately after the frontmatter. Insert the Dashboard Intercept before that Note:

  ```markdown
  ## Dashboard Intercept

  Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

  - **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    Then invoke `exploration-workflow` to resume from the correct phase.

  - **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

  ```

- [ ] **Step 2: Insert Stage 0 Scribe block before `## Stage 1: Context Gathering`**

  Find the line:

  ```markdown
  ## Stage 1: Context Gathering (Routing)
  ```

  Insert this complete block immediately before it:

  ```markdown
  ## Stage 0: Scribe Activities (Automated Capture Before Synthesis)

  Before opening the handoff dialogue, silently check for `exploration/prototype/`.

  If the prototype directory exists, run the following three capture activities in sequence.
  Announce each one briefly as you start it:
  > "Capturing [activity name] first — this gives us the raw material for the handoff."

  1. **Business Requirements Capture** (invoke `business-requirements-capture`)
     - Extract business rules and functional constraints from the Discovery Plan and prototype
     - Output: `exploration/captures/business-requirements.md`

  2. **User Story Capture** (invoke `user-story-capture`)
     - Translate validated prototype behaviors into Agile user stories
     - Output: `exploration/captures/user-stories.md`

  3. **Business Workflow Doc** (invoke `business-workflow-doc` — **only** if the Discovery Plan
     describes a process flow with sequential steps or decision branches)
     - Output: `exploration/captures/workflow-diagram.md`

  Once all applicable Stage 0 outputs are written, announce:
  > "Requirements and stories captured. Now let's put together your handoff package."

  If the prototype directory does not exist, skip Stage 0 entirely and proceed to Stage 1.
  The Stage 0 outputs (if created) are now available as source artifacts for synthesis.

  ```

- [ ] **Step 3: Append Terminal Return block at the end of the file**

  Add this block after the final `## Final Output Destination` section:

  ```markdown

  ## Completion — Return to Orchestrator

  Once the handoff package is approved and written to `exploration/handoffs/handoff-package.md`:
  1. Announce: "Your handoff package is complete — Phase 4 is done."
  2. If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
     > "Returning to your session dashboard now."
     Then invoke `exploration-workflow` to trigger the Phase 4 HARD-GATE, dashboard update,
     and Completion Block.

  If operating standalone (no dashboard file), the skill is complete.
  ```

- [ ] **Step 4: Verify all three sections are present**

  Run: `grep -n "Dashboard Intercept\|Stage 0\|Return to Orchestrator" plugins/exploration-cycle-plugin/skills/exploration-handoff/SKILL.md`
  Expected: Three matching lines.

- [ ] **Step 5: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/skills/exploration-handoff/SKILL.md
  git commit -m "feat(exploration-cycle): add dashboard intercept, Stage 0 scribe, and orchestrator return to exploration-handoff

  Stage 0 absorbs the Scribe Phase (business-requirements-capture, user-story-capture,
  business-workflow-doc) into exploration-handoff before synthesis begins, collapsing
  the old Phase 3 Scribe into Phase 4 Handoff per the 4-phase Dashboard Pattern.

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 7: Delete `exploration-orchestrator` Directories

**Files:**
- Delete: `skills/exploration-orchestrator/` (entire directory)
- Delete: `skills/deferred/exploration-orchestrator/` (entire directory)

- [ ] **Step 1: Confirm both directories exist before deleting**

  Run: `ls plugins/exploration-cycle-plugin/skills/exploration-orchestrator/ && ls plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/`
  Expected: Both directories listed with their contents.

- [ ] **Step 2: Delete both directories**

  ```bash
  rm -rf plugins/exploration-cycle-plugin/skills/exploration-orchestrator/
  rm -rf plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/
  ```

- [ ] **Step 3: Verify deletion**

  Run: `ls plugins/exploration-cycle-plugin/skills/ | grep orchestrator`
  Expected: No output (no remaining orchestrator directories).

- [ ] **Step 4: Commit**

  ```bash
  git add -A plugins/exploration-cycle-plugin/skills/exploration-orchestrator/
  git add -A plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/
  git commit -m "feat(exploration-cycle): retire exploration-orchestrator skill

  exploration-workflow is now the single canonical orchestrator entry point.
  The stub exploration-orchestrator directory and its deferred/ copy are removed
  to prevent registry conflicts from dynamic SKILL.md scanning.

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 8: Update Reference Files

**Files:**
- Modify: `README.md`
- Modify: `references/architecture.md`
- Modify: `references/post-run-survey.md`

- [ ] **Step 1: Update `README.md` — remove `exploration-orchestrator/` from the tree**

  Find this line in the skills tree listing:

  ```
  │   ├── exploration-orchestrator/
  ```

  Delete it entirely. No replacement needed.

- [ ] **Step 2: Update `references/architecture.md` — replace the orchestrator row in the skills table**

  Find this table row:

  ```markdown
  | `exploration-orchestrator` | Orchestration patterns and routing | ✅ Phase A |
  ```

  Replace it with:

  ```markdown
  | `exploration-workflow` | SME-facing state machine orchestrator. Manages `exploration-dashboard.md`, enforces 4-phase gates, routes to child skills. Single canonical entry point. | ✅ Phase A |
  ```

- [ ] **Step 3: Update `references/post-run-survey.md` — replace title and orchestrator references**

  Replace the title line:

  ```markdown
  # Post-Run Survey: exploration-orchestrator
  ```

  With:

  ```markdown
  # Post-Run Survey: exploration-workflow
  ```

- [ ] **Step 4: Verify all three files updated**

  Run:
  ```bash
  grep -n "exploration-orchestrator" plugins/exploration-cycle-plugin/README.md plugins/exploration-cycle-plugin/references/architecture.md plugins/exploration-cycle-plugin/references/post-run-survey.md
  ```
  Expected: No output (all references removed or replaced).

- [ ] **Step 5: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/README.md \
          plugins/exploration-cycle-plugin/references/architecture.md \
          plugins/exploration-cycle-plugin/references/post-run-survey.md
  git commit -m "docs(exploration-cycle): update references to reflect exploration-workflow as canonical orchestrator

  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Self-Review Checklist

- [x] **Spec coverage:** All 11 files in the spec's change summary have a corresponding task ✓
- [x] **Dashboard template created before workflow references it** — Task 1 before Task 2 ✓
- [x] **Dashboard Intercept block is identical across all 4 child skill tasks** — verified Tasks 3–6 ✓
- [x] **Scribe Phase collapse** — `business-requirements-capture`, `user-story-capture`, `business-workflow-doc` appear only in Task 6 (Stage 0), never in the orchestrator routing table ✓
- [x] **`deferred/` directory deletion included** — Task 7, Step 2 deletes both dirs ✓
- [x] **Natural language gate affirmations** — Block 5 lists "Yes", "Looks good", "Approved", "Go ahead", "That's right" ✓
- [x] **Edge case: missing prototype in Stage 0** — Task 6 includes "If the prototype directory does not exist, skip Stage 0 entirely" ✓
- [x] **No placeholder text** — all steps contain exact markdown content ✓
