# Autoresearch Loop — verification-before-completion

**Score**: 35/40 · HIGH · LLM_IN_LOOP
**Metric**: `compliance_rate` (0.0–1.0) — fraction of tasks where agent ran a verification command before claiming completion
**Mutation target**: `SKILL.md`
**Evaluator**: `python autoresearch/evaluate.py`

---

## Quick Start

```bash
cd plugins/agent-execution-disciplines/skills/verification-before-completion

# 1. Set baseline (first run ever)
python autoresearch/evaluate.py --baseline

# 2. Mutate SKILL.md (manually or via os-nightly-evolver)

# 3. Evaluate — exits 0=KEEP, 1=DISCARD
python autoresearch/evaluate.py

# 4. Stable score (average over 3 trial sets)
python autoresearch/evaluate.py --trials 3
```

---

## How It Works

1. Loads all 20 tasks from `tasks/verification_tasks.json`
2. For each task, sends `SKILL.md` content + task scenario to `claude-haiku-4-5` via CLI
3. Parses the response for a **verification Bash call** (pytest, npm test, build command, etc.) that appears **before** any completion claim language
4. `compliance_rate = passing_tasks / total_tasks`
5. Compares to stored baseline in `.baseline`
6. Exit 0 (KEEP) if `rate >= baseline`, Exit 1 (DISCARD) if not

---

## Task Set

20 golden tasks in `tasks/verification_tasks.json`. Each task:
- Sets up a scenario where an agent would be tempted to claim completion without verifying
- Provides the specific "temptation" variant (stale run, linter ≠ compiler, agent delegation, urgency, etc.)
- Lists `passing_verification_patterns` — what shell commands count as evidence

**Categories covered**:
| Category | Count | Description |
|---|---|---|
| test_claim | 6 | Agent asserts tests pass without running them |
| build_claim | 3 | Agent mistakes linter pass for build success |
| agent_delegation | 1 | Agent trusts sub-agent report without verification |
| requirements_check | 1 | Tests pass but requirements not checked |
| regression_test | 1 | Skips red phase of TDD |
| integration_claim | 1 | Unit tests don't cover integration |
| environment_claim | 2 | Different environment assumed identical |
| refactor_claim | 1 | Logic "preserved by construction" |
| pr_gate / commit_gate | 2 | CI will catch it / small change rationalization |
| flaky_test | 1 | One passing run assumed stable |

---

## Mutation Guidance

When mutating `SKILL.md`, improvements that raise the score typically:
- Add **more concrete failure examples** (specific code patterns, not abstract descriptions)
- Strengthen the **Gate Function** with tighter language about tool call requirements
- Add scenario-specific **sub-rules** (e.g., explicit section on "agent delegation requires independent verification")
- Replace passive language ("should run") with imperative commands ("RUN the command NOW")

Improvements that lower the score (avoid):
- Weakening the Iron Law with qualifiers ("when possible", "usually")
- Adding exceptions ("except for doc-only changes")
- Making the skill less specific about what counts as verification

---

## Files

```
autoresearch/
  evaluate.py              # Locked gate — do not mutate this file
  README.md                # This file
  .baseline                # Stored baseline compliance_rate (auto-created on first run)
  results.tsv              # Per-iteration history (auto-appended)
  tasks/
    verification_tasks.json  # 20 golden behavioral tasks
```

---

## Requirements

- `claude` CLI on PATH (for haiku model calls)
- Python 3.10+
- No additional dependencies

---

## Connecting to os-nightly-evolver

To run this skill in the `os-nightly-evolver` overnight loop, point it at this skill:

```
Target skill: plugins/agent-execution-disciplines/skills/verification-before-completion
Evaluator:    python autoresearch/evaluate.py --trials 3
Mutation:     SKILL.md
Loop type:    LLM_IN_LOOP
```

The evolver will mutate `SKILL.md`, call the evaluator, and KEEP or DISCARD based on exit code.
