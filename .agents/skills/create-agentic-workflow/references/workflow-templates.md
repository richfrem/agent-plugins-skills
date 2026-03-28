# Agentic Workflow Templates

Reference implementations for each workflow pattern. Copy and adapt for `create-agentic-workflow`.

---

## Template A — Sequential Workflow (Prompt Chaining)

Use when: steps run in order, each output feeds the next, subtasks are predictable.

```markdown
---
name: pr-review
description: Run an automated PR review. Use when user asks to "review my PR", "check this PR".
argument-hint: "[PR number or branch name]"
allowed-tools: Bash(git *), Read(*), Task(*)
disable-model-invocation: true
---

Review the pull request specified in $ARGUMENTS.

## Phase 1: Context Gathering
1. `git fetch origin`
2. `git diff origin/main...HEAD --stat` -- understand scope
3. `git log origin/main...HEAD --oneline` -- understand intent

## Phase 2: Review (sub-agent)
Spawn a Task:
  Agent: code-reviewer
  Objective: Review the diff for correctness, security, and style.
  Output: Markdown table — File | Finding | Severity (critical/moderate/minor) | Recommendation
  Task boundary: Only read files in the diff. Do not run tests or modify files.
  Tools: Read(*), Bash(git diff *)

Wait for sub-agent to complete.

## Phase 3: Output
Assemble the review table.
Add a Summary section with:
- Overall risk (critical / moderate / low)
- Count of findings by severity
- Verdict: Approve / Request changes / Needs design review
```

---

## Template B — Orchestrator-Workers (Parallel, Dynamic Decomposition)

Use when: you cannot predict subtasks in advance; task has independent parallel components;
each component needs its own context window.

> Anthropic guidance: each worker needs a clear objective, output format, tool list, and
> explicit task boundary. Vague worker instructions cause duplication and gaps.

```markdown
---
name: audit
description: Run a comprehensive code audit. Use for "audit this codebase", "code quality check", "security review".
allowed-tools: Task(*), Read(*), Bash(*)
disable-model-invocation: true
---

Orchestrate a parallel code audit for the current project.

## Pre-flight
Verify: `git status` — note any uncommitted changes (review only, do not block).

## Decomposition
Analyse the project first (read package.json / pyproject.toml / Makefile).
Then spawn three parallel Tasks — start all three in the same turn:

Task 1 — Security:
  Objective: Scan all source files for: SQL injection, XSS, hardcoded secrets,
    path traversal, insecure dependencies, missing input validation.
  Output format: JSON array [{file, line, finding, severity, cwe_id}]
  Tools: Read(*), Bash(grep *), Bash(find *)
  Do NOT: modify files, run package installs, make network requests
  Context: Project root is ${CLAUDE_PROJECT_DIR}

Task 2 — Performance:
  Objective: Find N+1 query patterns, large sync operations in async contexts,
    missing indexes (ORM usage), memory-intensive loops.
  Output format: JSON array [{file, line, pattern, estimated_impact, fix_suggestion}]
  Tools: Read(*), Bash(grep *)
  Do NOT: run benchmarks or tests

Task 3 — Style and Maintainability:
  Objective: Check for functions > 50 lines, files > 300 lines, missing error handling,
    debug statements (console.log/print), TODO comments.
  Output format: JSON array [{file, line, issue_type, value}]
  Tools: Read(*), Bash(*)

## Synthesis
After all three complete:
1. Merge the arrays
2. Sort by severity (critical first)
3. Deduplicate (same file+line from multiple tasks)
4. Output as severity-stratified table:

| File | Line | Finding | Severity | Recommendation |
|---|---|---|---|---|
```

