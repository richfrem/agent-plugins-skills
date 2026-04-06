# Exploration Cycle Plugin: Upgrade Implementation Plan

> **For agentic workers:** Use `superpowers:brainstorming` and `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the exploration-cycle-plugin to adopt the rigorous planning mechanics from the `superpowers` harness while translating all language and personas for non-technical Subject Matter Experts (SMEs), and adding full-prototype generation capability beyond static wireframes.

**Architecture:** The upgrade adds four new skills (`discovery-planning`, `visual-companion`, `subagent-driven-prototyping`, `spec-alignment-checker`), promotes `prototype-builder` from deferred to active, adds a `discovery-planning-agent.md`, enhances the orchestrator with a `<HARD-GATE>`, and adds Opportunity 4 format adapters to the handoff stack.

**Core Principle:** Every piece of developer language from `superpowers` must be translated into business-friendly SME language. The mechanics stay; the vocabulary changes.

**Source Reference:** The `superpowers` harness skills to reference and adapt are: `brainstorming/SKILL.md`, `brainstorming/visual-companion.md`, `brainstorming/spec-document-reviewer-prompt.md`, `writing-plans/SKILL.md`, `executing-plans/SKILL.md`, `subagent-driven-development/SKILL.md`, `using-git-worktrees/SKILL.md`, `verification-before-completion/SKILL.md`.

---

## Pre-Work: Set Up Worktree

- [ ] **Step 1: Create isolated worktree for this upgrade**

```bash
git worktree add ../exploration-cycle-plugin-upgrade -b feat/smr-upgrade
cd ../exploration-cycle-plugin-upgrade
```

---

## Task 1: Create `discovery-planning` Skill

> **Adapted from:** `superpowers/brainstorming/SKILL.md`
> **SME Translation:** "Brainstorming" → "Discovery Planning Session". Developer language removed. HARD-GATE enforced before any capture agents fire.

**Files:**
- Create: `skills/discovery-planning/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/discovery-planning
```

- [ ] **Step 2: Write `skills/discovery-planning/SKILL.md`**

Write the following content to `skills/discovery-planning/SKILL.md`:

```markdown
---
name: discovery-planning
description: >
  MUST run before any exploration capture begins. Leads the SME through a structured
  Discovery Planning Session to understand the problem, propose 2-3 solution
  approaches, build a Discovery Plan, and get explicit SME approval before
  dispatching any documentation or prototype agents. Trigger with "start exploration",
  "let's plan this out", "I have an idea", "help me scope this", or at the beginning
  of any new Opportunity 3 session.
---

# Discovery Planning Session

Help any Subject Matter Expert — technical or non-technical — turn a raw idea, business
problem, or process pain point into a structured Discovery Plan through natural,
guided conversation.

Start by understanding the current context, then ask one question at a time to refine
the idea. Once you understand what we are going to explore, present the plan and get
the SME's explicit approval before anything is documented or built.

<HARD-GATE>
Do NOT dispatch any documentation agents (requirements-doc-agent, prototype-companion-agent,
business-rule-audit-agent, handoff-preparer-agent) or trigger any prototype-building
activity until you have presented a Discovery Plan and the SME has explicitly approved it.
This applies to EVERY session regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple to Need a Plan"

Every session goes through this process. A simple automation, a process improvement,
a documentation need — all of them. Simple problems are where unexamined assumptions
cause the most wasted effort. The plan can be brief (a few sentences), but you MUST
present it and get approval.

## Discovery Planning Checklist

Complete these steps in order:

1. **Understand the context** — ask the SME what they are trying to solve, improve, or build
2. **Offer the Visual Companion** (if visual layouts or process flows are involved) — offer it once in its own message, get consent before proceeding
3. **Ask clarifying questions** — one at a time. Focus on: purpose, who is affected, what success looks like, any known constraints
4. **Propose 2-3 approaches** — lay out the options conversationally, with trade-offs and your recommendation
5. **Present the Discovery Plan** — summarise the agreed direction in plain language, section by section, get SME approval
6. **Write the Discovery Plan** — save to `exploration/discovery-plans/YYYY-MM-DD-<topic>-plan.md`
7. **Self-Review the Plan** — scan for vague sections, contradictions, unanswered questions (see Spec Alignment Checker below)
8. **SME Review Gate** — ask the SME to confirm the written plan before any agents are dispatched
9. **Transition to capture** — invoke the exploration-workflow skill to begin the capture phase

## How to Run the Session

