---
name: todo-check
plugin: agent-agentic-os
description: >
  Audit a file for TODO comments, pending work items, or technical debt markers. 
  Useful for checking code readiness before a commit or reviewing task status.
  Trigger with "check for todos", "audit for debt", "list pending work", or "scan for TODOs".
allowed-tools: Bash, Read
---

# Todo Check (`todo-check`)

Audit target source files for TODO comments, unfinished work items, or technical debt markers prior to commit or merge.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Read-Only Inspection**: Do not edit files to remove or suppress discovered TODOs.
2. **Standard Library Only**: Use built-in Python scripts without external pip dependencies.
3. **Report Exact Lines**: Output exact line numbers and comment contents for every debt marker found.

## Quick start

Scan a source file for pending TODO items:

```bash
python3 scripts/check_todos.py <path/to/file>
```

## Workflow

1. **Resolve Target**: Identify candidate source file or directory for debt auditing.
2. **Execute Audit**: Run `check_todos.py` against target path.
3. **Parse Findings**: Inspect reported markers (`TODO`, `FIXME`, `HACK`, `XXX`).
4. **Report Status**: Present summary of open items and file readiness to the user.

## Verification

Confirm script runs and outputs valid scan results:

```bash
python3 scripts/check_todos.py scripts/check_todos.py
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for todo scanning.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways if file cannot be read.
