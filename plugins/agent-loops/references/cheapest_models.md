# CLI Cheapest Models Reference

This authoritative document lists the current cost-effective models for each CLI engine as of June 2026.

| CLI Engine (`--cli`) | Low-Cost Model | Cost Tier | Notes |
|---|---|---|---|
| `llama` | `gemma-4-12b` | **Free** (self-hosted) | Local `llama-server` on port 8089. Metal accelerated. |
| `copilot` | `gpt-5-mini` | Paid (AI Credits) | Copilot Pro free tier ended. Uses AI Credits per token. |
| `agy` | `gemini-3.5-flash` | Paid (Per-token / Pro quotas) | Replacement for deprecated `gemini` CLI. |
| `claude` | `claude-haiku-4-5` | Paid (Per-token) | $1/MTok input, $5/MTok output. |
| `codex` | `gpt-5-mini` (or `gpt-4.1`) | Paid (Per-token) | Routed through custom OpenAI endpoint. |

> [!WARNING]
> Only `--cli llama` is free. Do not assume Copilot (`gpt-5-mini`) or Gemini/Agy (`gemini-3.5-flash`) are zero-cost. Use them carefully to manage credit usage. Standalone `gemini` CLI shuts down on June 18, 2026.
