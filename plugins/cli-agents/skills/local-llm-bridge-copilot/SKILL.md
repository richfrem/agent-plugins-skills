---
name: local-llm-bridge-copilot
plugin: cli-agents
description: >
  Experimental bridge configuration hosting local LLMs optimized for GitHub Copilot CLI.
allowed-tools: Bash, Read, Write
---

## Identity: The Local LLM Bridge (Gemma 4 + GitHub Copilot) (Experimental) 🌉

This skill defines the experimental configuration and scripts to run local models natively and attempt to bridge them with **GitHub Copilot CLI** using standard OpenAI-compatible completions.

---

## 🏗️ Architecture Overview (Experimental)

> [!WARNING]
> This integration is experimental and currently unverified. The Copilot CLI's respect for environment variable overrides is diagnostic.

```
Copilot CLI (Experimental BYOK + Offline)
   │  (Routes traffic using env: COPILOT_PROVIDER_BASE_URL=http://localhost:4000/v1)
   ▼
Routing Proxy (Port 4000)
   └── POST /v1/chat/completions ──► llama-server :8089/v1/chat/completions (Local Gemma 4 12B)
```

No format translation is needed because `llama-server` natively supports OpenAI's `/v1/chat/completions` API structure alongside Anthropic's Messages API.

---

## 🛠️ Configuration & Code Files

### 1. Environment Overrides
To launch Copilot CLI in offline BYOK mode, `run_copilot.py` injects:

```python
COPILOT_OFFLINE="true"
COPILOT_PROVIDER_TYPE="openai"
COPILOT_PROVIDER_BASE_URL="http://localhost:4000/v1"
COPILOT_PROVIDER_API_KEY="dummy"
COPILOT_MODEL="gemma-4-12b"
```

### 2. Execution Launcher (`run_copilot.py`)
Run the launcher from your terminal to establish context and start Copilot:
```bash
python3 run_copilot.py explain "def hello(): pass"
```

### 3. Diagnostic Mode (`run_copilot.py --diagnose`)
To verify your environment variables, check the path of your `copilot` binary, and see if it attempts to connect to the local proxy:
```bash
python3 run_copilot.py --diagnose
```
This prints the binary path, `copilot --version`, `copilot --help`, and the active env variables. Use proxy logs (`tail -f ~/.claude/proxy/logs/proxy.log`) to confirm requests.

---

## ⚠️ When This Works Well (and When It Doesn't)

### The CLI wrapper problem — confirmed by testing

`copilot --prompt "..."` was tested back-to-back without restarting llama-server. Both calls took 7–8 minutes. The LCP cache did **not** hit between non-interactive invocations.

Why: Copilot injects dynamic context (repo state, session IDs, file maps) into its system prompt each process start. The prefix changes enough between invocations to bust the cache every time — even with `--cache-ram` active and the server running. The community confirms: *"No one has a clean solution for the CLI wrapper problem. The workarounds all assume you control the prompt."*

**Good fit:**
- Long **interactive** Copilot sessions (`python3 run_copilot.py` with no `--prompt`) — cold prefill once, then all turns ~2 seconds

**Not a good fit:**
- `copilot --prompt "..."` one-shot calls — cold prefill every invocation (~7–8 min each)
- Delegating small tasks via scripted Copilot calls — cost is prohibitive
- Alternating with Claude Code or other CLIs — each evicts the other's single cache slot

**For quick one-off tasks**: Copilot's native cloud model (GPT-5-mini) is instant and free on the Pro plan — use that instead of routing through local Gemma.

### Disk cache (future path)

`run_server.py` launches with `--slot-save-path`. `kv_cache_orchestrator.py` in `scripts/` automates save/restore and is wired into the proxy — but only useful when you control the system prompt. Copilot controls its own prompt, so the cache key changes every session. Not currently useful for Copilot CLI sessions. See `local-llm-setup.md` for the manual save/restore API if you build direct API workflows.

---

## 🔍 Validation Checklist
To verify the setup:
1. Start the server and proxy: `./run_server.sh` and `./enable_global_routing.sh`
2. Run diagnostic check: `python3 run_copilot.py --diagnose`
3. Execute a request and verify it hits the proxy logs.
