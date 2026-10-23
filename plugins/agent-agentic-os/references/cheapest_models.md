# CLI Cheapest Models Reference

This file lists no model IDs, prices or versions. Model choice belongs to the `cli-agents` plugin;
ask its skills, which stay current:

| Need | Skill (in `cli-agents`) |
|---|---|
| Latest model IDs, capability tiers, cheapest models and prices | `cli-agent` (model catalog maintenance) |
| Which providers and models this project can use | `cli-agent` (project setup: provider capability profile) |
| Dispatch through a backend | `cli-agent` (`--cli claude`, `copilot`, `agy` or `codex`) |
| Free local model | `cli-agent` (`--cli llama`) |

Do not hard-code model IDs or cost claims in SKILL.md or agent files; name a tier and let the
dispatch skill resolve it.

## Lab guidance

- Pick the cheapest suitable tier for proposer and heartbeat calls; reserve the frontier tier for
  work that needs it.
- The local model (`cli-agent --cli llama`) is the only zero-cost option; every other backend bills.
