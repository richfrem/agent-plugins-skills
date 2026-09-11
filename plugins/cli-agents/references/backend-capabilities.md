# Backend Capability Matrix

Agent MUST select backend based on task type. Do NOT use the default blindly.

## Capability Table

| CLI | Binary | Strength | Weakness | Use For |
|---|---|---|---|---|
| `claude` | `claude` | Highest reasoning, best instruction following | Cost, interactive-only without `--yolo` | Complex analysis, nuanced content, open-ended reasoning |
| `copilot` | `copilot` | Multi-model selection, code-focused, IDE-native | Dynamic prompt injection kills KV cache; AI Credits cost | Code review, multi-file generation, structured output |
| `agy` | `agy` | All Gemini models (sole CLI since gemini binary retired June 2026); large context | Rate limits, `--dangerously-skip-permissions` required for headless; thinking level affects cost/latency | Routine and long-context tasks — default to gemini-3.8-flash-low |
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

## Native lifecycle facilities (verified September 2026)

Use a CLI's native facility only when that CLI is the active runtime. A model name or a
different host application's capability does not transfer it.

| CLI | Native planning | Native worktree creation | Native delegated/background agents | Control-plane action |
|---|---|---|---|---|
| `claude` | Yes: `--permission-mode plan` | Yes: `--worktree` | Yes: background agents and custom agents | Prefer the native session; still record governed receipts. |
| `agy` | Yes: `--mode=plan` | No documented CLI facility | Yes: asynchronous subagents and custom agents | Create a portable worktree, then use plan/subagents inside it. |
| `copilot` | Yes: `--plan` / `--mode plan` | No documented CLI facility | Yes: custom agents and model-selected subsidiary agents | Create a portable worktree; require approval before autopilot. |
| `codex` | No documented CLI mode | No documented CLI facility | No documented CLI delegation flag | Use portable planning/worktree/delegation; use `exec` or `review` within it. |

All four may expose a different surface in a host application or future release. Check the
installed CLI help before relying on a newly introduced flag; the portable fallback remains
the interoperable path.

## Quality vs Cost Positioning

| Need | Recommended CLI | Reason |
|---|---|---|
| Fastest output | `llama` | Direct HTTP, ~2s, local |
| Cheapest cloud | `copilot` with `mai-code-1.1-flash` | Current lowest published Copilot credit tier; verify live pricing with `models.list` |
| Best code analysis | `codex` or `copilot` | Code-trained models |
| Best reasoning | `claude` | Highest reasoning quality |
| Long context | `agy` (Gemini 3.8 Flash+) | 1M+ token window |
| Multi-perspective | Run same task on two CLIs, route through `debate-synthesizer` | |

## Capability Gaps — What NOT to Assume

- All backends support tool use the same way → **they do not**
- Model quality is equivalent across backends for the same task → **it is not**
- Output structure (markdown, code blocks) is consistent → **it is not**
- A backend that worked yesterday has the same API surface → **verify with heartbeat first**
