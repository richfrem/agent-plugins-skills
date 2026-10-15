---
name: github-issue-refactor-proposer
plugin: dev-utils
description: >
  Turns clustered GitHub-issue friction into one systemic refactoring proposal for human
  review. Consumes friction-cluster hotspot reports from github-issue-agent, groups the
  symptoms under one root cause, and drafts the proposal; it never creates branches,
  commits or PRs. Trigger with "synthesize a refactoring proposal from the friction
  hotspots", "what's the systemic fix for this friction cluster", or when a Tier 3
  (regression / architecture) friction event is escalated per github-issue-logging-policy.md.
  USE ONLY for Tier 3 systemic proposals from issue friction.
  DO NOT USE to log or comment on issues (use `github-issue-agent`), rank them
  (use `github-issue-prioritizer`), audit closed issues (use `github-issue-resolution-reviewer`),
  or implement a fix (use `github-issue-pr-lifecycle-agent`).
allowed-tools: Read, Write
---

# GitHub Issue Refactor Proposer (`github-issue-refactor-proposer`)

Consumes friction hotspot reports and synthesizes systemic refactoring proposals for human review regarding recurring Tier 3 architecture friction.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Related GitHub issue skills](#related-github-issue-skills)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Synthesis Only**: Never autonomously create git branches, write commits, or open pull requests.
2. **One Proposal Per Root Cause**: Group findings by systemic pattern rather than creating omnibus proposals.
3. **Target Tier 3 Specifically**: Focus on systemic architecture debt, recurring multi-component failures, and core design flaws.

## Quick start

Inspect active friction hotspots and unresolved Tier 3 issues:

```bash
cat references/map-debt.md
```

## Workflow

1. **Consume Hotspot Reports**: Inspect friction cluster analysis and identified Tier 3 architectural debt.
2. **Consolidate Root Causes**: Group related failure symptoms under a single root architectural deficiency.
3. **Draft Refactoring Proposal**: Save proposal to `temp/github-issue-refactor-proposal-<slug>.md` detailing patterns and impact.
4. **Human Review Gate**: Present proposal to the user and request explicit authorization before proceeding.
5. **Delegated Execution**: Upon approval, hand off execution to PR lifecycle agents in isolated worktrees.

## Related GitHub issue skills

| Skill | Role | Relation |
|---|---|---|
| `github-issue-agent` | Logs friction and clusters it into hotspots | Produces this skill's input |
| `github-issue-prioritizer` | Ranks issues P0-P3 | Ranks the issues a proposal covers |
| `github-issue-resolution-reviewer` | Audits closed issues for recurrence | Flags recurring friction that becomes a proposal |
| `github-issue-worktree-agent` | Creates `.worktrees/issue-NNN` | Workspace for an approved proposal |
| `github-issue-pr-lifecycle-agent` | Issue to PR to closure | Executes an approved proposal |
| `github-issue-backlog-agent` | Promotes local tasks to issues | Turns a proposal's follow-ups into issues |

## Verification

Confirm refactoring proposal is written with clear systemic rationale:

```bash
test -f "temp/github-issue-refactor-proposal-*.md" 2>/dev/null && echo "Proposal verified"
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for refactoring proposals.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when hotspot reports are ambiguous or missing.
- [map-debt.md](references/map-debt.md) — Active and resolved friction ledger.
