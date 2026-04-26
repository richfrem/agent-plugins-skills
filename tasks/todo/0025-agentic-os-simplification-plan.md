# agent-agentic-os Simplification Plan

**Context:** This document responds to three rounds of external architectural critique.
Round 1 proposed a value hierarchy for pruning components. Round 2 proposed a full
6-component rewrite. Round 3 reviewed the v1 plan and proposed five enhancements plus
one structural tweak. This plan accepts Round 1's cuts, accepts Round 2's mental model
shift, rejects Round 2's implementation, and integrates Round 3 selectively — accepting
four proposals, pushing back on two, and flagging two as already implemented.

**Version:** v3 — updated with Round 4 feedback response.

---

## The Core Thesis

The system is not too complex because it has too many components.
It is too complex because it is **documented as 17 equal things** when it is actually
**a learning loop with support infrastructure around it**.

The fix is: targeted cuts + reframing. Not a ground-up rewrite.

---

## What the System Actually Is

```
User input
    ↓
os-architect          ← router: classifies intent, delegates, cost-aware
    ↓
os-improvement-loop   ← learning engine: orchestrates the full improvement cycle
    ↓
os-eval-runner        ← inner gate: stateless scorer, KEEP/DISCARD per iteration
    ↓
os-eval-backport      ← human gate: review before lab winner goes to production
    ↓
os-experiment-log     ← scientific backbone: every run is a logged, reproducible experiment
    ↑
os-eval-lab-setup     ← isolation: sibling repo prevents lab contamination of main
os-memory-manager     ← persistence: deduplication + promotion prevents forgetting/bloat
agentic-os-setup      ← onboarding: reproducible scaffold for new projects
```

That is the system. Everything else is support infrastructure or dead weight.

---

## Cuts (Agree with Round 1)

### Remove entirely

| Component | Reason |
|-----------|--------|
| `triple-loop-architect` | Ceremony on top of os-improvement-loop. Adds hops, no new signal. |
| `triple-loop-orchestrator` | Same. The improvement loop already orchestrates multi-iteration runs. |
| `os-skill-improvement` | os-improvement-loop without isolation. Not a distinct capability — it's a subset. |

**Migration:** Collapse triple-loop agents into os-improvement-loop as invocation modes (e.g., `--lab` flag). Remove os-skill-improvement entirely; update docs to say the loop works on small targets without a full lab.

### Demote to utility tools (not core skills, not in eval pipeline)

| Component | Why keep | Why demote |
|-----------|----------|------------|
| `optimize-agent-instructions` | Useful for prompt rewrites | "Rewrite this prompt better" is not a learning system component; hard to eval objectively |
| `os-guide` | Good reference doc | Documentation retrieval; goes stale; not part of any loop |
| `todo-check` | Good eval proxy target | Should not be treated as a skill worth heavily optimizing |
| `os-clean-locks` | Essential operational tool | Infra utility, not intelligence; not worth running eval loops on |

These stay in the plugin as utilities. They are removed from the "core skills" table in the README and from the eval lab experiment queue.

---

## What We Keep and Why

### Core loop (8 components)

| Component | Role | Why it passes the value test |
|-----------|------|------------------------------|
| `os-architect` | Router + decision-maker | Cannot be replaced by a single prompt; drives delegation strategy |
| `os-improvement-loop` | Learning engine | Implements the full mutate→eval→keep/discard cycle |
| `os-eval-runner` | Inner gate | Stateless scorer; connects changes to measurable outcomes |
| `os-eval-lab-setup` | Isolation | Prevents lab contamination of production — rare and valuable |
| `os-eval-backport` | Human gate | Review step between lab winner and production; not optional in an autonomous system |
| `os-experiment-log` | Scientific backbone | Longitudinal learning, reproducibility, audit trail — most systems lack this entirely |
| `agentic-os-setup` | Onboarding | Reproducible scaffold; practical, not smart |
| `os-memory-manager` | Persistence | Deduplication + promotion; prevents bloat and forgetting across sessions |

### Support infrastructure (keep, clearly labeled as support)

