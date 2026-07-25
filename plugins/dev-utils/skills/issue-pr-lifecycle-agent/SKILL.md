---
name: issue-pr-lifecycle-agent
plugin: dev-utils
description: >
  Skill for orchestrating the end-to-end GitHub issue lifecycle flow: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.
  USE ONLY when running or dry-running full lifecycle orchestration for resolving an issue with a PR.
  DO NOT USE for isolated worktree management only (use `issue-worktree-agent`) or logging issues (use `github-issue-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# Issue PR Lifecycle Agent (`issue-pr-lifecycle-agent`)

> **Routing Directive:** USE ONLY when orchestrating or dry-running the full lifecycle flow (Issue -> Worktree -> PR -> Close resolution). DO NOT USE for individual isolated worktree setup (use `issue-worktree-agent` instead), task scratchpads (use `task-agent` instead), or friction logging (use `github-issue-agent` instead).

The `issue-pr-lifecycle-agent` skill connects git worktree execution with GitHub CLI operations (`gh pr create`, `gh issue close`) into a single, verifiable workflow pipeline.

---

## Safety & Security Contracts

1. **Dry-Run by Default:** Execution defaults to dry-run payload generation (`--execute` flag required for live changes).
2. **Linked Resolution:** Automatically appends `Closes #NNN` to PR bodies to enforce automatic resolution tracking.
3. **Structured Flow:** Sequence: Worktree Creation -> PR Submission -> Issue Closure -> Worktree Cleanup.

---

## Usage catalog

### Orchestrate End-to-End Lifecycle

- **Helper Script:** `plugins/dev-utils/skills/issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py`
- **CLI Usage:**
  ```bash
  # Dry-run payload generation for Issue #42:
  python3 plugins/dev-utils/skills/issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password"

  # Live execution of end-to-end lifecycle:
  python3 plugins/dev-utils/skills/issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password" --execute
  ```

---

## Python API Interface

```python
from plugins.dev_utils.skills.issue_pr_lifecycle_agent.scripts.issue_pr_orchestrate import (
    orchestrate_lifecycle,
    generate_lifecycle_payload,
)

# Generate dry-run payload
payload = generate_lifecycle_payload(issue_number=42, title="Fix bug", body="Fixes #42")

# Orchestrate lifecycle
res = orchestrate_lifecycle(issue_number=42, title="Fix bug", body="Fixes #42", dry_run=False)
```
