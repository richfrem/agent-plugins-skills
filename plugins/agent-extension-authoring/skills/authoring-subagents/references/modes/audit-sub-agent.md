> Retired skill `audit-sub-agent`, kept as the **audit-sub-agent** mode of `authoring-subagents`. Body unchanged apart from link targets, the scaffolder command and the model-field wording. Frontmatter removed.
>
> Original description: Audits sub-agent markdown specifications for metadata, system prompt structure, tool sandboxing, and packaging compliance. Use when validating new or updated sub-agents in agents/.

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
Reject pointer-wrapper stubs delegating directly to skills; agents must have distinct system prompts and tool bounds.
Verify that subagents do not attempt to be interactive user interviewers (in Claude Code `AskUserQuestion` is disabled in subagents; interactive work belongs in skills).
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
3. **Review Findings**: Inspect output for missing frontmatter (`model`, `color`), generic names, wrapper stubs, or misallocated interactive workflows.
4. **Author Corrections**: Apply targeted edits to resolve errors while preserving persona intent.
5. **Re-Verify**: Re-run the audit until zero errors and zero warnings remain before committing.

## Verification

```bash
# Strict verification failing on any warning
python3 scripts/audit_sub_agent.py /path/to/agents/<agent-name>.md --strict
```

Review [acceptance criteria](../acceptance-criteria.md) before publishing.

## References

- [skills-vs-agents-decision-framework.md](../skills-vs-agents-decision-framework.md): The 5-question diagnostic decision tree, tool sandboxing vs. pre-approval, and audit checkpoints.
- [acceptance-criteria.md](../acceptance-criteria.md): Structural gates and frontmatter contracts.
- [fallback-tree.md](../fallback-tree.md): Procedural fallback for invalid schemas.