| Component | Role | Note |
|-----------|------|------|
| `os-evolution-planner` | Cheap-model brainstorm layer | Kept separate from orchestrator for token cost reasons (runs on free-tier models). **Round 3 condition added:** the 3 options it produces must be materially different approaches, not relabeled variants. If outputs are consistently redundant across runs, fold into orchestrator with a `--cheap-brainstorm` flag. |
| `os-evolution-verifier` | System-level behavior tester | Tests whether the pipeline causes evolution — different scope from eval-runner. **Round 3 upgrade committed:** must become an adversarial checker (WS-N failure injection tests), not just a schema validator. If it still only checks structure after WS-N, demote to support. |
| `os-health-check` | Debugging visibility | Support tool; not part of the learning loop |
| `os-environment-probe` | Delegation strategy discovery | Runs once per project; writes environment profile for cost-aware routing |
| `os-clean-locks` | Operational utility | Stays as infra; not a "skill" |

---

## What We Reject from Round 2 (and Why)

### 1. Sub-agents as JSON `prompt_template` configs

**Rejected because:** The eval loop mutates SKILL.md files, tests them, and backports winners. Each SKILL.md is the "program" file in the Karpathy 3-file pattern. If instructions are embedded as strings in a JSON config, you cannot:
- Isolate which instruction changed per iteration
- Run evals against a specific skill in isolation
- Track improvement history per skill file
- Backport a winning change to a single versioned file

SKILL.md *is* the config. It is already what Round 2 proposes — just with human readability and version control granularity intact.

### 2. Merging os-eval-backport into the learning loop

**Rejected because:** Backport is the human-approval gate. In a system that autonomously mutates its own instructions, the review step before production is not optional. Removing it creates a self-modifying system with no human checkpoint.

### 3. Merging os-evolution-planner into the orchestrator

**Rejected because:** The planner is separate specifically so it runs on a cheap model (Copilot free tier, Gemini free). If merged into the orchestrator, every planning call costs a premium token. The separation is cost architecture, not agent complexity.

### 4. Merging os-eval-runner and os-evolution-verifier into "eval-engine"

**Rejected because:** Different scopes.
- os-eval-runner: tests whether a *skill patch* improves accuracy (inner loop gate)
- os-evolution-verifier: tests whether the *orchestration pipeline* causes real evolution (system behavior check)

One tests skills. The other tests the system. Merging produces a component with two unrelated responsibilities.

### 5. guided-interface as a new component

**Rejected because:** os-architect already is this. Users talk to it in plain language. Adding a layer in front of the existing router is not simplification.

### 6. Full rename + rewrite

**Rejected because:** The 6-component architecture is mostly renames (os-architect → core-orchestrator, os-improvement-loop → learning-loop, etc.). Renaming 6 things:
- Resets the experiment log history
- Breaks existing users
- Costs months of migration for no behavioral improvement
- Doesn't change how any of the loops actually work

---

## What We Do Accept from Round 2

### The mental model shift

> "One learning system with clear loops and modules" — not "many agents collaborating"

This is the right framing. The README and docs should be restructured around:

```
Core loop → support infrastructure → utility tools
```

Not a flat alphabetical list of 17 equal components. This is a docs change, not an architecture change, and it is the right fix.

### Cost-aware delegation as a first-class concern

The idea that routing decisions should explicitly consider model cost (free tier vs premium) is correct and already partially implemented via os-environment-probe + os-evolution-planner. This should be made more explicit in os-architect's decision logic.

---

## The Actual Before/After

### Before (current state)

- 17 skills + 7 agents documented as equals
- Triple-loop agents, os-skill-improvement, optimize-agent-instructions at same tier as os-eval-runner
- README reads as a feature list, not a system description
- User has to know which of 17 things to invoke

### After (proposed)

- 8 core components (the learning loop)
- 5 support/infrastructure components
- 4 utility tools (clearly labeled as such)
- Triple-loop agents removed
- os-skill-improvement removed
- README leads with the loop, not the component list
- User talks to os-architect; it routes everything

