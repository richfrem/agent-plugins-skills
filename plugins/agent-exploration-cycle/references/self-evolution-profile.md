# Self-Evolution Profile — Exploration Cycle Plugin

## Allowed Edit Directories

- plugins/agent-exploration-cycle/skills/ (each skill's SKILL.md, references/, assets/, scripts/)
- plugins/agent-exploration-cycle/references/

## Explicit Confirmation Required

- plugin.json
- CLAUDE.md
- .agent/rules/
- docs/

## Error Pattern → Tier Classification

| Pattern | Tier |
|---------|------|
| FileNotFoundError, No such file or directory | Tier 1 — Gap |
| AttributeError, TypeError, KeyError | Tier 2 — Failure |
| AssertionError, wrong output, test fails | Tier 3 — Regression |
| Workaround used, guessed, bypassed | Tier 0 — Friction |

## Domain Playbook Location

`plugins/agent-exploration-cycle/skills/running-exploration-cycle/references/` (domain patterns)

## Evolution Log Path

`plugins/agent-exploration-cycle/references/evolution-log.md`
