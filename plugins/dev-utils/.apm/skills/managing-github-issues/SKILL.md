---
name: managing-github-issues
plugin: dev-utils
description: >
  Logs, promotes, ranks, synthesizes and audits GitHub issues with dry-run-first,
  deduplicated, taxonomy-validated and secret-redacted payloads. Use to log repository
  friction, bugs or map debt as issues, promote a local tasks/*.md note to an issue,
  rank issues P0-P3, draft a systemic refactoring proposal from friction clusters, or
  audit whether closed issues were genuinely resolved, or produce a GitHub Advanced
  Security (GHAS) report. Not for worktrees or the
  issue-to-PR flow (use resolving-github-issues).
allowed-tools: Bash, Read, Write
---

# Managing GitHub Issues (`managing-github-issues`)

Create, promote, rank, propose and audit issues; report on GHAS without publishing changes.

## Contents

- [Constraints](#constraints) • [Quick Start](#quick-start) • [Modes](#modes) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Dry-run first**: every mutating script previews its payload; pass `--execute` only after review.
- **Redaction and taxonomy gates**: `redaction_gate.py` blocks secrets; labels need `type:*`, `tier:*`, `source:*`, `risk:*` and `area:*` or `plugin:*`.
- **Body sections**: `## Summary`, `## Observed Behavior`, `## Expected Behavior`, `## Evidence`, `## Impact`.
- **Human gates**: `propose-refactor` never creates branches, commits or PRs; `review-resolution` is read-only and never reopens or relabels.
- **Ledger**: friction history lives in the repository's `map-debt.md` (repository root, references folder).

## Quick Start

```bash
python3 scripts/gh_issue_search.py --title "Bug summary" --area-label "area:dev-utils"
python3 scripts/gh_issue_create.py --title "Bug summary" --body "<5 sections>" --labels "type:friction,tier:1-friction,source:agent,risk:low,area:dev-utils"
```

## Modes

| Mode | Script | Use for | Reference |
|---|---|---|---|
| `log` | `gh_issue_search.py`, `gh_issue_create.py`, `gh_issue_comment.py`, `gh_issue_close.py` | Friction, bugs, map debt; dedupe into existing issues | [log.md](references/log.md) |
| `backlog` | `task_to_issue_bridge.py` | Promote a local `tasks/*.md` note to an issue | [backlog.md](references/backlog.md) |
| `prioritize` | `gh_issue_prioritize.py` | Rank P0-P3 and sync Projects v2 fields | [prioritize.md](references/prioritize.md) |
| `propose-refactor` | `friction_cluster_agent.py` (input) | One systemic proposal per Tier 3 root cause | [propose-refactor.md](references/propose-refactor.md) |
| `review-resolution` | `gh issue list` (read-only) | Audit `resolution:fixed` / `resolution:superseded` issues | [review-resolution.md](references/review-resolution.md) |
| `ghas-report` | GitHub connector or `gh api` (read-only) | Report access, alerts, scanner coverage and repository security configuration | [ghas-reporting-guide.md](references/ghas-reporting-guide.md) |

## Workflow

1. Pick the mode from the table and read its reference before running anything.
   For GHAS reports, read the guide, collect evidence and draft the report, then stop; the remaining steps apply to issue operations.
2. Search for existing issues first; comment on a matching root cause instead of creating a duplicate.
3. Run the mode's script in dry-run, check redaction and taxonomy, then rerun with `--execute` when authorized.
4. On any failure follow that mode's section in [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 scripts/gh_issue_taxonomy_validate.py --labels "type:friction,tier:1-friction,source:agent,risk:low,area:dev-utils"
```

For GHAS reports, verify access limits, pagination, safe metadata and source citations using the guide. For issue operations, check [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [log.md](references/log.md) • [backlog.md](references/backlog.md) • [prioritize.md](references/prioritize.md) • [propose-refactor.md](references/propose-refactor.md) • [review-resolution.md](references/review-resolution.md)
- Detail: [operation-catalog.md](references/operation-catalog.md) • [taxonomy-guide.md](references/taxonomy-guide.md) • [issue-taxonomy.md](references/issue-taxonomy.md) • [bridge-guide.md](references/bridge-guide.md) • [priority-matrix.md](references/priority-matrix.md)
- GHAS reporting: [ghas-reporting-guide.md](references/ghas-reporting-guide.md) — access probes, alert history, configuration review, evidence and report template.
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
