---
name: local-llm-setup
model: gemini-2.5-flash
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

> **Path policy:** All canonical scripts (`run_server.py`, `routing_proxy.py`, `enable_global_routing.py`, launchers) live in this plugin's `scripts/` directory. When installed via the Claude marketplace, they are available as symlinks in each skill directory. Reference them via the installed skill path (e.g., `../scripts/run_server.py` relative to the skill root) — never hardcode a development checkout path.

---

# Architecture Overview

```
Claude Code / Copilot CLI / Antigravity / Codex (any project)
    │  ANTHROPIC_BASE_URL=http://localhost:4000
    ▼
Routing Proxy (Python, port 4000) — auto-starts on login
    ├── GET  /v1/models        → Anthropic API → prepend gemma-4-12b → merged list
    ├── POST /v1/messages
    │    ├── model: claude-*   → api.anthropic.com (passthrough, real key)
    │    └── model: gemma-*    → llama-server :8089/v1/messages (strips thinking + temperature)
    └── POST /v1/chat/completions
         └── model: gemma-*, local-*, claude-local → llama-server :8089/v1/chat/completions
                                        │
                              Gemma 4 12B (UD-Q4_K_XL.gguf)
                              GPU inference via platform backend
```

---

# Setup Workflow

## When to Use Local Gemma vs Cloud

Understanding the KV cache behaviour is critical before choosing this for any workflow.

### How the cache actually works

`--cache-ram` (enabled by default, 2048 MiB in `run_server.py`) keeps idle slot KV state in host RAM. When the next request arrives with a matching prefix, it restores from RAM instead of re-prefilling. This is **not** the active GPU KV cache — it's a separate host-memory prompt cache layered on top.

The KV cache survives across HTTP requests within the same `llama-server` process lifetime. With `-np 1` (one slot), only one system prompt prefix is cached at a time.

### The CLI wrapper problem (why delegation doesn't work)

CLI tools (Claude Code, Copilot, Agy) each inject their own system prompt per process invocation — often including dynamic content like repo file maps, session IDs, or git status. This means every fresh CLI process sends a different prefix that busts the cache, even though `llama-server` never restarted.

**Confirmed by testing**: `copilot --prompt "..."` takes the same 7–8 minutes on the second call as the first — the CLI tool controls the prefix, so you can't stabilize it for cache reuse.

The community is explicit: *"No one has a clean solution for the CLI wrapper problem. The workarounds all assume you control the prompt."*

### Use case decision table

| Use case | Recommended | Why |
|---|---|---|
| Long interactive Claude Code session | Local Gemma ✓ | Cache stays warm; turns 2+ are ~2s |
| Long interactive Copilot session | Local Gemma ✓ | Same — session prefix fixed once |
| Short one-off `--prompt` delegation | Cloud (Haiku/GPT-5-mini) | Cold prefill every call; CLI controls prefix |
| Mixed-CLI multi-agent loop | Cloud | Each CLI evicts the others' cache slot |
| `smallFastModel` background tasks | Cloud (Haiku) | Do **not** set `smallFastModel: "gemma-4-12b"` |
| Direct API calls with stable system prompt | Local Gemma ✓ | You control the prefix; warmup once, fast after |

### Cold prefill timing with GPU

| System prompt size | First request | Subsequent (same session) |
|---|---|---|
| Claude Code (~29K tokens) | ~2–4 min | ~2 seconds |
| Copilot CLI (~18K tokens) | ~4–8 min | ~2 seconds |
| Direct API with fixed prompt | Pay once, then instant | ~2 seconds |

### Disk-based KV cache: slot save/restore

> **`kv_cache_orchestrator.py` (in `scripts/`) automates this pattern** — SHA-256 hashes system messages, checks for a saved `.bin` file, calls `/slots/0/restore` before forwarding, and `/slots/0/save` in a background thread after the stream. 20 TDD tests. Proxy integration is wired in `routing_proxy.py`.

`run_server.py` now starts llama-server with `--slot-save-path ~/.claude/proxy/kv_cache/`. This enables REST API endpoints for persisting KV state across server restarts:

```bash
# Save slot 0's KV state to disk after warmup
curl -X POST http://localhost:8089/slots/0/save \
  -H "Content-Type: application/json" \
  -d '{"filename": "/path/to/kv_cache/my_prompt.bin"}'

# Restore it instantly before the next delegation call
curl -X POST http://localhost:8089/slots/0/restore \
  -H "Content-Type: application/json" \
  -d '{"filename": "/path/to/kv_cache/my_prompt.bin"}'
```

Restoring is nearly instant vs minutes of re-prefill. The saved files are binary KV snapshots (hundreds of MB for long contexts).

### Warmup pattern for direct API delegation

