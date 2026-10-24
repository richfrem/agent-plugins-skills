# Phase 3 Execution Discipline Reference

> Read this file when Phase 3 (Prototype) is the active phase. It was extracted from the workflow skill to keep that skill concise. Rewritten in the consolidation: the isolation and finishing steps now use the repository's own worktree skill, not an external plugin.

## Before any plan: inventory the execution contract

Before turning the Discovery Plan into a task ledger, inventory the artifacts that define the execution contract for this session: the brief, the dashboard state, the Discovery Plan and the execution-critical captures. Treat them as mandatory inputs to any decomposition. If the expert changed scope, priorities or expected outputs since the last plan draft, rewrite the task ledger from those artifacts before dispatching any worker.

## Isolation capability check

Silently check whether the `os-control-worktree` skill is available in the current host (its install location varies by harness, so do not assume a path).

- **Available**: proceed with the steps below.
- **Not available, greenfield session**: warn once ("I recommend installing the worktree skill for isolated workspaces. For now I'll proceed, but the build won't be isolated from your main work") and build in the dedicated prototype directory `exploration/prototype/` in `direct` mode.
- **Not available, brownfield session**: halt. Say: "Building directly into an existing codebase without an isolated workspace is risky. Please install the worktree skill first." Name the skill; give no install command that points at another project.
- **Analysis, docs and spike sessions** (no code branch): warn once and continue; isolation is not required.

## Step 1: Isolation

Before Phase 3 begins, use the `os-control-worktree` skill to create an isolated workspace for the build, with the context "Starting Phase 3 of exploration session '[session name]'". All build work happens there, not on the main branch. If there is no git repository, or the session is analysis/docs, skip this step. When speaking to the expert say "isolated workspace" or "feature branch", never "git worktree".

## Step 2: Build

This skill owns the build: component decomposition, per-component dispatch (using the strategy chosen at session setup), a plan-alignment review then a quality review per component, validation checks per component, assembly and completion. See [prototyping-build-guide.md](prototyping-build-guide.md). The conductor does not duplicate these steps.

## Step 3: Finishing

When the build signals Phase 3 complete:
1. Verify that all tests and evals pass.
2. Present the options to the expert: merge locally, create a pull request, keep the branch, or discard.
3. Clean up the isolated workspace when appropriate, following the worktree lifecycle rule: state which of its six states the work is in and verify `origin/main` before saying "merged".

Analysis and docs sessions skip this step.

## Expert-friendly language

| Engineering term | We say instead |
|---|---|
| spec reviewer | plan alignment check |
| code quality reviewer | quality check |
| TDD | validation check |
| git worktree | isolated workspace |
| spec | Discovery Plan |

## Why validate prototypes?

The prototype is the *evidence* that exploration captured the right thing. If it does not match the Discovery Plan, the expert reviews the wrong behavior, the handoff describes the wrong system, and the engineering team builds from a flawed spec. Validation is not about code quality; it is about **exploration accuracy**. Even a prototype that will be thrown away after handoff must be verified against the plan.
