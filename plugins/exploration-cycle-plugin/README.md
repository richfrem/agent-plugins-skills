# GenAI Double Diamond: The Operating System for Discovery

The **exploration-cycle-plugin** is a technical implementation of the **GenAI Double Diamond** framework — a structured but adaptive system that puts AI-powered exploration directly into the hands of Subject Matter Experts (SMEs) and Business Area Experts (BAEs).

It bridges the maturity gap between raw intent (*The Vibe*) and a hardened engineering contract (*The Spec*), while recognizing that **not every problem needs software, and not every solution needs formal engineering.**

![The GenAI Double Diamond — Opportunities 3 & 4](assets/resources/design-thinking/infographics/Opportunities-3-4-Prototyping-and-Engineering.png)

**Opportunity 3** (this plugin) is the Discovery Loop: explore, define, prototype, validate.
**Opportunity 4** is the Engineering Factory: spec-driven development, security hardening, production deployment. The **Handoff & Risk Gate** between them determines whether Opportunity 4 is even needed.

See also: [GenAI Double Diamond Flowchart](assets/diagrams/genai-double-diamond.mmd) | [Hybrid Workflow Diagram](assets/diagrams/hybrid-workflow.mmd)

---

## The Belief: Democratizing AI

This plugin exists because of a simple belief: **the people closest to the problem should be the ones exploring the solution.**

Today, when a business expert has an idea — a process improvement, a new internal tool, a workflow fix — they enter a queue. They wait for a Business Analyst to translate their vision. Then a UX designer interprets it. Then a developer builds what they understood. Each handoff introduces translation errors, delays, and cost. A $5,000 problem gets a $200,000 solution that doesn't quite solve it.

The exploration-cycle-plugin changes the equation:

- **Any SME** can run a structured discovery session with AI guidance — no technical background required
- **A fleet of cheap AI sub-agents** handles the work that used to require a full BA/UX/dev team: requirements gathering, process documentation, prototyping, user story capture, workflow mapping
- **The SME stays in control** — the AI asks questions, the human makes decisions. Every phase has a hard gate requiring explicit SME approval before proceeding
- **The output is whatever the problem actually needs** — a software prototype, a process map, a policy recommendation, a requirements document, or a "don't build this" conclusion. All are valid, high-value outcomes

The cost of exploration drops from tens of thousands of dollars and weeks of calendar time to a single afternoon conversation. Ideas that would never have been worth a formal project can now be explored, validated, and either shipped or killed — cheaply and safely.

---

## Core Principles

### 1. Right Problem First (The Inner Double Diamond)

The most expensive mistake in software development is building the right thing for the wrong problem. The UK's Blue Badge digitization project nearly built a sophisticated document verification portal — until service designers discovered the real problem was confusing policy language. A rewrite of the questions saved millions.

Phase 1 of the exploration loop contains its own double diamond:

```
Phase 1: Discovery Planning
├── DIVERGE: What's the problem? Who's affected? What does good look like?
├── CONVERGE: Intervention Check — is this a technology problem, a process
│   problem, a policy problem, or a communication problem?
├── DIVERGE: What must the solution deliver? What are the constraints?
└── CONVERGE: Discovery Plan — approved by SME before anything else happens
```

The **Intervention Check** (Q4) is the moment where the Scouting Party earns its keep. It explicitly asks: *"Is building something the right intervention here, or could this be solved by changing a rule, simplifying a process, or removing a step entirely?"*

If the answer is "don't build" — that's a success, not a failure. You discovered it in 20 minutes instead of 6 months.

### 2. Output-Agnostic

Not every exploration produces software. The plugin adapts to four session types:

| Type | What it produces | When to use |
|------|-----------------|-------------|
| **Greenfield** | Working prototype + handoff package | Building a new app or system from scratch |
| **Brownfield** | Features built into existing codebase | Adding to or modifying an existing application |
| **Analysis/Docs** | Requirements, process maps, policies, analysis | Non-software deliverables: legacy code analysis, workflow design, strategic planning, business process documentation |
| **Spike** | Investigation findings, may loop | Exploring a question or technology, flexible phases |

