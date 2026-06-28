# Self-Evolution Profile — CLI Agents

## Allowed Edit Directories

- plugins/cli-agents/skills/
- plugins/cli-agents/scripts/
- plugins/cli-agents/references/

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

`plugins/cli-agents/references/`

## Evolution Log Path

`plugins/cli-agents/references/evolution-log.md`
