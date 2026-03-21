---
name: continuous-skill-optimizer
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill-creator repositories.
description: >
  Autonomous optimization loop for any skill. Trigger with "optimize this skill",
  "run the continuous optimizer", "improve this trigger description", or when you want
  to automatically test variations of a skill's instructions to find the most empirically
  effective prompt using the benchmarking engine.
disable-model-invocation: false
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./././requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Continuous Skill Optimizer

You are an expert AI evaluations and prompt optimization engineer. 

This skill implements autoresearch-style optimization for skill trigger quality and instruction fidelity. It conducts iterative experiments against an evaluation dataset to empirically improve a target skill.

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 1: Guided Discovery
Conduct a setup interview to gather the experiment parameters:
1. **Target Skill**: The directory path to the skill to optimize (e.g., `plugins/my-plugin/skills/my-skill`).
2. **Eval Set Path**: The path to the evaluation `.jsonl` or `.csv` dataset (ask if they want to generate a default one first if they don't have it).
3. **Loop Budget**: How many iterations should the optimizer run? (e.g., `max-iterations=5`).
4. **Target Variable**: Are we optimizing the `description:` (trigger phrase) or the `body` (instructions)?
5. **Auto-Apply**: Should winning iterations automatically overwrite the source skill, or just be logged as recommendations?

Wait for the user's answers before proceeding.

### Phase 2: Recap & Confirm
Summarize the parameters decided in Phase 1 back to the user:
- Target Skill: [Path]
- Eval Set: [Path]
- Budget: [N] iterations
- Auto-Apply: [Yes/No]

Ask: "Should I proceed with the optimization loop?"

### Phase 3: Execute Optimization Loop
Once approved, execute the optimizer script. 

```bash
# Example syntax:
python ${CLAUDE_PLUGIN_ROOT}/scripts/execute_optimizer.py \
  --skill [target-skill] \
  --evals [eval-set-path] \
  --max-iterations [N] \
  --auto-apply [true/false]
```

**Under the Hood (Autoresearch Mechanics):**
The script runs a strict loop governed by these rules:
1. Run and record a baseline evaluation.
2. Change *one dominant variable* per iteration (e.g., description wording, scope, exclusions).
3. Classify the iteration as `keep`, `discard`, or `crash`.
4. If it crashes/timeouts, it logs the failure and reverts to the last known-good state.
5. All runs log a persistent ledger to `evals/results.tsv`.

### Phase 4: Post-Optimization Review
After execution, summarize the findings. If `auto-apply` was false, provide the winning description/body text and ask the user if they'd like you to manually apply it to the skill. 

Advise the user to review the ledger at `evals/results.tsv` or run `./../scripts/generate_review.py` for visual review of the iteration outcomes.
