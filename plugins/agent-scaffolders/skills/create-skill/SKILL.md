---
name: create-skill
plugin: agent-scaffolders
description: >
  Creates a new skill in an existing plugin, with concise instructions, direct
  references and task evaluations. Use when scaffolding or authoring a skill;
  supports instructional and executable variants.
allowed-tools: Bash, Read, Write
---

# Create a Skill

Generate a concise entry point, then supply task-specific instructions and evaluations.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Keep critical constraints and the first action early. Required references link directly
from SKILL.md; long references have early contents. Short skills may omit redundant
navigation. The first 100 lines are a preview budget, not a universal loading limit.
Canonical scripts/references/assets belong to the plugin root. Delegate managed
file-level links to symlink-manager; never create direct links or overwrite existing assets.

## Quick start

Reuse known requirements; read [discovery-interview.md](references/discovery-interview.md)
for missing authoring inputs. Run from this skill root with caller-supplied output paths:

```bash
python3 scripts/scaffold.py --type skill --name <name> --path /path/to/plugin/skills --desc "<does what; use when>" --variant instructional --json
```

For deterministic execution, select `--variant executable --plugin-root /path/to/plugin`.
Templates are in [assets/templates/skill-layout.md](assets/templates/skill-layout.md).

## Workflow

1. Choose the variant and observable task-success contract before extensive authoring.
2. Generate; review the JSON receipt. `pending_links` means the workflow is incomplete.
3. Delegate diagnose/register/restore/diagnose to symlink-manager using the proposed links.
4. Replace generic steps with necessary task knowledge, constraints, default commands,
   dependencies and validation loops. Add meaningful examples where useful.
5. Link detailed resources directly and say when to read them. Omit unused folders,
   historical retelling, conversation context and explanations the model already knows.
6. Create realistic routing cases and at least three task-success scenarios. Test with
   the intended models and refine against observed failures.

## Verification

Invoke audit-skill for source structure, then verify the installed skill with source
resources unavailable. Audit errors block readiness; static passes do not prove behavior.
Review [authoring acceptance criteria](references/authoring-acceptance.md) before publishing.

## References

- [Authoring contract](references/skill-authoring-contract.json): normative layout/rules.
- [Authoring guide](references/skill-authoring-guide.md): structure and severity profiles.
- [Platform primitives](references/platform-primitives.md): host-specific discovery boundaries.
- [Anthropic guidance](references/anthropic-skill-authoring-best-practices.md): external source.
- [Fallback](references/skill-authoring-fallback.md): generation and packaging failures.
