---
name: todo-check
description: >
  Audit a file for TODO comments, pending work items, or technical debt markers. 
  Useful for checking code readiness before a commit or reviewing task status.
  Trigger with "check for todos", "audit for debt", "list pending work", or "scan for TODOs".
allowed-tools: Bash, Read
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# todo-check

Check for TODOs and debt markers in a file.

## Usage
`python ${CLAUDE_PLUGIN_ROOT}/skills/todo-check/scripts/check_todos.py <path>`

<example>
Context: Directly auditing a specific file.
user: "Are there any todos left in project_logic.py?"
assistant: "I'll run the todo-check audit to find any pending work items in project_logic.py."
</example>

<example>
Context: Scanning for debt as part of a review.
user: "List the pending work items in utils.py before we merge."
assistant: "I'll use the todo-check tool to scan utils.py for any TODO markers or debt."
</example>

<example>
Context: Agent proactively audits before proposing a code change.
assistant: [autonomously, before suggesting a refactor] "Let me run todo-check on this file first to surface any existing debt markers before adding more changes."
<commentary>
Implicit audit trigger -- agent uses todo-check as a pre-flight check, no user prompt needed.
</commentary>
</example>
