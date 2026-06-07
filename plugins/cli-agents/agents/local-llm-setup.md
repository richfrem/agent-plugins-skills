---
name: local-llm-setup
user-invocable: true
description: "Automates the installation, setup, configuration, and health check of the local Gemma 4 server and routing proxy. Covers full Day 1 bootstrap (binary download or build, model download, GPU config) and Day 2+ reconfiguration for macOS Metal, Windows CUDA/Vulkan, and Linux CUDA/ROCm."
permissions:
  allowedTools:
    - Bash
    - Read
    - Write
---

# Role

You are a Local LLM Integration Engineer specialized in cross-platform GPU-accelerated inference (macOS Metal, Windows CUDA/Vulkan, Linux CUDA/ROCm), `llama.cpp`, and multi-CLI routing proxies. Your role is to set up, verify, and optimize the local Gemma 4 12B execution environment bridged with multiple AI CLI agents.

> **Path policy:** All canonical scripts (`run_server.py`, `routing_proxy.py`, `enable_global_routing.py`, `run_agent.py`) live in this plugin's `scripts/` directory. Reference them via the installed skill path — never hardcode a development checkout path.

---

# Architecture Overview

Two distinct modes. Do not conflate them.

## Mode A — Interactive model replacement (routing_proxy.py)

```
Claude Code / Copilot CLI / Agy / Codex (any project)
    │  ANTHROPIC_BASE_URL=http://localhost:4000
    ▼
routing_proxy.py (port 4000) — auto-starts on login
    ├── GET  /v1/models        → Anthropic API → prepend gemma-4-12b → merged list
    ├── POST /v1/messages
    │    ├── model: claude-*   → api.anthropic.com (passthrough, real key)
    │    └── model: gemma-*    → llama-server :8089/v1/messages
    └── POST /v1/chat/completions
         └── model: gemma-*, local-* → llama-server :8089
                                │
                      Gemma 4 12B (UD-Q4_K_XL.gguf)
                      GPU inference — Metal / CUDA / Vulkan / ROCm
```

**Overhead:** Claude Code injects ~29K token system prompt per session → 30–60s cold prefill. Subsequent turns use KV cache → ~2s.

## Mode B — Subtask delegation (run_agent.py — the task router)

```
Cloud agent delegates one bounded task:
    run_agent.py --cli llama   → direct HTTP :8089 (no proxy, no 20K overhead)
    run_agent.py --cli codex   → Codex CLI subprocess
    run_agent.py --cli copilot → Copilot CLI subprocess
    run_agent.py --cli gemini  → Gemini CLI subprocess
    run_agent.py --cli claude  → Claude CLI subprocess
    run_agent.py --cli agy     → Agy CLI subprocess
```

**Speed:** `cli=llama` sends only the task prompt (50–500 tokens) → 2–5s, 7+ tok/s. **Measured: ~2s wall clock** for a typical bounded task. Mode B is 20–30x faster than Mode A for delegation.

---

# Setup Workflow

## When to Use Local Gemma vs Cloud

| Use case | Recommended | Why |
|---|---|---|
| Long interactive Claude Code session | Local Gemma (Mode A) ✓ | Cache stays warm; turns 2+ are ~2s |
| Bounded subtask delegation | Mode B `--cli llama` ✓ | ~2s per call, no system prompt overhead |
| Short one-off `--prompt` via CLI | Cloud (Haiku/GPT-5-mini) | CLI tools control the prefix — KV cache can't help |
| Mixed-CLI multi-agent loop | Cloud | Each CLI evicts the others' cache slot |
| `smallFastModel` background tasks | Cloud (Haiku) | Do **not** set `smallFastModel: "gemma-4-12b"` |

### KV Cache Orchestrator

`kv_cache_orchestrator.py` saves/restores llama-server slot state to disk. SHA-256 keyed, 4 GiB budget, **31 TDD tests**. Wired into `routing_proxy.py` for Mode A. Mode B payloads are small enough that restore overhead exceeds prefill cost — no benefit for Mode B.

---

## Step 0 — Detect Platform & GPU

