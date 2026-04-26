# agent-agentic-os Simplification Plan

**Context:** This document responds to five rounds of external architectural critique across
GPT, Gemini, and Claude reviewers. Round 1 proposed a value hierarchy for pruning.
Round 2 proposed a 6-component rewrite (rejected). Rounds 3–4 proposed targeted upgrades
(selectively accepted). Round 5 (all three reviewers) confirmed the core is sound and
surfaced operational gaps in manifests, synthesis rigor, and the verifier contract.

**Version:** v4 — updated with Round 5 feedback (Gemini + Claude + GPT).

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
      STATUS is not 'crashed' AND EVOLUTION_VERIFICATION verdict is PASS
      (PARTIAL is logged but treated as FAIL for gating — Round 5 tightening)
FAIL: any of the above conditions not met, OR verdict is PARTIAL
```

WS-N failure injection experiments (N-01 through N-06) provide the adversarial test scenarios.
**Round 5 threshold (Claude reviewer):** The threshold of "3 of 6" was too low — a verifier
that only catches obvious crashes (N-01/N-02/N-03) while missing schema drift and path mismatch
still passes. New threshold:

- **Critical scenarios** (all must produce FAIL): N-04 (malformed run-config), N-05 (truncated plan), N-06 (bad evals schema) — these test whether the verifier catches *structural failures*, not just crashes
- **Overall threshold**: ≥ 4 of 6 adversarial scenarios must produce FAIL verdicts
- A verifier that passes all 6 adversarial inputs is not operational

---

### 3. Experiment synthesis step (accepted — highest-value Round 4 addition)

Round 4 identified the most important remaining gap: the experiment log records what happened
but does not feed patterns back into the system. Logging is not learning.

**Change:** Add a periodic synthesis step. **Round 5 trigger (Claude reviewer):** "every 5 experiments or at session close" are different triggers — sessions with 3 experiments never hit 5. Canonical trigger: **at session close if ≥ 3 new experiments since last synthesis**. This ensures the synthesis runs on enough data (minimum signal threshold) without requiring a human to remember to invoke it.

Synthesis output must be **data-backed** (GPT reviewer — prevents narrative-over-signal):
```md
## SYNTHESIZED LEARNINGS — [date]
### Patterns that consistently improve performance
- pattern: [description]
  supporting sessions: [IDs]
  avg delta: +[X]
  sample size: [N]  ← discard this pattern if N < 3
### Patterns that cause regressions
- pattern: [description]
  supporting sessions: [IDs]
  avg delta: -[X]
  sample size: [N]  ← discard this pattern if N < 3
### Recommended updates to core skills
- [skill] → [specific change] (supported by [session IDs])
```

Patterns with sample_size < 3 are silently dropped — they are noise, not signal.

The synthesis output is fed to `os-memory-manager` for promotion to long-term memory.
This closes the loop: experiments → patterns → memory → better future decisions.

Implementation: add `experiment_log.py synthesize` command that queries recent entries,
groups by target and outcome, and produces the synthesis block. os-memory-manager already
handles promotion — it just needs the structured input.

---

### 4. Evaluation budget guard (accepted)

With the critic, holdout sets, adversarial sets, and multiple eval datasets now in play,
cost per iteration compounds quickly.

**Change:** Enforce hard limits at the orchestrator level. **Round 5 note (Claude reviewer):** these values were asserted without rationale. Rationale added below:

```
max_eval_iterations_per_lab: 10
  rationale: 10 iterations provides enough signal for a learning curve without
             runaway cost; the validation plan established this empirically (0024)

max_eval_datasets_per_run: 3
  rationale: exactly base + holdout + adversarial — one of each kind; adding
             more datasets fragments the signal without improving the gate

critic_invocations_per_iteration: 1
  rationale: one cheap-model challenge per mutation is sufficient; multiple critic
             calls on the same mutation amplify the same signal, not different ones
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

## Round 5 Feedback — Accepted (Gemini + Claude + GPT)

### 1. Plugin manifest cleanup (Gemini — critical, missed by prior rounds)

`plugins/agent-agentic-os/.claude-plugin/plugin.json` currently lists `triple-loop-architect`,
`triple-loop-orchestrator`, and `os-skill-improvement` in its `agents` and `skills` arrays.
If these remain in the manifest after the files are deleted, `os-architect` may hallucinate
routes to them during Category 3 or 5 requests. This must be cleaned up as part of Phase 1.

**Changes to plugin.json:**
- Remove from `agents`: `triple-loop-architect`, `triple-loop-orchestrator`
- Remove from `skills`: `os-skill-improvement`
- Remove from `keywords`: `triple-loop`, `skill-improvement`
- Remove from `capabilities`: `triple-loop-learning`
- Update `description`: remove "Triple-Loop autonomous skill evaluation system"
- Bump version: `1.5.0` → `1.6.0`