**Net removal:** 3 top-level agents/skills removed, 4 demoted. 10 components remain at the same tier or clearly stratified below. No behavioral change to the learning loop itself.

---

---

## Plugin Merger Question: agent-agentic-os + agent-loops

The user asked whether the two plugins should be merged, given that both do orchestration
and both have "triple-loop" concepts.

### What agent-loops actually is

agent-loops is a **framework-agnostic library of execution patterns**. It provides 5 named
patterns (learning-loop, red-team-review, dual-loop, agent-swarm, triple-loop-learning) that
work in any repo, with any AI agent (Claude, Gemini, Copilot, local models). Its README
explicitly states it does NOT own memory synthesis, experiment logging, or eval infrastructure.

It is a pattern library. Think of it as "LEGO bricks for orchestration."

### What agent-agentic-os actually is

agent-agentic-os is a **self-improvement OS for a specific ecosystem** (the agent-plugins-skills
repo). It adds on top of loop execution:

- An **objective eval gate** (os-eval-runner + evaluate.py) that locks in measurable improvement
- An **isolated lab environment** (os-eval-lab-setup) that prevents contamination
- A **scientific experiment log** (os-experiment-log) for longitudinal tracking
- A **memory management layer** (os-memory-manager) for cross-session persistence
- A **human review gate** (os-eval-backport) before lab winners go to production

It is an improvement engine, not a pattern library.

### The real overlap

The duplication is in ONE place: **triple-loop**.

- agent-loops: `triple-loop-learning` (Pattern 5) — generic meta-learning loop, works anywhere
- agent-agentic-os: `triple-loop-architect` + `triple-loop-orchestrator` — same concept, reimplemented

This is the duplication that should be fixed. But the fix is not merging two plugins — it is
**removing the duplicate implementation from agent-agentic-os** and having it delegate to
agent-loops' Pattern 5 instead.

### Proposed relationship (not a merge)

```
agent-loops             agent-agentic-os
(how to run a loop)     (what to improve + how to measure it)
        │                       │
        │   uses Pattern 5      │
        └──────────────────────►│
        triple-loop-learning    os-improvement-loop
                                    + eval gate (KEEP/DISCARD)
                                    + experiment log
                                    + lab isolation
                                    + human backport gate
```

agent-agentic-os **uses** agent-loops patterns as its execution backbone.
It does not reimplement them.

### Why NOT a full merge

| Reason | Detail |
|--------|--------|
| Different scope | agent-loops is framework-agnostic; agent-agentic-os is ecosystem-specific |
| agent-loops has no eval gate | Adding eval infrastructure to agent-loops violates its "standalone, no ownership of X" design |
| agent-loops works in any repo | Merging would make it specific to agent-plugins-skills, breaking its core value proposition |
| Different users | agent-loops is for any developer running any AI workflow; agent-agentic-os is for someone running the improvement OS on this specific ecosystem |
| The ADR rule | ADR-001 prohibits cross-plugin runtime dependencies — but install-time usage (agent-agentic-os uses agent-loops as a substrate) is the correct pattern |

### Concrete changes from this analysis

1. **Remove** `triple-loop-architect` and `triple-loop-orchestrator` from agent-agentic-os (already agreed)
2. **Update** os-improvement-loop documentation to explicitly call agent-loops Pattern 5 (`triple-loop-learning`) as its execution backbone — not a separate reimplementation
3. **Update** agent-agentic-os README to describe the relationship: "agent-loops provides execution patterns; agent-agentic-os adds the eval gate, experiment log, and improvement infrastructure on top"
4. **Do not merge** the plugins — they have distinct purposes, distinct users, and distinct scopes

The analogy: agent-loops is like a database driver. agent-agentic-os is the application that
uses it. You don't merge the driver into the application just because they're both "database-related."

---

## Round 3 Feedback — Accepted Improvements

### 1. Add routing accuracy tracking for os-architect (accepted)

Round 3 correctly identified that the router is unverified at scale — misclassification
is the #1 failure mode for orchestrated systems.

