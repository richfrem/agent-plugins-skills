---
name: create-stateful-skill
plugin: agent-scaffolders
description: >
  Scaffolds an advanced stateful agent skill with filesystem-native state schemas, lifecycle state
  machines, and skill chaining. NOT for simple stateless skills (use `create-skill`), NOT for
  isolated conversational wizards / persona swarms (use `create-sub-agent`), and NOT for GitHub
  Actions workflows (use `create-agentic-workflow`).
argument-hint: "[skill-name]"
allowed-tools: Bash, Read, Write
---

# Create Stateful Skill (`create-stateful-skill`)

Scaffolds advanced stateful skills with filesystem-native state schemas, lifecycle state machines, and deterministic skill chaining in the main conversation context.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Stateful Skill vs Sub-Agent Boundary**: Stateful skills run directly in the main conversation using filesystem schemas (`.agent/state/` or artifact frontmatter). Isolated wizards use `create-sub-agent`; stateless procedures use `create-skill`.
2. **Deterministic Chaining**: Skill transitions must offer explicit next-step capabilities (`/skill-name`), not loose commands.
3. **Budget Compliance**: Generated skill instructions must stay within the lean advisory limit ($\le 80$ lines).

## Quick start

Scaffold a new stateful skill directory using the generator helper:

```bash
python3 scripts/scaffold.py --name <skill-name> --type stateful
```

## Workflow

1. **Pre-Scaffold Qualification**: Verify that the skill requires persistent state schemas or lifecycle transitions across turns.
2. **Select L4 Patterns**: Consult `pattern-decision-matrix.md` to select artifact lifecycle, state propagation, or escalation models.
3. **Design State Schema**: Formulate JSON/YAML schemas for `.agent/state/` or structured frontmatter.
4. **Scaffold Directory**: Generate `SKILL.md`, `evals/evals.json`, and reference files.
5. **Chain Next Steps**: Configure standard next-step blocks linking downstream capabilities.

## Verification

Audit the newly created skill for contract compliance and schema validity:

```bash
python3 scripts/audit_skill.py plugins/<plugin>/skills/<skill-name> --mode source
```

## References

- [pattern-decision-matrix.md](references/pattern-decision-matrix.md) — Decision matrix for L4 stateful skill patterns.
- [persistent-plugin-configuration.md](references/patterns/persistent-plugin-configuration.md) — Persistent configuration pattern reference.
- [cyclical-state-propagation-contract.md](references/patterns/cyclical-state-propagation-contract.md) — Cyclical state propagation pattern reference.
- [hitl-interaction-design.md](references/hitl-interaction-design.md) — Human-in-the-loop interaction guidelines and confirmation gates.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and structural requirements for stateful skills.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution when state schemas or chaining fail.
