# Quickstart: How to Run an Optimization Loop on Any Skill

> **Prerequisite:** The target skill folder must be inside a git repository.

You only need two things:
1. A copy of the **target skill folder** you want to improve.
2. The **skill-improvement-eval** engine (the stateless evaluator).

## 1. Scaffold the Experiment (One-Time)

```bash
python .agents/skills/skill-improvement-eval/scripts/init_autoresearch.py \
    --experiment-dir .agents/skills/your-target-skill \
    --mutation-target SKILL.md
```

This deploys:
- `references/program.md` — your optimization spec
- `evals/evals.json` — test cases
- `evals/results.tsv` — ledger header

## 2. Customize the Experiment (You Do This Once)

**Edit `references/program.md`**
Fill in the Notes section:
- What exactly you are optimizing
- Desired target `quality_score` (e.g. 0.95)
- Any special constraints

**Edit `evals/evals.json`**
Replace every `REPLACE` placeholder with real test prompts and correct `should_trigger` values.
*Important: This is the most critical step. Poor or incomplete test cases lead to meaningless optimization.*

## 3. Establish the Baseline

```bash
python .agents/skills/skill-improvement-eval/scripts/evaluate.py \
    --skill .agents/skills/your-target-skill \
    --baseline \
    --desc "initial baseline"
```
*This records the starting score and creates the SHA256 lock snapshot (.lock.hashes).*

## 4. Run the Autonomous Loop

Your main agent (or os-learning-loop) repeatedly runs:

```bash
# Example single iteration
python .agents/skills/skill-improvement-eval/scripts/evaluate.py \
    --skill .agents/skills/your-target-skill \
    --desc "improved trigger phrasing for edge case X"
```

**Behavior:**
- `exit 0` (KEEP) → Agent should `git add` + `git commit`
- `exit 1` (DISCARD) → `evaluate.py` already reverted the files automatically

The loop continues until you stop it manually or the target score in `program.md` is reached.

---

### Tips for Success
- Start with a HIGH viability skill from your ranked list.
- Ensure `evals/evals.json` contains a good mix of positive and adversarial (negative) examples.
- One focused change per iteration is critical — bulk rewrites are usually discarded.
- Monitor the first few iterations manually to confirm the agent is making sensible mutations.

You’re now ready to run continuous, autonomous improvement on any skill!
