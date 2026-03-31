# Enhancement Recommendations: os-eval-runner & os-skill-improvement

**Based on:** Meta-Harness (arXiv:2603.28052, Lee et al., March 2026) + artifact code analysis
**Related files:** [summary.md](./summary.md) · [code-analysis.md](./code-analysis.md)

---

## The Core Finding That Drives All Recommendations

From the Meta-Harness ablation study:

| Proposer access | Median Acc | Best Acc |
|---|---|---|
| Scores only | 34.6 | 41.3 |
| Scores + Summary | 34.9 | 38.7 |
| Full filesystem (traces) | **50.0** | **56.7** |

Summaries don't help — they can actually **hurt** (-2.6 best accuracy vs scores-only) by compressing away the diagnostic signal that traces preserve. The proposer needs to be able to `grep` and `cat` raw execution logs across all prior runs, not read a TSV of scores.

This is the fundamental gap between this repo's current autoresearch loop and the Meta-Harness approach.

---

## Current State

The `os-eval-runner` + `os-skill-improvement` flywheel currently produces:
- `evals/results.tsv` — one row per iteration: score, delta, KEEP/DISCARD, desc
- `evals/.lock.hashes` — SHA256 baseline snapshot
- Post-run survey to `temp/retrospectives/`

The proposer (`os-skill-improvement`) reads:
- The current `SKILL.md`
- The `results.tsv` score history
- The `program.md` spec

**What's missing:** The proposer has no access to *why* a discard happened — what specific eval inputs failed, what the agent produced, what the routing logic saw. It only knows the score went down.

---

## Recommendation 1: Structured Execution Trace Storage

**Priority: High — this is the #1 Meta-Harness finding**

After each `evaluate.py` run, write a structured trace file alongside `results.tsv`:

```
evals/
  results.tsv                       ← existing: one row per iteration
  traces/
    iter_001_KEEP_score0.87.json    ← NEW: full diagnostic per iteration
    iter_002_DISCARD_score0.71.json
    iter_003_KEEP_score0.89.json
```

Each trace file contains:
```json
{
  "iteration": 2,
  "verdict": "DISCARD",
  "score": 0.71,
  "baseline_score": 0.84,
  "delta": -0.13,
  "desc": "added 'audit' as trigger phrase",
  "mutation_diff": "--- SKILL.md\n+++ SKILL.md\n@@ -4,1 +4,1 @@...",
  "routing_eval": {
    "inputs_tested": 10,
    "per_input": [
      {
        "input": "my symlinks are showing up as text files",
        "should_trigger": true,
        "matched_keywords": ["symlinks", "text", "files"],
        "triggered": true,
        "correct": true
      },
      {
        "input": "audit all hyperlinks in markdown files",
        "should_trigger": false,
        "matched_keywords": ["audit", "files"],
        "triggered": true,
        "correct": false,
        "failure_reason": "keyword 'audit' introduced false-positive"
      }
    ]
  },
  "heuristic_penalties": [
    {"check": "example_blocks", "penalty": 0.0, "passed": true},
    {"check": "py_compile", "penalty": -0.15, "passed": false, "file": "scripts/foo.py"}
  ]
}
```

**Implementation:** Extend `eval_runner.py --json` output to include `per_input` routing detail. `evaluate.py` writes the trace file before exiting.

**Why this matters:** The `os-skill-improvement` proposer can then `grep` traces for "failure_reason" or "false_positive" across all prior iterations — the same selective retrieval the Meta-Harness proposer does over 10M-token execution logs. The proposer goes from knowing "iteration 2 scored lower" to knowing "iteration 2 introduced 'audit' which caused 3 false positives on these exact inputs."

---

## Recommendation 2: Environment Snapshot Injection (Pre-Proposal Context)

**Priority: Medium**

In the Meta-Harness artifact, `_gather_env_snapshot()` runs once before the agent loop and injects a compact environment context block — eliminating 2–5 early exploration turns spent on `ls`, `which python`, etc.

The equivalent for `os-skill-improvement`: before the proposer writes its first mutation, inject a compact **skill state snapshot**:

```markdown
## Skill State Snapshot (pre-proposal)
- Current score: 0.71 (baseline: 0.84)
- Iterations run: 12 (4 KEEP, 8 DISCARD)
- Last 3 verdicts: DISCARD, DISCARD, KEEP
- Highest ever score: 0.89 (iter 7, "added junction point trigger phrase")
- Current false-positive rate: 0.30 (3/10 should_trigger=false inputs misfire)
- Current false-negative rate: 0.00 (0/7 should_trigger=true inputs missed)
- Problem type: PRECISION (not recall) — adding words improves recall, hurts precision
```

This tells the proposer immediately: "the problem is false positives from over-broad keywords, not missed triggers." Without this, the proposer spends one or two iterations diagnosing what the traces would tell it directly.

**Implementation:** Add a `snapshot()` function to `eval_runner.py` that reads `results.tsv` + the last trace file and outputs this block. Call it at the top of the `os-skill-improvement` protocol.

---

## Recommendation 3: Native Structured Reasoning in Proposals

**Priority: Medium**

The Meta-Harness artifact forces structured chain-of-thought by embedding `analysis` and `plan` fields in the tool schema — the model must fill both before emitting `commands`. This reduced poorly-planned action sequences.

