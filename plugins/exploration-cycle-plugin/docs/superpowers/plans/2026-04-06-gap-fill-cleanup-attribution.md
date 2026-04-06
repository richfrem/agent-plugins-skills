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
   > to the next stage. If anything needs changing, just tell me what."
   
   Do NOT write the approved plan file or hand off to the prototype builder
   until the SME has explicitly typed YES (or equivalent affirmation).

6. **On approval:** Write the plan to file and report back:
   > "Your discovery plan is saved. We're ready to build your prototype."

### `evals/evals.json` format:
```json
{
  "skill": "discovery-planning",
  "evals": [
    {
      "id": "eval-001",
      "trigger": "start a discovery session",
      "expected_skill": "discovery-planning",
      "notes": "Primary trigger phrase"
    },
    {
      "id": "eval-002",
      "trigger": "let's plan this out before building",
      "expected_skill": "discovery-planning",
      "notes": "Planning intent"
    },
    {
      "id": "eval-003",
      "trigger": "I have an idea I want to explore",
      "expected_skill": "discovery-planning",
      "notes": "Ideation trigger"
    },
    {
      "id": "eval-004",
      "trigger": "help me figure out what we're building",
      "expected_skill": "discovery-planning",
      "notes": "Scoping intent"
    }
  ]
}
```

---

## Task 2 — Create `skills/visual-companion/SKILL.md`

**What it is:** The layout and visual direction skill. Invoked by `prototype-builder-agent`
before building starts. It presents 2-3 layout options to the SME and gets a confirmation
before the builder begins.

**Create the file:**
```
skills/visual-companion/SKILL.md
skills/visual-companion/evals/evals.json
```

### `SKILL.md` must contain:

**YAML frontmatter:**
```yaml
---
name: visual-companion
description: >
  Presents layout direction options to the SME before prototype construction begins.
  Invoked by prototype-builder-agent after Discovery Plan approval to confirm the
  visual structure of the prototype. Trigger with "what should it look like",
  "let me see some layout options", or when the prototype-builder-agent requests
  layout confirmation before building.
allowed-tools: Read, Write
---
```

**Core content the skill MUST implement:**

1. **Read the Discovery Plan** from `exploration/discovery-plans/` — use the most recent
   one. Understand the problem and stakeholders before proposing layouts.

2. **Present 3 layout options** in plain language with a simple ASCII or prose description:
   - Option A: Simple single-page dashboard with a summary view at top and details below
   - Option B: Step-by-step wizard that walks users through one thing at a time
   - Option C: Split-screen with a list on the left and details on the right
   (Adapt options to the context of the Discovery Plan — these are examples only.)

3. **Ask for confirmation:**
   > "Which of these feels closest to what you had in mind?
   > You can also describe something different if none of these fit."

4. **Write the layout decision** to `exploration/captures/layout-direction.md`:
   - Selected option
   - Any SME notes or modifications
   - Date confirmed

5. **Report back** to `prototype-builder-agent` that layout is confirmed and building
   can proceed.

### `evals/evals.json` format:
```json
{
  "skill": "visual-companion",
  "evals": [
    {
      "id": "eval-001",
      "trigger": "what should it look like",
      "expected_skill": "visual-companion",
      "notes": "Visual direction request"
    },
    {
      "id": "eval-002",
      "trigger": "show me some layout options",
      "expected_skill": "visual-companion",
      "notes": "Layout options request"
    },
    {
      "id": "eval-003",
      "trigger": "let me see the design options before we build",
      "expected_skill": "visual-companion",
      "notes": "Pre-build design confirmation"
    }
  ]
}
```

---

## Task 3 — Create `skills/subagent-driven-prototyping/SKILL.md`

**What it is:** The component-by-component build skill. Invoked by `prototype-builder-agent`
after layout is confirmed. Builds each component of the prototype separately using a
blank-slate subagent per component, then reviews each before presenting the full prototype
to the SME.

**Inspired by:** `obra/superpowers` subagent-driven execution pattern — blank-slate context
isolation per task. See attribution section below.

**Create the file:**
```
skills/subagent-driven-prototyping/SKILL.md
skills/subagent-driven-prototyping/evals/evals.json
```

### `SKILL.md` must contain:

**YAML frontmatter:**
```yaml
---
name: subagent-driven-prototyping
description: >
  Builds an interactive prototype component-by-component using isolated build passes.
  Each component is built separately and reviewed before the next begins, preventing
  context pollution and ensuring each piece matches the Discovery Plan. Invoked by
  prototype-builder-agent after visual-companion confirms the layout direction.
  Trigger with "build the prototype", "let's build it", or when dispatched by
  prototype-builder-agent.
allowed-tools: Bash, Read, Write
---
```

**Core content the skill MUST implement:**

1. **Read inputs:**
   - Discovery Plan: `exploration/discovery-plans/` (most recent)
   - Layout Direction: `exploration/captures/layout-direction.md`
   - Both are REQUIRED. If either is missing, stop and report which is missing.

2. **Decompose into components:** Based on the Discovery Plan and layout, identify
   the prototype components (e.g., navigation, summary panel, data table, form, etc.).
   List them and announce to the orchestrator:
   > "I'll build this in [N] parts. Each part will be reviewed before I move to the next."

