# Skill folder layout

## Contents

- [Instructional skills](#instructional-skills)
- [Executable skills](#executable-skills)
- [Self-contained resources](#self-contained-resources)

## Instructional skills

```text
.apm/skills/<name>/
  SKILL.md
  evals/evals.json
  evals/task-success.json  # add observed task-success scenarios
  references/<topic>.md   # only when needed; real files inside the skill
```

## Executable skills

Add `scripts/<name>.py` directly inside `.apm/skills/<name>/scripts/` as a real file.
Declare dependencies, expected inputs/outputs, execution intent and validation.
Do not create empty scripts, references or assets folders for unused capabilities.

## Self-contained resources

Every skill owns its resources directly inside `.apm/skills/<name>/`: executable helpers
in `scripts/`, reading material and contracts in `references/`, copied templates in `assets/`,
and unit tests in `tests/`. There are no plugin-root shared folders, symlinks, or copy
manifests. Installed skills resolve all resources from the installed skill root without
requiring the source repository.
