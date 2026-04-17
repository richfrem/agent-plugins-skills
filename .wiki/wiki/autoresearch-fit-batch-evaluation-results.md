---
concept: autoresearch-fit-batch-evaluation-results
source: research-docs
source_file: experiments/analyze-candidates-for-auto-reseaarch/batch-eval-results.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.448477+00:00
cluster: loop
content_hash: 1045d6bce624ab01
---

# Autoresearch Fit: Batch Evaluation Results

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Autoresearch Fit: Batch Evaluation Results

**Evaluator skill:** `eval-autoresearch-fit`
**Reference:** `karpathy-autoresearch-3-file-eval.md`
**Date:** 2026-03-28
**Status:** In Progress - Skills 1-2 of full list

---

## Autoresearch Fit Assessment: verification-before-completion

**Plugin:** `agent-execution-disciplines`
**Skill path:** `plugins/agent-execution-disciplines/skills/verification-before-completion/SKILL.md`
**Existing JSON viability score:** 37/40

### Scores

| Dimension | Score | Rationale |
|---|---|---|
| Objectivity | 8/10 | Core check is binary: did agent call Bash before claiming completion? But "parsed the output" requires some trace interpretation. JSON proposed binary 0/1 which is solid. Slight deduction because the compliance check itself requires an LLM agent run, not a pure shell assertion. |
| Execution Speed | 7/10 | The evaluator must run an LLM agent on a task (2-5 min per trial, need N=5+ for stability). Not a 30-second loop, but feasible with a fixed 3-minute budget per trial. |
| Frequency of Use | 10/10 | Triggered on every single session task completion. Highest-frequency skill in the ecosystem. |
| Potential Utility | 10/10 | False completion claims are one of the highest-cost agent failure modes -- causes rework, broken trust, and undetected bugs shipping. Optimizing this is systemic. |
| **TOTAL** | **35/40** | Slightly lower than JSON's 37 due to execution speed realism (LLM-in-the-loop eval). |

**Verdict: HIGH**

### Proposed 3-File Architecture

**Spec (`program.md`):**
> You are optimizing the `verification-before-completion` SKILL.md. The goal is to maximize `verification_compliance_rate` -- the fraction of coding tasks where the agent runs a shell verification command BEFORE claiming the task is complete. You may freely reword, restructure, add/remove examples, and change emphasis in SKILL.md. You MUST NOT modify `evaluate.py` or `tasks/`. The loop NEVER STOPS until manually interrupted.

**Mutation Target:**
> `SKILL.md` -- the agent rewrites or strengthens the language, examples, red-flag tables, iron laws, and gate function each iteration. One structural change per loop (e.g., move the Iron Law higher, add a new red flag, rewrite the Gate Function steps). This is classic prompt-engineering autoresearch.

**Evaluator (`evaluate.py`):**
```bash
# Run 5 trials: present agent with a task-with-planted-false-completion-temptation
# Check tool call trace: was Bash called before task_completed?
python evaluate.py \
  --skill SKILL.md \
  --tasks tasks/verification_tasks.json \
  --trials 5 \
  --model claude-haiku-4-5  # cheap model for fast loops
# Outputs: verification_compliance_rate (0.00 - 1.00)
# e.g., 0.80 = agent ran verification in 4/5 tasks
```
> Deterministic: **NO** - LLM calls are stochastic. Mitigate by averaging 5 trials. Seed the task prompts to keep inputs constant. A compliance rate improvement of >0.10 over 3 consecutive loops is a reliable signal.

### Key Barriers

1. **LLM-in-the-loop evaluator**: Every trial calls a Claude API, making each loop expensive (~$0.01-0.05 for haiku) and non-deterministic. Use haiku to contain costs; average 5 trials per loop iteration.
2. **Golden task set required**: Need 10-20 standardized tasks that reliably tempt an agent to skip verification (e.g., "the tests were already passing, just fix this small typo"). Does not yet exist -- must be built before the loop starts.
3. **Goodhart risk**: An agent could learn to always call `echo "running tests"` (a trivial Bash call) before claiming completion. Evaluator must check that the Bash command is a meaningful test/lint/build command, not just any shell call.

### Recommendation

**Proceed -- HIGH priority.** Build the golden task set first (10 tasks, 2 hours of work), then the evaluate.py harness. The loop can run overnight with haiku as the trial model. Expected to yield significant compliance improvements in 20-30 iterations. The Goodhart risk is manageable by checking that the Ba

*(content truncated)*

## See Also

- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[evaluate-autoresearch-fit]]
- [[optimization-program-eval-autoresearch-fit]]
- [[evaluate-autoresearch-fit]]
- [[optimization-program-eval-autoresearch-fit]]

## Raw Source

- **Source:** `research-docs`
- **File:** `experiments/analyze-candidates-for-auto-reseaarch/batch-eval-results.md`
- **Indexed:** 2026-04-17T06:42:10.448477+00:00
