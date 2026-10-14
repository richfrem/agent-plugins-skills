---
name: github-issue-resolution-reviewer
plugin: dev-utils
description: >
  Audits closed GitHub issues to verify whether root causes were genuinely resolved,
  whether follow-on friction appeared, or whether systemic improvements were retained.
  Trigger with "audit closed issues", "review issue resolution quality", "was this issue
  actually fixed", or as a post-closure quality gate on issues labeled resolution:fixed
  or resolution:superseded.
  USE ONLY for read-only audits of already-closed issues.
  DO NOT USE for logging or commenting on issues (use `github-issue-agent`), ranking them
  (use `github-issue-prioritizer`), or resolving them (use `github-issue-pr-lifecycle-agent`).
allowed-tools: Bash, Read
---

# GitHub Issue Resolution Reviewer (`github-issue-resolution-reviewer`)

Audits closed repository issues labeled `resolution:fixed` or `resolution:superseded` to verify whether root causes were genuinely fixed or recurred.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Related GitHub issue skills](#related-github-issue-skills)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Read-Only Audit**: Never reopen an issue, mutate labels, or file new issues autonomously.
2. **Deduplication Search**: Before proposing new issues for recurring friction, search existing issues.
3. **Honest Inconclusive Verdicts**: Classify as `INCONCLUSIVE` when empirical evidence is insufficient.

## Quick start

List recent closed and resolved issues:

```bash
gh issue list --state closed --label "resolution:fixed" --limit 10
```

## Workflow

1. **Collect Resolved Issues**: Query issues with `resolution:fixed` or `resolution:superseded`.
2. **Inspect Fix & Map Debt**: Review fix PR commits, CI test logs, and `references/map-debt.md`.
3. **Classify**: Assign `CONFIRMED_RESOLVED`, `RECURRING_FRICTION`, or `INCONCLUSIVE`.
4. **Produce Audit Table**: Present findings (`Issue # | Title | Classification | Evidence`).
5. **Human Gate**: If recurring friction is detected, ask user before reopening or logging consolidation issues.

## Related GitHub issue skills

This skill closes the loop on the `dev-utils` GitHub issue family. It only reads; the others act.

| Skill | Role | Hand off when |
|---|---|---|
| `github-issue-agent` | Logs friction and bugs as deduplicated issues | Recurring friction needs a new or consolidated issue (after the human gate) |
| `github-issue-backlog-agent` | Promotes local `tasks/*.md` items into issues | A finding is still only a local task note |
| `github-issue-prioritizer` | Ranks issues P0-P3 and syncs priority fields | A recurring issue needs re-ranking |
| `github-issue-worktree-agent` | Creates and cleans `.worktrees/issue-NNN` | A reopened issue needs an isolated workspace |
| `github-issue-pr-lifecycle-agent` | Runs issue to worktree to PR to closure | A reopened issue needs to be fixed again |

## Verification

Confirm audit report table is rendered with concrete empirical evidence:

```bash
gh issue list --state closed --limit 1
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for issue resolution audits.
- [fallback-tree.md](references/fallback-tree.md) — Failure escalation when GitHub CLI access is unavailable.
- [map-debt.md](references/map-debt.md) — Active and resolved friction ledger.
