# Self-Evolution Profile — Agent Scaffolders

## Allowed Edit Directories

- plugins/agent-scaffolders/skills/
- plugins/agent-scaffolders/scripts/
- plugins/agent-scaffolders/references/

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

`plugins/agent-scaffolders/references/`

## Evolution Log Path

`plugins/agent-scaffolders/references/evolution-log.md`
