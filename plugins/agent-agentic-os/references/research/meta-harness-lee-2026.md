# Meta-Harness: End-to-End Optimization of Model Harnesses

**Authors:** Yoonho Lee, Roshen Nair, Qizheng Zhang (Stanford IRIS Lab), Kangwook Lee (KRAFTON), Omar Khattab (MIT), Chelsea Finn (Stanford)
**Date:** March 30, 2026
**Source:** https://arxiv.org/abs/2603.28052
**Artifact:** https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
**Full analysis:** `plugin-research/meta-harness/` (summary.md, code-analysis.md, enhancement-recommendations.md)

---

## Relevance to This Skill

Meta-Harness runs the same outer loop as this repo's autoresearch Triple-Loop — propose a change, evaluate it, log the result, repeat — but with one critical difference: the proposer has unrestricted filesystem access to **every prior candidate's source code, evaluation scores, and raw execution traces**.

The ablation study directly measures the value of that access:

| Proposer access | Median Acc | Best Acc |
|---|---|---|
| Scores only | 34.6 | 41.3 |
| Scores + Summary | 34.9 | 38.7 |
| Full filesystem (traces) | **50.0** | **56.7** |

Summaries are worse than scores-only. Raw execution traces are the key ingredient.

**The current `os-eval-runner` gives the proposer scores and a TSV. It does not give it traces.**

---

## Key Innovations (from the TerminalBench-2 artifact)

### 1. Environment snapshot injection
Before the first agent turn, gather compact OS context (cwd, tools, memory) and inject it as a `[Environment Snapshot]` block. Eliminates 2–5 early exploration turns.

**Equivalent for this repo:** Before the proposer writes its first mutation, inject a skill state snapshot (current score, false-positive rate, problem type: precision vs recall). See `enhancement-recommendations.md` Recommendation 2.

### 2. Marker-based polling for early exit
Instead of fixed waits, send `echo '__CMDEND__<seq>__'` after each command and poll for it. Commands that finish in 0.1s don't wait 1.0s.

**Equivalent:** Not directly applicable to eval loops, but the pattern (detect completion early rather than wait) applies to iteration termination — stop when score threshold is met, not after a fixed count.

### 3. Native tool calling with structured reasoning fields
Tool schema includes `analysis` (what the proposer observes) and `plan` (what it intends to do) as required fields before `commands`. Forces explicit chain-of-thought before action.

**Equivalent for this repo:** Require a **hypothesis block** before any SKILL.md mutation in `os-skill-improvement`. See `enhancement-recommendations.md` Recommendation 3.

### 4. Layered context management
- Proactive: check context fill level each episode, summarize before hitting limit
- Reactive: on `ContextLengthExceededError`, compress and hand off with summary

**Equivalent:** Milestone summary files in `evals/traces/` at 25-iteration boundaries. See `enhancement-recommendations.md` Recommendation 4.

### 5. Double-confirmation task completion
`task_complete` requires two calls: first triggers a multi-perspective checklist, second terminates. Prevents false-completion.

**Equivalent:** Two-gate backport confirmation (machine gate: evaluate.py exit 0 + human gate: diff with 3-perspective commentary) before applying KEEP changes to master source.

---

## Bottom Line for the Autoresearch Loop

The single highest-leverage change is **structured per-input trace storage** after each `evaluate.py` run:

```
evals/traces/iter_NNN_VERDICT_scoreX.XX.json
```

Each file contains: mutation diff, per-input routing verdict, failure reasons, heuristic penalties. The proposer reads these traces selectively (grep for "false_positive", cat recent DISCARDs) rather than inferring failure modes from aggregate scores.

This is the same access pattern that produced the 56.7% best accuracy vs 41.3% for scores-only in the Meta-Harness ablation.

See `plugin-research/meta-harness/enhancement-recommendations.md` for prioritized implementation plan.
