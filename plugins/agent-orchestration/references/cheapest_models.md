# CLI Cheapest Models Reference

This is the single source of truth for current model costs per CLI engine.
Update here only — do not hardcode model names or cost claims in SKILL.md or agent files.

| CLI Engine | Model | Cost Tier | Notes |
|---|---|---|---|
| `llama` | `gemma-4-12b` | **Free** (self-hosted) | Local `llama-server` on port 8089. Only truly zero-cost option. |
| `copilot` | `gpt-5.4-nano` | Paid (AI Credits) | 20 cr/1M input, 125 cr/1M output. Cheapest tier — use for heartbeats and cost-sensitive calls. |
| `agy` | `gemini-3.5-flash` | Paid (Per-token / Pro quotas) | Antigravity CLI — replacement for deprecated `gemini` CLI. |
| `claude` | `claude-haiku-4.5` | Paid (Per-token) | $1/MTok input, $5/MTok output. |
| `codex` | `gpt-5.4-nano` | Paid (Per-token) | OpenAI-compatible endpoint. |

> [!WARNING]
> Only `llama` (self-hosted Gemma 4) is free. Copilot, Gemini/Agy, and Claude all bill per token as of June 2026.
> The standalone `gemini` CLI (Google) was deprecated and shut down June 18, 2026 — use `agy` instead.
