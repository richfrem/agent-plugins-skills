---
name: authoring-instructions
plugin: agent-extension-authoring
description: >-
  Creates and audits the instruction files agents read: agent rules (rules/*.md), the root AGENTS.md with its thin CLAUDE.md bridge, and event-driven hooks (.apm/hooks/hooks.json plus handler scripts). Use when the user wants to write, check, trim or migrate a rule, AGENTS.md or CLAUDE.md, or to add or lint a lifecycle hook such as PreToolUse or SessionStart. Not for skills (use authoring-skills), whole plugins (use authoring-plugins) or GitHub workflows (use authoring-github-workflows).
argument-hint: "[rule|agents-md|hook] [create|audit] [path]"
allowed-tools: Bash, Read, Write
---

# Authoring Instructions (`authoring-instructions`)

Writes lean, invariant-driven instruction files and audits them deterministically: rules, root `AGENTS.md` / `CLAUDE.md`, and plugin hooks.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Rules are constraints, skills are procedures.** A rule states MUST / NEVER / ALWAYS bounds in 30–70 lines (ceiling 80); anything with ordered steps becomes a skill.
2. **Timeless and portable**: no calendar dates, commit SHAs, usernames or absolute machine paths in a rule or root file.
3. **Never overwrite** an existing `AGENTS.md` or `CLAUDE.md`; propose a diff. `CLAUDE.md` stays a bridge of 5 lines or fewer.
4. **Audits are read-only.** They report findings; changes are reviewed edits.
5. **APM-native hooks (SF-11)**: hooks live in `plugins/<plugin>/.apm/hooks/hooks.json` and use `python3 ... || python ...` commands anchored on `${CLAUDE_PLUGIN_ROOT}/.apm/hooks/<name>.py`. Hook scripts run under every target harness (`claude`, `copilot`, `codex`): use `Path(__file__).resolve()` for sibling files, store runtime state in harness-neutral paths (`context/`), never `.claude/` or `.agents/`, exit silently when the repository is not initialised, and stay fast.
6. **Rules & APM (SF-9)**: APM does not deploy a plugin's `rules/` folder (instructions deploy from `.apm/instructions/`), so rules need no copy manifest or symlink registration step; setup copies needed rules into `.agent/rules/`.

## Modes

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `create-rule` | New rule file | write the canonical structure | [create-rule.md](references/modes/create-rule.md) |
| `audit-rule` | Check rules | `scripts/audit_rule.py` | [audit-rule.md](references/modes/audit-rule.md) |
| `create-agents-md` | Scaffold or migrate root files | `assets/templates/AGENTS.md.jinja` | [create-agents-md.md](references/modes/create-agents-md.md) |
| `audit-agents-md` | Check size, timelessness, disclosure | `scripts/audit_agents_md.py` | [audit-agents-md.md](references/modes/audit-agents-md.md) |
| `hook` | Add, lint or test a lifecycle hook | `scripts/scaffold_hook.py` | [create-hook.md](references/modes/create-hook.md) |

## Quick start

```bash
python3 scripts/audit_rule.py <rules-dir-or-file> --json
python3 scripts/audit_agents_md.py AGENTS.md --strict
python3 scripts/scaffold_hook.py --event PreToolUse --name check-command --plugin-root plugins/<plugin>
```

## Workflow

1. Pick the mode and read its reference before running anything.
2. Create modes: draft from the canonical structure or template, then run the matching audit.
3. Hook mode: scaffold, implement the handler under `.apm/hooks/`, then run `scripts/validate_hook_schema.py` and `scripts/hook_linter.py`; exercise it with `scripts/test_hook.py`.
4. On any failure follow that mode's section in [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 scripts/audit_rule.py <rule.md> --strict
python3 scripts/audit_agents_md.py . --all --strict
python3 scripts/validate_hook_schema.py plugins/<plugin>/.apm/hooks/hooks.json
```

Tests: `python3 -m pytest tests`. Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create-rule](references/modes/create-rule.md) • [audit-rule](references/modes/audit-rule.md) • [create-agents-md](references/modes/create-agents-md.md) • [audit-agents-md](references/modes/audit-agents-md.md) • [hook](references/modes/create-hook.md)
- Detail: [agents-md-contract.md](references/agents-md-contract.md) • [hooks-spec.md](references/hooks-spec.md) • [hook-patterns.md](references/hook-patterns.md) • [hook-advanced.md](references/hook-advanced.md) • [hook-migration.md](references/hook-migration.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
- Template: [AGENTS.md.jinja](assets/templates/AGENTS.md.jinja)
