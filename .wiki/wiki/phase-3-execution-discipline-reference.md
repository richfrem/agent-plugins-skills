---
concept: phase-3-execution-discipline-reference
source: plugin-code
source_file: exploration-cycle-plugin/skills/exploration-workflow/references/phase3-execution-discipline.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.602037+00:00
cluster: build
content_hash: c27b6c13a7e7ca20
---

# Phase 3 Execution Discipline Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Phase 3 Execution Discipline Reference

> Read this file when Phase 3 (Build) is the active phase. This content is extracted
> from the main workflow to keep the orchestrator concise.

## Superpowers Availability Check

Before invoking any superpowers skill, silently check whether it is available (e.g.,
try to resolve `superpowers:using-git-worktrees`). If superpowers is **not installed**:

- **Greenfield sessions:** Warn the SME: *"I recommend installing the superpowers plugin
  for isolated workspaces and build discipline. For now, I'll proceed without it, but
  the build won't be isolated from your main branch."* Then proceed with `direct` build
  mode — no worktrees, no TDD, no two-stage review. The prototype still gets built, but
  without execution discipline guardrails.
- **Brownfield sessions:** Halt. Announce: *"Building directly into an existing codebase
  without an isolated workspace is risky. Please install the superpowers plugin first."*
  Provide the install command from the README.

If superpowers IS available, proceed with the steps below.

## Step 1 — Isolation: Invoke `superpowers:using-git-worktrees`

Before Phase 3 begins, **invoke the `using-git-worktrees` skill**:

```
Skill invocation: superpowers:using-git-worktrees
Context: "Starting Phase 3 of exploration session '[session name]'.
Create a feature branch and worktree for the build work."
```

- All build work happens in the worktree, not on the main branch
- If worktrees are not available (no git repo, or analysis/docs session), skip this step
- When speaking to the SME, say "isolated workspace" or "feature branch" — not "git worktree"

## Step 2 — Build: Delegate to `subagent-driven-prototyping`

Route to the `subagent-driven-prototyping` skill. It owns all build execution:
- Component decomposition
- Per-component dispatch (using the strategy from Block 0)
- Two-stage review per component (plan alignment + quality)
- TDD validation per component
- Assembly and completion

The orchestrator does NOT duplicate these steps — `subagent-driven-prototyping` handles them.

## Step 3 — Finishing: Invoke `superpowers:finishing-a-development-branch`

When `subagent-driven-prototyping` signals Phase 3 is complete:
1. Invoke the `finishing-a-development-branch` skill
2. Verify all tests/evals pass
3. Present options to the SME: merge locally, create PR, keep branch, or discard
4. Clean up worktree if appropriate

For analysis/docs sessions, this step is skipped (no code branch to finish).

## SME-Friendly Language

| Superpowers term | We say instead |
|---|---|
| "spec reviewer" | "plan alignment check" |
| "code quality reviewer" | "quality check" |
| "TDD" | "validation check" |
| "git worktree" | "isolated workspace" |
| "spec" | "Discovery Plan" |

## Why Validate Prototypes?

The prototype is the *evidence* that the exploration captured the right thing. If the
prototype doesn't match the Discovery Plan, the SME reviews the wrong behavior, the
handoff describes the wrong system, and the engineering team builds from a flawed spec.

Validation isn't about code quality — it's about **exploration accuracy**. Even a
prototype that will be thrown away after handoff must be verified against the plan.


## See Also

- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[optimizer-engine-patterns-reference-design]]
- [[os-eval-backport-phase-guide]]
- [[project-setup-reference-guide]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[os-eval-backport-phase-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/exploration-workflow/references/phase3-execution-discipline.md`
- **Indexed:** 2026-04-17T06:42:09.602037+00:00