3. **Build loop (per component):**
   - Announce: "Building: [component name]..."
   - Write the component file to `exploration/prototype/components/[name].[ext]`
   - Self-review: check component against Discovery Plan rules
   - Report: COMPLETE | BLOCKED | NEEDS_CONTEXT
   - If BLOCKED or NEEDS_CONTEXT: stop and request clarification before continuing

4. **Assembly:** Once all components are COMPLETE, assemble the prototype:
   - Write `exploration/prototype/index.html` (or equivalent entry point)
   - Include all components
   - Write `exploration/prototype/README.md` with run instructions in plain language

5. **Announce completion** to `prototype-builder-agent`:
   - All components built and assembled
   - Location of entry point
   - Ready for SME walkthrough

6. **Persona rules (enforce strictly):**
   - Never use: "scaffold", "initialize", "spin up", "subagent", "context", "invoke"
   - Use: "build", "create", "put together", "set up", "prepare"
   - Progress updates should be brief and business-friendly

### `evals/evals.json` format:
```json
{
  "skill": "subagent-driven-prototyping",
  "evals": [
    {
      "id": "eval-001",
      "trigger": "build the prototype now",
      "expected_skill": "subagent-driven-prototyping",
      "notes": "Direct build trigger"
    },
    {
      "id": "eval-002",
      "trigger": "let's build it",
      "expected_skill": "subagent-driven-prototyping",
      "notes": "Colloquial build trigger"
    },
    {
      "id": "eval-003",
      "trigger": "start building the prototype",
      "expected_skill": "subagent-driven-prototyping",
      "notes": "Explicit build start"
    }
  ]
}
```

---

## Task 4 — Replace `skills/prototype-builder/SKILL.md` (stub → full skill)

The current file is a 1 KiB stub that says "STUB — execute.py not yet implemented."
Replace it completely.

**Overwrite:** `skills/prototype-builder/SKILL.md`

### New content:

**YAML frontmatter:**
```yaml
---
name: prototype-builder
description: >
  Orchestrates the full prototype build cycle: reads the approved Discovery Plan,
  invokes visual-companion for layout direction, then drives subagent-driven-prototyping
  to build each component. Trigger with "build a prototype", "create a working prototype",
  "show me a working version", or "prototype to clarify scope".
allowed-tools: Bash, Read, Write
---
```

**Core content:**

1. **HARD-GATE check:** Before anything else:
   ```bash
   ls exploration/discovery-plans/
   ```
   If no approved plan exists: stop and tell the user:
   > "Before we can build, I need to understand what we're building.
   > Can we start with a planning session first?"
   Do NOT proceed without an approved plan.

2. **Invoke `visual-companion` skill** for layout direction.

3. **Invoke `subagent-driven-prototyping` skill** to build component by component.

4. **Guide SME walkthrough** once all components are built.

5. **Write observations** to `exploration/captures/prototype-notes.md`.

6. **Hand off** to `prototype-companion-agent` for structured requirement extraction.

The skill must NOT do the actual building itself — it coordinates the two sub-skills above.
Announce progress to the SME in plain business language throughout.

---

## Task 5 — Clean Up `skills/deferred/`

The `skills/deferred/` directory contains orphaned stubs and misplaced files from before
the SMR upgrade. Clean it up as follows:

### 5a — Files to DELETE from `skills/deferred/`:
```
skills/deferred/exploration-cycle-orchestrator-agent.md   ← 52-byte stub, belongs in agents/
skills/deferred/prototype-companion-agent.md              ← 41-byte stub, belongs in agents/
```
These are placeholder stubs that duplicate (badly) files that already exist in `agents/`.
Delete them.

### 5b — Subdirectories to DELETE from `skills/deferred/`:
```
skills/deferred/exploration-orchestrator/    ← already promoted to skills/exploration-orchestrator/
skills/deferred/prototype-builder/           ← already promoted to skills/prototype-builder/
```
Both have been promoted to top-level skill directories. The copies inside `deferred/`
are old duplicates. Delete them entirely.

### 5c — What to KEEP in `skills/deferred/`:
```
skills/deferred/SKILL.md          ← keep (documents the deferred pattern)
skills/deferred/evals/            ← keep
skills/deferred/agents/           ← keep if non-empty, check contents first
skills/deferred/references/       ← keep if non-empty
```

### 5d — Update `skills/deferred/SKILL.md`:
After deleting the stubs, update the description in `SKILL.md` to reflect current state:
- Remove any references to `exploration-orchestrator` or `prototype-builder` as deferred
- Note they have been promoted to active skills

---

## Task 6 — Update `README.md` (Directory Map + Attribution + License)

The README has two issues: (1) the directory map is outdated, (2) no attribution to superpowers.

### 6a — Update the directory structure map

Replace the existing `### Directory Structure` block with:

