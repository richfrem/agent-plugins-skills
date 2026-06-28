# Self-Evolution Profile — Exploration Cycle Plugin

## Allowed Edit Directories

- plugins/exploration-cycle-plugin/skills/
- plugins/exploration-cycle-plugin/scripts/
- plugins/exploration-cycle-plugin/references/

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

`plugins/exploration-cycle-plugin/references/`

## Evolution Log Path

`plugins/exploration-cycle-plugin/references/evolution-log.md`