Phase 2 (Visual Blueprinting) adapts too — presenting UI layouts for software, process flow structures for workflows, or document structures for reports and analysis. The visual-companion skill reads the Discovery Plan and proposes options appropriate to the output type.

### 3. Quality Without Overhead

Even prototypes need validation — the prototype is the **evidence** that the exploration captured the right thing. If the prototype doesn't match the Discovery Plan, the SME reviews the wrong behavior, the handoff describes the wrong system, and the engineering team builds from a flawed spec.

But validation doesn't mean heavyweight process. The execution discipline scales with the session:
- **Greenfield/Brownfield**: Git worktree isolation, TDD per component, two-stage code review (plan alignment + quality), structured branch finishing
- **Analysis/Docs**: Outputs validated against Discovery Plan requirements, checked for completeness and contradictions
- **Spike**: Flexible — the SME decides what validation is appropriate as the investigation unfolds

### 4. Cheap Exploration, Smart Dispatch

The plugin uses a tiered dispatch strategy to minimize token cost without sacrificing quality. Full details: `references/dispatch-strategies.md`.

| Dispatch Strategy | Simple/Mechanical Tasks | Complex/Multi-File Tasks | Orchestration/Planning |
|---|---|---|---|
| **Copilot CLI** (recommended if available) | `gpt-5-mini` — free, unlimited | `claude-sonnet` — 1 premium request, batched dense | Current model (orchestrator) |
| **Claude Sub-agents** | `haiku` — cheapest | `sonnet` — mid-tier | Current model (orchestrator) |
| **Direct** | Inline | Inline | Inline |

The key insight: Copilot Pro charges per **request**, not per token. One dense prompt with 7 file specifications costs the same as one small prompt. The orchestrator (this skill, running on the primary model) never delegates judgment — only implementation.

**Token efficiency across turns:** Context cost compounds — every turn in a multi-turn session re-pays the full context window cost. The dispatch strategy applies not just to build tasks but to Q&A clarification passes too: batch questions, dispatch a cheap model to collect structured answers, read the output file back. This keeps the orchestrator's expensive context reserved for coordination and synthesis, not interactive back-and-forth.

### 5. Fast by Default, Safe by Design

Not everything needs a formal engineering cycle. The **TierGate** (Risk & Rigor Assessment) during handoff determines the proportional delivery path.

The SME answers four yes/no questions — each with a one-sentence evidence note — and the tier is determined automatically:

| Question | Yes → |
|---|---|
| Handles PII or sensitive data? | Tier 2 or 3 |
| Public-facing or external users? | Tier 2 or 3 |
| Requires high-privilege access? | Tier 3 |
| Financial transactions or compliance? | Tier 3 |

| Outcome | Risk Profile | What Happens Next |
|---|---|---|
| **Throwaway** | Idea proved non-viable during exploration | Session closed. Learning preserved at near-zero cost. |
| **Tier 1 (Low)** | All answers "no" — internal utility, no PII | BAE deploys directly — no formal engineering needed |
| **Tier 2 (Moderate)** | Any "yes" on Q1 or Q2 — internal data or broader exposure | Security review & mandatory Red Teaming before deployment |
| **Tier 3 (High)** | "yes" on Q3 or Q4, or PII + public-facing | Mandatory formal engineering cycle (Opportunity 4) with architectural hardening |

Answers and evidence are recorded verbatim in the handoff package. A missing or vague answer blocks finalization — the gate is non-bypassable by design.

A low-risk internal tool ships immediately. A high-risk public system gets the rigor it needs. A failed idea dies cheaply.

---

## The Exploration Loop

The plugin orchestrates a 4-phase discovery loop, managed by the `exploration-workflow` skill via a conversational dashboard. Phases can be skipped based on session type.

### Phase 1: Problem Framing (`discovery-planning`)
The inner double diamond. Five guided questions, one at a time, with an Intervention Check that asks whether software is even the right answer. Produces an SME-approved Discovery Plan. **Hard gate: nothing proceeds without explicit SME approval.**

### Phase 2: Visual Blueprinting (`visual-companion`)
Confirms the structure and shape of the output before any building starts. For software: UI layouts. For workflows: process flow structures. For documents: report structures. Optional for brownfield and analysis sessions.

