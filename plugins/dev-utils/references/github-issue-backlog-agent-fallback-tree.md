# Procedural Fallback Tree: GitHub Issue Backlog Agent

## 1. Task File Missing or Unreadable
- **Condition**: `--task-path` does not point to an existing readable markdown file.
- **Action**: Terminate with clear path error message; prompt user to supply valid task file.

## 2. GitHub CLI (`gh`) Unavailable
- **Condition**: Live execution requested (`--execute`) but `gh` CLI unavailable or unauthenticated.
- **Action**: Output payload JSON to stdout and inform user to install `gh` or create the issue manually.

## 3. Redaction Failure
- **Condition**: Secret token discovered in task file content.
- **Action**: Abort immediately without printing the secret; indicate line number for manual remediation.
