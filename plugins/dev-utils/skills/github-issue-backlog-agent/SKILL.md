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

# GitHub Issue Backlog Agent (`github-issue-backlog-agent`)

> **Routing Directive:** USE ONLY when promoting ephemeral single-session local tasks (`tasks/*.md`) into durable tracked GitHub Issues. DO NOT USE for friction logging or general issue search (use `github-issue-agent` instead).

The `github-issue-backlog-agent` skill bridges local task scratch items into durable GitHub Issues. It parses local task markdown files, constructs evidence-backed markdown bodies conforming to repository taxonomy guidelines, and invokes `gh_issue_create.py` in dry-run or live mode.

---

## Quick Start & CLI

- **Helper Script:** `plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py`

```bash
# Dry-run payload preview:
python3 plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py \
  --task-path tasks/backlog/0042-fix-deadlock.md \
  --labels "area:dev-utils,tier:2-structural"

# Live issue creation:
python3 plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py \
  --task-path tasks/backlog/0042-fix-deadlock.md \
  --labels "area:dev-utils,tier:2-structural" \
  --execute
```

---

## Progressive Disclosure & References

- **Bridge Guide & API**: [references/bridge-guide.md](references/bridge-guide.md) — safety contracts, configuration options, and Python API interface.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — verification contracts and test expectations.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — failure recovery procedures and error handling.