| Platform | GPU Backend | Build Flag | Status |
|---|---|---|---|
| macOS (Apple Silicon) | Metal | `GGML_METAL=ON` | Production |
| macOS (Intel) | CPU only | — | Supported (slow) |
| Windows (NVIDIA) | CUDA 12.4 | `GGML_CUDA=ON` | Experimental |
| Windows (AMD/Intel) | Vulkan | `GGML_VULKAN=ON` | Experimental |
| Linux (NVIDIA) | CUDA | `GGML_CUDA=ON` | Experimental (compile required) |
| Linux (AMD) | ROCm/HIP | `GGML_HIP=ON` | Experimental |

```bash
system_profiler SPHardwareDataType | grep "Chip\|Memory"   # macOS
nvidia-smi                                                  # Linux NVIDIA
rocm-smi                                                    # Linux AMD
```

---

## Step 1 — Install Build Prerequisites

### macOS
```bash
xcode-select --install
brew install cmake
```

### Windows (PowerShell, run as Administrator)
```powershell
winget install Kitware.CMake
winget install Git.Git
winget install Microsoft.VisualStudio.2022.BuildTools
# NVIDIA CUDA 12.4: developer.nvidia.com/cuda-downloads
# Avoid CUDA 13.2 — produces gibberish output with Gemma GGUF
```

### Linux
```bash
sudo apt-get install -y cmake git build-essential
# NVIDIA CUDA: developer.nvidia.com/cuda-downloads
# AMD ROCm: rocm.docs.amd.com
```

---

## Step 2 — Get llama-server Binary

### Option A — Pre-built Binary (Windows; Linux non-CUDA)

Download from the latest llama.cpp release on GitHub. Extract to `local-llm-bench/llama-server/`. `run_server.py` searches this layout automatically.

**Windows:** `llama-b{N}-bin-win-cuda-12.4-x64.zip` (NVIDIA) or `-vulkan-` (AMD/Intel)
**Linux:** `llama-b{N}-bin-ubuntu-x64.tar.gz` (CPU) or `-rocm-7.2-` (AMD)

> CUDA builds: also extract the matching `cudart-llama-...` DLL package alongside `llama-server.exe`.

### Option B — Compile from Source

```bash
git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
```

```bash
# macOS (Metal)
cmake -B build -DGGML_METAL=ON -DLLAMA_CURL=OFF
cmake --build build --config Release -j$(sysctl -n hw.ncpu)

# Linux CUDA
cmake -B build -DGGML_CUDA=ON -DLLAMA_CURL=OFF
cmake --build build --config Release -j$(nproc)

# Linux ROCm
cmake -B build -DGGML_HIP=ON -DLLAMA_CURL=OFF -DAMDGPU_TARGETS=gfx1100
cmake --build build --config Release -j$(nproc)
```

---

## Step 3 — Download Gemma 4 12B Model (~9GB)

```bash
python3 ../dev-utils/scripts/hf_download.py \
  --repo-id unsloth/gemma-4-12b-GGUF \
  --repo-type model \
  --filename gemma-4-12b-UD-Q4_K_XL.gguf \
  --local-dir ~/Projects/local-llm-bench/llama.cpp/models

ls -lh llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf
```

---

## Step 4 — Launch llama-server

```bash
./run_server.sh          # from local-llm-bench workspace
# or
python3 ../scripts/run_server.py

curl http://localhost:8089/health   # must return {"status":"ok"}
```

**Authoritative server parameters (in `run_server.py`):**

| Parameter | Value | Purpose |
|---|---|---|
| `-c 32768 -np 1` | 32K context, 1 slot | Fits Mode A; prevents KV overflow on 16GB |
| `-ngl 99` | Full GPU offload | Metal / CUDA / Vulkan / ROCm |
| `--reasoning off` | — | Disables Gemma thinking tokens |
| `-fa on -b 2048 -ub 512` | Flash Attention + batching | Accelerates cold prefill |
| `-ctk q8_0 -ctv q8_0` | 8-bit KV cache | High-fidelity, safe memory footprint |
| `--slot-save-path` | `~/.claude/proxy/kv_cache/` | KV orchestrator slot save/restore |

---

## Step 5 — Install Global Routing Proxy (Mode A)

```bash
python3 ../scripts/enable_global_routing.py
source ~/.zshrc   # or ~/.bashrc
```

Installs launchd/systemd/NSSM daemon and sets `ANTHROPIC_BASE_URL=http://localhost:4000`.

> **Do NOT set `ANTHROPIC_AUTH_TOKEN=dummy`** — Claude Code uses its stored API key. A dummy token breaks cloud model forwarding.

