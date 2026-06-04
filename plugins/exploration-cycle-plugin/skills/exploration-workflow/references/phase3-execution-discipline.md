# Phase 3 Execution Discipline Reference

> Read this file when Phase 3 (Build) is the active phase. This content is extracted
> from the main workflow to keep the orchestrator concise.

## Superpowers Availability Check

Before the availability check turns into Phase 3 planning, inventory the exploration artifacts that define the execution contract for the current session. Treat the brief, dashboard, discovery plan, and execution-critical captures as mandatory inputs to any Superpowers-backed design, plan, or task decomposition. If the SME changed scope, priorities, or expected outputs since the last plan draft, rewrite the task ledger from those artifacts before any worker is dispatched.

Before invoking any superpowers skill, silently check whether the required
Superpowers skills are resolvable in the current host environment. Install location
may vary by marketplace-managed installs, runtime skill directories such as
`.agents`, or other host-managed locations, so do not assume one fixed path.

Treat this as a capability check for these skills:

- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-prototyping`
- `superpowers:finishing-a-development-branch`

If those required skills are **not available**:

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
