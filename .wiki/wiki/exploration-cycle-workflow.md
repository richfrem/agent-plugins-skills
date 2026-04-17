---
concept: exploration-cycle-workflow
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/exploration-workflow/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.083856+00:00
cluster: phase
content_hash: 563ddd866bb09ff6
---

# Exploration Cycle Workflow

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

<example>
<commentary>User wants to run the full Phase A discovery loop on a problem.</commentary>
User: Run the exploration workflow on this problem — we need to understand why users are abandoning the onboarding flow.
Agent: [invokes exploration-workflow, starts Phase A: session brief → requirements capture → handoff package]
</example>

<example>
<commentary>User asks for end-to-end guidance on the exploration cycle.</commentary>
User: Walk me through the full Phase A exploration cycle.
Agent: [invokes exploration-workflow, explains and guides through each phase in order]
</example>

<example>
<commentary>BRD-only requests route to business-requirements-capture, not this skill.</commentary>
User: Generate a BRD from our session captures.
Agent: [invokes business-requirements-capture, NOT exploration-workflow]
</example>

# Exploration Cycle Workflow

This workflow describes the Phase A exploration cycle end-to-end. It runs independently of the Spec-Kitty engineering workflow and produces handoff packages that optionally feed into it.

**Loop patterns**: Adapts the `agent-loops` patterns (`learning-loop` for solo framing sessions, `triple-loop` for orchestrated documentation passes to the requirements-doc-agent sub-agent). These are reference patterns, not runtime dependencies — the current implementation borrows their structure without invoking those skills directly.

**Optimization discipline**: Baseline-first iteration — run one baseline, change one variable per iteration, log keep/discard decisions to `evals/results.tsv`, prefer simplicity over marginal gains.

**Visual reference**: [`exploration-cycle-workflow.mmd`](../../assets/diagrams/exploration-cycle-workflow.mmd)

**Inline Phase A workflow diagram** (machine-readable for agent routing):

```dot
digraph exploration_workflow_phase_a {
  rankdir=TB;
  node [shape=box, style="rounded,filled", fillcolor=white, fontname=Helvetica];
  edge [fontname=Helvetica, fontsize=10];

  node [shape=ellipse] Start [label="Session Trigger"];

  Phase0  [label="Phase 0: Intake\nintake-agent classifies session type\n(greenfield / brownfield / re-entry spike)\nwrites exploration/session-brief.md"];
  HG0     [label="Human Gate:\nbrief clear and confirmed?", shape=diamond, fillcolor=lightyellow];
  Phase1  [label="Phase 1: Requirements Capture\ntriple-loop via CLI (cheap model, many passes)\npass1: problem-framing\npass2: BRD draft\npass2b: workflow diagram (if process flow)\npass3: user stories\npass4: issues + opportunities (optional)"];
  GapCheck [label="check_gaps.py after each pass\n(non-zero exit halts the chain)", shape=diamond, fillcolor=lightyellow];
  HG1     [label="Human Gate:\nreview full capture set", shape=diamond, fillcolor=lightyellow];
  Phase2  [label="Phase 2: Prototype (optional)\nprototype-companion-agent via CLI\noutput: exploration/captures/prototype-notes.md"];
  Phase2b [label="Phase 2b: Business Rule Audit\nbusiness-rule-audit-agent via CLI\nautput: exploration/captures/business-rule-audit.md\nHard stop: resolve all Unresolved Drifts"];
  HG2     [label="Human Gate:\nall drifts resolved?", shape=diamond, fillcolor=lightyellow];
  Phase3  [label="Phase 3: Narrowing Gate\n5-check readiness table\n(problem, shape, constraints, risks, unknowns)"];
  NarrowOK [label="ready for handoff?", shape=diamond, fillcolor=lightyellow];
  MoreCapture [label="Run another capture pass\nor targeted spike", style=dashed];
  Phase4  [label="Pha

*(content truncated)*

## See Also

- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[exploration-cycle-plugin-design-recommendation]]
- [[exploration-cycle-plugin-upgrade-implementation-plan]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/exploration-workflow/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.083856+00:00
