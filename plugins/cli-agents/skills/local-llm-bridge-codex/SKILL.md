---
name: local-llm-bridge-codex
plugin: cli-agents
description: >
  Bridge configuration to run general OpenAI-compatible coding clients (Aider, Goose, etc.) via local LLMs.
allowed-tools: Bash, Read, Write
---

## Identity: The Local LLM Bridge (Gemma 4 + OpenAI/Codex Clients) 🌉

This skill defines the integration structure to wrap general OpenAI-compatible command-line agents (like Aider, Goose, etc.) and route them to our local Metal-accelerated Gemma 4 engine via the routing proxy.

---

## 🏗️ Architecture Overview

Many modern terminal agents support standard OpenAI API configurations via base URL overrides. By intercepting these requests and pointing them to the local routing proxy, they gain private offline inference.

```
OpenAI-Compatible CLI (Aider / Goose / etc.)
   │  (Routes using env: OPENAI_API_BASE=http://localhost:4000/v1)
   ▼
Routing Proxy (Port 4000)
   └── POST /v1/chat/completions ──► llama-server :8089/v1/chat/completions (Local Gemma 4 12B)
```

No format translation is needed because `llama-server` natively supports OpenAI's `/v1/chat/completions` API structure alongside Anthropic's Messages API.

---

## 🛠️ Configuration & Code Files

### 1. Environment Injection Variables
`run_codex.py` configures:
* `OPENAI_API_BASE="http://localhost:4000/v1"`
* `OPENAI_BASE_URL="http://localhost:4000/v1"`
* `OPENAI_API_KEY="dummy"`
* `OPENAI_MODEL="gemma-4-12b"`

### 2. Execution Launcher (`run_codex.py`)
Launch any compatible CLI by prefixing the command with the launcher:
```bash
python3 run_codex.py aider --model openai/gemma-4-12b
```

---

## ⚠️ When This Works Well (and When It Doesn't)

### The CLI wrapper problem

OpenAI-compatible CLIs (Aider, Goose, etc.) each inject their own system prompt per invocation. If that prompt includes dynamic content (repo context, timestamps, file maps), each fresh process busts the LCP cache — even with the server running.

**Good fit:**
- Long interactive Aider/Goose sessions (single process, prefix fixed for session lifetime)
- Tools with stable, deterministic system prompts — second invocation may hit `sim_best = 1.000`

**Not a good fit:**
- Scripted one-off calls (`run_codex.py aider --some-task`) — cold prefill per call (~4–8 min)
- Automated pipelines spawning fresh processes per task — cloud is always faster here
- Mixing multiple tools back-to-back — each evicts the other's single cache slot

**Best path for scripted delegation**: call llama-server's `/v1/chat/completions` directly with a fixed system prompt. `kv_cache_orchestrator.py` in `scripts/` handles this automatically when routed through the proxy — SHA-256 hashes the system prompt, restores a saved slot on hit (instant), saves after miss (background). See `local-llm-setup.md` for the manual save/restore API pattern.

---

## 🔍 Validation Checklist
To verify the setup:
1. Start the server and proxy: `./run_server.sh` and `./enable_global_routing.sh`
2. Run `python3 run_codex.py aider --version` (or other target tool)
3. Prompt the model through the wrapped client and verify the request is captured in the proxy log.
