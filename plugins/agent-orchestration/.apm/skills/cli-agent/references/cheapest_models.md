# CLI Cheapest Models Reference

This is the single source of truth for current model costs per CLI engine.
Update here only — do not hardcode model names or cost claims in SKILL.md or agent files.

| CLI Engine | Model | Cost Tier | Notes |
|---|---|---|---|
| `llama` | `gemma-4-12b` | **Free** (self-hosted) | Local `llama-server` on port 8089. Air-gapped zero-cost option. |
| `copilot` | `gpt-6-luna` | Included / AI Credits | Fast and affordable; **strictly restricted to work-related repositories**. |
| `agy` | `gemini-3.8-flash` | Paid (Per-token / Pro quotas) | Antigravity CLI — fast, large context; select Low effort for cost-sensitive tasks. |
| `claude` | `claude-haiku-5-5` | Paid (Per-token / Pro tier) | $0.10/MTok input, $0.50/MTok output (up to 100K prompt tokens); efficient subtask delegator. |
| `codex` | `gpt-6-luna` | Paid (Per-token / Plus tier) | Fast, cost-sensitive OpenAI model for mechanical edits. |
| `cursor` | `cursor-agent` | Included (Cursor Pro) | Headless non-interactive CLI reading root AGENTS.md. |
| `openrouter` | `meta-llama/llama-3.2-1b-instruct` | Paid ($0.027/$0.20 per MTok) | Ultra-cheap cloud micro-tier; also supports `llama-3.2-3b` and `qwen3-coder-flash` for routine mechanical chores. |

> [!WARNING]
> Only `llama` (self-hosted Gemma 4) is free. Copilot, Gemini/Agy, and Claude bill per token or consume subscription quota.
> Enterprise seats (e.g. Copilot) must remain isolated to corporate/work projects; use personal subscriptions (Claude Pro, ChatGPT Plus, Gemini Pro) for independent work.
> The standalone `gemini` CLI (Google) was deprecated and shut down June 18, 2026 — use `agy` instead.
