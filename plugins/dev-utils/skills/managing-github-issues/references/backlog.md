# Promote local task notes to GitHub issues (`backlog` mode)

Escalates ephemeral single-session local tasks (`tasks/*.md`) into durable, taxonomy-validated GitHub Issues.

## Critical Constraints
- **Scope Boundary**: USE ONLY for promoting local tasks (`tasks/*.md`) into durable backlog issues. DO NOT USE for general friction queries (use the `log` mode).
- **Dry-Run by Default**: Generate and preview issue payloads without `--execute` before committing live issues.
- **Redaction Gate**: Task descriptions and logs must pass secret scanning (`redaction_gate.py`) prior to export.
- **Mandatory Labels**: Issues must be tagged with explicit `area:*` or `plugin:*` and `tier:*` dimensions.

## Quick start

```bash
# Preview task escalation to GitHub issue payload (dry-run)
python3 scripts/task_to_issue_bridge.py \
  --task-path tasks/backlog/<task-file>.md \
  --labels "area:dev-utils,tier:2-structural"

# Execute live issue creation
python3 scripts/task_to_issue_bridge.py \
  --task-path tasks/backlog/<task-file>.md \
  --labels "area:dev-utils,tier:2-structural" \
  --execute
```

## Workflow

1. **Phase 1: Task Parsing**: Read the local task markdown file, extracting objective, observed blocker, and repro context.
2. **Phase 2: Payload Formatting**: Construct structured sections (`Summary`, `Observed Behavior`, `Expected Behavior`, `Evidence`, `Impact`).
3. **Phase 3: Validation & Gate Check**: Run `task_to_issue_bridge.py` in dry-run mode to verify redaction and taxonomy validity.
4. **Phase 4: Live Creation & Task Reference**: Run with `--execute` and record the generated issue URL into the local task notes.

## Verification
