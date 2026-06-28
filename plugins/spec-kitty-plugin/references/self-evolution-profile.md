# Self-Evolution Profile — Spec Kitty Plugin

## Allowed Edit Directories

- plugins/spec-kitty-plugin/skills/
- plugins/spec-kitty-plugin/scripts/
- plugins/spec-kitty-plugin/references/

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

`plugins/spec-kitty-plugin/references/`

## Evolution Log Path

`plugins/spec-kitty-plugin/references/evolution-log.md`
