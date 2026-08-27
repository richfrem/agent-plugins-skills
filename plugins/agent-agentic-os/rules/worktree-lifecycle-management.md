---
description: Mandatory protocol for creating, reporting on, and closing out git worktrees -- prevents the "where is it" confusion loop caused by collapsing five distinct states into one vague "done".
globs: ["**/*"]
---

# Worktree Lifecycle Management

## The Problem This Rule Solves

**2026-08-18 incident:** a session created two worktrees to execute SharePoint plugin
work, and repeatedly reported progress as "done"/"merged"/"pushed" without distinguishing
which of five genuinely different states a change was actually in. This caused the user to
ask "where are the CRUD scripts" and "is the worktree gone" many times over, each time
receiving an answer that was locally true but did not match what the user could actually
see on their own disk. Concretely:

1. A subagent-driven-development round finished, the branch was pushed, and the session
   reported "final review complete" without stating that nothing was merged yet.
2. A second worktree's work (file moves + new scripts) sat fully uncommitted for many
   turns while the session narrated architecture debates instead of stating the plain
   fact: "nothing is saved anywhere except the worktree's working directory."
3. After the user merged a PR on GitHub, the session ran `git fetch origin main:main`
   (updating the **local branch ref**) and reported the plugin as present -- without
   checking that the user's actual working directory was checked out on a **different
   branch**, so the files were invisible on disk. The user had to ask "i don't see it are
   you sure?" before this was caught.
4. Within one of the worktrees, symlinks were created with raw `ln -s` and a hand-edited
   `symlinks.json` instead of this repo's mandated `.agents/skills/symlink-manager/
   scripts/symlink_manager.py` (per `.agent/rules/symlink-cross-platform.md`), discovered
   only when the user separately flagged it.

None of these were lies -- each statement was true in isolation. The failure was treating
"local worktree state", "committed", "pushed to origin", "merged on GitHub", "local branch
ref updated", and "checked out on disk" as one undifferentiated bucket called "done".

## The Law

> **A worktree-related change is not "done" until you state which of the six states below
> it is actually in, using the exact vocabulary below.** Never use the bare words "done",
> "merged", "pushed", or "saved" without one of these qualifiers attached. When the user
> asks "where is X" or "is it gone", answer with the state name and the exact path/branch,
> not a general reassurance.

## The Six States (use this exact vocabulary)

1. **Written in the worktree** -- exists only as an uncommitted file inside the worktree's
   working directory. Invisible to git log, invisible to any other checkout, lost if the
   worktree is deleted.
2. **Committed in the worktree** -- has a commit hash, but only reachable from the
   worktree's local branch. Invisible outside this machine.
3. **Pushed to origin** -- the branch exists on GitHub. A PR *can* be opened. **Not yet
   merged.** State the exact `git push` result and the PR URL, and say explicitly "not
   merged yet" in the same sentence.
4. **Merged into `origin/main`** -- verify this yourself via `git fetch origin main &&
   git log --oneline origin/main -3` and quote the actual merge commit hash back. Never
   infer this from "I pushed it" or from the user saying "ok" -- confirm the merge commit
   exists on `origin/main` before calling anything merged.
5. **Local branch ref updated** -- `git fetch origin main:main` (or equivalent) updates
   what your local `main` branch *points to*. **This does not change any file on disk if
   the current checkout has a different branch checked out.** Always state explicitly
   which branch is currently checked out (`git branch --show-current`) in the same breath
   as reporting this.
6. **Checked out on disk** -- the actual working directory files match the target branch.
   Verify with `ls`/`git status` on the real path, not by inference. Only at this state can
   you tell the user "you can see it now" -- and even then, name the exact path.

## Non-Negotiables

1. **State the state.** Every progress report on worktree-related work names which of the
   six states applies, e.g. "pushed to origin, PR link below, not yet merged" or "merged
   into origin/main (commit `988b77a`), but your checkout is still on
   `feature/x` -- run `git checkout main` to see it."
2. **Never say "merged" without verifying `origin/main` yourself.** A user saying "I
   merged" is a trigger to `git fetch` and quote the resulting commit hash, not license to
   parrot "merged" back without checking.
3. **Never claim a file is visible "now" without checking the actual checked-out branch.**
   Updating a local branch ref is not the same as changing the working directory. If the
   current checkout is on a different branch than the one just updated, say so before the
   user has to ask why they can't see anything.
4. **State exact absolute paths for every file/plugin/worktree you reference.** "It's in
   the new plugin" is not an answer; `C:\...\plugins\sharepoint-provisioning-execution\
   scripts\spo-update-list.ps1` is.
5. **Before deleting any worktree, verify state 4 (merged into origin/main) first**, via
   `git fetch` + `git log origin/main`, not by assuming a prior push means the PR was
   merged. Only after that verification, delete via the native worktree-removal tool (or
   `git worktree remove` + `git worktree prune` if the native tool reports no active
   session), and confirm via `git worktree list` that it's gone.
6. **All symlink creation/removal inside a worktree goes through
   `.agents/skills/symlink-manager/scripts/symlink_manager.py`**, per
   `.agent/rules/symlink-cross-platform.md` -- this applies inside worktrees exactly as
   much as the main checkout. If the tool isn't present in the worktree, restore it from
   the marketplace-cached copy or the sibling monorepo before touching any symlink, never
   fall back to raw `ln -s`.
7. **When multiple worktrees exist, or worktree work spans several turns, restate the
   current state of every open worktree at the start of any status report** -- don't make
   the user re-derive it from scattered messages.

## Where This Applies

- Every `superpowers:using-git-worktrees` / `EnterWorktree` session in this repo.
- Every report to the user about progress on worktree-based work, from creation through
  final deletion.
- Applies in addition to, not instead of,
  `.agent/rules/worktree-subagent-leak-detection.md` (renamed 2026-08-18, formerly
  `worktree-subagent-isolation.md`) — that file covers a narrower, different failure mode
  (a dispatched subagent's writes leaking into the wrong checkout); this file covers the
  full lifecycle around the worktree itself. Both apply simultaneously in any
  subagent-driven-development session run inside a worktree.
