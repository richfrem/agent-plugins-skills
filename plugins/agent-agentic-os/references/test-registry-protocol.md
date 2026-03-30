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

4. **What friction patterns are accumulating across tests?** If the same friction cause
   appears in surveys across multiple different targets, that is a systemic gap in the OS
   itself (not a target-specific issue) — escalate to `os-learning-loop`.

5. **Is the test design improving?** Compare "Known weaknesses" from prior cycles to
   "Recommended next test design improvement." If the same weakness recurs across cycles,
   the test design protocol itself needs improvement.

---

## Promotion Rules

The test registry is NOT ephemeral. Do not skip it in `os-memory-manager`.

- `registry.md` index row -> always preserved (never archived, always in L3)
- CLOSED scenario files -> preserved in `context/memory/tests/` for 90 days, then
  archived to `context/memory/tests/archive/` (never deleted)
- Confirmed findings that change architectural understanding -> promote fact to
  `context/memory.md` L3 with dedup ID referencing the cycle ID
- Falsified hypotheses -> record in L3 as "DO NOT RE-TEST: [hypothesis] — falsified
  by [CYCLE_ID]" to prevent repeated wasted cycles

---

## Anti-Patterns

- **Testing without a prior-results check**: ORCHESTRATOR must read registry.md before
  writing any strategy packet. Testing without knowing what was already tried wastes cycles.
- **Hypothesis-free testing**: "Let's just run it and see" produces uninterpretable results.
  Every test must have a hypothesis, acceptance criteria, and failure criteria written
  before the test runs.
- **Not recording falsified results**: Negative results are as valuable as positive ones.
  A falsified hypothesis recorded properly prevents the same test being run again.
- **Closing without a recommended next test**: Every closed scenario must have a
  "Recommended Next Test" field. The registry is a chain — each test feeds the next.
