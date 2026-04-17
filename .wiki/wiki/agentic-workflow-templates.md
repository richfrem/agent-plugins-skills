---
concept: agentic-workflow-templates
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-agentic-workflow/references/workflow-templates.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.775770+00:00
cluster: template
content_hash: 361668877a5c3daf
---

# Agentic Workflow Templates

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

## Template C — Evalua

*(content truncated)*

## See Also

- [[procedural-fallback-tree-create-agentic-workflow]]
- [[procedural-fallback-tree-create-agentic-workflow]]
- [[procedural-fallback-tree-create-agentic-workflow]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-harness-learning-layer-formerly-agentic-os]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-agentic-workflow/references/workflow-templates.md`
- **Indexed:** 2026-04-17T06:42:09.775770+00:00