**Changes to `skills/os-init/runtime/agents.json`:**
- `Triple-Loop Retrospective` entry: this refers to the retrospective *phase* of
  os-improvement-loop, not the deleted agents. Rename to `os-improvement-loop-retrospective`
  for clarity. Do not delete it.

---

### 2. System dependency map (GPT — prevents silent coupling drift)

The system looks modular but has implicit couplings: os-architect decisions affect eval
frequency; os-memory-manager outputs influence future architect decisions; os-improvement-loop
depends on experiment log structure. Without an explicit map, a change to one component
silently breaks another.

Add `references/architecture/dependency-map.md` to the plugin:

```md
## SYSTEM DEPENDENCY MAP

| Component | Reads from | Writes to | Side effects on |
|-----------|-----------|-----------|-----------------|
| os-architect | context/memory/environment.md, context/memory.md | HANDOFF_BLOCK (stdout) | Routes to os-improvement-loop, os-evolution-planner |
| os-improvement-loop | HANDOFF_BLOCK, improvement/run-config.json | context/experiment-log/ | Invokes os-eval-runner, os-eval-lab-setup |
| os-eval-runner | evals/evals.json, evals/evals_holdout.json | results.tsv, stdout KEEP/DISCARD | Gating decision for os-improvement-loop |
| os-eval-backport | results.tsv, lab SKILL.md | plugins/ (main repo) | Human checkpoint — nothing automatic |
| os-experiment-log | --report file (temp/) | context/experiment-log/index.md, entry .md | Consumed by os-improvement-report, synthesize |
| os-memory-manager | context/events.jsonl, synthesis output | context/memory.md | Influences future os-architect routing |
| os-eval-lab-setup | HANDOFF_BLOCK | sibling repo (../lab-*/) | Isolates all subsequent eval-runner calls |
```

**Coupling rules derived from map:**
- Changing experiment log schema requires updating `os-improvement-report` and `synthesize` together
- Changing memory.md format requires updating `os-architect`'s Phase 1 read
- Never write directly to `plugins/` from inside the loop — only os-eval-backport does this

---

### 3. Anti-proliferation tracking location (Claude — implementation gap closed)

The rule "create a skill only if the gap persists across ≥ 3 separate architect sessions"
was committed without specifying where the recurrence count lives. Closing the gap:

**Decision: os-memory-manager promoted memory.** When os-architect identifies a capability
gap and routes Path C, it writes a structured gap record to `context/events.jsonl`:
```json
{"event": "capability_gap_detected", "gap": "monitoring plugin health", "session": "...", "date": "..."}
```
os-memory-manager promotes recurring gaps (same gap string, ≥ 3 events) to `context/memory.md`
under a `## Recurring Gaps` section. os-architect checks this section in Phase 2 before
proposing Path C. If the gap is NOT in Recurring Gaps, os-architect proposes modifying an
existing skill instead.

This is automatable — no manual tracking required.

---

### 4. Routing Pattern Analysis — periodic, not passive (GPT)

The Routing Decision Audit block logs decisions but does not feed back into architect improvements.
After every ~10 runs, a synthesis pass should produce:

```md
## ROUTING PATTERN ANALYSIS — [date]
- Most common misroutes: [path X → should have been path Y, N occurrences]
- Conditions where routing struggled: [input pattern]
- Suggested rule updates: [specific change to os-architect Phase 2]
```

This feeds into `os-architect-agent.md` updates via the normal os-evolution-planner path.
It is not automatic — it is a human-triggered analysis using the audit log as input.

---

### 5. Confidence tracking in eval outcomes (GPT)

Not all improvements carry the same signal quality. A +0.02 score improvement with variance
0.02 is strong signal; the same delta with variance 0.08 is noise. Add to os-eval-runner output:

```json
{
  "score": 0.82,
  "confidence": 0.91,
  "variance": 0.02,
  "verdict": "KEEP"
}
```

`confidence` = 1 - (variance / score); `variance` is computed from the 3× baseline runs
(EXP-17). Human reviewers should weight KEEP decisions by confidence, not just score delta.
Low-confidence KEEPs (confidence < 0.7) are still KEEPs but flagged for extra scrutiny in
os-eval-backport.

---

## Round 5 Feedback — Pushbacks

### 1. Skill deprecation as automated removal (GPT) — rejected, human-trigger only

GPT proposed: automatically deprecate skills that show no improvement across N experiments
or are never selected by os-architect across M sessions.

**Rejected because:** Selection frequency depends on the kinds of requests users make, not
on skill quality. `os-eval-backport` would rarely be selected if users don't run improvement
labs often — that doesn't make it worthless, it means it's rarely needed. Automated removal
based on selection frequency would delete infrastructure components during quiet periods.

