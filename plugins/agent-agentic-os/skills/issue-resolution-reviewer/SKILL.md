---
name: issue-resolution-reviewer
plugin: agent-agentic-os
description: >
  Audits closed GitHub issues to verify whether root causes were genuinely resolved,
  if follow-on execution friction appeared, or if systemic improvements were retained.
  Trigger with "audit closed issues", "review issue resolution quality", "was this issue
  actually fixed", or as a post-closure quality gate on issues labeled resolution:fixed
  or resolution:superseded. Migrated from the former issue-resolution-reviewer agent
  (2026-09-05): deterministic audit against fixed criteria, no interview, no code writes
  — fits the skill archetype, not the agent archetype.
allowed-tools: Bash, Read
---

# Issue Resolution Reviewer (`issue-resolution-reviewer`)

Audits closed repository issues labeled `resolution:fixed` or `resolution:superseded` to verify whether root causes were genuinely fixed or recurred.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
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

## Verification

Confirm audit report table is rendered with concrete empirical evidence:

```bash
gh issue list --state closed --limit 1
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for issue resolution audits.
- [fallback-tree.md](references/fallback-tree.md) — Failure escalation when GitHub CLI access is unavailable.
- [map-debt.md](references/map-debt.md) — Active and resolved friction ledger.
