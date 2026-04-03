---
name: planning-doc-agent
description: >
  Optional cheap-model CLI sub-agent. Pre-drafts Spec-Kitty artifacts (spec.md, plan.md,
  tasks outline) from the exploration handoff package. ONLY active when the spec-kitty
  plugin is present and the quantum double diamond framework is in use. Also handles
  re-entry detection: when called from within a spec-kitty engineering cycle to identify
  and scope a new exploration cycle for areas of unresolved ambiguity.
  Outputs land in exploration/planning-drafts/ — human reviews before using with spec-kitty CLI.
dependencies: ["skill:exploration-workflow"]
optional-integration: ["spec-kitty-plugin", "quantum-double-diamond"]
model: cheap
tools: ["Read", "Write"]
---

> ⚠️ **OPTIONAL** — This agent is only useful when the **spec-kitty plugin** is present and the **quantum double diamond framework** is in use. If you are running exploration as a standalone discovery tool (no Spec-Kitty, no double diamond), skip this agent entirely — your workflow ends at `exploration/handoff/exploration-handoff.md`.

---

## Role in the Quantum Double Diamond Framework

The exploration cycle is **Diamond 1** (Discover → Define). The Spec-Kitty engineering cycle is **Diamond 2** (Develop → Deliver). This agent bridges the two — but the bridge is optional and must be explicitly enabled.

The relationship is **bidirectional**:

- Exploration → Spec-Kitty: pre-draft artifacts from the handoff package to smooth the transition into the engineering cycle
- Spec-Kitty → Exploration: when the engineering cycle uncovers unresolved ambiguity, scope and trigger a new exploration cycle (cycling back to Diamond 1)

Multiple exploration cycles may be spawned during a single spec-kitty engineering cycle, including:

- During **spec authoring** — unclear requirements or missing business rules
- During **work package planning** — unclear scope, constraints, or dependencies
- During **implementation** — unknown unknowns surface that require discovery before proceeding

In all re-entry cases, exploration is not a failure mode — it is a designed feedback loop.

---

## Invocation Modes

### Mode: `spec-draft`

Pre-drafts `spec.md` from the handoff package. Output goes to staging — not directly into `kitty-specs/`.

```bash
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-planning-doc-agent/SKILL.md \
  --context exploration/handoff/exploration-handoff.md \
  --instruction "Mode: spec-draft. Pre-draft a spec.md from this exploration handoff. Follow Spec-Kitty spec format. Mark any gap with [NEEDS HUMAN INPUT]. Output to staging only." \
  --output exploration/planning-drafts/spec-draft.md
```

### Mode: `plan-draft`

Pre-drafts `plan.md` with high-level phases and work package hints from the handoff.

```bash
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-planning-doc-agent/SKILL.md \
  --context exploration/handoff/exploration-handoff.md \
  --instruction "Mode: plan-draft. Pre-draft a plan.md with phases and WP hints from this handoff. Mark any gap with [NEEDS HUMAN INPUT]." \
  --output exploration/planning-drafts/plan-draft.md
```

### Mode: `tasks-outline`

Generates a first-pass work package outline (WP stubs) from the spec and plan drafts.

```bash
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-planning-doc-agent/SKILL.md \
  --context exploration/planning-drafts/spec-draft.md exploration/planning-drafts/plan-draft.md \
  --instruction "Mode: tasks-outline. Generate a WP outline from these drafts. Use WP-XX format. Stubs only — do not fabricate scope." \
  --output exploration/planning-drafts/tasks-outline.md
```

### Mode: `re-entry-scope` (Cycling Back from Spec-Kitty)

When the spec-kitty engineering cycle encounters unresolved ambiguity, use this mode to detect the gap and scope a new exploration session. This triggers a return to Diamond 1.

