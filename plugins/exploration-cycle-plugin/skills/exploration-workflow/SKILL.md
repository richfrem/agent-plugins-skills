---
name: exploration-workflow
description: >
  Phase A exploration cycle workflow. Structured guidance for running discovery sessions,
  capturing requirements via cheap-model CLI sub-agent (requirements-doc-agent), observing
  prototypes, and producing handoff packages for downstream planning or spec-driven
  engineering. Adapted from autoresearch-style iteration discipline (baseline-first,
  one-variable loop) and doc-coauthoring structured capture. Runs independently — no
  Spec-Kitty CLI required.
allowed-tools: Bash, Read, Write
---

# Exploration Cycle Workflow

This workflow describes the Phase A exploration cycle end-to-end. It runs independently of the Spec-Kitty engineering workflow and produces handoff packages that optionally feed into it.

**Loop patterns**: Adapts the reference `agent-loops` patterns in [`temp/agent-plugins-skills/plugins/agent-loops/README.md`](../../../../temp/agent-plugins-skills/plugins/agent-loops/README.md) — especially `learning-loop` for optional solo framing sessions and `dual-loop` as the conceptual model for orchestrated documentation passes to the requirements-doc-agent sub-agent.

These are **reference patterns, not runtime skill dependencies** in Phase A. The current implementation borrows their structure but does not invoke those skills directly.

**Optimization discipline**: Adapts the [autoresearch](../../../../temp/autoresearch/program.md) loop — run one baseline first, change one variable per iteration, log keep/discard decisions to `evals/results.tsv`, prefer simplicity over marginal gains.

**Visual reference**: [`exploration-cycle-workflow.mmd`](./exploration-cycle-workflow.mmd)

**Orchestrator agent**: [`exploration-cycle-orchestrator-agent`](../../agents/exploration-cycle-orchestrator-agent.md)

---

## Running Independently of Spec-Kitty

This workflow does **not** require Spec-Kitty CLI. Output artifacts _may_ feed into Spec-Kitty, but the exploration cycle is self-contained:

```
exploration/
├── session-brief.md         — session framing (from template)
├── captures/
│   ├── problem-framing.md   — problem, users, goals
│   ├── brd-draft.md         — business requirements, rules, constraints
│   ├── user-stories-draft.md— user stories
│   ├── issues-opportunities.md — issue/opportunity themes (optional)
│   └── prototype-notes.md   — observations from prototype sessions (optional)
└── handoff/
    └── exploration-handoff.md — ready for spec or planning update
```

---

## Phase 0: Intake and Session Brief

The standard Phase A path starts with the interactive [`intake-agent`](../../agents/intake-agent.md), not with a blank manual template copy.

The intake-agent is intentionally the one expensive step in the loop: it runs in the primary model context so the session starts with a higher-quality classification and a better pre-filled brief. The cheaper CLI sub-agents are used after this point.

Standard path:

```bash
# interactive, main-session step
# intake-agent writes exploration/session-brief.md
```

Manual fallback if intake-agent is unavailable:

```bash
cp architecture/templates/exploration-session-brief-template.md exploration/session-brief.md
```

- `Exploration type`: `greenfield`, `brownfield`, or `re-entry spike`
- **Brownfield**: fill in the "Current System Behavior" section before starting captures
- **Re-entry spike**: describe the specific engineering question that blocked progress

**Human gate**: Confirm brief is clear before proceeding to capture.

---

## Phase 1: Requirements Capture (Dual-Loop via Copilot CLI)

The standard Phase A framing path is:

1. `intake-agent` classifies the session and drafts `session-brief.md`
2. `requirements-doc-agent` in `problem-framing` mode produces the first framing artifact

The standalone [`problem-framing-agent`](../../agents/problem-framing-agent.md) remains available as an **optional interactive alternative** when you want a higher-touch framing conversation. Do not run all three framing steps in sequence in the standard path.

Dispatch the requirements-doc-agent as a cheap CLI sub-agent. Each pass is focused on one artifact — do not try to capture everything in one invocation. For every pass, include the session brief plus all prior relevant captures so context accumulates instead of collapsing to only the most recent file.

### Pass 1: Problem Framing
```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
  --context exploration/session-brief.md \
  --instruction "Mode: problem-framing. Capture the problem statement, user groups, goals, and initial scope hypotheses." \
  --output exploration/captures/problem-framing.md
```

### Pass 2: Business Requirements
```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md \
  --instruction "Mode: business-requirements. Extract functional requirements, business rules, and constraints." \
  --output exploration/captures/brd-draft.md
```

### Pass 2b: Business Workflow Documentation (when process flow is relevant)

Run when the captures describe a multi-step process, approval flow, or state machine:

