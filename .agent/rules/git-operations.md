---
description: Rules for safe git operations — what requires explicit approval, what is forbidden without it.
globs: ["**/*"]
---

# Git Operations Policy

## Hard Rules (never violate)

### No git stash without explicit instruction
Never run `git stash`, `git stash pop`, or `git stash apply` unless the user explicitly says to.
**Reason:** A stash pop in a prior session applied content from an old unrelated stash onto the
current branch, introducing silent regressions. The risk is not worth it — there is always a
safer path.

### When a push is rejected
If `git push` is rejected because the remote is ahead:
1. Run `git pull --rebase` only (no stash).
2. If there are unstaged changes that block the rebase, **stop and tell the user** — do not stash.
3. Push after the rebase completes cleanly.
Never reach for stash as a shortcut around a rejected push.

### No force push to main/master
Never `git push --force` to main or master under any circumstances.

### No --no-verify
Never skip hooks with `--no-verify` unless the user explicitly requests it.

### Commit only what is asked
Do not commit files the user did not ask to commit. Auto-modified runtime files
(`plugin-sources.json`, `skills-lock.json`, `context/events.jsonl`) are noise — never commit them
unless explicitly asked.

## Approval Required

- Any `git reset` (hard or soft)
- Any `git rebase -i`
- Any branch deletion (`git branch -d` / `-D`)
- Any `git push --force-with-lease` or force variant
- Any `git clean`
- Committing files outside the scope of the current task

## Safe Without Asking

- `git status`, `git diff`, `git log` — read-only, always safe
- `git add <specific files>` + `git commit` when the user asked to commit
- `git push` (non-force) when the user asked to push
- `git pull --rebase` when a push is rejected (no stash)
- `git checkout -b <branch>` when the user asks for a new branch
