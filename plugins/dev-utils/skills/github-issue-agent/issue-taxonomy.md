# GitHub Issue Taxonomy

This document outlines the standardized, multi-dimensional taxonomy for repository issues logged by agents and humans.

## Mandatory Rules
Every issue logged in this repository **MUST** contain:
1. All required label dimensions: `type:*`, `tier:*`, `source:*`, `risk:*`.
2. At least one location dimension: `area:*` OR `plugin:*`.

## Dimensions

### Type (`type:*`)
- `type:bug`: Reproducible error or unexpected behavior.
- `type:friction`: Tool/runtime friction or execution blockage.
- `type:map-debt`: Outdated index, broken reference, or map drift.
- `type:enhancement`: Planned feature or systemic improvement.
- `type:documentation`: Doc gap or ambiguity.
- `type:security`: Vulnerability or security concern.
- `type:architecture`: Structural/layering rule violation.
- `type:test-gap`: Missing test coverage or untracked edge case.

### Tier (`tier:*`)
- `tier:0-quickfix`: Minor inline fix.
- `tier:1-friction`: Reusable script/rule friction.
- `tier:2-structural`: Multi-component structural fix required.
- `tier:3-architecture`: Deep architectural change required.

### Area (`area:*`)
- `area:dev-utils`, `area:agentic-os`, `area:skills`, `area:rules`, `area:subagents`, `area:scripts`, `area:tests`, `area:docs`, `area:ci`, `area:github`, `area:task-agent`

### Plugin (`plugin:*`)
- Prefixed with `plugin:`, e.g., `plugin:agent-loops`, `plugin:dev-utils`.

### Source (`source:*`)
- `source:agent`, `source:human`, `source:script`, `source:test`, `source:review`, `source:migration`

### Risk (`risk:*`)
- `risk:low`, `risk:medium`, `risk:high`, `risk:security-sensitive`, `risk:destructive-operation`

### Status (`status:*`)
- `status:needs-triage`, `status:needs-spec`, `status:ready`, `status:blocked`, `status:accepted-debt`, `status:duplicate`

### Resolution (`resolution:*`)
- `resolution:fixed`, `resolution:superseded`, `resolution:wont-fix`, `resolution:obsolete`