**Ask one question at a time.** Never ask multiple questions in the same message.
Prefer multiple-choice questions where possible — they are much easier for non-technical
users to answer than open-ended questions.

**Understand the problem space:**
- What is the problem, opportunity, or idea?
- Who is affected by it?
- What would "success" look like in plain language?
- Are there known constraints, deadlines, or non-negotiables?

**If the scope seems very large:**
Flag it immediately. Help the SME decompose into smaller explorations. What are the
independent pieces? What should be explored first?

**Propose 2-3 approaches:**
Always present options before committing. Include your recommendation and why.
Present in plain business language — no technical jargon.

**Present the Discovery Plan in sections:**
- Problem Statement
- Who Is Affected
- What We Are Going to Explore
- Proposed Approach
- What Success Looks Like
- Known Constraints and Risks
- What We Will Build or Document

Ask after each section if it looks correct. Be ready to revise.

## Writing the Discovery Plan

After approval, write the plan to `exploration/discovery-plans/YYYY-MM-DD-<topic>-plan.md`.

Then run the self-review (Spec Alignment Checker below).

Then ask the SME to review the written plan:
> "I've written up our Discovery Plan. Please read it and let me know if anything looks
> wrong or is missing before I start gathering the details."

Wait for explicit approval. Only after approval: invoke `exploration-workflow` to begin
Phase 1 capture.

## Spec Alignment Checker (Self-Review)

After writing the Discovery Plan, review it with fresh eyes:

1. **Vagueness scan:** Any sections that say "TBD", "to be determined", or "handle later"? Fix them.
2. **Contradiction check:** Does any section conflict with another? Pick one interpretation and make it explicit.
3. **Scope check:** Is this focused enough for one exploration session? If not, decompose.
4. **Ambiguity check:** Could any requirement be interpreted two different ways? Make the chosen interpretation explicit.

Fix inline. Do not re-review — just fix and move on.

## Visual Companion

Offer the Visual Companion when the session will involve layouts, process flows, or
interface design. Offer it once in its own message — do not combine with questions:

> "Some of what we're exploring might be easier to understand if I can show it to you
> visually in a browser — mockups, process diagrams, layout options. Would you like me
> to use that when helpful?" 

After consent, read and follow `skills/visual-companion/SKILL.md` for per-question
routing decisions (browser vs plain text).

## Key Principles

- One question per message — never ask multiple at once
- Multiple choice preferred over open-ended
- Always propose 2-3 approaches before committing
- Use plain business language throughout — no developer jargon
- The HARD-GATE is absolute: no capture, no prototype until the plan is approved
```

- [ ] **Step 3: Verify file written correctly**

```bash
head -5 skills/discovery-planning/SKILL.md
# Expected: YAML frontmatter starting with ---
```

---

## Task 2: Create `visual-companion` Skill

> **Adapted from:** `superpowers/brainstorming/visual-companion.md`
> **SME Translation:** Language cleaned of developer references. Offers visual mockups and process flows for business context, not code architecture.

**Files:**
- Create: `skills/visual-companion/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/visual-companion
```

- [ ] **Step 2: Write `skills/visual-companion/SKILL.md`**

Write a skill that:
- Opens a local browser session for rendering visual content
- Defines clear routing logic: use browser for visual questions (mockups, layouts, diagrams), use plain text for conceptual questions (requirements, options, trade-offs)
- Is offered once for consent — not invoked automatically
- Uses business language throughout ("layout options", "process flow", "mockup" — not "wireframe", "component tree", "diff")
- References `superpowers:visual-companion` as its mechanical source

Key routing rule to embed:
```
Use browser for: mockups, layout options, process diagrams, side-by-side visual comparisons
Use plain text for: requirement questions, option lists, conceptual trade-offs, scope decisions
A question about a UI topic is NOT automatically a visual question — test whether seeing it is better than reading it.
```

- [ ] **Step 3: Verify directory created**

```bash
ls skills/visual-companion/
# Expected: SKILL.md
```

---

## Task 3: Create `subagent-driven-prototyping` Skill

> **Adapted from:** `superpowers/subagent-driven-development/SKILL.md`
> **SME Translation:** "subagent-driven-development" → "subagent-driven-prototyping". "Git worktree" → "prototype sandbox". "Tests" → "prototype validation checks". "Code review" → "spec alignment review".

**Files:**
- Create: `skills/subagent-driven-prototyping/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/subagent-driven-prototyping
```

- [ ] **Step 2: Write `skills/subagent-driven-prototyping/SKILL.md`**

Write a skill that:
- Adapts the blank-slate subagent dispatch pattern for prototype building (not code development)
- Dispatches an isolated subagent per prototype component, with only the approved Discovery Plan as context
- Runs a two-stage review after each component:
  - **Stage 1 (Spec Alignment Review):** Does the prototype component match what the SME approved in the Discovery Plan?
  - **Stage 2 (Prototype Quality Check):** Does the component actually work and render correctly?
- Uses SME-friendly language throughout
- Announces: "I'm setting up your prototype sandbox and building each component separately to make sure everything matches what we planned."
- References `exploration/discovery-plans/` as the source of truth, not a developer spec

Two-stage review block to embed:
```
After each prototype component is built:
1. Spec Alignment Review: Read the approved Discovery Plan. Does this component do exactly what was described? No extra features, no missing features?
   - Pass: continue to Stage 2
   - Fail: rebuild the component against the plan before continuing