**Key orchestrator rules (from Anthropic's multi-agent research):**
- Each subtask must be independently completable — no shared mutable state
- Give each worker enough context to complete without calling back
- If subtask B requires subtask A's output → make it sequential, not parallel
- Scale effort to complexity: simple check = 1 worker, deep analysis = 3-5 workers
- Subagents do NOT inherit parent permissions — set tools explicitly per worker

---

## Template C — Evaluator-Optimizer

Use when: quality can be measured; iterative improvement is needed.

```markdown
---
name: write-tests
description: Write and iteratively improve tests for a file or function.
argument-hint: "[file path or function name]"
allowed-tools: Task(*), Read(*), Write(*), Bash(*)
disable-model-invocation: true
---

Write and evaluate tests for $ARGUMENTS using an evaluator-optimizer loop.

## Phase 1: Generate (Worker)
Spawn Task — writer:
  Objective: Write comprehensive unit tests for the target.
  Output: A test file with >= 5 cases covering: happy path, edge cases, error conditions.
  Tools: Read($ARGUMENTS), Write(tests/)
  Context: Use the existing test framework in the project.

## Phase 2: Evaluate
After writer completes, spawn Task — evaluator:
  Objective: Evaluate the generated tests:
    1. Happy path covered? (yes/no)
    2. Error conditions covered? (yes/no)
    3. Missing cases? (list them)
    4. Do tests run? (run them, report result)
  Output: JSON {score: 0-10, missing_cases: [], run_result: "pass|fail|error", feedback: ""}
  Tools: Read(tests/), Bash(npm test -- <file> OR pytest <file>)

## Phase 3: Iterate (if score < 8)
If score < 8 or run_result != pass:
  Spawn a new writer Task with:
  - Original task
  - Evaluator feedback embedded in objective
  - Max 2 additional iterations

## Output
Final test file path and coverage summary.
```

---

## Template D — Stateful / Checkpointed

Use when: workflow is long-running; must survive interruption; operates on many files.

```markdown
---
name: large-refactor
description: Orchestrate a large codebase refactor with checkpointing.
argument-hint: "[description of change]"
allowed-tools: Bash(*), Read(*), Write(*), Task(*)
disable-model-invocation: true
---

Run a checkpointed large-scale refactor for: $ARGUMENTS

## Safety Pre-flight
1. Verify git working tree is clean (`git status`)
2. Create checkpoint branch: `git checkout -b refactor/$(date +%Y%m%d)-checkpoint`
3. List all files to change and show count
4. Ask user: "Proceed with refactor of N files? (yes / cancel)"

## Checkpoint State
Store progress in `.claude/refactor-state.json`:
```json
{
  "task": "$ARGUMENTS",
  "total_files": 0,
  "completed": [],
  "failed": [],
  "checkpoint_branch": "refactor/YYYYMMDD-checkpoint"
}
```

## Execution — Batched Parallel Workers
Process files in batches of 10.
For each batch, spawn parallel Tasks (one per file):
  Objective: Apply the specified refactor to this single file only.
  Output: {file, status: "changed|unchanged|error", summary}
  Tools: Read(<file>), Write(<file>), Bash(grep * <file>)
  Do NOT: modify any other file

After each batch:
- Update `.claude/refactor-state.json`
- Commit: `git commit -m "refactor(checkpoint): batch N/M"`

## Failure Handling
- Log failed files to state file
- Continue with remaining files
- Report failures at end with suggested manual fixes

## Completion
1. Summary: N changed, M unchanged, K failed
2. Run test suite
3. If tests pass: offer to squash checkpoint commits
4. If tests fail: show which files to investigate
```

---

## Complexity Decision Reference

Before scaffolding any agentic workflow, use this table:

| Answer | Recommended approach |
|---|---|
| Single-step, predictable | Simple command (no agents) |
| Multi-step, linear, known subtasks | Sequential command with one Task |
| Independent parallel sections | Orchestrator-Workers (Template B) |
| Quality needs measurement + iteration | Evaluator-Optimizer (Template C) |
| Long-running, many files, needs recovery | Stateful/Checkpointed (Template D) |

Multi-agent workflows use ~15x more tokens than single-agent chat. Only use them when
the task genuinely warrants it.
