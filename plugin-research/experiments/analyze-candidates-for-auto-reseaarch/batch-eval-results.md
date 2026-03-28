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

**Proceed -- HIGH priority.** Build the golden task set first (10 tasks, 2 hours of work), then the evaluate.py harness. The loop can run overnight with haiku as the trial model. Expected to yield significant compliance improvements in 20-30 iterations. The Goodhart risk is manageable by checking that the Bash command matches patterns like `pytest`, `ruff`, `cargo test`, `npm test`, etc.

---

## Autoresearch Fit Assessment: context-bundler (context-bundling)

**Plugin:** `context-bundler`
**Skill path:** `plugins/context-bundler/skills/context-bundler/SKILL.md`
**Existing JSON viability score:** 35/40

### Scores

| Dimension | Score | Rationale |
|---|---|---|
| Objectivity | 6/10 | The JSON's proposed metric (token count minus gitignore penalty) is concrete, but "token density" optimization has ambiguity: fewer tokens is not always better if coverage drops. A cleaner metric is `covered_files / requested_files` minus `gitignore_violations * penalty`. Still, this is measurable with a script. |
| Execution Speed | 8/10 | The `bundle.py` script itself runs in seconds. The skill has interactive phases (discovery, confirmation) but these can be bypassed in eval mode by providing a pre-built `file-manifest.json` directly to the script. Fast loop feasible. |
| Frequency of Use | 8/10 | Used frequently for context sharing with other agents and external review. Not quite daily but several times per week. |
| Potential Utility | 7/10 | Optimizing token density is high-value in a context-window-constrained world. However, the primary failure mode (including gitignore files) is already well-understood and a relatively simple fix. Less systemic than verification compliance. |
| **TOTAL** | **29/40** | Lower than JSON's 35. The interactive phases reduce execution speed score; the metric ambiguity reduces objectivity. |

**Verdict: MEDIUM**

### Critical Insight: Two Separate Loops Needed

The context-bundler has two distinct mutation targets that should NOT be combined:

1. **Loop A - Script Quality**: Optimize `bundle.py` for token efficiency and gitignore compliance. Pure Python file, fast loop, very objective metric.
2. **Loop B - Prompt Quality**: Optimize `SKILL.md` to produce better manifests (fewer irrelevant files, better file selection guidance). LLM-in-the-loop, slower, semi-objective.

Start with Loop A -- it is far more viable.

### Proposed 3-File Architecture (Loop A - Script Quality)

**Spec (`program.md`):**
> Optimize `bundle.py` to maximize context bundle quality. Metric: `coverage_score = (files_covered / files_requested) - (gitignore_violations * 0.5) - (duplicate_content_ratio * 0.3)`. Higher is better, max 1.0. You may only modify `bundle.py`. NEVER modify `evaluate.py` or `test-fixtures/`. NEVER STOP.

**Mutation Target:**
> `scripts/bundle.py` -- the agent modifies file inclusion logic, deduplication, gitignore parsing, path resolution, and output formatting. One change per loop.

**Evaluator (`evaluate.py`):**
```bash
# Given a golden manifest with known expected outputs:
python evaluate.py \
  --manifest test-fixtures/golden-manifest.json \
  --expected test-fixtures/expected-coverage.json \
  --gitignore .gitignore
# Outputs: coverage_score (0.00 - 1.00)
# e.g., 0.85 = good coverage, 1 gitignore violation detected
```
> Deterministic: **YES** -- pure Python file operations. Same input always produces same score. This is the ideal evaluator.

### Key Barriers

1. **Interactive phases in SKILL.md**: The skill's core workflow requires human confirmation at Phase 2. For Loop A (script optimization), this is bypassed entirely since we test the script directly. For Loop B (prompt optimization), the interactive phases become a liability -- they make the loop dependent on simulating human responses.
2. **Metric completeness**: "Fewer tokens is better" is naive. A bundle with 100% coverage but 200k tokens is better than one with 80% coverage and 50k tokens. The evaluator needs a weighted formula that balances both.
3. **Test fixture required**: Need a golden `file-manifest.json` with known expected outputs and a matching `.gitignore` to test against. Medium effort to create.

### Recommendation

**Proceed with Loop A only (script optimization) -- MEDIUM-HIGH priority.** The script loop is deterministic and fast -- this is an excellent first autoresearch project. Build the test fixture (1-2 hours), then run Loop A overnight. Loop B (prompt optimization) should wait until Loop A is complete and the metric is validated. The interactive phases in SKILL.md are a barrier for prompt optimization but are completely irrelevant for script optimization.

---

## Comparative Summary

| Skill | Total | Verdict | Loop Type | Key Barrier |
|---|---|---|---|---|
| verification-before-completion | 35/40 | HIGH | LLM-in-loop (stochastic) | Need golden task set + haiku harness |
| context-bundler (Loop A - script) | 29/40 | MEDIUM-HIGH | Pure script (deterministic) | Need test fixtures |

**Recommended sequence:**
1. `context-bundler` Loop A first -- deterministic, fastest to set up, proves out the tooling
2. `verification-before-completion` second -- higher impact but requires more setup (golden tasks + haiku eval harness)

---

*Continue with next batch? Run eval on `test-driven-development` and `using-git-worktrees` (scores 35/35).*
