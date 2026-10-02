---
name: github-issue-backlog-agent
plugin: dev-utils
description: >
  Bridge skill for escalating ephemeral local task scratchpad items (`tasks/*.md`)
  into durable, taxonomy-validated, evidence-rich GitHub Issues.
  USE ONLY when promoting a single-session local task into durable repository backlog.
  DO NOT USE for directly querying/commenting on issues (use `github-issue-agent` instead).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Backlog Agent (github-issue-backlog-agent)

Escalates ephemeral single-session local tasks (`tasks/*.md`) into durable, taxonomy-validated GitHub Issues.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for promoting local tasks (`tasks/*.md`) into durable backlog issues. DO NOT USE for general friction queries (use `github-issue-agent`).
- **Dry-Run by Default**: Generate and preview issue payloads without `--execute` before committing live issues.
- **Redaction Gate**: Task descriptions and logs must pass secret scanning (`redaction_gate.py`) prior to export.
- **Mandatory Labels**: Issues must be tagged with explicit `area:*` or `plugin:*` and `tier:*` dimensions.

## Quick start

```bash
# Preview task escalation to GitHub issue payload (dry-run)
python3 plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py \
  --task-path tasks/backlog/<task-file>.md \
  --labels "area:dev-utils,tier:2-structural"

# Execute live issue creation
python3 plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py \
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

```bash
# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/github-issue-backlog-agent --mode source
```

## References
- [bridge-guide.md](references/bridge-guide.md) - Safety contracts, configuration options, and Python API.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification contracts and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Failure recovery and error handling procedures.
