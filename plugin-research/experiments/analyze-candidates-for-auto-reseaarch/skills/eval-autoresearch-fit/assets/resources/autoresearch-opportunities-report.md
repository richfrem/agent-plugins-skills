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

**Evaluator**: `ruff check test_fixtures/ --output-format concise 2>&1 | wc -l`

---

### 4. `agent-execution-disciplines/using-git-worktrees` — 33/40 · HIGH · DETERMINISTIC

**Opportunity**: **Best first loop to build** if you want a DETERMINISTIC loop with no golden task set
dependency. Evaluator checks whether the agent ran `git worktree add` instead of a destructive
`git checkout -b` in the main tree. Shell-measurable: `git worktree list | grep -c feature/test`.
No LLM trial averaging. Iteration time ~15 seconds.

**Metric**: Did agent issue `git worktree add` for the new branch? Binary (1=yes, 0=no). Secondary:
`git worktree list` count matches expected.

**Blocker**: Human confirmation gate when preferred directory is ambiguous. Proxy metric must exclude
heavy installs to keep iterations fast.

**Evaluator**: `git worktree add .worktrees/feature/test -b feature/test && git worktree list | grep -c feature/test`

---

### 5. `spec-kitty-plugin/spec-kitty-status` — 33/40 · HIGH · DETERMINISTIC

**Opportunity**: The spec-kitty status skill exposes a `progress_percentage` via a Python API, making it
a clean numeric target. Mutate the workflow markdown, run the status command, extract the percentage.
No fixture needed — any real work package in the repo serves as live test data.

**Metric**: `progress_percentage` (0.0–100.0) from `show_kanban_status()['progress_percentage']`.
Higher is better (more WP tasks tracked and reported correctly).

**Blocker**: No dedicated headless `evaluate.py` yet. Needs a thin wrapper; 30-minute build.

**Evaluator**: `python -c "from specify_cli.agent_utils.status import show_kanban_status; print(show_kanban_status()['progress_percentage'])"`

---

### 6. `agent-agentic-os/os-eval-runner` — 32/40 · HIGH · DETERMINISTIC

**Opportunity**: The eval runner already has a `quality_score` (0.0–1.0) emitted by `eval_runner.py --json`.
This is a recursive loop: improve the skill that runs other skills' evals. A better routing quality score
cascades to every other autoresearch loop downstream. The evaluator is already headless and deterministic.

**Metric**: `quality_score` (0.0–1.0) from `eval_runner.py --json`. KEEP/DISCARD enforced by evaluate.py
exit code (0=KEEP, 1=DISCARD).

**Blocker**: Requires authored `evals.json` and `references/program.md` fixtures before the loop produces
meaningful results. Absolute paths in `.lock.hashes` cause portability issues in new environments.

**Evaluator**: `python scripts/eval_runner.py --skill plugins/agent-agentic-os/skills/os-eval-runner --json | python -c 'import sys,json; print(json.load(sys.stdin)["quality_score"])'`

---

### 7. `agent-plugin-analyzer/self-audit` — 32/40 · HIGH · LLM_IN_LOOP

**Opportunity**: Self-audit uses deterministic scanners (programmatic assertion checks) against three
fixtures: self, gold-standard plugin, and flawed plugin. The score is the count of failing assertions
across all three — fully shell-measurable. High frequency of use (runs every time plugins are reviewed)
and high utility (catches structural regressions automatically).

**Metric**: `failing_assertion_count` (integer ≥0) — sum of failing checks across self/gold/flawed
fixtures. Target = 0.

**Blocker**: Evaluator invokes a 6-phase LLM analysis, introducing non-determinism. Pin evaluator to
deterministic assertion exit codes only; constrain mutations to one file (`analyzer.py`).

**Evaluator**: Shell command asserting fixture outcomes; see assessment file for full command.

---

### 8. `copilot-cli/copilot-cli-agent` — 32/40 · HIGH · LLM_IN_LOOP

**Opportunity**: A smoke-test loop that mutates the Copilot persona prompt and verifies the CLI responds
correctly. Evaluator sends one deterministic probe (`Reply with exactly: COPILOT_CLI_OK`) and checks
for exact string match. Fast (~20s per iteration) and directly improves the sub-agent used by this
sweep itself.

**Metric**: Binary pass/fail — `grep -c '^COPILOT_CLI_OK$'` returns 1 (KEEP) or 0 (DISCARD).

**Blocker**: Auth token environment variable conflicts can cause flaky failures. Requires consistent
`env -u GITHUB_TOKEN -u GH_TOKEN` handling.

**Evaluator**: `env -u GITHUB_TOKEN -u GH_TOKEN copilot -p "Reply with exactly: COPILOT_CLI_OK" 2>/dev/null | grep -c '^COPILOT_CLI_OK$'`