### Phase 3: Build (`subagent-driven-prototyping`)
Component-by-component construction with per-component validation. Brownfield sessions build directly into the existing codebase. Greenfield sessions produce standalone prototypes. Powered by superpowers execution discipline (worktrees, TDD, code review). Skipped for analysis/docs sessions.

### Phase 4: Handoff & Specs (`exploration-handoff`)
Automated capture of business requirements, user stories, and workflow diagrams, synthesized into a structured handoff package. Includes the TierGate risk assessment that determines the delivery path. Optional for brownfield self-builds.

### Early Exit
At any phase, if the SME says "this isn't going to work" — the session closes cleanly, preserving what was learned. Failing fast and cheap is a valid, valuable outcome.

---

## Bidirectional Re-Entry

Engineering is rarely linear. When Opportunity 4 (Execution) uncovers an "unknown unknown" — unresolved ambiguity, a missed edge case, a shift in vision — the `planning-doc-agent` triggers a re-entry cycle back to Opportunity 3. The team resolves the gap in low-cost discovery mode without losing momentum in the production factory.

---

## Built on `obra/superpowers`

The `exploration-cycle-plugin` is built on top of [**obra/superpowers**](https://github.com/obra/superpowers), an open-source agentic harness by Jesse Vincent (obra). Superpowers is a **required runtime dependency** — the execution discipline skills are invoked directly during Phase 3.

### What we borrow (and why it's brilliant)

Superpowers provides world-class execution discipline for AI-assisted development. Its patterns for context isolation, verification, and structured workflows are the foundation this plugin builds on:

| Pattern | Superpowers Source | How We Use It |
|---|---|---|
| `<HARD-GATE>` execution block | `brainstorming` skill | `discovery-planning` — SME approval gate before anything proceeds; canonical redirect text in `references/hard-gate-enforcement.md` |
| Blank-slate context isolation | `subagent-driven-development` | `subagent-driven-prototyping` — fresh sub-agent per component |
| Two-stage verification | Spec + Quality reviewers | Plan alignment check + Quality check per component |
| Git worktree isolation | `using-git-worktrees` | Isolated workspace before any build work |
| TDD cycle | `test-driven-development` | Verification that each component matches the Discovery Plan |
| Branch finishing | `finishing-a-development-branch` | Structured merge/PR/cleanup flow |
| Model tiering | Cheap → standard → capable | 3 dispatch strategies with decision tree per task complexity |
| Linguistic Detox | Jargon policing | Plain language enforcement across all SME-facing agents |

### What we add

The exploration-cycle-plugin extends superpowers into territory it wasn't designed for — the fuzzy front end before a spec exists:

| Capability | What It Does | Why Superpowers Doesn't Cover It |
|---|---|---|
| **Discovery Planning with Intervention Check** | Guided problem framing that asks whether software is even the right answer | Superpowers assumes the spec already exists — it doesn't question whether to build |
| **Session Type Adaptation** | Greenfield, brownfield, analysis/docs, spike — each with different phase requirements | Superpowers has one workflow for all development |
| **Visual Blueprinting** | Adaptive structure confirmation — UI layouts, process flows, or document structures | Superpowers doesn't address pre-build design confirmation |
| **Output-Agnostic Exploration** | Non-software deliverables: process maps, policy recommendations, business analysis | Superpowers is code-focused |
| **TierGate with Four Outcomes** | Risk assessment that routes to direct deployment, security review, formal engineering, or throwaway | Superpowers assumes all work enters the engineering pipeline |
| **Copilot CLI Dispatch** | Token-optimized orchestration using free/cheap models for mechanical tasks | Superpowers uses Claude model tiering only |
| **SME-First Language** | Every user-facing message in plain language — "build" not "scaffold", "check" not "validate" | Superpowers speaks to developers |
| **Early Exit / Fail Fast** | Clean session kill at any phase, preserving learning | Superpowers doesn't model session abandonment |
| **Bidirectional Re-Entry** | Loop from engineering back to discovery when unknowns surface | Superpowers is forward-only |

### The relationship

```
exploration-cycle-plugin              obra/superpowers
============================          ================
Owns the WHAT                         Owns the HOW
(discovery, framing, intervention     (isolation, dispatch, testing,
 check, layout, handoff, risk gate)    review, finishing)

Phase 1: Problem Framing         →   (standalone)
Phase 2: Visual Blueprinting     →   (standalone)
Phase 3: Build                   →   uses: worktrees, sub-agent dispatch, TDD, code review
Phase 4: Handoff                 →   (standalone)
```

**superpowers is licensed under the MIT License.** Full text: https://github.com/obra/superpowers/blob/main/LICENSE

The `exploration-cycle-plugin` is independently authored and not affiliated with or endorsed by obra/superpowers.

---

## Technical Architecture

### CLI Invocation Pattern (Cheap Sub-Agents)
All documentation sub-agents are invoked via a dedicated `dispatch.py` wrapper for cost efficiency and context isolation:

```bash
python ./skills/exploration-workflow/scripts/dispatch.py \
  --agent ./agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md \
  --instruction "Mode: business-requirements. Extract functional requirements." \
  --output exploration/captures/brd-draft.md
```

### Directory Structure
```text
exploration-cycle-plugin/
├── README.md                       # This file — vision, principles, architecture
├── OVERVIEW.md                     # Deeper conceptual dive into the GenAI Double Diamond
├── BAE-start-guide.md              # Quick start guide for Business Area Experts
├── agents/                         # Vision Translators and Scribes
├── assets/
│   ├── diagrams/                   # Technical flowcharts (Mermaid)
│   ├── resources/design-thinking/  # Framework infographics and references
│   └── templates/                  # Dashboard and session templates
├── references/
│   ├── hard-gate-enforcement.md    # Canonical HARD-GATE redirect text (shared by all agents)
│   ├── environment-check.md        # Pre-flight superpowers + dispatch strategy check
│   ├── dispatch-strategies.md      # Dispatch tiers, task complexity guide, token efficiency
│   └── agent-loop-patterns.md      # Loop architecture reference (dual-loop, learning-loop)
├── skills/
│   ├── discovery-planning/         # Phase 1: Problem framing with Intervention Check
│   ├── visual-companion/           # Phase 2: Adaptive structure confirmation
│   ├── prototype-builder/          # Phase 3 coordinator: orchestrates build cycle
│   ├── subagent-driven-prototyping/# Phase 3 builder: component-by-component construction
│   ├── exploration-handoff/        # Phase 4: Synthesis, TierGate, and handoff packaging
│   ├── exploration-workflow/       # Orchestrator: state machine managing the full loop
│   ├── business-requirements-capture/
│   ├── business-workflow-doc/
│   ├── exploration-optimizer/
│   ├── exploration-session-brief/
│   └── user-story-capture/
└── requirements.in                 # Python dependencies
```

### Installation

**Claude Code (recommended):**
```bash
# Install superpowers first (required dependency)
claude mcp add-plugin orba/superpowers

# Then install exploration-cycle-plugin
claude mcp add-plugin richfrem/agent-plugins-skills --path plugins/exploration-cycle-plugin
```

**Manual installation:**
1. Clone `https://github.com/obra/superpowers` into your plugins directory
2. Clone or symlink `plugins/exploration-cycle-plugin` from this repo into your plugins directory
3. Ensure both are discoverable by your agent harness (Claude Code, Copilot CLI, Gemini CLI, etc.)

**Verification:**
```bash
# In Claude Code
/skills  # should list both exploration-workflow and using-git-worktrees
```

---

## Getting Started

**For Business Area Experts:** See the [BAE Quick Start Guide](./BAE-start-guide.md) for a plain-language walkthrough.

**For AI agents:** The canonical entry point is the `exploration-workflow` skill. Say "start an exploration" or "let's explore this idea" to begin.

**Recommended first-time flow:** Start with the `intake-agent` for an interactive onboarding conversation, then let `exploration-workflow` guide the rest.

*See [OVERVIEW.md](OVERVIEW.md) for a deeper conceptual dive into the GenAI Double Diamond framework.*
