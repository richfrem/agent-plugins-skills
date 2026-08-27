---
description: A subagent's pwd/git-branch confirmation does not guarantee its Edit/Write calls stay inside the assigned worktree — a mandatory post-task check does.
globs: ["**/*"]
---

# Worktree/Subagent Isolation

## The Problem This Rule Solves

Dispatching an implementer or fix subagent into a `superpowers:subagent-driven-development`
worktree, with an explicit instruction to `cd` into the worktree path and confirm via
`pwd` / `git branch --show-current` before making any change, is the project's standard
isolation pattern. It has still failed **twice**:

1. **Phase 2b, Task 3** — an implementer committed a change onto the user's active
   main-checkout branch instead of its assigned worktree (documented informally in
   `start_here.md` at the time; caught by independently verifying `git log`/`readlink`
   after the subagent's report, not by the subagent noticing its own mistake).
2. **Phase 3 C2, Task 7 fix rounds (2026-07-09)** — a fix subagent left a stray,
   uncommitted, *incomplete* copy of its changes in the main checkout's
   `plugins/portfolio-advisor/scripts/daily_brief.py`, despite reporting a passing
   `pwd`/`git branch --show-current` confirmation at task start. Not caught until the
   final pre-merge `git status` check on the main checkout — logged as
   `.agent/map-debt.md`'s "subagent-driven-development implementer wrote to main
   checkout instead of worktree (2nd occurrence)" entry.

Both times the subagent's own confirmation step passed. Both times a stray write still
landed in the main checkout anyway.

## The Law

> **A `cd`-and-confirm step at task start is not evidence that every subsequent
> Edit/Write call in that session targets the confirmed directory.** `cd` only changes
> the *Bash tool's* persisted shell state — the Edit/Write/Read tools resolve on the
> exact absolute path parameter they're given, independent of any prior `cd`. Treat the
> confirmation step as a cheap first-line check, not a guarantee, and verify the
> **controller's own main checkout** after every task, not just the worktree.

## Non-Negotiables

1. **Every subagent-driven-development dispatch still gets the standard confirmation
   step.** Instruct the subagent to `cd` into the exact worktree path as its first
   action and confirm via `pwd` and `git branch --show-current` before editing anything.
   This remains necessary — it just isn't sufficient on its own.

2. **After every implementer or fix subagent reports back, the controller runs
   `git status --short` in the main checkout (not the worktree) before generating the
   review package.** This is the mandatory second check. It catches a leak within one
   task cycle — while it's still uncommitted and trivially discardable — instead of
   only surfacing at final-merge time, when it's had 5+ more tasks to compound or get
   tangled into review history.

   ```bash
   # From the main repo root, not the worktree:
   git status --short
   ```

   Any unexpected `M` entry that wasn't present before the task's dispatch is a leak.
   Diff it before touching anything (`git diff <path>`) — don't assume.

3. **A leak found this way is virtually always safe to discard, but verify first.**
   The signature of this exact failure mode is: the main checkout's stray diff is an
   *incomplete* or *superseded* subset of work that's already properly committed in the
   worktree branch (e.g. missing a later fix-round commit's changes). If the diff
   content matches that pattern, discard it via `git checkout -- <path>` in the main
   checkout before merging. If the diff contains anything that doesn't look like a
   partial duplicate of the worktree's own committed work — stop and investigate before
   discarding; it may be unrelated, real, uncommitted user work that predates the
   session (check the pre-session `git status` baseline first).

4. **Log a repeat occurrence, don't just re-fix it silently.** Per
   `.agent/rules/self-evolution-policy.md`'s Map Debt register: a `Repeat: YES` entry
   requires action on next encounter, not further deferral. A third occurrence of this
   exact failure mode should prompt investigating the harness-level root cause directly
   (e.g. checking whether a specific tool or dispatch pattern is the common thread)
   rather than only reapplying this same procedural mitigation a third time.

## Where This Applies

- Any `superpowers:subagent-driven-development` or `superpowers:executing-plans`
  session that dispatches implementer/fix subagents into an isolated worktree.
- Applies to every task in a plan, not just the first or last — the leak in the C2
  incident happened during a mid-plan fix round (Task 7's second fix dispatch), not at
  the boundaries.
- Applies directly to `graph-planning-superpowers-policy.md` §3.1 (Phase 2: Worktree State
  Isolation) — any implementer dispatched into a Phase 2 worktree is subject to this rule's
  mandatory second check (main-checkout `git status --short` after every task), not just the
  subagent's own `pwd`/`git branch --show-current` confirmation.
