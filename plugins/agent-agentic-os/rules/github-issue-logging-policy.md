---
trigger: always_on
description: Policy and decision matrix governing when and how agent friction events, map debt, and bugs are logged as GitHub issues.
globs: ["**/*"]
---

# GitHub Issue Logging Policy (`github-issue-logging-policy`)

## 1. Purpose & Integration with `self-evolution-policy.md`

This policy governs when and how friction events, execution workarounds, tool failures, and map debt identified during agent runs are logged into GitHub Issues.

It directly extends `self-evolution-policy.md` by defining the decision boundary between in-session fixes, local Map Debt entries (`map-debt.md`), and formal GitHub Issue creation.

---

## 2. Friction Tier Decision Alignment Matrix

Every friction event or failure detected during agent execution must be evaluated against the friction tiers defined in `self-evolution-policy.md`:

| Friction Tier | Condition | Primary Action | GitHub Issue Logging Action | Required Labels |
|---|---|---|---|---|
| **Tier 0 (Quickfix)** | Small friction, fixable inline within allowed edit boundaries in < 5 mins. | Patch inline, update rules/docs ("The Map"). | **Optional**. Log issue only if pattern recurs across sessions. | `type:friction`, `tier:0-quickfix`, `source:agent`, `risk:low` |
| **Tier 1 (Friction / Gap)** | Workaround used, capability missing or awkward, but non-blocking. | Patch inline OR record Map Debt in `map-debt.md`. | **Fix inline or log issue**. If deferred as Map Debt, log issue payload. | `type:friction`, `tier:1-friction`, `source:agent`, `risk:low` |
| **Tier 2 (Failure / Structural)** | Script/tool broken, execution error, or recurring friction. | Collect stack trace & empirical logs. Patch code or log debt. | **Mandatory Issue Logging** (or comment on existing root-cause issue). | `type:bug` or `type:friction`, `tier:2-structural`, `source:agent` |
| **Tier 3 (Regression / Architecture)** | External change, breaking API/selector change, core design flaw. | Collect full evidence bundle & present formal Escalation Template. Synthesized by `repository-improvement`. | **Mandatory Issue Logging + Architecture Review**. | `type:architecture` or `type:bug`, `tier:3-architecture` |

---

## 2.1 Hotspot Synthesis Engine (`repository-improvement`)

For Tier 3 architecture friction and recurring friction clusters identified by `friction_cluster_agent`:
- The **`repository-improvement`** skill consumes cluster hotspot reports and synthesizes proposals for human review. It never creates branches, commits, or PRs itself — see the skill's Human Gate section.
- High-density hotspots are consolidated into architectural refactoring initiatives rather than fragmented single-line patches.

---

## 3. The Root-Cause Consolidation Principle

Before creating any new GitHub issue, the agent MUST perform root-cause consolidation:

> **Root-Cause Question:** *"Is this event itself the root issue, or is it merely one instance/symptom of a broader systemic issue?"*

### Operating Rules for Consolidation:
1. **Deduplication Search**: Run `search-related-issues` (via `gh_issue_search.py`) with title keywords and location labels (`area:*` or `plugin:*`).
2. **Existing Root Cause Found**: If an existing issue covers the root cause, do NOT create a new issue. Instead, use `comment-on-existing-issue` (`gh_issue_comment.py`) to append the new empirical evidence and log context to the open issue.
3. **Symptom vs. Cause**: Never open separate issues for "Script A failed line 10" and "Script B failed line 12" if both failed due to the same missing environment variable or missing helper parameter. Open one consolidated issue capturing the root cause.

---

## 4. Human Suppression Override

Humans retain full override control over automated issue logging.

If a prompt, system instruction, configuration, or issue logging context contains:
```yaml
issue_logging: suppressed
```
or if the user explicitly instructs "do not log issues" / "suppress issue creation":
- **Issue creation and commenting MUST be completely bypassed**.
- Friction events MUST still be recorded locally in `map-debt.md` or logged in the execution context, but no calls to `gh` issue creation scripts shall be executed.

---

## 5. Staged Rollout Stages

To ensure repository stability and prevent issue spam, automated issue logging follows a 4-phase rollout protocol:

- **Phase 1: Payload Generation (Current Default)**
  - All script runs operate in dry-run mode (`execute=False`).
  - Output is formatted as structured JSON payload containing issue title, body, taxonomy labels, and validation status.
  - No live network requests are made to GitHub.
- **Phase 2: Comment Operations**
  - Live commenting (`execute=True`) enabled for adding evidence to existing human-verified issues.
  - New issue creation remains dry-run.
- **Phase 3: Issue Creation**
  - Live issue creation (`execute=True`) enabled for Tier 2 and Tier 3 friction events passing all safety gates.
- **Phase 4: Label & Status Sync**
  - Full bidirectional sync of issue state, status labels, and resolution states.

---

## 6. Mandatory Body Evidence Requirements

Every issue body (whether generated as payload or submitted live) MUST strictly include all 5 markdown sections:

1. `## Summary`: Concise explanation of what failed or caused friction.
2. `## Observed Behavior`: Exact error output, stack trace snippet, or observed unexpected behavior.
3. `## Expected Behavior`: What should have happened according to specifications or rules.
4. `## Evidence`: Command executed, reproduction steps, log locations, or environment details.
5. `## Impact`: Impact on execution, developer flow, or system capabilities (e.g., blocked pipeline, workarounds required).

*Note: The `body_validator.py` script automatically verifies the presence of these 5 sections.*

---

## 7. Task Completion Reporting Rules

When completing a task where friction occurred:
- State whether issue logging was executed or produced dry-run payload.
- Include the issue number (if submitted live) or the dry-run payload summary (if in Phase 1).
- Emit the standard `PRE-COMPLETION GATE` block per `self-evolution-policy.md`.
