---
name: github-issue-pr-lifecycle-agent
plugin: dev-utils
description: >
  Skill for orchestrating the end-to-end GitHub issue lifecycle flow: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.
  USE ONLY when running or dry-running full lifecycle orchestration for resolving an issue with a PR.
  DO NOT USE for isolated worktree management only (use `github-issue-worktree-agent`) or logging issues (use `github-issue-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue PR Lifecycle Agent (`github-issue-pr-lifecycle-agent`)

> **Routing Directive:** USE ONLY when orchestrating or dry-running the full lifecycle flow (Issue -> Worktree -> PR -> Close resolution). DO NOT USE for individual isolated worktree setup (use `github-issue-worktree-agent` instead) or friction logging (use `github-issue-agent` instead).

The `github-issue-pr-lifecycle-agent` skill connects git worktree execution with GitHub CLI operations (`gh pr create`, `gh issue close`) into a single, verifiable workflow pipeline.

---

## Quick Start & CLI

- **Helper Script:** `plugins/dev-utils/skills/github-issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py`

```bash
# Dry-run payload generation for Issue #42:
python3 plugins/dev-utils/skills/github-issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password"

# Live execution of end-to-end lifecycle:
python3 plugins/dev-utils/skills/github-issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password" --execute
```

---

## Progressive Disclosure & References

- **Detailed Guide & API**: [references/lifecycle-guide.md](references/lifecycle-guide.md) — execution sequence, safety contracts, and Python API interface.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — verification contracts and test expectations.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — failure recovery procedures and manual workarounds.