---

### 9. `excel-to-csv/excel-to-csv` — 32/40 · HIGH · DETERMINISTIC

**Opportunity**: `verify_csv.py` already exists and produces an `error_count`. Mutate `convert.py`,
run converter on test fixtures, check error count. Fully deterministic, no LLM involved. Strong
signal: either the output CSV is valid or it isn't.

**Metric**: `error_count` (integer ≥0) from `verify_csv.py`. Target = 0.

**Blocker**: No canonical `evaluate.py` entrypoint yet; `verify_csv.py` needs a thin wrapper. Requires
`pandas`/`openpyxl` in environment.

**Evaluator**: `python scripts/verify_csv.py output/Sheet1.csv && echo 0 || echo 1`

---

### 10. `dependency-management/dependency-management` — 31/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Mutate `requirements-core.in` (or a single service `.in`), run `pip-compile` across
all services, count failures. A clean compile = all downstream lockfiles regenerated successfully.
High utility: dependency management issues cascade to every other Python skill.

**Metric**: `compile_failure_count` — count of services that fail `pip-compile` or `pip install`
after the mutation (integer, 0 = all succeed).

**Blocker**: Requires PyPI network access (introduces nondeterminism). Target a single service `.in`
rather than core to minimize cascade effects.

**Evaluator**: Shell script counting `pip-compile` failures per service.

---

### 11. `agent-agentic-os/todo-check` — 31/40 · MEDIUM · DETERMINISTIC

**Opportunity**: The evaluator is a one-liner: count TODO/FIXME/XXX markers in the target file.
Perfectly deterministic, runs in milliseconds. Mutate `check_todos.py`, run against a test file
with known markers, verify count matches expected. Lowest-friction loop to bootstrap.

**Metric**: `marker_count` (integer ≥0) from `python scripts/check_todos.py <path> | wc -l`.
Lower is better; target = 0.

**Blocker**: Missing `evaluate.py` and defined single-file mutation target. ~1 hour to add both.

**Evaluator**: `python ${CLAUDE_PLUGIN_ROOT}/skills/todo-check/scripts/check_todos.py <path> | wc -l`

---

### 12. `obsidian-integration/obsidian-graph-traversal` — 31/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Orphan note count is a deterministic, fast shell-measured metric. Mutate `graph_ops.py`,
run against a test vault, count orphans. The metric directly reflects graph quality and is
immediately actionable. Fast iteration time (~2s per loop).

**Metric**: `orphan_count` (integer ≥0) from `python ./graph_ops.py orphans --vault-root ./test_vault | wc -l`.
Lower is better; target = 0.

**Blocker**: No `evaluate.py` and no guaranteed single-file mutation boundary (realistic improvements
likely span multiple modules).

**Evaluator**: `python ./graph_ops.py orphans --vault-root ./test_vault | wc -l`

---

### 13. `spec-kitty-plugin/spec-kitty-accept` — 31/40 · MEDIUM · DETERMINISTIC

**Opportunity**: The CLI emits deterministic JSON with `.summary.ok` — a clean binary KEEP/DISCARD
signal. Mutate the workflow markdown, run acceptance in headless mode with pre-supplied args, check
the flag.

**Metric**: Binary `summary.ok` (1=accepted, 0=rejected).

**Blocker**: Skill is interactive by design; discovery stage prompts block headless runs. Evaluator
wrapper must supply all args and convert error cases to deterministic outcomes.

**Evaluator**: `spec-kitty agent feature accept --json --actor windsurf --mode pr --feature $FEATURE | jq -r '.summary.ok | if . then 1 else 0 end'`

---

### 14. `spec-kitty-plugin/spec-kitty-merge` — 31/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Dry-run mode yields `effective_wp_branches` count — a numeric signal available
without touching repo state. Useful for optimizing merge detection accuracy.

**Metric**: `effective_wp_branches` count (integer ≥0) from dry-run JSON.

**Blocker**: Actual merges change repo state across branches, violating the single-file mutation
constraint. Evaluator must stay in dry-run mode only.

**Evaluator**: `spec-kitty merge --feature "$FEATURE" --dry-run --json | jq '.effective_wp_branches | length'`

---

### 15. `mermaid-to-png/convert-mermaid` — 30/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Binary verifier already exists (`verify_png.py`). Mutate `SKILL.md`, generate
a PNG from a test `.mmd` file, verify the output. Clean deterministic pass/fail signal. Useful
for any documentation-heavy workflow.

**Metric**: `mmdc` exit code (0=success, 1=syntax error). Secondary: `verify_png.py` status JSON.

