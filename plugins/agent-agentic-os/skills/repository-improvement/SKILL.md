---
name: repository-improvement
plugin: agent-agentic-os
description: >
  Consumes friction_cluster_agent hotspot reports and synthesizes systemic refactoring
  proposals for human review, for Tier 3 architecture friction. Trigger with "synthesize
  a refactoring proposal from the friction hotspots", "what's the systemic fix for this
  friction cluster", or when os-architect/self-evolution escalates a Tier 3 (Regression /
  Architecture) friction event per github-issue-logging-policy.md. Migrated from the
  former repository-improvement-agent (2026-09-05): deterministic report-synthesis task,
  no interview, no self-directed git/PR execution — fits the skill archetype, not the
  agent archetype. Never creates branches, commits, or PRs itself — see "Human Gate"
  below.
allowed-tools: Read, Write
---

# Repository Improvement (`repository-improvement`)

Consumes friction hotspot reports and synthesizes systemic refactoring proposals for human review regarding recurring Tier 3 architecture friction.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
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
3. **Draft Refactoring Proposal**: Save proposal to `temp/repo-improvement-proposal-<slug>.md` detailing patterns and impact.
4. **Human Review Gate**: Present proposal to the user and request explicit authorization before proceeding.
5. **Delegated Execution**: Upon approval, hand off execution to PR lifecycle agents in isolated worktrees.

## Verification

Confirm refactoring proposal is written with clear systemic rationale:

```bash
test -f "temp/repo-improvement-proposal-*.md" 2>/dev/null && echo "Proposal verified"
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for repository improvement proposals.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when hotspot reports are ambiguous or missing.
