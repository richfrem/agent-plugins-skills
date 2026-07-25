# Design Spec: GitHub Issue Agent & Agentic OS Friction Logging Policy

**Date**: 2026-07-25  
**Authors**: Antigravity + User + Opus  
**Status**: Revised (Approved for Implementation)  
**Target Skill**: `plugins/dev-utils/skills/github-issue-agent/`  
**Target Rule**: `plugins/agent-agentic-os/rules/github-issue-logging-policy.md`  

---

## 1. Executive Summary & Purpose

This design introduces a formal, dual-track protocol for externalizing agent execution friction, script failures, map debt, missing capabilities, stale documentation, and architectural drift into durable GitHub Issues.

### Core Distinctions
- **Local Ephemeral Tasks (`task-agent` / scratch files)**: Preserved strictly for temporary intra-run checklists, wave/subtask decompositions, and execution state scaffolding during an active turn/session.
- **Durable Externalized Backlog (`github-issue-agent`)**: Serves as the repository's permanent memory of execution friction, debt, missing capabilities, and deferred improvements across sessions, agents, and human collaborators.

---

## 2. Non-Goals

- **No total replacement of `task-agent`**: Ephemeral local task lists remain intact for scratch work and in-progress checklists.
- **No issue spam for one-off friction**: Minor, fully-resolved, non-recurring friction without reusable learnings will NOT trigger GitHub Issue creation.
- **No auto-syncing of repository labels**: The agent will NOT automatically create or mutate GitHub repository label definitions unless explicitly requested.
- **No GitHub Projects v2 requirement for MVP**: Label-based taxonomy is the mandatory MVP baseline; GitHub Projects v2 custom fields are optional enhancements.
- **No secrets or credentials in issues**: Never log tokens, API keys, credentials, connection strings, or sensitive internal data into issue titles, bodies, or comments.

---

## 3. Mandatory Location & Taxonomy Requirements (`issue-taxonomy.json`)

Every issue MUST specify a location using either an `area:*` label or a `plugin:*` label. Submissions without a location label will fail validation.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "dimensions": {
    "type": ["type:bug", "type:friction", "type:map-debt", "type:enhancement", "type:documentation", "type:security", "type:architecture", "type:test-gap"],
    "tier": ["tier:0-quickfix", "tier:1-friction", "tier:2-structural", "tier:3-architecture"],
    "area": ["area:dev-utils", "area:agentic-os", "area:skills", "area:rules", "area:subagents", "area:scripts", "area:tests", "area:docs", "area:ci", "area:github", "area:task-agent"],
    "source": ["source:agent", "source:human", "source:script", "source:test", "source:review", "source:migration"],
    "status_fallback": ["status:needs-triage", "status:needs-spec", "status:ready", "status:blocked", "status:accepted-debt", "status:duplicate"],
    "risk": ["risk:low", "risk:medium", "risk:high", "risk:security-sensitive", "risk:destructive-operation"],
    "resolution": ["resolution:fixed", "resolution:superseded", "resolution:wont-fix", "resolution:obsolete"]
  },
  "plugin_prefix": "plugin:",
  "required_dimensions": ["type", "tier", "source", "risk"]
}
```

---

## 4. Root-Cause Consolidation Protocol

Before creating an issue, the agent MUST evaluate whether the event is an isolated occurrence or evidence of a broader root cause:
- **Ask**: *"Is this event itself the issue, or is it evidence of a broader issue?"*
- **Action**: If a broader root-cause issue exists, append evidence as a structured comment to that issue instead of opening a new event-level issue.

---

## 5. Evidence Quality & Body Validation (`body_validator.py`)

Issue body rendering is enforced by programmatic validation. Issues MUST contain:
- `## Summary`
- `## Observed Behavior`
- `## Expected Behavior`
- `## Evidence`
- `## Impact`

If any required header is missing or empty, `validate_issue_body` will block issue generation.

---

## 6. Human Suppression Override

Agents support human suppression directives in project context or metadata:
```yaml
issue_logging: suppressed
reason: "Performing massive refactoring wave; defer issue creation until completed."
```
When `issue_logging: suppressed` is present, issue creation and commenting are bypassed, and friction events are summarized strictly in the task completion report.

---

## 7. Staged Rollout Model

- **Phase 1 (MVP)**: Payload generation mode (`proposed_issues.json` / `--dry-run`). No live GitHub writes.
- **Phase 2**: Commenting on existing issues allowed.
- **Phase 3**: Controlled issue creation for Tier 1+ events with deduplication and root-cause consolidation.
- **Phase 4**: Optional GitHub Projects v2 custom field integration and label synchronization.

---

## 8. Alignment with Self-Evolution Policy Tiers

| Friction Tier | Self-Evolution Action | GitHub Logging Action |
| :--- | :--- | :--- |
| **Tier 0 (Quickfix)** | Fix inline if safe | Issue optional (only if repeated or preserves evidence) |
| **Tier 1 (Friction)** | Patch or record Map Debt | Fix inline OR log issue |
| **Tier 2 (Structural)** | Update rules & playbooks | Issue creation mandatory unless fixed in same changeset |
| **Tier 3 (Architecture)** | Hard stop & escalate | Issue creation + architecture review mandatory |
