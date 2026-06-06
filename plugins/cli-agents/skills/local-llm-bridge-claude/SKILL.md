---
name: local-llm-bridge-claude
plugin: cli-agents
description: >
  Guide and instructions to host Google Gemma 4 12B locally and bridge it
  directly to Claude Code CLI using a custom routing proxy on port 4000.
  Supports macOS Metal, Windows CUDA/Vulkan, and Linux CUDA/ROCm.
allowed-tools: Bash, Read, Write
---

## Identity: The Local LLM Bridge (Gemma 4 + Claude Code) 🌉

This skill defines the architecture and scripts to run **Google Gemma 4 12B** natively on Apple Silicon M1 (16GB RAM), Windows (NVIDIA/AMD GPU), or Linux and seamlessly bridge it with **Claude Code** to run agentic coding tasks for free.

---

## 🏗️ Architecture Overview

```
Claude Code (any project)
   │  ANTHROPIC_BASE_URL=http://localhost:4000
   ▼
Routing Proxy (Python, port 4000) — auto-starts on login
   ├── GET  /v1/models        → Anthropic API → prepend gemma-4-12b → merged list
   ├── POST /v1/messages
   │    ├── model: claude-*   → api.anthropic.com  (Cloud — paid)
   │    └── model: gemma-*    → llama-server :8089/v1/messages  (local, strips thinking + temperature)
   └── POST /v1/chat/completions
        └── model: gemma-*    → llama-server :8089/v1/chat/completions
                                     │
                           Gemma 4 12B (UD-Q4_K_XL.gguf)
                           GPU inference via platform backend
```

Both paths are pure transparent relays. No format translation needed — `llama-server` speaks the Anthropic Messages API natively.

---

## 🛠️ Configuration & Code Files

All scripts are in the plugin's `scripts/` directory, symlinked into this skill directory.

### 1. The Local Server (`run_server.py`)

Cross-platform launcher — auto-detects binary (pre-built or compiled), model file, and thread count.

**Server parameters:**

| Parameter | Value | Purpose |
|---|---|---|
| `-c 32768` | 32K context | Fits Claude Code's ~29K token system prompt |
| `-np 1` | 1 slot | Prevents KV cache overflow on 16GB RAM |
| `-ngl 99` | 99 GPU layers | Full GPU offload (Metal / CUDA / Vulkan / ROCm) |
| `--reasoning off` | — | Disables Gemma thinking tokens |
| `-fa on` | Flash Attention | Accelerates large prompt prefill |
| `-b 2048 -ub 512` | Batch sizes | Optimized prefill throughput |
| `-t auto` | Platform-detected | M1=4 perf cores; Windows/Linux=physical÷2 |
| `-ctk q8_0 -ctv q8_0` | 8-bit KV cache | High-fidelity cache |
| `--chat-template-kwargs '{"enable_thinking": false}'` | — | Prevents thinking block injection |

```bash
python3 ../scripts/run_server.py
```

### 2. Telemetry and Attribution Bypass (`~/.claude/settings.json`)

Disabling telemetry headers prevents cache-busting on every turn. Ensure:

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "DISABLE_TELEMETRY": "1"
  }
}
```

`run_claude.py` patches this automatically.

### 3. The Claude Session Launcher (`run_claude.py`)

Patches settings, ensures the proxy is running, and launches Claude Code:

```bash
python3 ../scripts/run_claude.py
# Or via bench repo wrapper:
./run_gemma.sh
```

Environment injected:
```
ANTHROPIC_BASE_URL=http://localhost:4000
CLAUDE_CODE_MAX_CONTEXT=32768
claude --model gemma-4-12b
```

---

## ⚠️ When This Works Well (and When It Doesn't)

### What the cache does

`--cache-ram` keeps idle KV state in host RAM. When the next request sends the same system prompt prefix, llama-server restores it instead of re-prefilling (`sim_best = 1.000` → ~2 seconds). This survives across separate Claude Code sessions as long as the server process stays running.

### The CLI wrapper problem

Claude Code injects a dynamic system prompt per session — including repo file maps, tool definitions (~29K tokens), and session context. Each fresh `claude` process sends a slightly different prefix, which can bust the LCP cache between sessions even with the server running.

**Good fit:**
- Long interactive Claude Code sessions (cold prefill once, all turns after ~2s)
- Back-to-back sessions on the same project with stable context (prefix may match)

**Not a good fit:**
- One-off background tasks or short delegated calls — cold prefill cost (~2–4 min) exceeds the work
- Alternating with Copilot/Agy/Codex — each CLI evicts the other's cache slot (`-np 1` = one prefix cached at a time)
- `smallFastModel` background tasks — do **not** set `smallFastModel: "gemma-4-12b"` in `.claude/settings.json`; use Haiku

### Disk cache for direct API delegation

`run_server.py` starts with `--slot-save-path ~/.claude/proxy/kv_cache/`. For direct API delegation workflows (bypassing CLI wrappers), `kv_cache_orchestrator.py` in `scripts/` automates this: SHA-256 hashes the system prompt, checks `~/.claude/proxy/kv_cache/<hash>.bin`, restores on hit (instant), saves on miss (background thread). Wired into `routing_proxy.py`. See `local-llm-setup.md` for the manual save/restore API pattern.

---

## 🔍 Validation Checklist

Confirm KV cache hits are active (check `llama-server` logs on subsequent prompts):
* `selected slot by LCP similarity, sim_best = 1.000`
* `restored context checkpoint`
* `init: chat template, thinking = 0`

### Cold Prefill Latency

| Platform | First query (cold prefill) | Subsequent queries |
|---|---|---|
| macOS M1 — Metal | Under 30 seconds | Under 2 seconds |
| macOS M1 — CPU only | 6–8 minutes | Under 2 seconds |
| Windows/Linux — CUDA/Vulkan (8GB+ VRAM) | Under 30 seconds | Under 2 seconds |
| Windows/Linux — CPU only | 10+ minutes | Under 2 seconds |

Do not cancel during cold prefill — the server is processing the ~29K token system prompt. Once complete, all subsequent turns are near-instant.