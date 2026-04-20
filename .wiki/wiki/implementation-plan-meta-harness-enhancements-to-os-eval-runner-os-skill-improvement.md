---
concept: implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement
source: research-docs
source_file: meta-harness/implementation-plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.456921+00:00
cluster: enhancement
content_hash: 7c0f4daa0f2d6464
---

# Implementation Plan: Meta-Harness Enhancements to os-eval-runner & os-skill-improvement

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Implementation Plan: Meta-Harness Enhancements to os-eval-runner & os-skill-improvement

**Self-contained — can be executed on any machine with a fresh clone of `agent-plugins-skills`.**

**Repo:** https://github.com/richfrem/agent-plugins-skills
**Research basis:** arXiv:2603.28052 (Lee et al., March 2026) — see `summary.md` and `code-analysis.md` in this folder
**Enhancement rationale:** `enhancement-recommendations.md` in this folder

---

## Observed Emergent Behavior (Important Prior Art from Weekend Experimentation)

Before implementing anything, note this validated pattern from direct experimentation:

When a lab repo (subproject) has **both** the target skill and `os-eval-runner` installed as peer copies, the autoresearch loop naturally improves **both** — not just the target. This happened unexpectedly during a weekend run and was welcomed, not a bug.

**Why it's safe:**
- The lab repo contains installed copies (physical files, not symlinks to master)
- The loop mutates the local copies freely — worst case it breaks the lab copy, not master
- `os-eval-backport` skill is the explicit human review gate before anything returns to the canonical source in `agent-plugins-skills`
- Master only ever receives mutations that passed both `evaluate.py` (machine gate) and backport review (human gate)

**Why this matters for the enhancements:**
- The nightly evolver (`os-nightly-evolver`) hard-blocks modification of anything outside the target skill folder — by design for safety in master-adjacent environments
- But in a lab repo, that restriction is unnecessarily conservative — the backport gate provides the safety guarantee
- This pattern is structurally identical to Meta-Harness: the proposer can modify the harness itself (not just the target), operating in an isolated search space, with a human Pareto gate before changes reach production
- Enhancement 1 (trace storage) makes this even more powerful: when `eval_runner.py` writes richer traces, the proposer in the lab can read those traces and propose improvements to `eval_runner.py` itself — the very kind of harness self-improvement Meta-Harness was built to discover

**Practical implication for this implementation:**
When running the enhancements in a lab repo, expect the loop to propose changes to `eval_runner.py` and `evaluate.py` alongside changes to the target SKILL.md. This is correct behavior in lab context. Review those changes in `os-eval-backport` with extra care — the evaluator modifying its own scoring logic is high-leverage and high-risk.

---

## Context for a Cold-Start Agent

This repo is a monorepo of AI agent plugins and skills. The key plugin for this work is:

```
plugins/agent-agentic-os/
  skills/
    os-eval-runner/       ← stateless evaluation engine (scorer + loop gate)
    os-skill-improvement/ ← RED-GREEN-REFACTOR improvement methodology
  scripts/
    eval_runner.py        ← pure scorer: reads SKILL.md + evals.json → outputs metrics JSON
    evaluate.py           ← loop gate: calls eval_runner.py, reads baseline, exits 0 (KEEP) or 1 (DISCARD)
    init_autoresearch.py  ← template deployer: scaffolds experiment dirs
```

The autoresearch loop works like this:
1. Agent reads `<experiment-dir>/references/program.md` (goal, rules)
2. Agent edits one file (SKILL.md or a script) — one change per iteration
3. Agent runs `python plugins/agent-agentic-os/scripts/evaluate.py --skill <experiment-dir> --desc "what changed"`
4. `evaluate.py` calls `eval_runner.py --json`, compares to baseline, writes row to `results.tsv`, exits 0 or 1
5. Agent: exit 0 → commit the change; exit 1 → `evaluate.py` already reverted via `git checkout`
6. Repeat

**The gap (from Meta-Harness research):** The agent proposer only sees scores in `results.tsv`. It does not see *which specific eval inputs failed*, *what keywords caused false positives*, or *what the mutation diff was*. The Meta-Harness ablation proves that raw execution traces are worth +15 accuracy points over scores-only

*(content truncated)*

## See Also

- [[enhancement-recommendations-os-eval-runner-os-skill-improvement]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[os-eval-runner]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[optimization-program-os-eval-runner]]

## Raw Source

- **Source:** `research-docs`
- **File:** `meta-harness/implementation-plan.md`
- **Indexed:** 2026-04-17T06:42:10.456921+00:00