**Clarification (pushback on "missing"):** `os-architect-tester` already runs 8
pre-scripted scenario transcripts and `EXP-14` exercises it. What IS missing is
**quantified routing accuracy** — tracking misclassification rate across runs, not just
"did it produce a reasonable output."

**Change:** Add a routing accuracy eval set to `os-architect-tester`:
```json
{"input": "improve todo-check skill", "expected_route": "os-improvement-loop"},
{"input": "probe my environment", "expected_route": "os-environment-probe"},
{"input": "there's no skill for X", "expected_route": "Path C / os-evolution-planner"}
```
Track: routing accuracy % across the 8 scenarios. Log as a metric in the experiment log.
This makes os-architect a component with a measurable error rate, not just a black box.

---

### 2. Global overfitting detection in os-eval-runner (accepted)

Round 3 correctly noted that the overfit detection rule (base↑ && holdout↓ → force DISCARD)
was added to EXP-08+ but should be a system-wide invariant, not an optional per-lab setting.

**Change:** Enforce the overfit detection rule inside `os-eval-runner` as a hard gate:
```
IF base_score > prev_base AND holdout_score < prev_holdout → OVERFIT → force DISCARD
```
os-eval-runner should refuse to KEEP any iteration that overfits, regardless of how the
lab was configured. The holdout set becomes a required input, not optional.

---

### 3. Skill creation threshold / anti-proliferation rule (accepted)

Round 3 correctly flagged the risk of "skill explosion" if os-architect creates new skills
too readily.

**Change:** Add a creation threshold rule to os-architect's decision logic:
- A new skill is only created if the capability gap persists across ≥ 3 separate architect
  sessions (not 3 runs of the same session)
- The gap must not be solvable by modifying an existing skill (audit required first)
- Document this rule explicitly in `os-architect-agent.md` Phase 2 (gap detection)

---

### 4. Critic mode in the improvement loop — as a flag, not always-on (accepted with modification)

Round 3 proposed: mutate → critic → eval → keep/discard. The critic challenges the mutation
using a cheap model before it goes to eval.

**Why the core idea is right:** The eval gate is objective but silent. A cheap-model critic
that articulates predicted failure modes before eval gives the human reviewer better signal
when reviewing results, and may catch obviously bad mutations before spending eval budget.

**Modification from Round 3 proposal:** The critic must **flag, not gate**. It cannot block
a mutation from going to eval — that would reintroduce subjective judgment into the gate
and undermine the eval-first principle. The critic's output is logged alongside the eval
result so you can audit whether critic predictions correlated with DISCARD outcomes over time.

```
mutate → critic (cheap model, flags predicted failure modes) → eval → KEEP/DISCARD
                                                                      ↑
                                                              critic prediction logged here
```

**Round 4 upgrade:** The critic must be a **scored predictor**, not just a commentary log.
Each critic invocation outputs a structured prediction:
```json
{
  "predicted_outcome": "KEEP | DISCARD",
  "confidence": 0.0–1.0,
  "failure_modes": ["overfits on edge cases", "breaks scenario X"]
}
```
Track critic accuracy vs actual eval outcome over time. A critic with >70% prediction accuracy
becomes a useful early-warning signal; below 50% and it is turned off. This gives the critic
a measurable track record and prevents it from becoming ignored commentary.

This is a future enhancement — implement after the core loop is validated, not before.

---

## Round 3 Feedback — Pushbacks

### 1. "Failure-triggered automatic learning" — reject as default behavior

Round 3 proposed: if eval score drops or repeated failures occur, auto-invoke
`os-improvement-loop` in repair mode without human trigger.

**Rejected because:** In a system that autonomously mutates its own instructions, the human
trigger is not an inconvenience — it is a safety property. Auto-triggering the improvement
loop in response to failures creates a feedback loop where the system may:
- Misclassify normal variance as a failure signal
- Trigger improvement runs during unstable periods (exactly when the loop is least reliable)
- Compound a problem by running mutations on a broken eval baseline

The right response to repeated failures is a human checkpoint (the phase gate), not
automatic self-modification. This may be revisited once the system has 50+ logged iterations
and the failure signal is well-characterized.

---

### 2. "Experiment log not queryable" — already implemented