```bash
python3 plugins/exploration-cycle-plugin/skills/business-workflow-doc/scripts/generate_workflow.py \
  --input exploration/session-brief.md exploration/captures/brd-draft.md \
  --output exploration/captures/workflow-map.md
# Then fan out to agent to populate the Mermaid skeleton:
# python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
#   --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
#   --context exploration/captures/workflow-map.md \
#   --instruction "Mode: workflow-map. Fill in the Mermaid diagram with actual process steps from the captures." \
#   --output exploration/captures/workflow-map.md
```

### Pass 3: User Stories
```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md exploration/captures/brd-draft.md \
  --instruction "Mode: user-stories. Generate an initial user story set from the requirements." \
  --output exploration/captures/user-stories-draft.md
```

### Pass 3b: Gherkin Acceptance Criteria (optional — high-fidelity stories)

Run when you need formal `Given / When / Then` AC blocks ready for backlog entry:

```bash
python3 plugins/exploration-cycle-plugin/skills/user-story-capture/scripts/execute.py \
  --input exploration/captures/brd-draft.md exploration/captures/user-stories-draft.md \
  --format gherkin \
  --output exploration/captures/user-stories-gherkin.md
```

### Pass 4: Issues and Opportunities (optional)
```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md exploration/captures/brd-draft.md \
  --instruction "Mode: issues-and-opportunities. Extract issue themes, challenges, and opportunities." \
  --output exploration/captures/issues-opportunities.md
```

After each pass, run the gap checker before dispatching the next one. If the exit code is non-zero, stop, refine the session brief, and re-run from the affected pass — do not push a weak context chain through the remaining passes.

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/check_gaps.py \
  --files exploration/captures/problem-framing.md \
  --threshold 3
# Repeat after each pass, pointing --files at the file just written.
# Non-zero exit halts the chain.
```

**Human gate**: Review the full capture set after the pass chain completes.

---

## Phase 2: Prototype Session (Optional)

If exploration needs a runnable prototype to resolve ambiguity:

1. Use `prototype-builder` skill to generate the prototype.
2. After running it, dispatch the prototype-companion-agent for observation capture:

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/prototype-companion-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md exploration/captures/brd-draft.md exploration/captures/user-stories-draft.md \
  --optional-context exploration/captures/issues-opportunities.md \
  --instruction "Mode: prototype-observations. Capture implied requirements, assumptions, and edge cases observed." \
  --output exploration/captures/prototype-notes.md
```

---

## Phase 2b: Business Rule Audit (Required gate — do not skip)

Run after prototype observations are captured and before the Narrowing Gate. This step checks that the prototype's implied behaviour does not contradict the business rules in `brd-draft.md`. It is **not optional** — skipping it means the narrowing gate and handoff will not catch logic drift introduced during prototyping.

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/business-rule-audit-agent.md \
  --context exploration/captures/brd-draft.md \
  --optional-context exploration/captures/prototype-notes.md \
  --instruction "Run a full business rule audit. Compare all BR-xxx rules in the BRD against the prototype observations (if present). Produce a structured report with a required ## Unresolved Drifts section. List every rule with no corresponding evidence. If no prototype-notes are present, flag all rules as unverified." \
  --output exploration/captures/business-rule-audit.md
```

Then check the output for unresolved drifts before proceeding:

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/check_gaps.py \
  --files exploration/captures/business-rule-audit.md \
  --threshold 0
# Threshold 0: any [NEEDS HUMAN INPUT] marker in the audit report is a hard stop.
# Resolve all drifts before the Narrowing Gate.
```

**Human gate**: Read `## Unresolved Drifts` in the audit report. Each item must be resolved (clarified in `brd-draft.md` or accepted as a known constraint) before handoff.

---

## Phase 3: Narrowing Gate

Before handoff, confirm readiness. Each item requires a one-sentence evidence field:

| Check | Evidence Required |
|-------|------------------|
| Problem is clear | One sentence from `problem-framing.md` |
| Product shape is understood | Summary line from `brd-draft.md` |
| Key constraints are known | Constraint count from `brd-draft.md` |
| Major risks are understood | Top risk from `issues-opportunities.md` |
| Remaining unknowns are acceptable | Decision rationale (human judgment) |

If NOT ready: run another capture pass or a targeted spike. Do not force handoff — premature handoff produces unusable specs.

---

## Phase 4: Handoff Preparation

Synthesize all captures into a single handoff package:

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/handoff-preparer-agent.md \
  --context exploration/captures/problem-framing.md exploration/captures/brd-draft.md exploration/captures/user-stories-draft.md \
  --optional-context exploration/captures/issues-opportunities.md exploration/captures/prototype-notes.md exploration/captures/business-rule-audit.md \
  --instruction "Synthesize all exploration captures into a structured handoff package. If a business rule audit is present, include its Unresolved Drifts section as a top-level risk section." \
  --output exploration/handoff/exploration-handoff.md
