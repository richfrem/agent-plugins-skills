---
name: github-issue-backlog-agent
plugin: dev-utils
description: >
  Bridge skill for escalating ephemeral local task scratchpad items (`tasks/*.md`)
  into durable, taxonomy-validated, evidence-rich GitHub Issues.
  USE ONLY when promoting a single-session local task into durable repository backlog.
  DO NOT USE for managing local kanban boards (use `task-agent` instead) or directly querying/commenting on issues (use `github-issue-agent` instead).
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

> **Routing Directive:** USE ONLY when promoting ephemeral single-session local tasks (`tasks/*.md`) into durable tracked GitHub Issues. DO NOT USE for managing local kanban boards (use `task-agent` instead) or directly creating/searching issues from execution friction (use `github-issue-agent` instead).

The `github-issue-backlog-agent` skill bridges local task scratch items into durable GitHub Issues. It parses local task markdown files, constructs evidence-backed markdown bodies conforming to repository taxonomy guidelines, and invokes `gh_issue_create.py` in dry-run or live mode.

---

## Safety & Security Contracts

1. **Dry-Run Execution Default (`execute=False`):** By default, calling `task_to_issue_bridge.py` outputs a structured JSON payload detailing the issue title, body, and labels without creating a live GitHub issue. Live creation requires `--execute`.
2. **Taxonomy Enforcement:** Every escalated issue is validated against `issue-taxonomy.json` rules (`type:*`, `tier:*`, `source:*`, `risk:*`, and `area:*`/`plugin:*`).
3. **Secret Redaction:** Both title and body undergo secret scanning via `redaction_gate.py` prior to payload generation or issue submission.

---

## Usage catalog

### Promote Task Scratch Item to GitHub Issue

- **Helper Script:** `plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py`
- **CLI Usage:**
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

## Python API Interface

```python
from pathlib import Path
from plugins.dev_utils.skills.github_issue_backlog_agent.scripts.task_to_issue_bridge import promote_task_to_issue

result = promote_task_to_issue(
    task_path=Path("tasks/backlog/0042-fix-deadlock.md"),
    extra_labels=["area:dev-utils", "tier:2-structural"],
    execute=False,  # Dry-run default
)
```