Round 3 suggested upgrading the experiment log to a queryable knowledge base with tags
and queries like "what fixes improved X?"

**Already shipped:** `experiment_log.py query <term>` does this. The `Actions Taken`
field is surfaced in query results (fixed in round5 commit c268d081). The query command
searches across session IDs, targets, and improvement actions.

What IS missing: **structured tags** (failure type, improvement type). These would make
cross-session queries more precise. Adding a `tags:` field to the experiment log schema
is a net-new improvement worth adding — but it's an enhancement to an existing feature,
not a missing capability.

---

### 3. "Reproducibility check missing" — already planned as EXP-17

Round 3 proposed: rerun best iteration 2–3 times, track variance.

**Already in the plan:** EXP-17 (Baseline Stability Check) was added in v3 of the
ecosystem validation plan (2026-04-26). It runs the same eval 3× before any mutations,
verifies variance ≤ 0.03, and blocks labs that show unstable baselines. This is a gate,
not a retrospective check — which is stronger than what Round 3 proposed.

---

## Round 4 Feedback — Accepted Improvements

Round 4 confirmed the architecture is coherent and the core invariants are correct.
It identified four remaining gaps and proposed five targeted upgrades.

---

### 1. Routing Decision Audit for os-architect (accepted, with scope limit)

Round 4 distinguishes between routing *classification accuracy* (did it pick the right path?)
and routing *decision quality* (was that path optimal for the situation?). Both matter.

**Accepted:** Add a `ROUTING DECISION AUDIT` block to every os-architect output:
```md
## ROUTING DECISION AUDIT
- Chosen path: [A / B / C / no-op]
- Alternatives considered: [list]
- Why chosen: [one sentence]
```

This makes routing decisions reviewable and auditable — human reviewers can flag decisions
that were formally correct but contextually suboptimal. Over time, patterns in the audit
log reveal systematic routing weaknesses.

**Scope limit (pushback on "optimality as a metric"):** Tracking "% of decisions that were
suboptimal" requires defining optimal, which requires ground truth that does not exist at
run time. The audit block captures the inputs; human review assesses optimality in retrospect.
Full optimality metrics are a future enhancement requiring 50+ logged routing decisions first.

---

### 2. os-evolution-verifier binary contract (accepted)

Round 4 correctly identified that a verifier with no clear failure definition becomes
"ceremony that always passes." "If it can't fail, it's useless."

**Change:** Define a binary PASS/FAIL contract for os-evolution-verifier with an explicit
minimum threshold:

```
PASS: pipeline produces ≥ 1 artifact at the declared path AND HANDOFF_BLOCK is valid AND
      STATUS is not 'crashed' AND EVOLUTION_VERIFICATION verdict is PASS or PARTIAL
FAIL: any of the above conditions not met
```

WS-N failure injection experiments (N-01 through N-06) provide the adversarial test scenarios.
The verifier must fail these inputs — if it passes N-04 (malformed run-config), it is not
doing its job. At least 3 of 6 adversarial scenarios must produce FAIL verdicts for the
verifier to be considered operational.

---

### 3. Experiment synthesis step (accepted — highest-value Round 4 addition)

Round 4 identified the most important remaining gap: the experiment log records what happened
but does not feed patterns back into the system. Logging is not learning.

**Change:** Add a periodic synthesis step (run after every 5 experiments or at session close):

```md
## SYNTHESIZED LEARNINGS — [date]
### Patterns that consistently improve performance
- [pattern] → seen in [session IDs], avg delta +[X]
### Patterns that cause regressions
- [pattern] → seen in [session IDs], avg delta -[X]
### Recommended updates to core skills
- [skill] → [specific change suggested by pattern]
```

The synthesis output is fed to `os-memory-manager` for promotion to long-term memory.
This closes the loop: experiments → patterns → memory → better future decisions.

Implementation: add `experiment_log.py synthesize` command that queries recent entries,
groups by target and outcome, and produces the synthesis block. os-memory-manager already
handles promotion — it just needs the structured input.

---

### 4. Evaluation budget guard (accepted)

