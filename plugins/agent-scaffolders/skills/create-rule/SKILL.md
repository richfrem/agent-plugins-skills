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

# Create Rule (`create-rule`)

Scaffolds lean, invariant-driven markdown rules (`plugins/<plugin>/rules/<rule-name>.md`) adhering to agentic engineering standards.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Template](#template)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Strict invariants**: State hard constraints (`MUST`, `NEVER`, `ALWAYS`), forbidden actions, and deterministic verifiers.
- **Zero historical fluff**: No session dates, incident post-mortems, commit hashes, or absolute machine paths (`/Users/...`).
- **High information density**: Target 30–70 lines. Strip background exposition.
- **Rules vs Skills**: Rules define passive constraints and policies; skills define active multi-step procedures.

## Quick start

```bash
# Scaffold a new rule in target plugin rules directory
touch plugins/<plugin-name>/rules/<rule-name>.md
```

## Template

```markdown
---
trigger: always_on | on_match
description: Concise summary of the constraint and why it exists.
globs: ["**/*"]
---

# Rule Title

## The Law
> **Core invariant stated in 1-2 sentences.** Every action MUST comply.

## Invariants & Forbidden Actions
1. **[Invariant 1]**: Concrete MUST / NEVER constraint.
2. **[Invariant 2]**: Specific forbidden action.
```

## Workflow

1. **Discovery**: Determine slug, invariant, trigger scope (`always_on` or `globs`), and location (`plugins/<plugin>/rules/`).
2. **Scaffold**: Populate YAML frontmatter and invariant rules following the canonical template.
3. **Register Symlinks**: Register rule symlink via `symlink_manager.py create`.
4. **Synchronize**: Run `python3 plugins/cli-agents/scripts/sync_instruction_files.py` to update root instructions.

## Verification

```bash
# Verify rule contains zero dates or absolute machine paths
grep -E "202[0-9]-[0-9]{2}-[0-9]{2}|/Users/|/home/" plugins/<plugin>/rules/<rule-name>.md && echo "FAIL" || echo "PASS"
# Verify rule line budget <= 80 lines
wc -l plugins/<plugin>/rules/<rule-name>.md
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and structural requirements for rules.
- [fallback-tree.md](references/fallback-tree.md) — Fallback escalation protocol for rule authoring.