For workflows where **you** control the system prompt (direct API calls, not CLI wrappers), warm the cache once after server boot:

```bash
curl -s http://localhost:8089/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-12b",
    "messages": [
      {"role": "system", "content": "YOUR_FIXED_DELEGATION_PROMPT_HERE"},
      {"role": "user", "content": "warmup"}
    ],
    "max_tokens": 1
  }'
# Then save the slot:
curl -X POST http://localhost:8089/slots/0/save \
  -d '{"filename": "/Users/$(whoami)/.claude/proxy/kv_cache/delegation.bin"}'
```

All subsequent direct API calls with the same system prompt prefix skip prefill entirely.

---

## Step 0 — Detect Platform & GPU

Identify the host platform and available GPU backend:

| Platform | GPU Backend | Build Flag | Status |
|---|---|---|---|
| macOS (Apple Silicon) | Metal | `GGML_METAL=ON` | Production |
| macOS (Intel) | CPU only | — | Supported (slow) |
| Windows (NVIDIA) | CUDA | `GGML_CUDA=ON` | Experimental |
| Windows (AMD/Intel) | Vulkan | `GGML_VULKAN=ON` | Experimental |
| Linux (NVIDIA) | CUDA | `GGML_CUDA=ON` | Experimental (must compile) |
| Linux (AMD) | ROCm/HIP | `GGML_HIP=ON` | Experimental |

```bash
# macOS
system_profiler SPHardwareDataType | grep "Chip\|Memory"

# Windows (PowerShell)
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM

# Linux
nvidia-smi    # NVIDIA
rocm-smi      # AMD ROCm
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
# NVIDIA CUDA: https://developer.nvidia.com/cuda-downloads (use 12.4, avoid 13.2 — produces gibberish output)
# Visual Studio 2022 Build Tools with "Desktop development with C++" + "C++ CMake Tools for Windows"
winget install Microsoft.VisualStudio.2022.BuildTools
```

### Linux
```bash
sudo apt-get install -y cmake git build-essential   # Debian/Ubuntu
sudo dnf install -y cmake git gcc-c++               # Fedora/RHEL
# NVIDIA CUDA: https://developer.nvidia.com/cuda-downloads
# AMD ROCm: https://rocm.docs.amd.com/en/latest/deploy/linux/
```

---

## Step 2 — Get llama-server Binary

### Option A — Pre-built Binary (Recommended for Windows; also available for Linux)

Download from: **https://github.com/ggml-org/llama.cpp/releases** (latest build, e.g. `b9542`)

**Windows asset names:**

| Asset | GPU Backend |
|---|---|
| `llama-b{N}-bin-win-cuda-12.4-x64.zip` | NVIDIA CUDA 12.4 ✓ |
| `llama-b{N}-bin-win-vulkan-x64.zip` | AMD/Intel Vulkan |
| `llama-b{N}-bin-win-x64.zip` | CPU only |
| `llama-b{N}-bin-win-hip-x64.zip` | AMD ROCm |

For CUDA builds, also download and extract the matching CUDA runtime package:
`cudart-llama-bin-win-cuda-12.4-x64.zip` (copy DLLs alongside `llama-server.exe`)

> **CUDA 13.2 warning:** Avoid CUDA 13.2 specifically — it produces gibberish output with current Gemma GGUF models. CUDA 12.4 is the confirmed safe version.

**Linux asset names:**

| Asset | GPU Backend |
|---|---|
| `llama-b{N}-bin-ubuntu-x64.tar.gz` | CPU |
| `llama-b{N}-bin-ubuntu-vulkan-x64.tar.gz` | Vulkan |
| `llama-b{N}-bin-ubuntu-rocm-7.2-x64.tar.gz` | AMD ROCm |

> **Linux CUDA:** No pre-built binary — must compile from source (Step 2B below).

**Extract to your workspace:**
```
local-llm-bench/
└── llama-server/
    ├── llama-server.exe   (Windows)
    └── llama-server       (Linux)
```

`run_server.py` searches this layout automatically.

---

### Option B — Compile from Source (macOS required; Linux CUDA required; Windows optional)

Clone into the `local-llm-bench` workspace:
```bash
cd ~/Projects/local-llm-bench   # macOS/Linux
git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
```

**macOS (Apple Silicon — Metal):**
```bash
cmake -B build -DGGML_METAL=ON -DLLAMA_CURL=OFF
cmake --build build --config Release -j$(sysctl -n hw.ncpu)
```

