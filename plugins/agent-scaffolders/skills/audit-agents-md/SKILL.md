---
name: audit-agents-md
plugin: agent-scaffolders
description: >
  Audits AGENTS.md, CLAUDE.md, and root instruction files against progressive disclosure,
  zero calendar dates, zero machine paths, and modular rule link standards. Use when verifying
  or refactoring repository instruction files.
allowed-tools: Bash, Read, Write
---

# Audit AGENTS.md (`audit-agents-md`)

Performs deterministic structural audits of repository root instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) against authoring standards and progressive disclosure budgets.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Audits are read-only; never modify instruction files automatically.
Enforce progressive disclosure line budgets (target <= 150 lines, max 200).
Enforce zero temporal fluff: fail on any calendar dates (`202X-XX-XX`) or absolute machine paths (`/Users/`, `/home/`).
Flag structural bloat: multi-line ASCII directory trees belong in `architecture.md`; multi-item pitfalls belong in dedicated reference docs; 'Key Files' and 'Tool Name Mapping' tables are redundant.
Enforce modularity: Non-negotiable rules must be concise invariants with markdown links to `.agent/rules/<rule>.md`.

## Quick start

Run from this skill root with caller-supplied target:

```bash
# Audit a specific instruction file
python3 scripts/audit_agents_md.py /path/to/AGENTS.md --json

# Scan all instruction files in a repository
python3 scripts/audit_agents_md.py /path/to/repository --all --json
```

Exit 0: clean pass; 1: compliance errors or date/path violations; 2: invalid input.

## Workflow

1. **Target Selection**: Specify `AGENTS.md` or repository root.
2. **Execute Audit**: Run `audit_agents_md.py` to evaluate line count, dates, paths, and bloat.
3. **Evaluate Findings**: Check for calendar dates, absolute paths, ASCII directory trees, or rule link gaps.
4. **Refactor Invariants**: Extract inlined pitfalls to `docs/architecture/known-pitfalls.md`, link directory structure to `architecture.md`, and link rules to `.agent/rules/`.
5. **Re-Audit**: Confirm clean exit code 0 before committing.

## Verification

```bash
# Strict verification failing on any warning
python3 scripts/audit_agents_md.py /path/to/AGENTS.md --strict
```

Review [acceptance criteria](references/acceptance-criteria.md) before publishing.

## References

- [Acceptance criteria](references/acceptance-criteria.md): structural gates and formatting requirements.
- [Fallback protocol](references/fallback-tree.md): escalation protocol for instruction authoring.
