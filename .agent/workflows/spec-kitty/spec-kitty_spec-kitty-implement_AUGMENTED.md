# Project Sanctuary: Implement Augmentation

> This file contains project-specific best practices for the implement workflow.
> It is NOT overwritten by `sync_configuration.py` — only `SKILL.md` is auto-synced.

## Worktree Discipline

### Absolute Paths Only

When editing files in a worktree, ALWAYS use absolute paths:
```
/Users/.../Project_Sanctuary/.worktrees/<FEATURE>-WP01/path/to/file.py
```

NEVER use relative paths — agents frequently drift into the wrong directory.

### Verify Before Coding

Before writing any code, confirm you're in the correct worktree:
```bash
pwd
git branch --show-current
```

The branch name must match the WP you're implementing (e.g., `<FEATURE>-WP01`).

### One WP Per Worktree

- Each WP has its own isolated worktree with its own branch
- NEVER write deliverable files to the main repo root
- Changes in main repository will NOT be seen by reviewers looking at the WP worktree

## Commit Hygiene

### Stage Only Deliverables

```bash
# CORRECT: Stage specific deliverables
git add plugins/my-plugin/scripts/new_script.py tests/test_new_script.py

# WRONG: Never use git add -A or git add .
# This captures kitty-specs changes, .gitignore noise, etc.
```

### Commit Message Format

```bash
git commit -m "feat(WP01): implement markdown parser with wikilink support"
```

Format: `feat(WP##): <imperative description>`

### Before Moving to Review

The `move-task` command validates:
1. Worktree has commits beyond main
2. No uncommitted changes exist
3. No kitty-specs artifacts leaked into the WP branch

If validation fails:
```bash
# For staged but uncommitted changes:
git checkout -- <file>

# For kitty-specs leakage (use --force only if content is valid):
spec-kitty agent tasks move-task WP## --to for_review --force
```

## Dependency Management

When a WP depends on another WP:
1. Check that the dependency WP is already merged to main
2. If not merged, your worktree may be missing files — create worktree off the dependency branch instead
3. Document the dependency in the WP frontmatter

## Known Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Files written to main instead of worktree | Agent used wrong cwd | Always verify with `pwd` before editing |
| `move-task` blocked by uncommitted changes | Forgot to commit or staged extra files | `git status` then commit or checkout |
| `move-task` blocked by kitty-specs artifacts | Serial implementation leaked status changes | Use `--force` if content is valid |
| Missing files from dependency WP | WP was created before dependency was merged | Rebase worktree onto main after dependency merges |