2. Prototype Quality Check: Does the component render and function correctly? Can the SME click through it without errors?
   - Pass: mark component complete
   - Fail: fix and re-check
```

- [ ] **Step 3: Verify file written**

```bash
ls skills/subagent-driven-prototyping/
# Expected: SKILL.md
```

---

## Task 4: Promote and Rewrite `prototype-builder` Skill

> **Current state:** Deferred in `skills/deferred/prototype-builder/`.  
> **Target state:** Active at `skills/prototype-builder/`, rewritten to build fully functional interactive prototypes — not wireframes.

**Files:**
- Modify: `skills/prototype-builder/SKILL.md` (promote from deferred and rewrite)

- [ ] **Step 1: Check if the active skills/prototype-builder exists or is still in deferred**

```bash
ls skills/prototype-builder/
ls skills/deferred/prototype-builder/
```

- [ ] **Step 2: Update `skills/prototype-builder/SKILL.md`**

Rewrite the skill with the following key requirements:
- The goal is a **fully working, interactive software prototype** — not a wireframe or static mockup
- The SME must be able to click through real business flows and validate logic
- The skill uses `subagent-driven-prototyping` for building each prototype component
- It offers the Visual Companion for the initial wireframe-confirm step before full build
- It requires the Discovery Plan to be approved first (references the HARD-GATE)
- Language: "building your prototype", "testing your business flow", "prototype sandbox" — never "scaffolding", "component tree", "framework"

Steps to embed in the skill:
```
1. Confirm Discovery Plan is approved (HARD-GATE check)
2. Offer Visual Companion for initial layout validation (wireframe confirm step)
3. SME approves the visual layout direction
4. Invoke subagent-driven-prototyping to build each component against the approved plan
5. SME clicks through the working prototype and validates business logic
6. Capture prototype observations for the business-rule-audit-agent
```

- [ ] **Step 3: Verify prototype-builder SKILL.md exists and is substantial**

```bash
wc -l skills/prototype-builder/SKILL.md
# Expected: > 40 lines
```

---

## Task 5: Create `discovery-planning-agent.md`

> **New agent.** Runs the discovery-planning skill before any other agent in the session. Acts as the planning gate for the orchestrator.

**Files:**
- Create: `agents/discovery-planning-agent.md`

- [ ] **Step 1: Write `agents/discovery-planning-agent.md`**

Write an agent file with:
- Name: `discovery-planning`
- Description: Runs before any capture agents. Leads the SME through the Discovery Planning Session. Enforces the HARD-GATE.
- Dependencies: `skill:discovery-planning`, `skill:visual-companion`
- Tools: Read, Write (no Bash — this agent is conversational, not mechanical)
- Routing: This agent ALWAYS runs first in a new exploration session. It does not route to capture agents — it approves and hands off to the orchestrator.
- Language: fully SME-friendly throughout

- [ ] **Step 2: Verify file created**

```bash
head -10 agents/discovery-planning-agent.md
# Expected: YAML frontmatter with name: discovery-planning
```

---

## Task 6: Rewrite `agents/prototype-companion-agent.md`

> **Current state:** Minimal placeholder (41 bytes). 
> **Target state:** Full agent for running the subagent-driven-prototyping flow and capturing observations.

**Files:**
- Modify: `agents/prototype-companion-agent.md`

- [ ] **Step 1: Rewrite `agents/prototype-companion-agent.md`**

Rewrite with:
- Name: `prototype-companion`
- Description: Builds fully working interactive prototypes using subagent-driven-prototyping. Runs after Discovery Plan is approved and visual layout is confirmed. Captures prototype observations for the business-rule-audit-agent.
- Dependencies: `skill:prototype-builder`, `skill:subagent-driven-prototyping`, `skill:visual-companion`
- Tools: Bash, Read, Write
- Session flow embedded in the agent:
  1. Confirm Discovery Plan approved
  2. Offer Visual Companion for visual confirm step
  3. Invoke subagent-driven-prototyping for each component
  4. SME validates the working prototype
  5. Write observations to `exploration/captures/prototype-notes.md`

- [ ] **Step 2: Verify file is no longer a stub**

```bash
wc -c agents/prototype-companion-agent.md
# Expected: > 1000 bytes
```

---

## Task 7: Add HARD-GATE to Orchestrator Agent

> **Current state:** `agents/exploration-cycle-orchestrator-agent.md` has no HARD-GATE. It routes directly to capture agents.
> **Target state:** The orchestrator enforces that discovery-planning-agent must complete and be approved before any capture agents are dispatched.

**Files:**
- Modify: `agents/exploration-cycle-orchestrator-agent.md`

- [ ] **Step 1: Add HARD-GATE block to the orchestrator**

After the `## Ecosystem Role` section, insert:

