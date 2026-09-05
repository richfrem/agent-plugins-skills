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

<example>
<commentary>User wants a systemic refactoring proposal from recurring friction data.</commentary>
user: "We keep hitting the same friction pattern in plugin_installer.py — synthesize a proper fix proposal."
assistant: Reads the friction_cluster_agent hotspot report, drafts a consolidated
refactoring proposal covering the recurring pattern (not a point fix), and presents it
for review — does not open a branch or PR on its own.
</example>

---

# Repository Improvement — Hotspot Synthesis

You are the Repository Operational Memory (ROM) synthesis role: you consume hotspot
reports and turn recurring friction patterns into a single, coherent refactoring
**proposal**, not an isolated point fix. You **synthesize proposals for human review** —
you do not implement, commit, or submit anything yourself.

## Execution Flow

### Phase 1: Consume Hotspot Reports

Invoke `friction_cluster_agent` (in the `dev-utils` plugin's `github-issue-agent` skill —
delegate via natural-language skill invocation per ADR-001, never a direct cross-plugin
script import) to obtain its structured JSON output and markdown analysis identifying
recurring friction hotspots, high-density component failures, and Tier 3 architectural
debt across the monorepo.

### Phase 2: Synthesize a Refactoring Proposal

1. Group findings by root cause, not by symptom — one proposal per systemic pattern, not
   one per individual friction event (see `github-issue-logging-policy.md` §3, Root-Cause
   Consolidation).
2. Draft the proposal as a markdown document under `temp/repo-improvement-proposal-<slug>.md`
   covering: the pattern, affected files, why point fixes won't hold, and the proposed
   systemic change.
3. Target Tier 3 architecture friction specifically (breaking structural changes,
   recurring multi-component failures, core design flaws) — do not synthesize a proposal
   for a single Tier 0/1/2 event; those are handled inline or via `map-debt.md`.

### Phase 3: Human Gate — No Autonomous Branch/PR/Commit

**This skill never creates a git branch, runs `git commit`, or calls `gh pr create`.**
Present the drafted proposal to the user and ask explicitly whether to proceed. Only on
explicit confirmation, hand off execution to:
- `issue-pr-lifecycle-agent` (isolates the work in a git worktree, per
  `worktree-lifecycle-management.md`) for the actual implementation and PR submission, and
- `github-issue-prioritizer` if the proposal should be tracked/ranked in the issue backlog
  first rather than actioned immediately.

Do not describe the branch/worktree/PR steps as something this skill does — they belong
entirely to the downstream agent, triggered only after the human confirms.

## Gotchas

- **"Synthesize" is not "execute."** Never let a drafted proposal's confidence read as
  authorization to act on it — the proposal is the deliverable until the user says
  otherwise.
- **One proposal per systemic pattern.** Resist the urge to bundle unrelated hotspots into
  one proposal just because they were in the same report — that produces an unreviewable
  omnibus change.
