# Exploration Cycle Plugin Architecture Reference

This plugin is the implementation boundary for the exploration-cycle system described in:

- [architecture/exploration-cycle-architecture.md](../../../architecture/exploration-cycle-architecture.md)
- [architecture/exploration-cycle-spec.md](../../../architecture/exploration-cycle-spec.md)
- [ADRs/001_augment_spec_kitty_with_exploration_cycle.md](../../../ADRs/001_augment_spec_kitty_with_exploration_cycle.md)

## Intent

The plugin provides:

- an orchestrated multi-agent exploration loop
- skill-level generation of core exploration artifacts
- prototype generation support
- handoff generation into formal spec workflows
- optimization loops for improving the exploration process itself

It is intentionally not designed around a specific MCP architecture, model vendor, or IDE shell. The plugin acts as a repository-native workflow package in the same general spirit as Spec-Kit or Spec-Kitty extensions.

Implementation is incremental. The repository validates the smallest useful exploration loop before hardening this plugin boundary into a richer workflow package.

---

## Phase A Implementation (Current)

### Agents

| Agent | Role | Status |
|-------|------|--------|
| `intake-agent` | Front-door interviewer — clarifies session type, pre-fills session brief | ✅ Phase A |
| `exploration-cycle-orchestrator-agent` | Coordinates the full Phase A loop | ✅ Phase A |
| `requirements-doc-agent` | Cheap CLI sub-agent — 5 capture modes | ✅ Phase A |
| `problem-framing-agent` | Optional higher-touch interactive framing alternative | ✅ Phase A |
| `prototype-companion-agent` | Cheap CLI sub-agent — prototype observation capture | ✅ Phase A |
| `handoff-preparer-agent` | Cheap CLI sub-agent — synthesizes captures into handoff | ✅ Phase A |
| `planning-doc-agent` | Optional — pre-drafts Spec-Kitty artifacts; re-entry scope mode | ✅ Phase A |

### Skills

| Skill | Purpose | Status |
|-------|---------|--------|
| `exploration-workflow` | End-to-end Phase A workflow guidance | ✅ Phase A |
| `exploration-orchestrator` | Orchestration patterns and routing | ✅ Phase A |
| `exploration-session-brief` | Session brief creation and refinement | ✅ Phase A |
| `business-requirements-capture` | BRD generator — `brd / rules / constraints` modes | ✅ Phase A |
| `user-story-capture` | Story generator — `standard / gherkin` AC formats | ✅ Phase A |
| `business-workflow-doc` | Mermaid diagram generator — `flowchart / stateDiagram / sequenceDiagram` | ✅ Phase A |
| `prototype-builder` | Exploratory prototype generation | ✅ Phase A |
| `exploration-handoff` | Handoff synthesis | ✅ Phase A |
| `exploration-optimizer` | Autoresearch-style loop optimization | ✅ Phase A |
| `exploration-session-brief` | Session brief management | ✅ Phase A |

### Phase A Capture Output Classes

All of these are now available in Phase A:

1. Living discovery document / session brief
2. Business requirements document (functional, non-functional, rules, constraints)
3. Business workflow diagrams (Mermaid: flowchart, state machine, sequence)
4. User stories — standard format + Gherkin Acceptance Criteria
5. Issues, challenges, and opportunities capture
6. Prototype evidence and observations
7. Exploration handoff package

---

## Next Capability Groups (Phase B+)

1. **Phase B**: Background requirements scribe — autonomous passive capture during sessions
2. **Phase C**: Full multi-agent orchestrator with telemetry and routing rules
3. **Phase D**: Goals & objectives capture, roadmap routing, advanced story specialization

---

## Evaluation Expectations

The exploration-cycle plugin is designed from the start for repeated-run evaluation.

Early runs capture manual friction notes and outcome summaries to establish a baseline before adding optimization machinery.

The orchestrator is expected to emit or maintain:

- loop-state telemetry
- routing and agent-invocation traces
- handoff and re-entry decisions
- run-level artifact outcomes
- a post-run orchestrator survey

The `exploration-optimizer` skill uses those outputs in a baseline-first, one-hypothesis-at-a-time improvement loop.