```

Review output against `architecture/templates/exploration-handoff-template.md`.

**Recommended next step options**:
- Generate formal spec using Spec-Kitty
- Update roadmap and defer implementation
- Run a targeted exploration spike for remaining open questions

---

## Phase 5: Planning Draft — Optional Integration with Spec-Kitty

> ⚠️ **OPTIONAL** — Only relevant when the **spec-kitty plugin** is installed and you are using the **quantum double diamond framework**. If running exploration standalone, skip this phase. Your workflow ends at Phase 4.

This phase uses the [`planning-doc-agent`](../../agents/planning-doc-agent.md) to pre-draft Spec-Kitty artifacts from the handoff package. Outputs land in a **staging area** — a human must review and approve before any spec-kitty CLI commands are run.

### Running the three draft modes in sequence

```bash
# Mode 1: spec-draft
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/planning-doc-agent.md \
  --context exploration/handoff/exploration-handoff.md \
  --instruction "Mode: spec-draft. Pre-draft a spec.md from this handoff. Mark any gap with [NEEDS HUMAN INPUT]." \
  --output exploration/planning-drafts/spec-draft.md

# Mode 2: plan-draft
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/planning-doc-agent.md \
  --context exploration/handoff/exploration-handoff.md \
  --instruction "Mode: plan-draft. Pre-draft a plan.md with phases and WP hints. Mark any gap with [NEEDS HUMAN INPUT]." \
  --output exploration/planning-drafts/plan-draft.md

# Mode 3: tasks-outline (reads the two drafts above)
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/planning-doc-agent.md \
  --context exploration/planning-drafts/spec-draft.md exploration/planning-drafts/plan-draft.md \
  --instruction "Mode: tasks-outline. Generate a WP outline. WP-XX stubs only — do not fabricate scope." \
  --output exploration/planning-drafts/tasks-outline.md
```

**Human gate**: Review all staging drafts. Approve before running `spec-kitty agent feature create-feature`.

---

## Re-Entry: Cycling Back from Spec-Kitty to Exploration

The relationship between exploration and formal engineering is **bidirectional**. When the engineering cycle uncovers unresolved ambiguity — during spec authoring, work package planning, or implementation — a new exploration cycle is spawned. This is not a failure; it is a designed feedback loop in the quantum double diamond framework.

### Re-entry with Spec-Kitty present

```bash
# Triggered from within the spec-kitty engineering cycle.
# Step 1: write the blocker description to a temp file (dispatch.py requires a real file, not an empty string)
# Use a session-scoped path for parallel session safety: /tmp/reentry-context-$$.md
echo "CONTEXT: [describe the blocking ambiguity or engineering question here]" > /tmp/reentry-context-$$.md

# Step 2: dispatch
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/planning-doc-agent.md \
  --context /tmp/reentry-context-$$.md \
  --instruction "Mode: re-entry-scope. Identify the exploration gap. Suggest exploration type. Draft a session brief." \
  --output "exploration/session-brief-reentry-$(date +%Y%m%d).md"
```

Feed the output session brief back into the exploration-cycle-orchestrator and restart from Phase 0 for the scoped re-entry.

### Standalone re-entry without Spec-Kitty

If Spec-Kitty is not present, re-entry is scoped by running the intake-agent again with the engineering ambiguity as the new trigger. Classify it as a `re-entry spike`, draft a fresh `session-brief.md`, and restart from Phase 0. No planning-doc-agent is required for the standalone path.

Multiple re-entry cycles per engineering run are expected and supported.

---

## Optimization Loop (Phase D Preview)

Once the Phase A baseline is established (3+ sessions completed), use the autoresearch-style loop via `exploration-optimizer`:

- Establish baseline: run 3 sessions, log artifact quality scores to `evals/results.tsv`
- Change one variable per iteration: prompt text, capture pass ordering, session brief structure
- Keep only changes that measurably improve handoff usefulness
- Prefer simpler capture sequences over marginally better complex ones

---

## Phase A Gate Criteria (Before Proceeding to Phase B)

The Phase A slice is validated when **all three** are true:

1. At least 3 exploration sessions complete the full loop (brief → captures → handoff)
2. At least 2 handoff packages are used as input to a downstream spec or planning update
3. The downstream spec/planning author rates at least 2 of 3 handoff packages as "materially helpful" in post-run survey

The helpfulness rating is made **after** the downstream spec or planning draft is complete, not at handoff time.

Do not build the Phase B requirements-scribe specialist agent until these criteria are met.
