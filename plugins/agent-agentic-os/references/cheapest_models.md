# CLI Cheapest Models Reference

This file lists no model IDs, prices or versions. Model choice belongs to the `cli-agents` plugin;
ask its skills, which stay current:

| Need | Skill (in `cli-agents`) |
|---|---|
| Latest model IDs, capability tiers, cheapest models and prices | `update-cli-models` |
| Which providers and models this project can use | `project-setup` (provider capability profile) |
| Dispatch through a backend | `claude-cli-agent`, `copilot-cli-agent`, `agy-cli-agent`, `codex-cli-agent` |
| Free local model | `local-llm-bridge` |

Do not hard-code model IDs or cost claims in SKILL.md or agent files; name a tier and let the
dispatch skill resolve it.

## Lab guidance

- Pick the cheapest suitable tier for proposer and heartbeat calls; reserve the frontier tier for
  work that needs it.
- The local model (`local-llm-bridge`) is the only zero-cost option; every other backend bills.