**What IS accepted:** A human-readable "skill health report" produced by `experiment_log.py synthesize`
that flags skills with zero improvement across 10+ experiments and zero routing hits across
20+ sessions. A human decides whether to deprecate. The system flags; the human cuts.

---

### 2. Cross-session budget limits (GPT) — reject as system constraints

GPT proposed: `max_total_tokens_per_session` and `max_experiments_per_day` as soft limits.

**Rejected because:** The system does not have access to token counts (Copilot CLI does not
expose them), and "max_experiments_per_day" is an operational practice, not a system invariant.
Enforcing it at the code level would require a persistent counter that creates more state
management overhead than it prevents. The per-lab limits already in the plan (10 iterations,
3 datasets) address the token-cost risk at the right scope. Cross-session limits belong in
a usage guide, not the system.

---

## Summary

**Round 1:** Cut dead weight (triple-loop agents, os-skill-improvement). Accepted.
**Round 2:** Mental model shift (one learning system, not 17 equals). Mental model accepted; rewrite implementation rejected.
**Round 3:** Routing accuracy, global overfitting gate, skill creation threshold, critic mode. All accepted with modifications.
**Round 4:** Routing decision audit, verifier binary contract, experiment synthesis, budget guard. All accepted with one scope limit (decision quality metrics require data first).
**Round 5:** Plugin manifest cleanup, system dependency map, synthesis rigor, verifier threshold tightened, anti-proliferation tracking location defined. All accepted. Skill auto-deprecation and cross-session budget limits rejected.
**Plugin merger:** Use, not merge — agent-loops is the execution substrate; agent-agentic-os owns the eval gate, experiment log, and improvement infrastructure.

**Execution priority:**

*Phase 1 — Execute now (task 0025 copilot dispatch):*
1. Delete triple-loop-architect, triple-loop-orchestrator agent files
2. Delete os-skill-improvement skill directory
3. Update plugin.json manifest (remove deprecated entries, bump to v1.6.0)
4. Update agents.json (rename Triple-Loop Retrospective entry to `os-improvement-loop-retrospective` with an explicit description: "Retrospective phase of os-improvement-loop — analyzes friction events and feeds next iteration", pointing to `os-improvement-loop` skill)
5. Update os-architect-agent.md:
   - Remove deprecated rows and explicitly route Category 3 to `improvement-intake-agent → os-improvement-loop`
   - Path B: Replace optional `os-skill-improvement` validator with `os-improvement-loop`
   - Add Routing Decision Audit block (must appear immediately after every `emit HANDOFF_BLOCK` line in Paths A, B, and C):
     ```md
     ## ROUTING DECISION AUDIT
     - Chosen path: [A+ / A / B / C]
     - Alternatives considered: [list, or "none — single clear match"]
     - Why chosen: [one sentence citing the match quality and signal that determined path]
     ```
   - Add skill creation threshold
6. Update os-improvement-loop SKILL.md (remove os-skill-improvement refs in lifecycle close protocol, add budget guard with rationales, add agent-loops relationship note)
7. Update README.md, CHANGELOG.md, and SUMMARY.md (remove deprecated components, add Utilities section, reframe How It Works, update plugin triad table, and document stale component list post-cleanup)

*Phase 2 — High priority (before Phase 3 eval labs):*
8. Add routing accuracy eval set to os-architect-tester (Round 3)
9. Enforce global overfitting detection in os-eval-runner as hard gate (Round 3)
10. Define binary PASS/FAIL + PARTIAL=FAIL for gating in os-evolution-verifier (Rounds 4+5)
11. Add confidence tracking (score + confidence + variance) to os-eval-runner output (Round 5)
12. Add `references/architecture/dependency-map.md` (Round 5)
13. Add gap event logging to os-architect for anti-proliferation tracking (fires when Path C is concluded; write `{"event":"capability_gap_detected","gap":"<description>","session":"<date>"}` to `context/events.jsonl`)

*Phase 3 — Medium priority (after first 5 experiments):*
14. Add `experiment_log.py synthesize` with data-backed format and sample_size < 3 filter (Rounds 4+5)
15. Add structured tags to experiment log schema

*Future (after 20+ logged runs):*
16. Add critic mode as scored predictor (non-gating) to os-improvement-loop (Rounds 3+4)
17. Add Routing Pattern Analysis trigger after every ~10 runs (Round 5)
18. Add routing decision quality metrics once 50+ audit logs exist (Round 4 scope-limited)

*Invariants — never change without a documented architectural decision:*
- **Eval gate** (os-eval-runner KEEP/DISCARD): changing this invalidates all historical comparison baselines
- **Human backport gate** (os-eval-backport): removing human review creates a self-modifying system with no safety checkpoint
- **Lab isolation** (os-eval-lab-setup sibling repo): without it, a failed mutation contaminates production
- **Experiment log core schema** (append/query commands): schema changes break query and summary across existing entries without a migration
