# Audit closed issues for genuine resolution (`review-resolution` mode)

Audits closed repository issues labeled `resolution:fixed` or `resolution:superseded` to verify whether root causes were genuinely fixed or recurred.

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
2. **Inspect Fix & Map Debt**: Review fix PR commits, CI test logs, and the repository's map-debt ledger (`map-debt.md` in the repository root's references folder).
3. **Classify**: Assign `CONFIRMED_RESOLVED`, `RECURRING_FRICTION`, or `INCONCLUSIVE`.
4. **Produce Audit Table**: Present findings (`Issue # | Title | Classification | Evidence`).
5. **Human Gate**: If recurring friction is detected, ask user before reopening or logging consolidation issues.

## Verification

Confirm audit report table is rendered with concrete empirical evidence:

```bash
gh issue list --state closed --limit 1
```
