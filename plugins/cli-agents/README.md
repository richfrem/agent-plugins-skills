# cli-agents

Multi-LLM Task Router Suite. `run_agent.py` dispatches bounded tasks to six backends: Claude CLI, GitHub Copilot, Gemini CLI, Antigravity (Agy), Codex/OpenAI-compatible, and a direct-HTTP local Gemma 4 12B bridge. Also maintains the API Compatibility Proxy — a global routing proxy that lets interactive CLI tools treat a local llama-server as a drop-in Anthropic/OpenAI endpoint (Mode A model replacement).

## Architecture: Two Modes

```
Mode A — Interactive model replacement (routing_proxy.py)
  Claude Code / Copilot / Agy / Codex → ANTHROPIC_BASE_URL=:4000
  → routing_proxy → llama-server :8089 (Gemma 4 12B)

Mode B — Task delegation (run_agent.py — the task router)
  Primary agent → run_agent.py cli=<backend>
  ├── cli=llama   → http://localhost:8089/v1/chat/completions  (direct, 2–5s)
  ├── cli=copilot → GitHub Copilot CLI subprocess
  ├── cli=gemini  → Gemini CLI subprocess
  ├── cli=claude  → Claude CLI subprocess
  ├── cli=agy     → Antigravity CLI subprocess
  └── cli=codex   → Codex/OpenAI-compatible CLI subprocess
```

## Plugin Structure

```
cli-agents/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── README.md                     # This file
├── agents/
│   ├── refactor-expert.md
│   ├── security-auditor.md
│   ├── architect-review.md
│   └── local-llm-setup.md        # Cross-platform local LLM setup agent
├── references/
│   ├── local_llm_debrief.md      # Technical history: optimization battles + architecture
│   ├── routing_latency_findings.md # Measured timing data: Mode A vs Mode B comparison
│   └── routing-proxy.mmd         # Sequence diagram: full routing flow
├── scripts/
│   ├── run_agent.py              # Task router — 6 backends, argparse v2, isolated security contract
│   ├── test_run_agent.py         # 37 tests: command builders, isolated-flag contract, llama payload
│   ├── test_routing_proxy.py     # 8 tests: _extract_cache_key empty-system collision guard
│   ├── conductor.py              # Unified execution conductor
│   ├── path_security.py          # Path boundary assertions
│   ├── test_harness.py           # MAF adapter test simulator
│   ├── agt_ops.py                # AGT sandbox & key validator
│   ├── routing_proxy.py          # API compatibility proxy (port 4000) — Mode A only
│   ├── run_server.py             # llama-server launcher (cross-platform, authoritative params)
│   ├── enable_global_routing.py  # Install proxy daemon (launchd/NSSM/systemd)
│   ├── disable_global_routing.py # Remove proxy daemon (cross-platform)
│   ├── kv_cache_orchestrator.py  # KV slot save/restore middleware (ds4-inspired, stdlib only)
│   ├── test_kv_cache.py          # 31 TDD tests for kv_cache_orchestrator
│   ├── smoke_test_kv_cache.py    # End-to-end smoke test: timing + MISS/HIT log check
│   └── adapters/                 # Lightweight provider CLI adapters
│       ├── claude_adapter.py
│       ├── copilot_adapter.py
│       └── gemini_adapter.py
└── skills/
    ├── claude-cli-agent/         # cli=claude backend — Claude CLI task delegation
    ├── copilot-cli-agent/        # cli=copilot backend — Copilot CLI task delegation
    ├── gemini-cli-agent/         # cli=gemini backend — Gemini CLI task delegation
    ├── agy-cli-agent/            # cli=agy backend — Antigravity CLI task delegation
    ├── codex-cli-agent/          # cli=codex backend — Codex/OpenAI-compatible task delegation
    ├── local-llm-bridge/         # cli=llama backend — direct Gemma 4 12B, no proxy, 2–5s
    ├── project-setup/            # Unifies project setups
    ├── maf-adapter/              # MAF adapter specifications & simulation
    └── agt-security/             # AGT sandboxing, HMAC controls
```

## Features

1. **Multi-LLM Task Router**: `run_agent.py` routes one bounded task to one selected backend. Named-flag interface (`--cli`, `--model`, `--max-tokens`, `--isolated`) + legacy positional compat. 37 TDD tests covering command builders, isolated-flag security contract, and llama HTTP payload. 76 total tests across 3 test files.
2. **Local Gemma Direct Bridge**: `cli=llama` POSTs a lean prompt directly to `http://localhost:8089/v1/chat/completions`. No proxy, no 20K system prompt overhead. Measured: 2–5s typical vs 46s average through Mode A with a 20K prompt.
3. **API Compatibility Proxy**: `routing_proxy.py` (port 4000) routes `claude-*` → Anthropic API, `gemma-*` → llama-server. Used for Mode A interactive sessions only — not for task delegation.
4. **KV Cache Orchestrator**: `kv_cache_orchestrator.py` eliminates cold prefill for repeated calls with the same system prompt via llama-server's slot save/restore REST API. SHA-256 keyed, 4 GiB budget. 31 TDD tests. Proxy integration wired. Eviction scoring inspired by [antirez/ds4](https://github.com/antirez/ds4) — credit to Salvador Sanfilippo.
5. **Secure by Default**: Sub-agents default to isolated execution (no tool access). Tool execution requires explicit validation.
6. **Path Traversal Protection**: `path_security.py` checks target paths before passing to CLIs.

## Testing & Benchmarking

### Unit tests (no server required)

```bash
cd plugins/cli-agents/scripts

python3 -m pytest test_run_agent.py -v        # 37 tests — command builders + isolated security contract
python3 -m pytest test_kv_cache.py -v         # 31 tests — KV cache orchestrator
python3 -m pytest test_routing_proxy.py -v    # 8 tests  — cache collision guard

# All at once — expect 76 passing
python3 -m pytest test_run_agent.py test_kv_cache.py test_routing_proxy.py -v
```

### Start llama-server (required for live tests)

```bash
# In a dedicated terminal — from local-llm-bench workspace
./run_server.sh
curl http://localhost:8089/health    # must return {"status":"ok"}
```

### Mode B — task delegation speed test (the fast path)

```bash
time python3 plugins/cli-agents/scripts/run_agent.py \
  /dev/null /dev/null /tmp/test_b.md \
  "List three capital cities. Be terse." \
  --cli llama
cat /tmp/test_b.md
```

**Measured result: ~2s wall clock, 7+ tok/s.** Example output:

```
Paris, Tokyo, Ottawa.
[run_agent] llama complete → /tmp/test_b.md
python3 ... --cli llama  0.06s user 0.03s system 4% cpu 1.977 total
```

### Mode A — interactive proxy comparison (the slow path)

```bash
# Proxy must be running: launchctl list | grep richfrem
time claude --model gemma-4-12b -p "List three capital cities. Be terse."
```

**Typical result: 40–60s cold** (29K token system prompt prefill at ~30 tok/s), then ~5–10s generation.

**Why Mode B is ~20–30x faster:** Mode A injects Claude Code's full 29K-token system prompt on every request. Mode B sends only the task — typically 50–500 tokens. Same hardware, same GGUF. Context size is the bottleneck.

### KV cache smoke test (proxy + orchestrator)

```bash
python3 plugins/cli-agents/scripts/smoke_test_kv_cache.py
tail -20 ~/.claude/proxy/logs/proxy.log
# First call: [kv-cache] MISS → save
# Second call: [kv-cache] HIT → restore (skips prefill)
```
