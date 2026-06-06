# cli-agents

Unified CLI Conductor Suite. Orchestrates task delegation to Claude, Copilot, and Gemini CLI engines with integrated AGF/AGT security controls, path boundary assertions, and default-isolated execution modes. Also provides the Local LLM Bridge — routing all CLI traffic through a local Gemma 4 12B instance via a cross-platform routing proxy.

## Plugin Structure

```
cli-agents/
├── .claude-plugin/
│   └── plugin.json               # Unified manifest
├── README.md                     # This file
├── agents/
│   ├── refactor-expert.md
│   ├── security-auditor.md
│   ├── architect-review.md
│   └── local-llm-setup.md        # Cross-platform local LLM setup agent
├── references/
│   ├── local_llm_debrief.md      # Technical briefing: optimizations + architecture
│   └── routing-proxy.mmd         # Sequence diagram: full routing flow
├── scripts/
│   ├── conductor.py              # Unified execution conductor
│   ├── path_security.py          # Path boundary assertions
│   ├── test_harness.py           # MAF adapter test simulator
│   ├── agt_ops.py                # AGT sandbox & key validator
│   ├── routing_proxy.py          # Global routing proxy (port 4000)
│   ├── run_server.py             # llama-server launcher (cross-platform)
│   ├── run_claude.py             # Claude Code session launcher → local Gemma
│   ├── run_copilot.py            # GitHub Copilot CLI session launcher → local Gemma
│   ├── run_agy.py                # Antigravity CLI session launcher → local Gemma
│   ├── run_codex.py              # Generic OpenAI-compatible CLI launcher → local Gemma
│   ├── enable_global_routing.py  # Install proxy daemon (launchd/NSSM/systemd)
│   ├── disable_global_routing.py # Remove proxy daemon (cross-platform)
│   ├── kv_cache_orchestrator.py  # KV slot save/restore middleware (ds4-inspired, stdlib only)
│   ├── test_kv_cache.py          # 20 TDD tests for kv_cache_orchestrator
│   └── adapters/                 # Lightweight provider CLI adapters
│       ├── claude_adapter.py
│       ├── copilot_adapter.py
│       └── gemini_adapter.py
└── skills/
    ├── claude-cli-agent/         # Claude CLI execution wrapper
    ├── copilot-cli-agent/        # Copilot CLI execution wrapper
    ├── gemini-cli-agent/         # Gemini CLI execution wrapper
    ├── agy-cli-agent/            # Antigravity CLI execution wrapper
    ├── local-llm-bridge-claude/  # Gemma 4 → Claude Code bridge
    ├── local-llm-bridge-copilot/ # Gemma 4 → Copilot CLI bridge
    ├── local-llm-bridge-agy/     # Gemma 4 → Antigravity CLI bridge
    ├── local-llm-bridge-codex/   # Gemma 4 → OpenAI-compatible CLI bridge
    ├── project-setup/            # Unifies project setups
    ├── maf-adapter/              # MAF adapter specifications & simulation
    └── agt-security/             # AGT sandboxing, HMAC controls
```

## Features

1. **Secure by Default**: Sub-agents default to `isolated=True` (no tool access). Tool execution requires explicit `--allow-tools` parameter validation.
2. **Path Traversal Protection**: Unified `path_security.py` checks target paths before passing to CLIs.
3. **Pre-flight Heartbeats**: Adapters perform model and authentication status health checks.
4. **Local LLM Bridge**: Routes all LLM traffic through a local Gemma 4 12B instance. Supports macOS Metal, Windows CUDA/Vulkan, and Linux CUDA/ROCm. See `agents/local-llm-setup.md`.
5. **KV Cache Orchestrator**: `kv_cache_orchestrator.py` eliminates cold prefill (~7–8 min) for repeated calls with the same system prompt via llama-server's slot save/restore REST API. SHA-256 keyed, 4 GiB budget. Proxy integration wired in `routing_proxy.py`. Eviction scoring inspired by [antirez/ds4](https://github.com/antirez/ds4) (`ds4_kvstore.c`) — credit to Salvador Sanfilippo.