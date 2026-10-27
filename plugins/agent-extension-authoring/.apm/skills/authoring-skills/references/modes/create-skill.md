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
In APM-native packages, skills reside in `.apm/skills/<skill-name>/`.
Scripts, references and assets live inside the skill that uses them (no plugin-root hub,
no symlinks, no copy manifest); never overwrite existing assets.

## Quick start

Reuse known requirements; read [discovery-interview.md](../discovery-interview.md)
for missing authoring inputs. Run from this skill root with caller-supplied output paths
(pointing to `.apm/skills` in APM-native packages, or `skills` in legacy plugins):

```bash
python3 scripts/scaffold.py --type skill --name <name> --path /path/to/plugin/.apm/skills --desc "<does what; use when>" --variant instructional --json
```

For deterministic execution, select `--variant executable --plugin-root /path/to/plugin`.
Templates are in [assets/templates/skill-layout.md](../../assets/templates/skill-layout.md).

## Workflow

1. Verify capability structure via [skills-vs-agents-decision-framework.md](../skills-vs-agents-decision-framework.md). If the task requires tool sandboxing or context isolation, author a subagent via `authoring-subagents`; interactive workflows and operator steering belong in skills in the main thread. Choose the variant and observable task-success contract before extensive authoring.
2. Generate; review the JSON receipt (`status: generated`, `links: []`; an executable script is written inside the skill).
3. Nothing to register or link; the skill is self-contained.
4. Replace generic steps with necessary task knowledge, constraints, default commands,
   dependencies and validation loops. Add meaningful examples where useful.
5. Link detailed resources directly and say when to read them. Omit unused folders,
   historical retelling, conversation context and explanations the model already knows.
6. Create realistic routing cases and at least three task-success scenarios. Test with
   the intended models and refine against observed failures.

## Verification

Invoke audit-skill for source structure, then verify the installed skill with source
resources unavailable. Audit errors block readiness; static passes do not prove behavior.
Review [authoring acceptance criteria](../authoring-acceptance.md) before publishing.

## References

- [Decision framework](../skills-vs-agents-decision-framework.md): 5-question tree, tool sandboxing vs. pre-approval, and Anthropic refinements.
- [Authoring contract](../skill-authoring-contract.json): normative layout/rules.
- [Authoring guide](../skill-authoring-guide.md): structure and severity profiles.
- [Platform primitives](../platform-primitives.md): host-specific discovery boundaries.
- [Anthropic guidance](../anthropic-skill-authoring-best-practices.md): external source.
- [Fallback](../skill-authoring-fallback.md): generation and packaging failures.