```
exploration-cycle-plugin/
├── OVERVIEW.md
├── README.md
├── agents/                        # Vision Translators and Scribes
│   ├── exploration-cycle-orchestrator-agent.md
│   ├── prototype-builder-agent.md
│   ├── prototype-companion-agent.md
│   ├── handoff-preparer-agent.md
│   ├── intake-agent.md
│   ├── planning-doc-agent.md
│   ├── problem-framing-agent.md
│   ├── business-rule-audit-agent.md
│   ├── requirements-doc-agent.md
│   └── requirements-scribe-agent.md
├── assets/                        # Diagrams and visual references
├── docs/                          # Design plans and analysis documents
├── evals/                         # Plugin-level evaluation suite
├── hooks/                         # Session lifecycle hooks
├── references/                    # Architectural patterns
├── scripts/                       # Dispatch and utility scripts
└── skills/                        # Technical capabilities
    ├── business-requirements-capture/
    ├── business-workflow-doc/
    ├── discovery-planning/         # NEW: HARD-GATE brainstorming (post-SMR)
    ├── exploration-handoff/
    ├── exploration-optimizer/
    ├── exploration-orchestrator/
    ├── exploration-session-brief/
    ├── exploration-workflow/
    ├── prototype-builder/          # Full build orchestrator (post-SMR)
    ├── subagent-driven-prototyping/ # NEW: Component-by-component build (post-SMR)
    ├── user-story-capture/
    ├── visual-companion/           # NEW: Layout direction (post-SMR)
    └── deferred/                   # Parked capabilities (not yet active)
```

### 6b — Add Attribution & License section

Add a new `## 📜 Attribution & License` section at the bottom of README.md,
BEFORE the closing line, with the following exact content:

```markdown
---

## 📜 Attribution & License

### Architectural Inspiration: `obra/superpowers`

The `exploration-cycle-plugin` borrows core architectural patterns from
[**obra/superpowers**](https://github.com/obra/superpowers), an open-source
agentic harness by Jesse Vincent (obra).

Specifically, the following patterns were adapted:

| Pattern | Source (superpowers) | Adapted As (this plugin) |
|---|---|---|
| `<HARD-GATE>` execution block | `brainstorming` skill | `discovery-planning` skill |
| Blank-slate subagent per task | Execution harness | `subagent-driven-prototyping` skill |
| Spec Compliance + Code Quality two-stage review | Verification layer | Business Rule Audit + Prototype Walkthrough |
| Linguistic Detox (persona scan) | Jargon policing layer | SME language enforcement across all agents |
| Manifest-Driven Scaffolding | Pre-flight scaffolding | Pre-Phase 0 Silent Discovery |

**superpowers is licensed under the MIT License:**

> MIT License
>
> Copyright (c) Jesse Vincent (obra)
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
> THE SOFTWARE.

Full license: https://github.com/obra/superpowers/blob/main/LICENSE

The `exploration-cycle-plugin` is independently authored and extends these
patterns for a non-technical SME audience. It is not affiliated with or
endorsed by obra/superpowers.
```

---

## Task 7 — Commit

After all tasks are complete, stage and commit:

```bash
git add skills/discovery-planning/
git add skills/visual-companion/
git add skills/subagent-driven-prototyping/
git add skills/prototype-builder/SKILL.md
git add README.md
git rm -r skills/deferred/exploration-orchestrator/
git rm -r skills/deferred/prototype-builder/
git rm skills/deferred/exploration-cycle-orchestrator-agent.md
git rm skills/deferred/prototype-companion-agent.md
git add skills/deferred/SKILL.md   # updated version

git commit -m "feat: fill SMR gap skills, clean deferred/, add superpowers attribution

- Add discovery-planning skill (HARD-GATE brainstorming, SME-led)
- Add visual-companion skill (layout direction before build)
- Add subagent-driven-prototyping skill (component-by-component build)
- Replace prototype-builder SKILL.md stub with full orchestration skill
- Remove orphaned stubs from skills/deferred/ (promoted to active)
- Add obra/superpowers attribution and MIT license notice to README

Architectural patterns adapted from https://github.com/obra/superpowers (MIT)"
```

---

## Verification Checklist

After commit, confirm:

- [ ] `skills/discovery-planning/SKILL.md` exists and contains HARD-GATE session flow
- [ ] `skills/discovery-planning/evals/evals.json` exists
- [ ] `skills/visual-companion/SKILL.md` exists and contains layout option flow
- [ ] `skills/visual-companion/evals/evals.json` exists
- [ ] `skills/subagent-driven-prototyping/SKILL.md` exists and contains component build loop
- [ ] `skills/subagent-driven-prototyping/evals/evals.json` exists
- [ ] `skills/prototype-builder/SKILL.md` is NOT a stub (no "STUB" warning in content)
- [ ] `skills/deferred/exploration-orchestrator/` does NOT exist
- [ ] `skills/deferred/prototype-builder/` does NOT exist
- [ ] `skills/deferred/exploration-cycle-orchestrator-agent.md` does NOT exist
- [ ] `skills/deferred/prototype-companion-agent.md` does NOT exist
- [ ] `README.md` contains "obra/superpowers" and MIT license text
- [ ] `README.md` directory map includes the 3 new skills

---

*Plan authored by Antigravity (Google DeepMind). Execution target: Claude Sonnet 4.6 via GitHub Copilot.*
