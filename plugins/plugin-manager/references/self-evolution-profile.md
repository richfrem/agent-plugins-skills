# Self-Evolution Profile — Plugin Manager

## Allowed Edit Directories

- plugins/plugin-manager/skills/
- plugins/plugin-manager/scripts/
- plugins/plugin-manager/references/

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

`plugins/plugin-manager/references/`

## Evolution Log Path

`plugins/plugin-manager/references/evolution-log.md`