With the critic, holdout sets, adversarial sets, and multiple eval datasets now in play,
cost per iteration compounds quickly.

**Change:** Enforce hard limits at the orchestrator level:
```
max_eval_iterations_per_lab: 10  (already in validation plan — formalize as enforced rule)
max_eval_datasets_per_run: 3     (base + holdout + adversarial — no more)
critic_invocations_per_iteration: 1  (one cheap-model call only)
```

These are not suggestions — the orchestrator must reject lab configurations that exceed
them. This keeps the system usable in real-world environments where token cost matters.

---

## Round 4 Feedback — Pushbacks

### 1. Decision quality as a tracked metric (near-term) — scope-limited, not rejected

Round 4 correctly identifies that classification accuracy ≠ decision quality. It's right
that the system could route correctly but suboptimally.

**Pushback on near-term measurement:** Tracking decision quality requires ground truth on
what "optimal" means for each input — and that ground truth does not exist at run time.
You would need a labeled dataset of inputs where the optimal path is known in advance.
Building that dataset requires 50+ real routing decisions reviewed by a human who can
compare outcomes across paths. This is not a near-term metric.

**What is accepted:** The Routing Decision Audit block (see above) captures the inputs
needed to make optimality assessments in retrospect. Once 50+ audit logs exist, patterns
in suboptimal routing can be extracted and turned into evals. The metric follows the data;
it is not designed in advance.

---

## Summary

**Round 1** correctly identified the dead weight. Cuts accepted.
**Round 2** correctly identified the mental model problem. Mental model accepted; implementation rejected.
**Round 3** correctly identified four gaps (architect validation, global overfitting, skill proliferation, critic mode). Two items flagged as already implemented (experiment log query, EXP-17).
**Round 4** confirmed the core is sound. Accepted four targeted upgrades (routing audit, verifier binary contract, experiment synthesis, budget guard). Scope-limited one (decision quality metrics require data first).
**The merger question**: not a merge — agent-agentic-os uses agent-loops as execution substrate; owns the eval gate, experiment log, and improvement infrastructure.

**The right execution in priority order:**
**Round 2** correctly identified the mental model problem. Mental model accepted; implementation rejected.
**Round 3** correctly identified four gaps (architect validation, global overfitting, skill proliferation, critic mode). Also surfaced two items already implemented (experiment log query, reproducibility check).
**The merger question**: not a merge — a cleaner dependency relationship. agent-agentic-os
delegates to agent-loops for execution patterns; agent-agentic-os owns the eval gate,
experiment log, and improvement infrastructure.

**The right execution in priority order:**

*Immediate (pre-execution):*
1. Make Round 1's cuts: remove triple-loop agents, os-skill-improvement; demote utility skills
2. Apply Round 2's mental model to the docs — one learning system, not 17 equal components
3. Clarify agent-loops / agent-agentic-os relationship: use, not merge; remove triple-loop duplication

*High priority (before Phase 3 eval labs):*
4. Add routing accuracy eval set to os-architect-tester (Round 3) + Routing Decision Audit block (Round 4)
5. Enforce global overfitting detection in os-eval-runner as a hard gate (Round 3)
6. Define binary PASS/FAIL contract for os-evolution-verifier with WS-N threshold (Round 4)
7. Enforce evaluation budget guard at orchestrator level (Round 4)

*Medium priority (after first 5 experiments complete):*
8. Add `experiment_log.py synthesize` command + os-memory-manager integration (Round 4)
9. Add skill creation threshold rule to os-architect (Round 3)
10. Add structured tags to experiment log schema (Round 3 enhancement)

*Future (after core loop validated with 20+ runs):*
11. Add critic mode as scored predictor in improvement loop, non-gating (Rounds 3 + 4)
12. Add routing decision quality metrics once 50+ audit logs exist (Round 4 scope-limited)

*Never touch:*
- Eval gate (os-eval-runner KEEP/DISCARD logic)
- Human backport gate (os-eval-backport review step)
- Lab isolation (os-eval-lab-setup sibling repo)
- Experiment log core schema and append/query commands