```markdown
<HARD-GATE>
Do NOT dispatch requirements-doc-agent, prototype-companion-agent, business-rule-audit-agent,
or handoff-preparer-agent until the discovery-planning-agent has completed a Discovery Planning
Session and the SME has explicitly approved the Discovery Plan. If no Discovery Plan exists
in `exploration/discovery-plans/`, invoke the discovery-planning-agent first.
</HARD-GATE>
```

- [ ] **Step 2: Add discovery-planning-agent to the routing decision tree**

In the `## Routing Decision` section, add as the first entry:

```
Is there an approved Discovery Plan in exploration/discovery-plans/?
  └─ NO  -> Invoke discovery-planning-agent FIRST. Stop. Do not proceed until approved.
  └─ YES -> Continue with existing routing logic below.
```

- [ ] **Step 3: Add discovery-planning-agent to the Phase A Scope table**

Add a row at the top of the scope table:
```
| Discovery Planning Session director | ✅ Phase A | `discovery-planning-agent` — MUST run first |
```

- [ ] **Step 4: Verify all three changes present**

```bash
grep -n "HARD-GATE" agents/exploration-cycle-orchestrator-agent.md
grep -n "discovery-planning" agents/exploration-cycle-orchestrator-agent.md
# Expected: multiple matches in both
```

---

## Task 8: Enhance `agents/handoff-preparer-agent.md` with Opp 4 Format Adapters

> **Current state:** Synthesizes captures into `exploration-handoff.md`.
> **Target state:** Adds a format selection step to produce Opportunity 4-ready artifacts.

**Files:**
- Modify: `agents/handoff-preparer-agent.md`

- [ ] **Step 1: Add Placeholder Scan step before synthesis**

Before the synthesis step, insert a self-review block:

```markdown
## Pre-Synthesis Self-Review (Placeholder Scan)

Before synthesising the handoff package, scan all capture files for:
- Any section marked `[NEEDS HUMAN INPUT]` — resolve or flag explicitly
- Any business rule with no corresponding evidence from prototype observations
- Any user story with no acceptance criteria

Do not proceed to synthesis until these are resolved or explicitly accepted as known gaps.
```

- [ ] **Step 2: Add Opportunity 4 format selection step**

After the handoff synthesis, add:

```markdown
## Opportunity 4 Format Selection

After writing `exploration/handoff/exploration-handoff.md`, ask the SME or engineer:

> "We're ready to hand this off to the engineering team. Which format does your team use?
> 1. **Spec-Kitty** — I'll generate `spec-draft.md`, `plan-draft.md`, and a tasks outline
> 2. **Superpowers** — I'll generate a spec document in `docs/superpowers/specs/` format
> 3. **Generic** — I'll produce a plain structured specification document

**If Spec-Kitty chosen:** Dispatch planning-doc-agent in spec-draft → plan-draft → tasks-outline sequence. Stage to `exploration/planning-drafts/`. Human must approve before any spec-kitty CLI is run.

**If Superpowers chosen:** Write handoff content to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`. Include architecture, components, data flow, and acceptance criteria sections matching superpowers spec format.

