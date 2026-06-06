---
name: local-llm-bridge-agy
plugin: cli-agents
description: >
  Experimental bridge configuration hosting local LLMs optimized for Antigravity (Agy) CLI.
allowed-tools: Bash, Read, Write
---

## Identity: The Local LLM Bridge (Gemma 4 + Antigravity/Agy) (Experimental) 🌉

This skill defines the configuration and scripts to run local models natively and bridge them with **Antigravity (Agy)**.

---

## 🏗️ Architecture Overview (Experimental)

> [!WARNING]
> This integration is experimental. While Antigravity natively supports Google Gemini API formats, this bridge configures Agy's `config.toml` to communicate using standard OpenAI-compatible completions endpoints at `http://localhost:4000/v1`.

```
Antigravity CLI (agy)
   │  (Mapped to endpoint: http://localhost:4000/v1)
   ▼
Routing Proxy (Port 4000)
   └── POST /v1/chat/completions ──► llama-server :8089/v1/chat/completions (Local Gemma 4 12B)
```

By specifying the `LOCAL_PASSTHROUGH` environment key, Agy bypasses remote endpoints and attempts to execute tasks using the local Metal-accelerated Gemma 4 engine via the proxy.

---

## 🛠️ Configuration & Code Files

### 1. Model Configuration (`~/.config/antigravity/config.toml`)
`run_agy.py` automatically checks and patches this configuration file. Ensure the following block is present inside `~/.config/antigravity/config.toml` to register your local model:

```toml
[[models]]
name = "Gemma 4 Local"
model = "gemma-4-12b"
base_url = "http://localhost:4000/v1"
env_key = "LOCAL_PASSTHROUGH"
```

### 2. Execution Launcher (`run_agy.py`)
Run the launcher from your terminal to patch the configuration dynamically, inject the required `LOCAL_PASSTHROUGH` key environment variable, and start Antigravity:
```bash
python3 run_agy.py chat "Explain quantum computing in one paragraph."
```

---

## ⚠️ When This Works Well (and When It Doesn't)

### The CLI wrapper problem

Agy injects its own system prompt per process. If the prompt varies between invocations, each call cold-prefills (~4–8 min) regardless of whether the server stayed running.

**Good fit:**
- Long interactive Agy sessions (single process stays open, cache warms once)
- Agy with a stable, deterministic system prompt — second call may hit the cache

**Not a good fit:**
- Short one-off `agy chat "..."` delegation tasks — cold prefill cost exceeds the work
- Alternating Agy with Claude Code or Copilot — each CLI evicts the other's cache slot
- Multi-agent orchestration loops using Agy as a sub-agent — every spawn is a fresh cold start

**For delegated sub-agent work**: use cloud Gemini directly — no warmup, instant, free tier available.

### Disk cache (future path)

`run_server.py` launches with `--slot-save-path`. `kv_cache_orchestrator.py` in `scripts/` automates save/restore and is wired into the proxy — but only when you control the system prompt. Agy injects its own system prompt per process, so the cache key changes every session. Not useful for Agy CLI sessions. See `local-llm-setup.md` for the manual save/restore API if you build direct API workflows.

---

## 🔍 Validation Checklist
To verify the setup:
1. Start the server and proxy: `./run_server.sh` and `./enable_global_routing.sh`
2. Run `python3 run_agy.py chat "test"`
3. Verify that Agy targets the local endpoint and that the request gets processed by checking the proxy output (`tail -f ~/.claude/proxy/logs/proxy.log`).
