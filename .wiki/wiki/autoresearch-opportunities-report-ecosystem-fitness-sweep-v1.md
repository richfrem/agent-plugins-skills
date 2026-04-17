---
concept: autoresearch-opportunities-report-ecosystem-fitness-sweep-v1
source: research-docs
source_file: experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/autoresearch-opportunities-report.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.450409+00:00
cluster: deterministic
content_hash: 51202ea596e18975
---

# Autoresearch Opportunities Report — Ecosystem Fitness Sweep v1

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Autoresearch Opportunities Report — Ecosystem Fitness Sweep v1

**Generated**: 2026-03-30
**Scope**: 116/120 skills evaluated (4 scored in prior sessions)
**Model**: GPT-5 mini via Copilot CLI
**Scoring rubric**: Objectivity (10) + Execution Speed (10) + Frequency of Use (10) + Potential Utility (10) = 40 max

---

## How to Read This Report

Each entry shows the skill's **autoresearch viability score**, the **loop type** best suited to it, and the
**proposed benchmark metric** — the single number an `evaluate.py` would track. The **opportunity summary**
explains what an improvement loop would actually optimize and what stands in the way of building it today.

Loop types:
- **DETERMINISTIC** — evaluator uses only shell commands, no LLM. Fastest to iterate, lowest variance.
- **HYBRID** — deterministic core with one LLM-scored quality gate. Medium complexity.
- **LLM_IN_LOOP** — evaluator sends tasks to a model and judges responses. Requires N=5 trial averaging to stabilize scores.

---

## Top 20 Autoresearch Opportunities

### 1. `agent-execution-disciplines/verification-before-completion` — 35/40 · HIGH · LLM_IN_LOOP

**Opportunity**: This skill teaches the agent to run a concrete verification command (test, lint, build) before
claiming a task is complete. An improvement loop would mutate `SKILL.md`, then send 10–20 "temptation tasks"
to a haiku model and measure how often it runs a real shell check before declaring done. The gap between an
agent that claims completion vs. one that proves completion is one of the highest-leverage behavioral changes
in the ecosystem — it directly reduces hallucinated success across all other skills.

**Metric**: `verification_compliance_rate` (0.0–1.0) — fraction of tasks where the agent issued a
`Bash` call matching a test/lint/build pattern before closing the task, averaged over N=5 trials.

**Blocker**: Needs a golden task set of 10–20 problems that tempt false completion claims. That set is the
critical path; evaluate.py architecture is straightforward once it exists.

**Evaluator**: `python evaluate.py --skill SKILL.md --tasks tasks/verification_tasks.json --trials 5 --model claude-haiku-4-5`

---

### 2. `agent-execution-disciplines/test-driven-development` — 35/40 · HIGH · LLM_IN_LOOP

**Opportunity**: TDD skill enforces red-green-refactor order. An improvement loop sends coding challenges
where pre-written code already exists (tempting the agent to skip the red phase) and checks tool call
order: `test_X.py` created → pytest run (must FAIL) → `X.py` modified → pytest run (must PASS). Improving
this skill's routing language tightens one of the most commonly bypassed engineering practices.

**Metric**: `tdd_compliance_rate` — Did the agent produce a failing test before any implementation
changes? Parse pytest stdout for `FAILED` keyword in the first run. Averaged over N=5 haiku trials.

**Blocker**: Same harness architecture as #1; consider sharing `evaluate.py`. Main evaluator complexity
is confirming the "red must fail" phase — harder than simply confirming a test was run.

**Evaluator**: `python evaluate.py --skill SKILL.md --tasks tasks/tdd_tasks.json --trials 5 --model claude-haiku-4-5`

---

### 3. `coding-conventions/coding-conventions-agent` — 34/40 · HIGH · HYBRID

**Opportunity**: Best candidate for an immediate DETERMINISTIC loop (Loop A). The evaluator is zero-setup:
mutate `SKILL.md`, generate code against test fixtures, run `ruff check` and count violations. No golden
task set required. Loop B (JS/TS/docstring quality) can be added later as a HYBRID gate. The ruff score
is perfectly reproducible and runs in under 2 seconds.

**Metric**: `ruff_violation_count` — integer count of `ruff check test_fixtures/` violations. Lower is
better; target = 0. If code breaks `pytest` during mutation, apply a large penalty (+50).

**Blocker**: Ruff covers Python only; JS/TS and C# require separate evaluators for a full-coverage loop.
Start with Python-only Loop A now.

**Evaluator**: `ru

*(content truncated)*

## See Also

- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[autoresearch-architecture]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[overview-of-autoresearch-programmd]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathy-autoresearch-3-file-eval]]

## Raw Source

- **Source:** `research-docs`
- **File:** `experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/autoresearch-opportunities-report.md`
- **Indexed:** 2026-04-17T06:42:10.450409+00:00
