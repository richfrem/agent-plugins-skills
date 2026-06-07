# CLI Cheapest Models Reference

This is the single source of truth for current model costs per CLI engine.
Scripts load this file dynamically — update here only, not in individual scripts or SKILL.md files.

| CLI Engine | Model | Cost Tier | Notes |
|---|---|---|---|
| `llama` | `gemma-4-12b` | **Free** (self-hosted) | Local `llama-server` on port 8089. Only truly zero-cost option. |
| `copilot` | `gpt-5-mini` | Paid (AI Credits) | Copilot Pro free tier ended June 2026. Per-token billing. |
| `agy` | `gemini-3.5-flash` | Paid (Per-token / Pro quotas) | Replacement for deprecated `gemini` CLI. |
| `claude` | `claude-haiku-4-5` | Paid (Per-token) | $1/MTok input, $5/MTok output. |
| `codex` | `gpt-5-mini` | Paid (Per-token) | OpenAI-compatible endpoint. |
| `gemini` | `gemini-3-flash-preview` | Deprecated | Standalone CLI shuts down June 18, 2026. Use `agy` instead. |

> [!WARNING]
> Only `llama` (self-hosted Gemma 4) is free. Do not assume Copilot or Gemini/Agy are zero-cost.
