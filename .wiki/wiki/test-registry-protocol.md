---
concept: test-registry-protocol
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-skill-improvement/references/testing/test-registry-protocol.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.184950+00:00
cluster: plugin-code
content_hash: 3eb36351c68a16c9
---

# Test Registry Protocol

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Test Registry Protocol

Every loop cycle that tests a skill, workflow, script, or agent interaction MUST be
documented in the test registry. The registry is how the OS learns which tests revealed
useful information, which test designs were weak, and how to design better tests over time.

---

## Registry Locations

```
context/memory/tests/
  registry.md                           <- index of all test scenarios (human-readable)
  [CYCLE_ID]_[TARGET_SLUG].md           <- one file per cycle with full scenario + results
```

`registry.md` is the index. Every closed cycle gets one row. It is read at Orientation
so that ORCHESTRATOR designs each new test informed by what was tried before.

---

## Before the Test: Document the Scenario

ORCHESTRATOR MUST write the test scenario record BEFORE emitting `task.assigned`.
Save to `context/memory/tests/[CYCLE_ID]_[TARGET_SLUG].md`:

```markdown
# Test Scenario: [CYCLE_ID] — [TARGET_SLUG]

## Design
- **Target**: [skill/script/hook/workflow being tested]
- **Hypothesis**: [what change or question is this test designed to answer]
- **Why this target now**: [what prior result, survey finding, or friction pattern motivated this]
- **What prior tests told us**: [reference to relevant prior cycles in registry.md — or "first test of this target"]
- **Acceptance criteria**: [what result would confirm the hypothesis — be specific]
- **Failure criteria**: [what result would falsify it]
- **Known weaknesses in this test design**: [any limitations acknowledged upfront]

## Status: IN PROGRESS
```

Then add a row to `context/memory/tests/registry.md`:
```
| [CYCLE_ID] | [TARGET_SLUG] | [DATE] | [HYPOTHESIS_ONE_LINE] | IN PROGRESS |
```

---

## After the Test: Record Results

When the loop report is written (Stage 4.5), update the scenario file:

```markdown
## Results

### Eval Scores
- Baseline: [score from results.tsv]
- After: [new score]
- Delta: [+/-]
- Verdict: KEEP / DISCARD

### Metrics
- Friction events this cycle: N
- Human interventions: N
- Cycles to KEEP: N (how many sub-cycles before a KEEP verdict)

### Survey Findings
- INNER_AGENT headline friction: [one line]
- PEER_AGENT headline friction: [one line]
- ORCHESTRATOR headline friction: [one line]
- Shared friction pattern (if any): [same issue cited by 2+ agents]

### Hypothesis Outcome
- Confirmed / Falsified / Inconclusive
- Evidence: [cite specific score delta, survey excerpt, or event]

### What This Test Did Not Cover
- [known gaps in what was measured]

### Recommended Next Test
- **Target**: [same or different target]
- **Hypothesis**: [what to test next, directly informed by these results]
- **Design improvement**: [one specific change to make the next test more discriminating]

## Status: CLOSED — [VERDICT]
```

Update `registry.md` row to CLOSED with verdict.

---

## Registry Index Format (`context/memory/tests/registry.md`)

```markdown
# Test Registry

| Cycle ID | Target | Date | Hypothesis | Status | Verdict |
|----------|--------|------|------------|--------|---------|
| cycle-20260321-001 | os-memory-manager | 2026-03-21 | Phase 5 survey addition improves routing | CLOSED | KEEP |
| cycle-20260321-002 | os-eval-runner | 2026-03-21 | Adversarial prompt coverage gap | IN PROGRESS | - |
```

---

## How to Use the Registry to Design Better Tests

ORCHESTRATOR reads `registry.md` at every Orientation. Before writing the next strategy
packet, answer these questions from the registry:

1. **What targets have been tested?** Do not re-test the same hypothesis that was already
   confirmed or falsified unless there is new evidence it has changed.

2. **What did the last test of this target reveal?** Check the "What This Test Did Not Cover"
   section. The next test should specifically address that gap.

3. **What was the recommended next test?** The prior cycle's "Recommended Next Test" field
   is the default starting point for the next cycle's hypothesis — not a blank slate.

4. **What friction patterns are accumulating a

*(content truncated)*

## See Also

- [[triple-loop-architect-sample-test-prompt]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[the-lab-space-protocol-full-lifecycle]]
- [[test-scenarios-seed]]
- [[test-driven-development-tdd]]
- [[test-automator]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-skill-improvement/references/testing/test-registry-protocol.md`
- **Indexed:** 2026-04-17T06:42:10.184950+00:00
