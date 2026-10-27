> Retired skill `ecosystem-standards`, kept as the **ecosystem-standards** mode of `authoring-skills`. Body unchanged apart from link targets, retired-skill names (now the new skills) and the corrected commands. Frontmatter removed.
>
> Original description: Provides active execution protocols to rigorously audit how code, directory structures, and agent actions comply with the authoritative ecosystem specs. Trigger when validating new skills, plugins, or workflows.

# Ecosystem Standards Review Protocol (`ecosystem-standards`)

Active audit execution protocol validating skills, plugins, and workflows against ecosystem specifications.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Directory schema**: Only allowed subdirectories (`scripts/`, `references/`, `assets/`, `evals/`, `tests/`).
- **Gerund naming**: Skills must use gerund form (`verb + -ing`); directory slug must match `name`.
- **Third-person voice**: Descriptions must be written strictly in third-person without personal pronouns.
- **Progressive disclosure**: `SKILL.md` target $\le 80$ lines (hard preview limit 100).
- **Connector abstraction**: MCP plugins must use `~~category` abstraction in `CONNECTORS.md`.

## Quick start

```bash
# Audit a skill against ecosystem standards
python3 scripts/audit_skill.py plugins/<plugin>/.apm/skills/<skill>
```

## Workflow

1. **Identify Subject**: Determine if auditing a plugin, skill, hook, agent, or workflow.
2. **Structural Validation**: Check directory schema, root cleanliness, and absence of symlinks.
3. **Manifest & Frontmatter**: Verify semver, object author, and third-person description.
4. **Execution Protocol**: Validate plan-validate-execute patterns, error handling, and test fixtures.
5. **Actionable Report**: Emit structured audit findings with concrete remediation diffs.

## Verification

```bash
# Validate skill compliance against progressive disclosure rules
python3 scripts/audit_skill.py plugins/<plugin>/.apm/skills/<skill>
# Validate plugin structure (via sibling authoring-plugins skill)
python3 ../authoring-plugins/scripts/audit_plugin_structure.py plugins/<plugin>
```

## References

- [plugins.md](../plugins.md) — Comprehensive plugin specification.
- [acceptance-criteria.md](../acceptance-criteria.md) — Ecosystem standards review acceptance criteria.
- [fallback-tree.md](../fallback-tree.md) — Fallback protocol for standards review deadlocks.
