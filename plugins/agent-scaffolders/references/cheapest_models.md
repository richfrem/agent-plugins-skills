# CLI Cheapest Models Reference

This is the single source of truth for current model costs per CLI engine.
Update here only — do not hardcode model names or cost claims in SKILL.md or agent files.

| CLI Engine | Model | Cost Tier | Notes |
|---|---|---|---|
| `llama` | `gemma-4-12b` | **Free** (self-hosted) | Local `llama-server` on port 8089. Only truly zero-cost option. |
| `copilot` | `mai-code-1.1-flash` | Paid (AI Credits) | 20 cr/1M input, 120 cr/1M output. Cheapest current tier — use for heartbeats and cost-sensitive calls. |
| `agy` | `gemini-3.8-flash-low` | Paid (Per-token / Pro quotas) | Antigravity CLI — replacement for deprecated `gemini` CLI; Low is the default dispatch tier. |
| `claude` | `claude-haiku-4-5` | Paid (Per-token) | $1/MTok input, $5/MTok output. |
| `codex` | `gpt-5.6-luna` | Paid (Per-token) | $0.20/1M input, $1.20/1M output; current cost-sensitive OpenAI model. |

> [!WARNING]
> Only `llama` (self-hosted Gemma 4) is free. Copilot, Gemini/Agy, and Claude all bill per token as of June 2026.
> The standalone `gemini` CLI (Google) was deprecated and shut down June 18, 2026 — use `agy` instead.
