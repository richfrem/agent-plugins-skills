# GitHub Issue Backlog Agent Guide

## Safety & Security Contracts

1. **Dry-Run Execution Default (`execute=False`):** By default, calling `task_to_issue_bridge.py` outputs a structured JSON payload detailing the issue title, body, and labels without creating a live GitHub issue. Live creation requires `--execute`.
2. **Taxonomy Enforcement:** Every escalated issue is validated against `issue-taxonomy.json` rules (`type:*`, `tier:*`, `source:*`, `risk:*`, and `area:*`/`plugin:*`).
3. **Secret Redaction:** Both title and body undergo secret scanning via `redaction_gate.py` prior to payload generation or issue submission.

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
