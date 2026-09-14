# Control-plane simulation protocol

This protocol is for an agent dropped into the pipeline for the first time. It
uses the production `ControlPlane` and `TransitionCoordinator` against a
temporary SQLite database. It is an improvement loop, not a replacement state
machine and not a license to bypass a gate.

## Round objective

Find the smallest point where a first-time agent could make the wrong move,
determine whether the observed behavior is a bug or correct enforcement, and
apply at most one surgical fix. A round must be deterministic and replayable.

## Questions the agent must answer

### 1. Orientation

- What task ID and persisted state am I operating on?
- What legal next states does the live registry expose?
- What transition guidance and YAML questions apply to the requested edge?
- Is this a work-package, task, slice, transition, or execution-step action?

### 2. Authority

- Which source owns each fact: state machine, YAML registry, Python policy,
  SQLite trigger, or receipt table?
- Am I using the supported facade/coordinator rather than writing transition
  decisions or state rows directly?
- Is the actor identity truthful? Programmatic answers must not claim interactive
  human provenance.

### 3. Preconditions

- Which deterministic checks, artifacts, receipts, and human questions are
  required before this edge?
- Are adaptive follow-ups required by the recorded answer?
- Are defaults merely display recommendations? Defaults are not inferred answers.
- Must questions be presented one question at a time?

### 4. Move and denial

- What exact supported command or API call is the next move?
- If the move is denied, does the error identify the missing prerequisite?
- Does a denied move preserve the persisted state and avoid orphan transition,
  decision, receipt, and follow-up rows?

#### Denial invariant

A denied move is state-preserving: no lifecycle transition, authorization
decision, receipt, or follow-up may be committed by the failed attempt.

### 5. Closeout

- What state and receipts were persisted after the move?
- What evidence proves success or denial?
- What friction occurred, and is it Tier 0/1/2/3 map debt or a surgical fix?
- What is the smallest next experiment?

## Round procedure

1. Create or select a task in a temporary database. Never use the repository
   `context/control_plane.db` or a real worktree for a simulation.
2. Read live registry guidance and record the expected state, edge, questions,
   checks, and authority before acting.
3. Make exactly one move. Use the production ControlPlane or coordinator and,
   for human gates, an injected interactive input stream.
4. Record the result as `PASS`, `DENIED_AS_EXPECTED`, or `UNEXPECTED_FAILURE`.
5. Compare state and persistence before and after. A denial must be
   state-preserving and must not leave an orphan transition or receipt.
6. If friction indicates a defect, write one failing contract test, apply one
   surgical fix in the owning layer, and rerun the same round.
7. Close the round with a short handoff containing the evidence and next test.

## First two improvement rounds

### Round 1: incomplete interview

Attempt `INTERVIEW -> RETROSPECTIVE` without recording the required interview
classification. Expected result: explicit denial naming
`interview_classification`, state remains `INTERVIEW`, and no transition is
appended. If the error only says “missing answer,” improve the YAML or Python
guidance so the missing question and supported recording mechanism are visible.

### Round 2: wrong adaptive route

Record complete `STANDARD` interview answers, then attempt the trivial
`INTERVIEW -> RETROSPECTIVE` edge. Expected result: route denial naming the
required `TRIVIAL` classification, state remains `INTERVIEW`, and staged
decisions are not committed as a transition. This checks that adaptive routing
is enforced rather than inferred from the destination requested by the agent.

After Round 2, run the focused simulator and guidance tests. Do not expand the
scope unless the evidence identifies a concrete contract gap.

## Surgical-fix decision table

| Observation | Owning layer | Action |
| --- | --- | --- |
| Illegal edge accepted | State machine / policy / SQLite | Add a failing production-boundary test, then fix the owning enforcement layer. |
| Required question unclear | YAML guidance | Clarify `next_steps_hint` or checklist; preserve the requirement. |
| Required question bypassed | Coordinator / SQLite | Add provenance or trigger enforcement; never weaken the gate. |
| Denial changes state or leaves rows | Persistence adapter | Add atomic rollback coverage and fix the transaction boundary. |
| Diagram or overview drifts | Contract tests/docs | Update the derived documentation after confirming the executable source. |
| Simulator uses a second rule graph | Simulator | Delete the duplicate rule and derive from the live registry. |

## Mandatory handoff

Every completed loop emits this record, following the `os-improvement-loop`
`HANDOFF_BLOCK` shape:

```markdown
## HANDOFF_BLOCK
- Cycle ID: cycle-YYYYMMDD-HHMMSS
- Target: control-plane simulator and transition guidance
- Verdict: KEEP / DISCARD
- Score (Before -> After): contract tests before -> after
- Friction Events: encountered / resolved
- Outstanding Map Debt: IDs or none
- Recommended Next Step: one bounded experiment
```

The protocol is guidance. It cannot authorize a transition, substitute for a
human approval, or change the legal state graph.
