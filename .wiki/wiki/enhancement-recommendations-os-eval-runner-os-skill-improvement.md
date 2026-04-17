---
concept: enhancement-recommendations-os-eval-runner-os-skill-improvement
source: research-docs
source_file: meta-harness/enhancement-recommendations.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.455539+00:00
cluster: meta
content_hash: 606ab0905e3b6a06
---

# Enhancement Recommendations: os-eval-runner & os-skill-improvement

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
## Skill State Snapsho

*(content truncated)*

## See Also

- [[implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[os-eval-runner]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[optimization-program-os-eval-runner]]

## Raw Source

- **Source:** `research-docs`
- **File:** `meta-harness/enhancement-recommendations.md`
- **Indexed:** 2026-04-17T06:42:10.455539+00:00
