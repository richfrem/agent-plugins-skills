# Exploration Optimizer (`exploration-optimizer`) (absorbed skill)

> Absorbed from the retired `exploration-optimizer` skill into `running-exploration-cycle`; the full original body follows.
> Original trigger description: Evaluates and improves the exploration-cycle skills, prompts, routing, and artifact quality using baseline-first, one-hypothesis iteration loops with keep-discard decisions and experiment ledgers.
> Original allowed-tools: Bash, Read, Write

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)
- [Appendix A: optimization program (former `program.md`)](#appendix-a-optimization-program-former-programmd)
- [Notes (fill in before starting the loop)](#notes-fill-in-before-starting-the-loop)
- [Appendix B: proposer prompt (former `copilot_proposer_prompt.md`)](#appendix-b-proposer-prompt-former-copilot_proposer_promptmd)
- [System Instructions](#system-instructions)
- [Trap Warning (update after each DISCARD — prevents repeating failed approaches)](#trap-warning-update-after-each-discard--prevents-repeating-failed-approaches)
- [Appendix C: former executor `exploration_optimizer_execute.py`](#appendix-c-former-executor-exploration_optimizer_executepy)

Evaluates and optimizes exploration-cycle skills and prompts using disciplined, baseline-first iteration loops.

## Constraints

- **One-hypothesis discipline**: Change exactly one variable per iteration loop.
- **Programmatic baselines**: Acceptance requires automated benchmark score improvement over baseline.
- **Fail-safe revert**: Automatically discard regressions; retain only verified improvements.

## Quick start

```bash
# Execute optimization loop on target skill
python ./scripts/execute.py \
  --target skills/<skill>/SKILL.md \
  --eval-script ./scripts/eval_runner.py \
  --goal "Improve routing precision" \
  --iterations 3
```

## Workflow

1. **Configuration**: Confirm target skill, evaluation benchmark script, and iteration budget.
2. **Baseline Run**: Establish baseline score using deterministic evaluation fixtures.
3. **Mutation**: Mutate one hypothesis at a time in isolated worktree.
4. **Scoring**: Re-evaluate against the baseline. Keep wins, discard regressions.
5. **Ledger Declaration**: Conclude with Source Transparency Declaration and iteration ledger.

## Verification

```bash
# Verify evaluation fixtures run cleanly
python3 -m pytest scripts   # from the running-exploration-cycle skill folder
```

## References

- [dispatch-strategies.md](dispatch-strategies.md) — Model dispatching and evaluation strategies.


---

## Appendix A: optimization program (former `program.md`)

# Optimization Program: agent-exploration-cycle

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly matched against
  the mutation target's content (frontmatter only for SKILL.md; full content otherwise)
- `heuristic_score`: structural health check (varies by target type)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  (dual guard prevents metric gaming: padding increases recall but drops precision/F1)

Mutation target: `OVERVIEW.md` — you may ONLY edit this file each iteration.
One focused change per iteration. No bulk rewrites.

Locked (never modify during the loop):
- `../agent-agentic-os/skills/os-lab-scorer/scripts/evaluate.py`
- `../agent-agentic-os/skills/os-lab-scorer/scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `OVERVIEW.md` (one focused change)
2. `python3 ../agent-agentic-os/skills/os-lab-scorer/scripts/evaluate.py --skill OVERVIEW.md --desc "what you changed"`
3. If KEEP (exit 0): `git add OVERVIEW.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted `OVERVIEW.md` automatically

Run iteratively. Stop when the target score is reached or when manually interrupted.

---

## Notes (fill in before starting the loop)

- **What is being optimized**: <!-- e.g. skill trigger phrase coverage, function accuracy, config tuning -->
- **Target score**: <!-- e.g. 0.95, or leave blank to run until manually interrupted -->
- **Max iterations**: <!-- e.g. 50, or leave blank to run until manually interrupted -->
- **Baseline established**: <!-- date + commit hash, filled in by evaluate.py --baseline -->


---

## Appendix B: proposer prompt (former `copilot_proposer_prompt.md`)

# Copilot Proposer Prompt — agent-exploration-cycle

> **This file is a first-class evolvable artifact.**
> The loop reads this file each iteration and appends the dynamic context (current skill,
> evals, failure analysis) at call time. Improve this file when the proposals feel off —
> a better prompt produces better mutations and faster convergence.
>
> **After the session:** if this prompt evolved significantly, contribute a refined copy
> to the `skill-proposer-prompt` reference of the `cli-agent` skill
> so future loops start from a stronger baseline.

---

## System Instructions

You are an expert at optimizing OVERVIEW.md files for a boolean-OR keyword scorer (4+ characters).

**HOW THE SCORER WORKS:**
- Extracts every word ≥4 chars from the `description` field: `re.findall(r'\b\w{4,}\b', description.lower())`
- Checks exact word overlap with each eval prompt — semantics and synonyms do NOT matter
- Score = (routing_accuracy × 0.7) + (heuristic × 0.3). F1 must not regress.

**STRATEGY — do this analysis before proposing:**
1. Safe tokens = 4+ char words in `should_trigger: true` prompts but NOT in any false prompt → add these
2. Bridge words = words in BOTH true and false prompts → never add, cause false positives
3. Pollution words = words in false prompts that already appear in the description → remove these

**CONSTRAINTS:**
- Minimal edits (≤10 lines). Fix ONLY `description` and/or `<example>` blocks.
- No `keywords:` field — it disables description scanning (known footgun).
- Output raw OVERVIEW.md only — no commentary, no fences, no explanation.
- **Bridge word guard (mandatory before every proposal):** When refining an existing description, do NOT silently re-introduce words that were previously removed. Before writing your proposal, compare every 4+ char word you plan to add against the false-prompt word list. If a word appears in ANY `should_trigger: false` prompt, it is a bridge word — do not add it, even if it seems semantically correct for the skill. Use the collision matrix in the Trap Warning section to verify.

---

## Trap Warning (update after each DISCARD — prevents repeating failed approaches)

Known bridge words for this skill that cause false positives when added to the description.
**Run the collision matrix before proposing** (see Step A3 in eval-instructions):
```bash
python -c "
import json, re
evals = json.load(open('./evals/evals.json'))
desc = open('./OVERVIEW.md').read()
desc_m = re.search(r'description: (.+?)(?=\n\w|\Z)', desc, re.S)
desc_words = set(re.findall(r'\b\w{4,}\b', desc_m.group(1).lower())) if desc_m else set()
false_words = set(w for e in evals if not e['should_trigger'] for w in re.findall(r'\b\w{4,}\b', e['prompt'].lower()))
print('Bridge words (remove from description):', sorted(desc_words & false_words))
"
```

Discovered bridge words (fill in as they are found):
- *(none yet — add as discovered, e.g. `branch` — appears in FP prompts 9, 10, 12)*


---

## Appendix C: former executor `exploration_optimizer_execute.py`

```text
exploration_optimizer_execute.py
=====================================

Purpose:
    Implements an autoresearch-style optimization loop: Propose -> Test -> Decide.
    Optimizes skills based on routing and artifact quality evaluations.

Layer: Execution / Optimization

Usage Examples:
    pythonexploration_optimizer_execute.py --target skill.md --eval-script eval.py --goal "improve clarity"

Supported Object Types:
    SKILL.md files

CLI Arguments:
    --target: Path to the skill file to optimize.
    --eval-script: Path to eval_runner.py.
    --goal: Optimization goal.
    --iterations: Number of iterations.
    --ledger: Path to results TSV.
    --dispatch-script: Enabling artifact quality eval.
    --scenario-brief: Canonical session brief for eval.
    --check-gaps-script: Counting gap markers in output.

Input Files:
    - Target skill.md file
    - scenario brief

Output:
    - Updated skill file.
    - Updated ledger results TSV.

Key Functions:
    run_eval(): Runs routing evaluation.
    run_artifact_eval(): Runs artifact quality evaluation.
    propose_change(): Proposes optimization changes.
    main(): Coordinates the optimization loop.

Script Dependencies:
    os, sys, argparse, subprocess, json, shutil, re, pathlib, datetime

Consumed by:
    - Exploration cycle orchestrator
```

The executor itself is retired: the `os-lab-*` skills in `agent-agentic-os` (scorer, loop, planner) implement this loop now. `program.md` and the proposer prompt above already call `os-lab-scorer`'s `evaluate.py`.
