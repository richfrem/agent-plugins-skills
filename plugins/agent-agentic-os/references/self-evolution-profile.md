# Self-Evolution Profile — Agent Agentic OS

## Allowed Edit Directories

- plugins/agent-agentic-os/skills/
- plugins/agent-agentic-os/scripts/
- plugins/agent-agentic-os/references/

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

`plugins/agent-agentic-os/references/`

## Evolution Log Path

`plugins/agent-agentic-os/references/evolution-log.md`