**Blocker**: Headless browser (Chromium/mmdc) dependency can be flaky in CI. Thin wrapper needed
to emit numeric metric.

**Evaluator**: `python scripts/convert.py -i tests/architecture.mmd -o /tmp/arch.png && echo 1 || echo 0`

---

### 16. `agent-plugin-analyzer/path-reference-auditor` — 30/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Missing reference count is a deterministic, auditable metric. Mutate the inventory
scanner, run against the repo, count stale paths. High frequency of use (every plugin delivery).

**Metric**: `missing_reference_count` (integer ≥0). Target = 0.

**Blocker**: Skill only detects issues — it doesn't fix them. Single-file mutation target or
automated fix strategy needed before a useful improvement loop can close the gap.

**Evaluator**: `python scripts/path_reference_auditor.py --project . --phase verify && python -c "import json; inv=json.load(open('temp/inventory.json')); print(sum(1 for r in inv if r.get('status')=='missing'))"`

---

### 17. `plugin-manager/auto-update-plugins` — 30/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Count plugins successfully synced per run. Direct impact on every project that
consumes this repo via pull-based sync. Deterministic when run against reproducible fixtures.

**Metric**: `sync_success_count` (integer ≥0) — plugins correctly installed after a sync run.

**Blocker**: Depends on machine-specific env vars and real external repos. Needs fixture environment
to reproduce headlessly. No compact `evaluate.py` yet.

**Evaluator**: `python scripts/check_and_sync.py --plugins-dir "$PLUGINS_DIR" --report-count`

---

### 18. `context-bundler/context-bundler` — 29/40 · MEDIUM · DETERMINISTIC

**Opportunity**: Split into two loops. **Loop A (start here)**: mutate `bundle.py` script, run
against a golden manifest, measure `coverage_score = (files_covered / files_requested) - penalties`.
Fully DETERMINISTIC, no interactive phases. **Loop B (later)**: mutate `SKILL.md` prompt quality
using LLM judge. Loop A is near-ideal as a first autoresearch project.

**Metric**: `coverage_score` (0.0–1.0) — files covered minus gitignore violations and
duplicate content penalties.

**Blocker**: Needs golden manifest fixture with known expected outputs. ~2 hours to build.

**Evaluator**: `python evaluate.py --manifest test-fixtures/golden-manifest.json --expected test-fixtures/expected-coverage.json`

---

### 19. `memory-management/memory-management` — 29/40 · MEDIUM · LLM_IN_LOOP

**Opportunity**: Memory quality improvement loop. Mutate `snapshot.txt` (the single memory file),
run retrieval queries against the snapshot, measure how often exact or semantically correct answers
are returned. High frequency of use and high utility — every agent session depends on memory quality.

**Metric**: `retrieval_accuracy` (0.0–1.0) — averaged over 5 LLM judgments. Or exact-match rate
on synthetic queries for a deterministic proxy.

**Blocker**: Skill currently writes many files per iteration (hot cache, domain dirs, snapshots).
Must be refactored to single-file mutation before the loop constraint holds. No `evaluate.py` yet.

**Evaluator**: `python skills/memory-management/evaluate.py --trials 5 --mode headless --metric retrieval_accuracy --output json | jq -r '.avg_score'`

---

### 20. `rlm-factory/rlm-search` — 29/40 · MEDIUM · HYBRID

**Opportunity**: RLM search accuracy improvement loop. The ledger is the mutation target;
evaluator checks whether summary lookup returns correct file paths for known queries.
High utility for any agent that uses RLM to navigate large repos.

**Metric**: `search_precision` (0.0–1.0) — fraction of queries where top result matches
expected file, averaged over a held-out query set.

**Blocker**: Assessment file needed to detail evaluator command. Requires pre-populated
ledger as test fixture.

---

## Summary: What to Build First

| Priority | Action | Why |
|---|---|---|
| **1** | Build golden task set for `verification-before-completion` | Unblocks #1 and #2 simultaneously |
| **2** | Scaffold `ruff`-based loop for `coding-conventions-agent` | Zero setup cost, immediate DETERMINISTIC loop |
| **3** | Build worktree evaluator for `using-git-worktrees` | Fastest DETERMINISTIC loop with no task set dependency |
| **4** | Add `evaluate.py` wrapper to `todo-check` and `excel-to-csv` | Both are 1–2 hour jobs; low-hanging fruit |
| **5** | Build Loop A for `context-bundler` (script only) | High-quality loop with clear coverage metric |

**Rule of thumb**: Start with the two DETERMINISTIC skills (#3, #4) to validate the loop infrastructure,
then tackle the LLM_IN_LOOP skills (#1, #2) once `evaluate.py` architecture is proven.