The `os-skill-improvement` SKILL.md already has a RED-GREEN-REFACTOR structure, but the proposer can skip to writing mutations without documenting its causal hypothesis. Add an explicit **hypothesis block** requirement before any mutation:

```markdown
## Required Proposal Format (add to os-skill-improvement)

Before writing any mutation to SKILL.md, output a hypothesis block:

```
HYPOTHESIS:
  Failure mode observed: [specific input that triggered incorrectly + why]
  Root cause: [which keyword/phrase/example caused it]
  Proposed change: [one sentence — add/remove/modify what]
  Expected effect: [which specific eval inputs should flip from wrong → correct]
  Risk: [which inputs might regress — be specific]
```

If you cannot fill all 5 fields from the trace data, read more traces before proposing.
```

This mirrors the `analysis` + `plan` fields in the Meta-Harness tool schema. It prevents the failure mode where the proposer makes a reasonable-sounding change with no causal grounding.

---

## Recommendation 4: Proactive Trace Summarization at Milestone Boundaries

**Priority: Low-Medium**

The Meta-Harness artifact runs `_check_proactive_summarization()` every episode — if context is filling up, it compresses before hitting the hard limit (which is harder to recover from).

For long autoresearch runs (50+ iterations), the trace directory grows. Add a milestone summary that fires every 25 iterations:

```
evals/traces/
  milestone_025.md    ← "Iterations 1–25: best strategy was X, worst failure was Y, never try Z"
  milestone_050.md
  iter_026_KEEP_...
  iter_027_DISCARD_...
```

The proposer reads milestone summaries for distant history and raw traces for recent iterations. This lets the loop run indefinitely without the proposer losing context on early experiments — the Meta-Harness equivalent of `_summarize()` feeding a handoff prompt.

---

## Recommendation 5: Double-Confirmation Before Backport

**Priority: Low**

The Meta-Harness artifact uses a two-call `task_complete` confirmation: first call triggers a multi-perspective checklist (test engineer, QA engineer, end-user), second call terminates the episode. This reduced false-completion errors.

The `os-eval-runner` already has a backport stage (`Stage 6`), but it's easy to skip. Add a mandatory **two-gate backport confirmation** before any KEEP change is applied to the master source:

```markdown
Gate 1 — Machine: evaluate.py exits 0 (score improved, F1 maintained)
Gate 2 — Human: proposer prints the diff with 3-perspective commentary:
  - Test engineer view: "which eval inputs changed verdict and why"
  - Routing precision view: "what would a mis-similar query hit now"
  - Regression view: "any skills that could now conflict with this trigger"
Only after both gates: apply to master source.
```

This is especially valuable when running the loop autonomously overnight — the nightly evolver needs a forcing function to not silently apply marginal KEEPs.

---

## Suggested Implementation Order

1. **Trace storage** (Rec 1) — highest leverage, directly addresses the ablation gap
2. **Skill state snapshot** (Rec 2) — quick win, reduces proposer warm-up turns
3. **Hypothesis block** (Rec 3) — add to `os-skill-improvement` SKILL.md, no code change needed
4. **Milestone summaries** (Rec 4) — implement when a loop runs >25 iterations
5. **Double-confirmation backport** (Rec 5) — add to `os-eval-runner` Stage 6

---

## Credit and Prior Art

### Karpathy 3-File Autoresearch Pattern
The foundational pattern this repo's eval loop is built on. The 3-file constraint (spec / mutation target / immutable evaluator) prevents Goodhart's Law exploitation. Already cited in `os-eval-runner` SKILL.md and `references/karpathy-autoresearch-3-file-eval.md`.

### Meta-Harness (Lee et al., 2026)
**Full citation:**
Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn.
*"Meta-Harness: End-to-End Optimization of Model Harnesses"*
arXiv:2603.28052, March 30, 2026.
Paper: https://arxiv.org/abs/2603.28052
Artifact: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

**Key contributions borrowed here:**
- The ablation proof that filesystem access to raw traces outperforms score+summary access by ~15 accuracy points → motivates Recommendation 1
- Environment snapshot injection before the agent loop → motivates Recommendation 2
- Structured tool schema as forced chain-of-thought (`analysis` + `plan` fields) → motivates Recommendation 3
- Proactive context summarization at milestone boundaries → motivates Recommendation 4
- Double-confirmation `task_complete` with multi-perspective checklist → motivates Recommendation 5

The Meta-Harness proposer is Claude Code (Opus 4.6 with max reasoning) — the same agent family running this repo's improvement loops. The approach is designed to improve automatically as coding agents improve.

---

## What NOT to Do (Anti-Patterns from the Research)

- **Don't compress traces into summaries** — the ablation shows summaries hurt vs raw access (-2.6 accuracy points)
- **Don't add a `keywords:` YAML field** — already documented as a footgun in `os-eval-runner`; the Meta-Harness lesson is the same: metadata that bypasses the primary signal channel causes regressions
- **Don't increase iteration count as the primary lever** — Meta-Harness reaches score parity with prior text optimizers in 4 evaluations vs their 40–60; more iterations without better trace access just loops on the same failure modes
