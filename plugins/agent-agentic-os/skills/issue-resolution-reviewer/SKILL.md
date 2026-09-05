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

<example>
<commentary>User wants a post-closure quality audit on resolved issues.</commentary>
user: "Audit the issues we closed last week — did the fixes actually stick?"
assistant: Lists closed issues with resolution:fixed/resolution:superseded, checks recent
test runs and friction logs for each, and reports which are confirmed-resolved vs. which
show recurring friction.
</example>

## Dependencies

This skill requires **Python 3.8+** and standard library only, plus the `gh` CLI
(GitHub CLI) authenticated for this repository.

---

# Issue Resolution Reviewer

Performs post-closure quality audits on resolved repository issues labeled
`resolution:fixed` or `resolution:superseded`. This is a read-only report generator —
it never mutates issue state or repository files on its own.

## Execution Flow

### Phase 1: Collect Closed, Resolved Issues

```bash
gh issue list --state closed --label "resolution:fixed" --json number,title,closedAt,labels
gh issue list --state closed --label "resolution:superseded" --json number,title,closedAt,labels
```

### Phase 2: Verify Root Cause & Regression State

For each issue:
1. Read the issue body and closing comment for the stated root cause and fix commit/PR.
2. Check recent test runs, CI logs, and `references/map-debt.md` for any friction event
   referencing the same file/component logged **after** the issue's `closedAt` date.
3. Classify each issue: `CONFIRMED_RESOLVED`, `RECURRING_FRICTION`, or `INCONCLUSIVE`
   (insufficient evidence either way).

### Phase 3: Report — Human Gate Before Any Mutation

**This skill never reopens an issue, changes a label, or creates a new issue on its own.**
Produce a report table (`Issue # | Title | Classification | Evidence`) and, for any issue
classified `RECURRING_FRICTION`, present the specific evidence and **ask the user
explicitly** whether to:
- Reopen the original issue (`gh issue reopen <n>`), or
- File a new root-cause consolidation issue per `github-issue-logging-policy.md` §3
  (dedup search via `gh_issue_search.py` first, then `gh_issue_create.py`/`gh_issue_comment.py`
  in dry-run mode per that policy's staged rollout).

Do not execute either action until the user has confirmed which one they want. If the user
doesn't respond or declines, leave the report as the deliverable — do not take a default
action.

## Gotchas

- **Do not skip the dedup search.** Before proposing a new consolidation issue, always run
  the existing-issue search first — filing a duplicate for a friction pattern already
  tracked elsewhere is worse than leaving it unfiled.
- **`INCONCLUSIVE` is a valid, honest classification.** Do not force a `CONFIRMED_RESOLVED`
  or `RECURRING_FRICTION` verdict when the evidence genuinely doesn't support either.
