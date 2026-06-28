# Backend Capability Matrix

Agent MUST select backend based on task type. Do NOT use the default blindly.

## Capability Table

| CLI | Binary | Strength | Weakness | Use For |
|---|---|---|---|---|
| `claude` | `claude` | Highest reasoning, best instruction following | Cost, interactive-only without `--yolo` | Complex analysis, nuanced content, open-ended reasoning |
| `copilot` | `copilot` | Multi-model selection, code-focused, IDE-native | Dynamic prompt injection kills KV cache; AI Credits cost | Code review, multi-file generation, structured output |
| `agy` | `agy` | Frontier Gemini (3.5 Flash+), large context | Rate limits, `--dangerously-skip-permissions` required for headless | Long context tasks, frontier Gemini models |
| `codex` | `codex` | Code transformation, OpenAI models | Weaker language reasoning than Claude | Code-only tasks, diff generation, code analysis |
| `llama` | `llama-server` (HTTP) | Fastest (~2s), zero API cost, private | Weaker reasoning than cloud models | Bounded loops, high-frequency local tasks, private data |
| `gemini` | `gemini` | Older Gemini models, no AI Credits | Deprecated for frontier work — use `agy` | Cost-efficient older Gemini only (2.5-pro, 3-flash-preview) |

## Isolation Behavior Per Backend

These CLIs are **not interchangeable** from an isolation standpoint:

| CLI | Headless flag | Isolation mechanism |
|---|---|---|
| `claude` | `--no-permissions` | Suppresses tool calls |
| `copilot` | `--yolo` | Enables tool access; absent = read-only |
| `agy` | `--dangerously-skip-permissions` | Suppresses permission prompts |
| `codex` | stdin-native | Prompt via stdin; tool flags vary |
| `llama` | N/A | Pure HTTP POST — no tool concept |
| `gemini` | `-y` | Headless mode |

When `run_agent.py --isolated` is set, dangerous flags are suppressed and a safety
footer is appended. This normalizes isolation across backends — but the underlying
mechanisms remain different. Do not assume equivalent behavior.

## Quality vs Cost Positioning

| Need | Recommended CLI | Reason |
|---|---|---|
| Fastest output | `llama` | Direct HTTP, ~2s, local |
| Cheapest cloud | `copilot` with `gpt-5-mini` | Included model, no credit cost |
| Best code analysis | `codex` or `copilot` | Code-trained models |
| Best reasoning | `claude` | Highest reasoning quality |
| Long context | `agy` (Gemini 3.5 Flash+) | 1M+ token window |
| Multi-perspective | Run same task on two CLIs, route through `debate-synthesizer` | |

## Capability Gaps — What NOT to Assume

- All backends support tool use the same way → **they do not**
- Model quality is equivalent across backends for the same task → **it is not**
- Output structure (markdown, code blocks) is consistent → **it is not**
- A backend that worked yesterday has the same API surface → **verify with heartbeat first**
