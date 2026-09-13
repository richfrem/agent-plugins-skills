# Worktree Reconciliation & Multi-Worktree Practices

Consumed by: `worktree-manager` skill.

Origin: [github issue #609](https://github.com/richfrem/agent-plugins-skills/issues/609) — an agent
was asked twice, explicitly, whether pre-worktree dirty changes on the source checkout had been
carried into a newly created worktree, and falsely confirmed they had without checking. Root cause:
`git worktree add` only checks out a **committed ref** — it never carries uncommitted/dirty files
into the new worktree, by design, regardless of what tooling or agent creates it.

## 1. Pre-worktree dirty state (single worktree)

**Mechanism now enforced in code, not by agent self-report:** the `APPROVED -> IN_WORKTREE`
transition runs the `main_worktree_reconciliation` deterministic check
(`plugins/agent-agentic-os/scripts/control_plane/policy.py`). It force-copies dirty
(modified/untracked) source-checkout files into the registered worktree at transition time and
hard-blocks the transition on any genuine content conflict — never silently overwrites either
side. See `plugins/agent-agentic-os/scripts/agent_control.py::_reconcile_main_into_worktree`.

**Preferred practice, not yet enforced:** don't let dirty state accumulate on `main` in the first
place. Commit interim work made during INTAKE/INTERVIEW/DRAFT_PLAN to a small branch and PR it
before the task reaches `APPROVED`, so `main` is already clean by the time a worktree is created.
This is the standard git-community pattern — worktrees are documented to only ever carry committed
content, and the reconciliation check above is a safety net for what slips through, not a
substitute for keeping `main` clean.

## 2. Always branch from a fresh base, never stale local `main`

Fetch `origin/main` immediately before creating a worktree; base the new branch on
`origin/main`, not on local `main` (which may be behind, or hold state from a squash-merged PR
whose commit isn't an ancestor of the new branch's base — see §3).

## 3. Multiple worktrees: preventing one from undoing another's work

Each worktree only ever sees what was **committed and merged into the ref it was created from**.
It does not automatically see another worktree's uncommitted work, or another worktree's committed
but not-yet-merged branch. Two failure modes follow directly from this:

- **Stale base**: worktree B is created from the same base commit as worktree A, before A merges.
  When B later tries to merge/rebase, it has no knowledge that A's content already landed in
  `origin/main` — especially dangerous with squash merges (this repo's convention), since a
  squashed PR's resulting commit is not an ancestor of the original branch, so ancestry checks
  can't shortcut this. Fix: rebase B onto current `origin/main` immediately before B's own merge,
  every time — never assume B's original base commit is still current.
- **Silent conflict resolution**: if a rebase/merge conflict surfaces because A and B touched the
  same file, resolving it by blindly taking "ours" or "theirs" without diffing can revert already
  merged work from either side. Always diff what a conflict resolution would discard before
  choosing a side.

**Standard practice for concurrent worktrees (multi-agent or otherwise), per 2026 industry
guidance** (see Sources below):

1. Every worktree branches from the same fresh commit on `origin/main`.
2. Scope tasks with explicit file/module ownership before launching parallel work — the single
   biggest lever for avoiding conflicts is non-overlapping work, not merge tooling.
3. Isolate non-filesystem shared state too — ports, `.env` files, local databases — a worktree
   only isolates the filesystem, not running services.
4. For genuinely overlapping/uncertain work, merge into a **staging/integration branch** first,
   run the full test suite there, then promote to `origin/main` — rather than merging every
   worktree branch straight to `origin/main` independently. (Not yet implemented in this
   repository's pipeline as an automated gate — currently a manual practice to follow.)
5. Never auto-merge; require diff review and automated gates before any integration.
6. If running many worktrees at once regularly, consider dedicated orchestration tooling rather
   than manual coordination.

## Sources

- [Git worktrees for AI coding: how to run multiple agents without conflicts](https://www.mindstudio.ai/blog/git-worktrees-parallel-ai-coding-agents)
- [How to run a multi-agent coding workspace (2026)](https://www.augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace)
- [How to use git worktrees for parallel AI agent execution](https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution)
- [Running coding agents in parallel with git worktrees](https://dev.to/andrea_schiona/running-coding-agents-in-parallel-with-git-worktrees-4cnk)
- [Parallel AI agents with git worktree](https://www.gitworktree.org/ai-tools/parallel-agents)
- [git-worktree documentation](https://git-scm.com/docs/git-worktree)
