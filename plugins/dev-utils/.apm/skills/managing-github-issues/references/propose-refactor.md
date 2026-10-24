# Systemic refactoring proposals from friction clusters (`propose-refactor` mode)

Consumes friction hotspot reports and synthesizes systemic refactoring proposals for human review regarding recurring Tier 3 architecture friction.

## Critical Constraints

1. **Synthesis Only**: Never autonomously create git branches, write commits, or open pull requests.
2. **One Proposal Per Root Cause**: Group findings by systemic pattern rather than creating omnibus proposals.
3. **Target Tier 3 Specifically**: Focus on systemic architecture debt, recurring multi-component failures, and core design flaws.

## Quick start

Inspect active friction hotspots and unresolved Tier 3 issues:

```bash
cat "$(git rev-parse --show-toplevel)/references/map-debt.md"
```

## Workflow

1. **Consume Hotspot Reports**: Inspect friction cluster analysis and identified Tier 3 architectural debt.
2. **Consolidate Root Causes**: Group related failure symptoms under a single root architectural deficiency.
3. **Draft Refactoring Proposal**: Save proposal to `temp/github-issue-refactor-proposal-<slug>.md` detailing patterns and impact.
4. **Human Review Gate**: Present proposal to the user and request explicit authorization before proceeding.
5. **Delegated Execution**: Upon approval, hand off execution to PR lifecycle agents in isolated worktrees.

## Verification

Confirm refactoring proposal is written with clear systemic rationale:

```bash
test -f "temp/github-issue-refactor-proposal-*.md" 2>/dev/null && echo "Proposal verified"
```
