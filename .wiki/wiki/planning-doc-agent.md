---
concept: planning-doc-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/exploration-workflow/planning-doc-agent.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.086582+00:00
cluster: spec
content_hash: fd2557d6fe700846
---

# Planning Doc Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
  --agent .agents/skills/exploration-c

*(content truncated)*

## See Also

- [[exploration-cycle-plugin-planning-doc-agent]]
- [[exploration-cycle-plugin-planning-doc-agent]]
- [[discovery-planning-agent]]
- [[discovery-planning-agent]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/exploration-workflow/planning-doc-agent.md`
- **Indexed:** 2026-04-17T06:42:10.086582+00:00