**Windows — NVIDIA CUDA** (from Developer Command Prompt for VS 2022):
```powershell
cmake -B build -DGGML_CUDA=ON -DBUILD_SHARED_LIBS=OFF
cmake --build build --config Release -j $env:NUMBER_OF_PROCESSORS
# Binary: build\bin\Release\llama-server.exe
```
> DLL fix: copy `cudart64_12.dll`, `cublas64_12.dll`, `cublasLt64_12.dll` from CUDA bin dir into the same folder as `llama-server.exe` if CUDA DLLs aren't found at runtime.

**Windows — Vulkan:**
```powershell
cmake -B build -DGGML_VULKAN=ON -DLLAMA_CURL=OFF
cmake --build build --config Release
```

**Linux — NVIDIA CUDA:**
```bash
cmake -B build -DGGML_CUDA=ON -DLLAMA_CURL=OFF
cmake --build build --config Release -j$(nproc)
```

**Linux — AMD ROCm:**
```bash
cmake -B build -DGGML_HIP=ON -DLLAMA_CURL=OFF -DAMDGPU_TARGETS=gfx1100
cmake --build build --config Release -j$(nproc)
```

Verify:
```bash
ls llama.cpp/build/bin/llama-server         # macOS/Linux compiled
ls llama-server/llama-server.exe             # Windows pre-built
```

---

## Step 3 — Download Gemma 4 12B Model

Use the `hf_download.py` script from the `dev-utils` plugin (locate it in the installed skill or scripts directory):

```bash
# macOS/Linux — adjust path to where dev-utils plugin is installed
python3 ../dev-utils/scripts/hf_download.py \
  --repo-id unsloth/gemma-4-12b-GGUF \
  --repo-type model \
  --filename gemma-4-12b-UD-Q4_K_XL.gguf \
  --local-dir ~/Projects/local-llm-bench/llama.cpp/models

# Windows (PowerShell)
python ..\dev-utils\scripts\hf_download.py `
  --repo-id unsloth/gemma-4-12b-GGUF `
  --repo-type model `
  --filename gemma-4-12b-UD-Q4_K_XL.gguf `
  --local-dir $env:USERPROFILE\Projects\local-llm-bench\llama.cpp\models
```

Confirm (~9GB):
```bash
ls -lh llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf   # macOS/Linux
dir llama.cpp\models\gemma-4-12b-UD-Q4_K_XL.gguf       # Windows
```

---

## Step 4 — Interactive Discovery (Target CLI Selection)

Ask the user which CLI target(s) to configure. Multiple can be active simultaneously — the proxy handles all routing.

| Target | Skill | Status |
|---|---|---|
| Claude Code | `local-llm-bridge-claude` | Production |
| GitHub Copilot CLI | `local-llm-bridge-copilot` | Experimental |
| Antigravity (Agy) | `local-llm-bridge-agy` | Experimental |
| Codex / Aider / Goose | `local-llm-bridge-codex` | Production |

---

## Step 5 — Launch llama-server

Run `run_server.py` from the installed `scripts/` directory. It auto-detects the binary (pre-built or compiled), model file, and thread count for the current platform:

```bash
# macOS/Linux (from skill or scripts directory)
python3 ../scripts/run_server.py

# Windows
python ..\scripts\run_server.py

# Via bench repo wrapper (macOS/Linux only)
cd ~/Projects/local-llm-bench && ./run_server.sh
```

**Server parameters applied by `run_server.py`:**

| Parameter | Value | Purpose |
|---|---|---|
| `-c 32768` | 32K context | Accommodates Claude Code's ~29K token system prompt |
| `-np 1` | 1 slot | Prevents KV cache memory overflow on 16GB RAM |
| `-ngl 99` | 99 GPU layers | Full GPU offload (Metal / CUDA / Vulkan / ROCm) |
| `--reasoning off` | — | Disables Gemma thinking tokens (prevents 10+ min waits) |
| `-fa on` | Flash Attention | Accelerates prefill of large system prompts |
| `-b 2048 -ub 512` | Batch sizes | Optimized prefill throughput |
| `-t auto` | Platform-detected | M1=4 perf cores; Windows/Linux=physical_cores÷2 |
| `-ctk q8_0 -ctv q8_0` | 8-bit KV cache | High-fidelity cache with safe memory footprint |
| `--chat-template-kwargs '{"enable_thinking": false}'` | — | Prevents thinking block injection via Jinja template |

Verify health:
```bash
curl http://localhost:8089/health
```
Expected: `{"status":"ok"}`

---

## Step 6 — Initialize Global Routing Proxy

Check if already running:
```bash
# macOS/Linux
lsof -i :4000

# Windows (PowerShell)
netstat -ano | findstr :4000
```

Enable and auto-start:

### macOS (launchd — production)
```bash
python3 ../scripts/enable_global_routing.py
source ~/.zshrc
```

### Windows — NSSM (recommended over Task Scheduler)

NSSM provides auto-restart on crash and structured logging — Task Scheduler does not.

