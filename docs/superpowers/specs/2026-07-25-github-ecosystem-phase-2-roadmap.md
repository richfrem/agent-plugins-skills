# Design Spec: GitHub Ecosystem Phase 2 Roadmap & Architectural Evolution

**Date**: 2026-07-25  
**Authors**: Antigravity + User + Opus  
**Status**: Future Roadmap (Phase 2 Spec)  
**Target Systems**: `plugins/dev-utils/skills/github-issue-agent/`, `plugins/agent-agentic-os/`, `plugins/agent-memory/`  

---

## 1. Overview & Vision

Phase 1 establishes **Agent Friction Observability & GitHub Issue Logging** (dry-run default, secret redaction, strict taxonomy, and root-cause consolidation).

**Phase 2** expands this capability into **Repository Operational Memory & Self-Evolution Intelligence**, transforming GitHub Issues from an externalized friction log into an active, closed-loop organizational learning substrate.

```
+------------------------------------+
|  Phase 1: Friction & Issue Logging |
|  (Dry-run, Taxonomy, Dedup, Redact)|
+-----------------+------------------+
                  |
                  v
+------------------------------------+
|  Phase 2: Repository Operational   |
|            Memory (ROM)            |
+-----------------+------------------+
                  |
       +----------+----------+
       |                     |
       v                     v
+--------------+     +---------------+
| Cluster      |     | Automated     |
| Friction     |     | Backlog &     |
| Hotspots     |     | Lifecycle     |
+--------------+     +---------------+
```

---

## 2. Phase 2 Capabilities & Workstreams

### Workstream 1: Issue Lifecycle Ownership & Resolutions
Extend `github-issue-agent` to support issue closure and lifecycle transitions cleanly without cluttering the backlog:
- **Resolution Taxonomy**: `resolution:fixed`, `resolution:superseded`, `resolution:wont-fix`, `resolution:obsolete`.
- **Operations**:
  - `close-issue-with-resolution`: Appends structured resolution comment, sets `resolution:*` label, closes issue.
  - `merge-duplicate-issues`: Merges candidate issue threads, reassigns evidence links, and marks duplicate with `resolution:superseded`.

### Workstream 2: GitHub Projects v2 Custom Field Integration
Transition mutable workflow state from label fallback (`status:*`) to native GitHub Projects v2 custom fields when available:
- `Priority`: P0 / P1 / P2 / P3
- `Agent Action`: Fix Inline / Log Issue / Needs Human / Needs Spec / Duplicate
- `Friction Tier`: T0 / T1 / T2 / T3
- `Detected By`: Agent / Human / Script / Test / Review

### Workstream 3: Friction Hotspot Clustering & Root-Cause Analysis
Build an offline analysis agent (`friction-cluster-agent` or `os-friction-analyzer`) that periodically inspects open/closed friction issues across repositories to:
1. **Cluster Hotspots**: Identify recurring patterns in script failures, broken documentation, or selector repairs across plugins.
2. **Synthesize Recommendations**: Automatically propose new reusable skills, subagents, or Agentic OS rules to prevent recurring friction classes.
3. **Map Debt Reduction**: Feed clustered friction directly into `os-improvement-loop` and `self-evolution-policy.md`.

### Workstream 4: Full Multi-Stage Staged Rollout Enablement
Execute the remaining stages of the rollout policy:
- **Stage 2**: Enable agent proposal of issue payloads in task completion reports (`proposed_issues.json`).
- **Stage 3**: Controlled live GitHub issue creation for Tier 1+ events with deduplication and root-cause consolidation.
- **Stage 4**: GitHub Projects v2 field synchronization.
- **Stage 5**: Automated label taxonomy synchronization upon explicit human authorization.

---

## 3. Alignment with Repository Operational Memory (ROM)

By bridging `github-issue-agent` with `agent-agentic-os` memory managers (e.g. `rlm-curator`, `os-experiment-log`), Phase 2 establishes a continuous repository feedback loop:

```
[Agent Execution Friction]
          │
          ▼
[gh_issue_search (Root Cause Dedup)]
          │
          ▼
[Durable GitHub Issue Backlog] ◄──┐
          │                      │
          ▼                      │ (Feeds operational context)
[friction-cluster-agent] ────────┘
          │
          ▼
[Propose New Rule / Skill / Refactor]
```

---

## 4. Phase 2 Acceptance Criteria

1. `gh_issue_comment.py` and `gh_issue_close.py` support `resolution:*` lifecycle management.
2. `issue-taxonomy.json` provides schema for GitHub Projects v2 custom fields alongside fallback labels.
3. `friction-cluster-agent` can parse issue data and generate friction hotspot analysis reports.
4. Live GitHub creation/commenting flags can be selectively enabled per repository environment stage.