**If Generic chosen:** Write structured specification to `exploration/handoff/specification.md` with sections: Problem Statement, Solution Approach, Business Rules, User Stories, Acceptance Criteria, Known Risks.
```

- [ ] **Step 3: Verify changes present**

```bash
grep -n "Placeholder Scan" agents/handoff-preparer-agent.md
grep -n "Opportunity 4 Format" agents/handoff-preparer-agent.md
# Expected: one match each
```

---

## Task 9: Add Discovery Planning Phase to `exploration-workflow` Skill

> **Current state:** `exploration-workflow` starts at Phase 0: Intake.
> **Target state:** Adds a pre-Phase 0 planning gate and updates Phase 2 prototype description.

**Files:**
- Modify: `skills/exploration-workflow/SKILL.md`

- [ ] **Step 1: Add pre-Phase 0 Discovery Planning gate**

Before `## Phase 0: Intake and Session Brief`, insert:

```markdown
## Pre-Phase 0: Discovery Planning (Required)

Before any intake or capture begins, a Discovery Planning Session MUST be completed.

The `discovery-planning-agent` leads the SME through a structured planning session:
- One question at a time to understand the problem and goals
- 2-3 approach options presented with trade-offs
- Discovery Plan written and approved by the SME

**This is a hard prerequisite.** Do not proceed to Phase 0 intake until `exploration/discovery-plans/` contains an approved plan for this session.

Invoke: `discovery-planning-agent`
Output: `exploration/discovery-plans/YYYY-MM-DD-<topic>-plan.md`
```

- [ ] **Step 2: Expand Phase 2 prototype description**

Replace the current Phase 2 section description with:

```markdown
## Phase 2: Prototype Session (Optional)

If exploration needs a runnable prototype to resolve ambiguity or validate business flows:

1. The `prototype-builder` skill is invoked — NOT the prototype-companion-agent directly.
2. `prototype-builder` first offers the Visual Companion for a wireframe-confirm step.
3. After layout direction is confirmed, `subagent-driven-prototyping` builds the full working prototype component by component.
4. Each component passes a two-stage review (Spec Alignment → Prototype Quality).
5. The SME clicks through the working prototype and validates the business logic.
6. After validation, dispatch prototype-companion-agent for observation capture:
```

- [ ] **Step 3: Verify both changes**

```bash
grep -n "Pre-Phase 0" skills/exploration-workflow/SKILL.md
grep -n "subagent-driven-prototyping" skills/exploration-workflow/SKILL.md
# Expected: one match each
```

---

## Task 10: Finalize — Review, Commit, and Report

- [ ] **Step 1: Verify all new and modified files are present**

```bash
ls skills/discovery-planning/SKILL.md
ls skills/visual-companion/SKILL.md
ls skills/subagent-driven-prototyping/SKILL.md
ls skills/prototype-builder/SKILL.md
ls agents/discovery-planning-agent.md
wc -c agents/prototype-companion-agent.md
grep -c "HARD-GATE" agents/exploration-cycle-orchestrator-agent.md
grep -c "Placeholder Scan" agents/handoff-preparer-agent.md
grep -c "Pre-Phase 0" skills/exploration-workflow/SKILL.md
# All expected: output present / count > 0
```

- [ ] **Step 2: Commit all changes**

```bash
git add skills/discovery-planning/ \
        skills/visual-companion/ \
        skills/subagent-driven-prototyping/ \
        skills/prototype-builder/SKILL.md \
        agents/discovery-planning-agent.md \
        agents/prototype-companion-agent.md \
        agents/exploration-cycle-orchestrator-agent.md \
        agents/handoff-preparer-agent.md \
        skills/exploration-workflow/SKILL.md

git commit -m "feat: upgrade exploration-cycle-plugin with SME-targeted superpowers mechanics

- Add discovery-planning skill (adapted from superpowers brainstorming + HARD-GATE)
- Add visual-companion skill (adapted from superpowers visual-companion)
- Add subagent-driven-prototyping skill (adapted from superpowers sdd)
- Promote prototype-builder from deferred; rewrite for full functional prototypes
- Add discovery-planning-agent; enforce HARD-GATE in orchestrator
- Rewrite prototype-companion-agent from stub to full agent
- Add Opp 4 format adapters to handoff-preparer-agent
- Add pre-Phase 0 planning gate to exploration-workflow"
```

- [ ] **Step 3: Report completion**

Report the following when complete:
1. List all files created or modified with line counts
2. Note any steps where the superpowers source file was consulted
3. Flag any steps where a design decision was made differently than the plan and explain why
