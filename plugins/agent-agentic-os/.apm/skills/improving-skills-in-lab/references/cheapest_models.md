# CLI Cheapest Models Reference (used by the `setup` and `loop` modes)

This file lists no model IDs, prices or versions. Model choice belongs to the `cli-agent` skill
(in the `agent-orchestration` plugin); ask it, because it stays current:

| Need | Ask the `cli-agent` skill |
|---|---|
| Latest model IDs, capability tiers, cheapest models and prices | `cli-agent` (model catalog maintenance) |
| Which providers and models this project can use | `cli-agent` (project setup: provider capability profile) |
| Dispatch through a backend | `cli-agent` (`--cli claude`, `copilot`, `agy` or `codex`) |
| Free local model | `cli-agent` (`--cli llama`) |

Do not hard-code model IDs or cost claims in SKILL.md or agent files; name a tier and let the
dispatch skill resolve it.

## Lab guidance

- Proposer and heartbeat calls use the cheapest suitable tier; reserve the frontier tier for work that needs it. Escalate to a higher tier only when the
  cheap tier repeatedly fails to produce a usable mutation.
- The local model (`cli-agent --cli llama`) is the only zero-cost option; every other backend bills.
