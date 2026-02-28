# Project Sanctuary: Merge Augmentation

> This file contains project-specific best practices and safety guidance for the merge workflow.
> It is NOT overwritten by `sync_configuration.py` — only `SKILL.md` is auto-synced.

## Pre-Merge Safety Protocol (Mandatory)

### 1. Remote Branch Backup

Before ANY merge, push all WP branches to origin:
```bash
for wt in .worktrees/<FEATURE>-WP*/; do
  branch=$(basename "$wt")
  git -C "$wt" push origin "$branch"
done
```

Verify each push:
```bash
for wt in .worktrees/<FEATURE>-WP*/; do
  branch=$(basename "$wt")
  local_sha=$(git -C "$wt" rev-parse HEAD)
  remote_sha=$(git ls-remote origin "$branch" | cut -f1)
  [ "$local_sha" = "$remote_sha" ] && echo "OK $branch" || echo "FAIL $branch"
done
```

**STOP if any branch shows FAIL.**

### 2. Branch Protection Awareness

If `origin/main` is protected (requires PRs):
- `spec-kitty merge` will succeed *locally* but `--push` will fail with `GH006`
- **Workaround**: Push merged main as a feature branch and create a PR:
  ```bash
  git push origin main:feat/<feature-slug>
  ```
- Then merge via GitHub PR — do NOT disable branch protection

### 3. kitty-specs Conflict Resolution

When WPs are implemented serially, every merge will conflict on `kitty-specs/*/tasks/*.md` status files. These are safe to auto-resolve:
```bash
git checkout --theirs kitty-specs/
git add kitty-specs/
git commit -m "merge: resolve kitty-specs status conflicts (accept theirs)"
```

### 4. Always Use `--push`

Never run `spec-kitty merge` without `--push`. Without it, worktree cleanup can destroy the only copies of feature branches.

### 5. Post-Merge Cleanup

After merge is verified on origin:
```bash
# Delete remote WP backup branches
for wp in WP01 WP02 ...; do
  git push origin --delete <FEATURE>-$wp
done

# Prune stale local refs
git fetch --prune
```

## Known Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| `GH006: Protected branch update failed` | Branch protection enabled | Push to feature branch, create PR |
| Worktree deleted but content not on origin | Ran merge without `--push` | Restore from git reflog |
| kitty-specs conflicts on every WP | Serial implementation (expected) | Accept theirs for status files |
| Merge ran from inside worktree | Wrong working directory | Always `cd` to project root first |
