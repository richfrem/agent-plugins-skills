# Self-Evolution Profile — Dependency Management

## Allowed Edit Directories

- plugins/dependency-management/skills/
- plugins/dependency-management/scripts/
- plugins/dependency-management/references/

## Explicit Confirmation Required

- plugin.json
- CLAUDE.md
- .agent/rules/
- ADRs/
- docs/

## Error Pattern → Tier Classification

| Pattern | Tier |
|---------|------|
| FileNotFoundError, No such file or directory | Tier 1 — Gap |
| AttributeError, TypeError, KeyError | Tier 2 — Failure |
| AssertionError, wrong output, test fails | Tier 3 — Regression |
| Workaround used, guessed, bypassed | Tier 0 — Friction |

## Domain Playbook Location

`plugins/dependency-management/references/`

## Evolution Log Path

`plugins/dependency-management/references/evolution-log.md`
