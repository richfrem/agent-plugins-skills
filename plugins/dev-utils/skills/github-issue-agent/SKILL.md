---
name: github-issue-agent
plugin: dev-utils
description: >
  Agent skill for safe, dry-run-first, deduplicated, root-cause-consolidated, evidence-validated, and secret-redacted logging of repository execution friction into GitHub Issues.
  USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements.
  DO NOT USE for managing git worktrees (use `github-issue-worktree-agent`) or full PR lifecycles (use `github-issue-pr-lifecycle-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Agent (`github-issue-agent`)

> **Routing Directive:** USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements. DO NOT USE for isolated worktree setup (use `github-issue-worktree-agent` instead) or PR lifecycle flows (use `github-issue-pr-lifecycle-agent` instead).

The `github-issue-agent` skill provides a safe, standardized interface for querying, searching, creating, commenting on, and validating GitHub Issues stemming from agent execution friction, map debt, bugs, and system improvements.

---

## Safety & Validation Gates

1. **Dry-Run by Default:** All issue operations execute in payload generation mode unless `--execute` is specified.
2. **Secret Redaction Gate:** Blocks submission if credentials or tokens are detected in title or body.
3. **Taxonomy Validation Gate:** Enforces required taxonomy dimensions (`type:*`, `tier:*`, `source:*`, `risk:*`, and `area:*`/`plugin:*`).
4. **Body Structure Gate:** Requires structured Markdown sections (`## Summary`, `## Observed Behavior`, `## Expected Behavior`, `## Evidence`, `## Impact`).

---

## Quick Start & Operations

- **Create Friction Issue:**
  ```bash
  python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py --title "Bug summary" --body "..." --labels "type:friction,tier:1-friction,source:agent,risk:low,area:dev-utils"
  ```
- **Search Related Issues (Deduplication):**
  ```bash
  python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_search.py --title "Bug summary" --area-label "area:dev-utils"
  ```
- **Comment on Existing Issue:**
  ```bash
  python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_comment.py --issue 42 --comment "Additional evidence..."
  ```

---

## Progressive Disclosure & References

- **Operation Catalog**: [references/operation-catalog.md](references/operation-catalog.md) — complete CLI parameters and scripts.
- **Taxonomy Guide**: [references/taxonomy-guide.md](references/taxonomy-guide.md) — label schemas and taxonomy reference.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — verification contracts and test requirements.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — failure recovery and offline workarounds.
