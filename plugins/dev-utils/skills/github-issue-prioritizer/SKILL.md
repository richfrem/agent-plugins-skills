---
name: github-issue-prioritizer
plugin: dev-utils
description: >
  Automatically ranks GitHub issues (P0-P3) based on friction tier, frequency, and blockages, synchronizing priority labels and GitHub Projects v2 custom fields.
  USE ONLY when calculating issue priority ranks or generating Projects v2 payload mutations.
  DO NOT USE for logging issues (use `github-issue-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Prioritizer (`github-issue-prioritizer`)

> **Routing Directive:** USE ONLY when calculating issue priority ranks (P0-P3), updating priority labels (`priority:P0`..`P3`), or generating payload updates for GitHub Projects v2 custom fields. DO NOT USE for friction logging (use `github-issue-agent` instead) or task promotion (use `github-issue-backlog-agent` instead).

The `github-issue-prioritizer` skill computes priority ranks from friction tiers, work blockages, and occurrence frequencies to maintain an up-to-date queue of repository tasks.

---

## Quick Start & Usage

- **Helper Script:** `plugins/dev-utils/skills/github-issue-prioritizer/scripts/gh_issue_prioritize.py`

```bash
# Prioritize an issue via CLI:
python3 plugins/dev-utils/skills/github-issue-prioritizer/scripts/gh_issue_prioritize.py --issue 42
```

---

## Progressive Disclosure & References

- **Priority Matrix & API**: [references/priority-matrix.md](references/priority-matrix.md) — complete ranking logic and Python API interface.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — verification contracts and test expectations.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — missing label defaults and GraphQL fallback procedures.
