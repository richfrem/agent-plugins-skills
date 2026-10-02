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

# GitHub Issue Prioritizer (github-issue-prioritizer)

Computes deterministic priority ranks (P0-P3) for GitHub issues from friction tiers, recurrence frequency, and blockages.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for calculating priority ranks (P0-P3) and syncing priority labels/fields. DO NOT USE for logging issues (use `github-issue-agent`).
- **Deterministic Formula**: Calculate priority ranks strictly using the weighted matrix in `priority-matrix.md` without manual override inflation.
- **Dry-Run Default**: Preview calculated scores and proposed label diffs before mutating GitHub metadata.
- **Rate-Limit Hygiene**: Batch queries when prioritizing bulk backlogs to avoid secondary GitHub API limits.

## Quick start

```bash
# Calculate priority score and preview update (dry-run)
python3 plugins/dev-utils/skills/github-issue-prioritizer/scripts/gh_issue_prioritize.py --issue 42

# Execute live priority label and Projects v2 update
python3 plugins/dev-utils/skills/github-issue-prioritizer/scripts/gh_issue_prioritize.py --issue 42 --execute
```

## Workflow

1. **Phase 1: Issue Inspection**: Retrieve issue metadata, friction tier labels (`tier:*`), and linked blocker relationships.
2. **Phase 2: Score Calculation**: Evaluate score via matrix formula considering tier severity, recurrence count, and pipeline blocks.
3. **Phase 3: Payload Preview**: Review proposed priority designation (`priority:P0` through `priority:P3`) in preview mode.
4. **Phase 4: Label & Field Sync**: Apply the resulting priority label and update GitHub Projects v2 fields using `--execute`.

## Verification

```bash
# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/github-issue-prioritizer --mode source
```

## References
- [priority-matrix.md](references/priority-matrix.md) - Ranking logic, weighting formula, and Python API.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification contracts and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Missing label defaults and GraphQL fallback procedures.
