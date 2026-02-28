# Project Sanctuary: Review Augmentation

> This file contains project-specific review standards and best practices.
> It is NOT overwritten by `sync_configuration.py` — only `SKILL.md` is auto-synced.

## Review Standards

### What to Review

For each WP, verify:
1. **Diff quality**: `git diff main...<WP-branch>` — check for unintended changes
2. **Deliverable completeness**: All files listed in the WP prompt are present
3. **Code quality**: Follows project coding conventions (dual-layer docs, type hints, file headers)
4. **Separation of concerns**: WP doesn't touch files outside its scope
5. **No planning artifacts**: kitty-specs files should NOT be in the WP diff

### Batch Review Protocol

When reviewing multiple WPs in sequence (common for serial implementation):
1. Review WP01 first, approve if clean
2. For each subsequent WP, compare against what the PREVIOUS WP already changed
3. Use `git diff <FEATURE>-WP01..<FEATURE>-WP02 --stat` to see ONLY what WP02 added
4. Approve or reject each independently

### Dependency Verification

Before approving a WP with dependencies:
```bash
# Check if dependency WPs are already merged
spec-kitty agent tasks move-task WP## --to done --note "Review passed"
```

The CLI will block if dependencies aren't met.

## Review Commands

### Approve
```bash
spec-kitty agent tasks move-task WP## --to done --note "Review passed: <summary>"
```

### Reject
```bash
spec-kitty agent tasks move-task WP## --to planned --review-feedback-file <temp-file-path>
```

### Force Approve (when kitty-specs artifacts are expected)
```bash
spec-kitty agent tasks move-task WP## --to done --force --note "Review passed. kitty-specs artifact leak expected from serial implementation."
```

## Known Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| `move-task` blocked by kitty-specs artifacts | WPs implemented serially, status files leaked | Use `--force` if deliverable content is valid |
| `move-task` blocked by uncommitted changes | Reviewer or implementer left staged deletions | `git checkout -- <file>` in worktree |
| Review of wrong diff | Compared against wrong base | Use `git diff main...<WP-branch>` not `git diff` |
| Approved WP missing from dashboard | Lane transition didn't commit to main | Run `/spec-kitty.status` to verify |
