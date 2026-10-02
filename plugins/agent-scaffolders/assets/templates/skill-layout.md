# Skill folder layout

## Contents

- [Instructional skills](#instructional-skills)
- [Executable skills](#executable-skills)
- [Managed resources](#managed-resources)

## Instructional skills

```text
skills/<name>/
  SKILL.md
  evals/evals.json
  evals/task-success.json  # add observed task-success scenarios
  references/<topic>.md   # only when needed; managed file links in source
```

## Executable skills

Add `scripts/<name>.py` as a managed file link to the plugin-root canonical script.
Declare dependencies, expected inputs/outputs, execution intent and validation.
Do not create empty scripts, references or assets folders for unused capabilities.

## Managed resources

Canonical resources live at plugin root: executable helpers in scripts, reading
material and contracts in references, copied templates in assets. The authoring
contract JSON declares available variants and required directories.

Generation proposes manifest entries; delegate diagnose/register/restore/diagnose
to symlink-manager. Installed resources become hard copies and must resolve from
the installed skill root without the source repository.
