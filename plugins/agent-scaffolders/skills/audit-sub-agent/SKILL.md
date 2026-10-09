---
name: audit-sub-agent
plugin: agent-scaffolders
description: >
  Audits sub-agent markdown specifications for metadata, system prompt structure,
  tool sandboxing, and packaging compliance. Use when validating new or updated
  sub-agents in agents/.
allowed-tools: Bash, Read, Write
---

# Audit Sub-Agent

Performs deterministic structural and schema audits of sub-agent definitions against authoring standards.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Audits are read-only; mutations are forbidden. Validate frontmatter fields (`name`, `model`, `color`, `tools`).
Verify that descriptions contain 2–4 `<example>` trigger blocks and define clear trigger bounds.
Reject pointer-wrapper stubs delegating directly to skills; agents must be genuine autonomous personas.
Verify system prompt addresses the agent in second person ("You are...") and establishes concrete responsibilities.

## Quick start

Run from this skill root with caller-supplied target:

```bash
# Audit a single sub-agent definition
python3 scripts/audit_sub_agent.py /path/to/agents/<agent-name>.md --json

# Scan all sub-agents in a plugin or repository
python3 scripts/audit_sub_agent.py /path/to/repository --all --json
```

Exit 0: clean pass; 1: structural or metadata errors; 2: invalid input or missing file.

## Workflow

1. **Target Discovery**: Locate agent specification under `plugins/<plugin>/agents/` or `.claude/agents/`.
2. **Execute Audit**: Run `audit_sub_agent.py` in source mode to check schema conformance.
3. **Review Findings**: Inspect output for missing frontmatter (`model`, `color`), generic names, or wrapper stubs.
4. **Author Corrections**: Apply targeted edits to resolve errors while preserving persona intent.
5. **Re-Verify**: Re-run the audit until zero errors and zero warnings remain before committing.

## Verification

```bash
# Strict verification failing on any warning
python3 scripts/audit_sub_agent.py /path/to/agents/<agent-name>.md --strict
```

Review [acceptance criteria](references/acceptance-criteria.md) before publishing.

## References

- [Acceptance criteria](references/acceptance-criteria.md): structural gates and frontmatter contracts.
- [Fallback protocol](references/fallback-tree.md): procedural fallback for invalid schemas.
