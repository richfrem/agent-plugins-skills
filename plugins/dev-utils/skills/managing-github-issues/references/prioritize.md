# Rank GitHub issues P0-P3 (`prioritize` mode)

Computes deterministic priority ranks (P0-P3) for GitHub issues from friction tiers, recurrence frequency, and blockages.

## Critical Constraints
- **Scope Boundary**: USE ONLY for calculating priority ranks (P0-P3) and syncing priority labels/fields. DO NOT USE for logging issues (use the `log` mode).
- **Deterministic Formula**: Calculate priority ranks strictly using the weighted matrix in `priority-matrix.md` without manual override inflation.
- **Dry-Run Default**: Preview calculated scores and proposed label diffs before mutating GitHub metadata.
- **Rate-Limit Hygiene**: Batch queries when prioritizing bulk backlogs to avoid secondary GitHub API limits.

## Quick start

```bash
# Calculate priority score and preview update (dry-run)
python3 scripts/gh_issue_prioritize.py --issue 42

# Execute live priority label and Projects v2 update
python3 scripts/gh_issue_prioritize.py --issue 42 --execute
```

## Workflow

1. **Phase 1: Issue Inspection**: Retrieve issue metadata, friction tier labels (`tier:*`), and linked blocker relationships.
2. **Phase 2: Score Calculation**: Evaluate score via matrix formula considering tier severity, recurrence count, and pipeline blocks.
3. **Phase 3: Payload Preview**: Review proposed priority designation (`priority:P0` through `priority:P3`) in preview mode.
4. **Phase 4: Label & Field Sync**: Apply the resulting priority label and update GitHub Projects v2 fields using `--execute`.

## Verification