```powershell
# Download nssm.exe (single .exe, no installer) from https://nssm.cc/download
# Then register the proxy as a Windows service:
nssm install LlamaProxy "C:\Python312\python.exe" "-u" "C:\path\to\scripts\routing_proxy.py"
nssm set LlamaProxy AppDirectory "C:\path\to\scripts"
nssm set LlamaProxy AppStdout "C:\Users\%USERNAME%\.claude\proxy\logs\proxy.log"
nssm set LlamaProxy AppStderr "C:\Users\%USERNAME%\.claude\proxy\logs\proxy.error.log"
nssm set LlamaProxy Start SERVICE_AUTO_START
nssm start LlamaProxy
```

### Linux — systemd (automated via `enable_global_routing.py`)
```bash
python3 ../scripts/enable_global_routing.py
source ~/.bashrc  # or ~/.zshrc
```

**Shell environment (all platforms):**
```bash
# macOS/Linux — add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_BASE_URL=http://localhost:4000

# Windows — permanent (PowerShell)
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "http://localhost:4000", "User")
```

> **Do NOT set `ANTHROPIC_AUTH_TOKEN=dummy`** — Claude Code uses its stored API key. A dummy token breaks cloud model forwarding.

---

## Step 7 — Target-Specific Configuration

### Claude Code
Patch `~/.claude/settings.json` to prevent telemetry headers from invalidating the KV cache:
```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "DISABLE_TELEMETRY": "1"
  }
}
```
Verify `CLAUDE_CODE_MAX_CONTEXT=32768` in session env.
Launch: `python3 ../scripts/run_claude.py`

### GitHub Copilot CLI (Experimental)
`run_copilot.py` injects: `COPILOT_OFFLINE=true`, `COPILOT_PROVIDER_TYPE=openai`, `COPILOT_PROVIDER_BASE_URL=http://localhost:4000/v1`, `COPILOT_MODEL=gemma-4-12b`
```bash
python3 ../scripts/run_copilot.py --diagnose   # verify env/binary first
python3 ../scripts/run_copilot.py
```

### Antigravity — Agy (Experimental)
`run_agy.py` idempotently patches `~/.config/antigravity/config.toml`:
```toml
[[models]]
name = "Gemma 4 Local"
model = "gemma-4-12b"
base_url = "http://localhost:4000/v1"
env_key = "LOCAL_PASSTHROUGH"
```
Launch: `python3 ../scripts/run_agy.py`

### Generic OpenAI — Codex / Aider / Goose
`run_codex.py` injects: `OPENAI_BASE_URL=http://localhost:4000/v1`, `OPENAI_API_KEY=dummy`, `OPENAI_MODEL=gemma-4-12b`
```bash
python3 ../scripts/run_codex.py aider --model openai/gemma-4-12b
```

---

## Step 8 — Verify Full Path

```bash
curl -s http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: dummy" \
  -d '{"model":"gemma-4-12b","max_tokens":30,"messages":[{"role":"user","content":"Say hi"}]}' \
  | python3 -m json.tool
```
Expected: Anthropic-format JSON with Gemma's response.
503 = llama-server offline. Run `run_server.py` first.

**KV cache hit confirmation (in llama-server logs after 2nd+ query):**
```
selected slot by LCP similarity, sim_best = 1.000
init: chat template, thinking = 0
```

### Cold prefill timing

| Platform | First query (cold prefill) | Subsequent queries |
|---|---|---|
| macOS M1 — Metal | Under 30 seconds | Under 2 seconds |
| macOS M1 — CPU only | 6–8 minutes | Under 2 seconds |
| Windows/Linux — CUDA/Vulkan (8GB+ VRAM) | Under 30 seconds | Under 2 seconds |
| Windows/Linux — CPU only | 10+ minutes | Under 2 seconds |

> Do not cancel during cold prefill — the server is processing the ~29K token Claude Code system prompt. Once done, the KV cache is saved and all subsequent turns are near-instant.

---

## Known Cross-Platform Gaps

| Feature | macOS | Windows | Linux |
|---|---|---|---|
| Auto-start proxy on login | `launchd` ✓ | NSSM ✓ (via `enable_global_routing.py`) | `systemd` ✓ (via `enable_global_routing.py`) |
| Port conflict detection | `lsof` ✓ | `netstat` ✓ (in `run_server.py`) | `lsof` ✓ |
| Pre-built binary | Compile only | Download ✓ (recommended) | Download (non-CUDA) |
| Shell profile auto-config | `.zshrc` ✓ | PowerShell User env var ✓ | `.bashrc` / `.zshrc` ✓ |
| `enable_global_routing.py` | launchd ✓ | NSSM service ✓ | systemd user service ✓ |