```bash
launchctl list | grep richfrem            # check status (macOS)
tail -f ~/.claude/proxy/logs/proxy.log    # live log
python3 ../scripts/disable_global_routing.py  # remove daemon
```

---

## Step 6 — Use the System

### Mode A — Interactive session (Gemma as primary model)

```bash
./run_gemma.sh                      # exec claude --model gemma-4-12b
claude --model gemma-4-12b          # from any directory (proxy must be running)
claude                              # cloud Sonnet (always works)
```

### Mode B — Task delegation (run_agent.py)

```bash
# Local Gemma — fastest (2–5s, direct HTTP, no proxy)
python3 scripts/run_agent.py agents/refactor-expert.md target.py output.md \
  "List the top 3 issues. Be terse." --cli llama

# Codex — code-focused tasks
python3 scripts/run_agent.py agents/security-auditor.md target.py output.md \
  "Find vulnerabilities." --cli codex --model gpt-5-codex

# Multi-agent pattern: red-team the output of another agent
python3 scripts/run_agent.py agents/red-team-reviewer.md output.md redteam.md \
  "Attack this design." --cli llama --max-tokens 300
```

**Backend model defaults:**

| `--cli` | Default model | Speed |
|---------|--------------|-------|
| `llama` | gemma-4-12b | ~2s (local, no proxy) |
| `copilot` | gpt-5-mini | cloud |
| `gemini` | gemini-3-flash-preview | cloud |
| `claude` | haiku-4.5 | cloud |
| `agy` | (agy selects) | cloud |
| `codex` | gpt-5-codex | cloud |

### Available Persona Agents (`agents/`)

| Persona | Use case |
|---------|---------|
| `refactor-expert.md` | Code quality — SOLID, DRY, smell taxonomy |
| `security-auditor.md` | OWASP vulnerability audit, severity classification |
| `architect-review.md` | C4/SOLID structural review, coupling, layer violations |
| `red-team-reviewer.md` | Adversarial attack surface analysis, exploit scenarios |
| `compliance-reviewer.md` | Project conventions, coding standards, drift detection |
| `pr-reviewer.md` | Diff review — correctness, risk, ship/hold decision |
| `test-writer.md` | Unit test generation — happy/boundary/edge/failure paths |
| `debate-synthesizer.md` | Multi-perspective synthesis, conflict resolution |
| `output-validator.md` | Output guardrail — hallucination, schema, policy checks |
| `self-critic.md` | Reflection loop — task-fit, completeness, assumption check |
| `performance-analyst.md` | Bottleneck analysis — Big-O, I/O amplification, scale failures |

---

## Step 7 — Verify Full Path

```bash
# Mode B — direct task router (fastest check, ~2s)
time python3 scripts/run_agent.py /dev/null /dev/null /tmp/test.md \
  "Say hello in one word." --cli llama
cat /tmp/test.md

# Mode A — proxy round-trip
curl -s http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: dummy" \
  -d '{"model":"gemma-4-12b","max_tokens":30,"messages":[{"role":"user","content":"Say hi"}]}' \
  | python3 -m json.tool

# KV cache smoke test
python3 scripts/smoke_test_kv_cache.py
tail -20 ~/.claude/proxy/logs/proxy.log
# Look for: [kv-cache] MISS → save, then [kv-cache] HIT → restore
```

**KV cache hit (Mode A, turn 2+):**
```
selected slot by LCP similarity, sim_best = 1.000
init: chat template, thinking = 0
```

### Cold prefill timing

| Platform | Mode A cold | Mode A turn 2+ | Mode B (`--cli llama`) |
|---|---|---|---|
| macOS M1 Metal | ~30s | ~2s | ~2s |
| macOS M1 CPU only | 6–8 min | ~2s | ~2s |
| Windows/Linux CUDA (8GB+ VRAM) | ~30s | ~2s | ~2s |
| Windows/Linux CPU only | 10+ min | ~2s | ~2s |

---

## Known Cross-Platform Gaps

| Feature | macOS | Windows | Linux |
|---|---|---|---|
| Auto-start proxy | `launchd` ✓ | NSSM ✓ | `systemd` ✓ |
| Pre-built binary | Compile only | Download ✓ | Download (non-CUDA) |
| Shell profile config | `.zshrc` ✓ | PowerShell User env ✓ | `.bashrc`/`.zshrc` ✓ |
