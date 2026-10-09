---
name: create-rule
plugin: agent-scaffolders
description: >
  Scaffolds a lean, invariant-driven agent rule following universal best practices. Enforces
  hard constraints, zero incident post-mortems, zero dates, zero usernames, high information density,
  and strict separation between rules (constraints) and skills (procedures).
argument-hint: "[rule-name or constraint-intent]"
allowed-tools: Bash, Read, Write
---

# Create Rule

Scaffolds lean, invariant-driven agent rules (`plugins/<plugin>/rules/<name>.md`) adhering to repository standards.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Rules define passive constraints and policy invariants; skills define active multi-step procedures.
State hard invariants (`MUST`, `NEVER`, `ALWAYS`), forbidden actions, and deterministic verifiers.
Enforce zero historical fluff: no session dates, incident post-mortems, commit hashes, or absolute machine paths (`/Users/...`).
Target high information density (30–70 lines; hard ceiling <= 80 lines). Strip speculative rationale and background exposition.
Plugin rules reside in `plugins/<plugin>/rules/<name>.md`. Installed rules must be self-contained; never invoke cross-plugin scripts directly.

## Quick start

Author the rule file at the designated target path using the canonical structure:

```markdown
---
description: Concise summary of the constraint and why it exists.
globs: ["**/*"]
---

# Rule: [Rule Title]

## 1. The Iron Law
> **Core invariant stated in 1-2 sentences.** Every action MUST comply.

## 2. Invariants & Forbidden Actions
1. **[Invariant 1]**: Concrete MUST / NEVER constraint.
2. **[Invariant 2]**: Specific forbidden action.

## 3. Evaluation Checklist
- [Deterministic verification question 1]
- [Deterministic verification question 2]
```

## Workflow

1. **Rule vs Skill Boundary**: Confirm the requirement is a passive constraint or guardrail, not an active procedure.
2. **Scaffold & Author**: Write the rule to `plugins/<plugin>/rules/<name>.md` with frontmatter `description` and `globs`.
3. **Draft The Iron Law**: Place the non-negotiable core constraint prominently in the first 20 lines.
4. **Enumerate Invariants**: Add concrete MUST/NEVER operational bounds without historical narratives.
5. **Register Rule Symlink**: Delegate rule registration to symlink-manager (`symlink_manager.py create`).
6. **Verify Invariants**: Run regex checks and line count validation to guarantee zero fluff and budget compliance.

## Verification

```bash
# 1. Verify rule contains zero calendar dates, commit SHAs, or absolute machine paths
grep -E "202[0-9]-[0-9]{2}-[0-9]{2}|/Users/|/home/" /path/to/rule.md && echo "FAIL" || echo "PASS"

# 2. Verify rule line budget (must be <= 80 lines)
wc -l /path/to/rule.md
```

Review [acceptance criteria](references/acceptance-criteria.md) and [fallback tree](references/fallback-tree.md) before publishing.

## References

- [Acceptance criteria](references/acceptance-criteria.md): structural gates and formatting requirements for rules.
- [Fallback protocol](references/fallback-tree.md): procedural fallback and escalation for rule authoring.