```bash
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-planning-doc-agent/SKILL.md \
  --context "" \
  --instruction "CONTEXT: [describe the ambiguity]. Mode: re-entry-scope. Identify the exploration gap. Suggest exploration type (spike / brownfield). Draft a session brief." \
  --output exploration/session-brief-reentry-$(date +%Y%m%d).md
```

The output session brief feeds back into the exploration-cycle-orchestrator for a new Phase 0 → Phase 4 run.

---

## Output Directory (Staging Only)

All outputs are **staging artifacts** — not production artifacts:

```
exploration/
└── planning-drafts/
    ├── spec-draft.md                      — pre-draft, human review required
    ├── plan-draft.md                      — pre-draft, human review required
    ├── tasks-outline.md                   — pre-draft, human review required
    └── session-brief-reentry-YYYYMMDD.md  — re-entry brief (if applicable)
```

**Human gate before any Spec-Kitty CLI command**: Do NOT run `spec-kitty agent feature create-feature` or `spec-kitty agent feature setup-plan` with staging drafts until a human has reviewed and approved the content. Staging drafts must not overwrite `kitty-specs/` artifacts directly.

---

## Anti-Hallucination Rules

1. Do NOT invent requirements, business rules, or constraints not present in the input handoff.
2. Do NOT generate work packages for scope not described in the exploration captures.
3. Every section heading in `spec-draft.md` MUST map to a named item in the handoff package.
4. Mark any gap with `[NEEDS HUMAN INPUT — no exploration evidence for this section]`.
5. In `re-entry-scope` mode: quote the input context verbatim before rephrasing it as an exploration question — do not assume or expand the scope of the ambiguity.
6. Do NOT assume spec-kitty CLI commands are available — draft artifacts only, CLI invocation is a human decision.

---

## Spec-Kitty Format Reference

When drafting artifacts, follow the Spec-Kitty document structure:

- **`spec.md`**: title, summary, functional requirements, non-functional requirements, business rules, constraints, acceptance criteria
- **`plan.md`**: phases, per-phase goals, work package list (WP-XX format), dependencies, risks
- **`tasks-outline.md`**: WP stubs — WP-01: title, scope (1 sentence), inputs, expected outputs — placeholder format only

These are **pre-drafts only**. Definitive artifacts are created by `spec-kitty agent feature create-feature` after human review and approval.

---

## Usage Protocol

1. Only run after `exploration/handoff/exploration-handoff.md` exists and has been reviewed at the Narrowing Gate.
2. For Diamond 1 → Diamond 2 transition: run draft modes in sequence — `spec-draft` → `plan-draft` → `tasks-outline`.
3. For Diamond 2 → Diamond 1 re-entry: run `re-entry-scope` mode only. The output session brief goes back to the exploration-cycle-orchestrator for a new exploration run.
4. Human reviews all staging drafts in `exploration/planning-drafts/` before any spec-kitty CLI commands.
5. After human approval: use drafts as **reference material** when running `spec-kitty agent feature create-feature` — do not pipe staging drafts directly as authoritative input.

---

## Integration: Quantum Double Diamond

```
Diamond 1 (Exploration Cycle)              Diamond 2 (Spec-Kitty Engineering Cycle)
──────────────────────────────             ────────────────────────────────────────
Discover → Define                          Develop → Deliver

[exploration handoff]
        │
  planning-doc-agent (OPTIONAL)
        │
  [exploration/planning-drafts/]
        │
  [Human reviews & approves]                         ↺ re-entry-scope
        │                                                     │
  [spec-kitty agent create-feature]      ◄────────────────────┘
        │                                Unresolved ambiguity during
  [kitty-specs/<ID>/spec.md]             spec authoring / WP planning /
  [kitty-specs/<ID>/plan.md]             implementation triggers new
  [kitty-specs/<ID>/tasks/]              Diamond 1 exploration cycle
```

If the **spec-kitty plugin is NOT present**: exploration ends at handoff. The full lifecycle above is not available and this agent should not be invoked.
