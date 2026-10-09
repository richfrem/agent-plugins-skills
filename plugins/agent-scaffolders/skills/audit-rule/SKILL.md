---
name: audit-rule
plugin: agent-scaffolders
description: >
  Audits agent rule markdown files for line budget compliance, fluff sanitization,
  and invariant structure. Use when checking or validating rules in rules/.
allowed-tools: Bash, Read, Write
---

# Audit Rule

Performs deterministic structural audits of agent rule policies against authoring standards.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Audits are read-only; never modify rule files automatically.
Enforce the progressive disclosure line budget (target 30–70 lines, hard ceiling <= 80 lines).
Enforce zero temporal fluff: fail on any calendar dates (`202X-XX-XX`) or absolute machine paths (`/Users/`).
Verify canonical structure: The Iron Law block early, Invariants & Forbidden Actions, and Evaluation Checklist.
Flag procedural drift where multi-step execution procedures are placed in rules rather than skills.

## Quick start

Run from this skill root with caller-supplied target:

```bash
# Audit a single rule file
python3 scripts/audit_rule.py /path/to/rules/<rule-name>.md --json

# Scan all rules in a plugin or repository
python3 scripts/audit_rule.py /path/to/repository --all --json
```

Exit 0: clean pass; 1: compliance errors or date/path violations; 2: invalid input.

## Workflow

1. **Target Selection**: Specify rule path under `plugins/<plugin>/rules/` or `.agent/rules/`.
2. **Execute Audit**: Run `audit_rule.py` to evaluate line count, fluff sanitization, and headings.
3. **Evaluate Findings**: Check for calendar dates, absolute paths, missing "Iron Law", or line bloat.
4. **Refactor Invariants**: Strip historical incident post-mortems and consolidate into MUST/NEVER bounds.
5. **Re-Audit**: Confirm clean exit code 0 before registering symlinks or committing.

## Verification

```bash
# Strict verification failing on any warning
python3 scripts/audit_rule.py /path/to/rules/<rule-name>.md --strict
```

Review [acceptance criteria](references/acceptance-criteria.md) before publishing.

## References

- [Acceptance criteria](references/acceptance-criteria.md): structural gates and rule formatting requirements.
- [Fallback protocol](references/fallback-tree.md): escalation protocol for rule authoring.
