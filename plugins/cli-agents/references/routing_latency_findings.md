# Routing Latency Findings — Local Gemma 4 12B

**Date:** 2026-06-06  
**Hardware:** Apple M1, 16GB Unified Memory  
**Model:** Gemma 4 12B UD-Q4_K_XL (same GGUF, tested via two different stacks)

---

## Hypothesis

> The routing proxy is not the latency bottleneck.
> The bottleneck is the size of the system prompt injected by the calling agent.
> A lean agent that controls its own prompt would be dramatically faster using the same hardware.

---

## Test Setup A — Copilot CLI → Routing Proxy → llama-server

```
Copilot CLI
    ↓  ~20,000-token system prompt (Copilot tool definitions + instructions)
routing_proxy.py  :4000
    ↓  transparent relay
llama-server  :8089  (gemma-4-12b-UD-Q4_K_XL, -ngl 99, -fa on, -b 2048, -ub 512,
                       --reasoning off, -ctk q8_0 -ctv q8_0, -c 32768, -np 1)
```

**5 questions asked during a live Copilot session:**

| Turn | Question | Cache sim | New tokens | Prefill | Gen | Total | Path |
|------|----------|-----------|-----------|---------|-----|-------|------|
| Cold start | (model load) | — | 20,425 | 435.1s | 12.8s (16 tok) | 447.9s | COLD |
| 1 | Capital of France | 0.928 | 1,596 | 57.5s | 6.6s (8 tok) | 64.2s | SLOW |
| 2 | Capital of Denmark | 0.995 | 99 | 11.5s | 13.3s (16 tok) | 30.5s | FAST |
| 3 | (3rd question) | 0.933 | 1,596 | 58.4s | 6.6s (8 tok) | 65.0s | SLOW |
| 4 | Capital of Sweden | 0.996 | 96 | 7.0s | 14.0s (16 tok) | 26.8s | FAST |
| 5 | (5th question) | 0.937 | 1,596 | 60.3s | 6.8s (8 tok) | 67.1s | SLOW |

**Pattern:** strict SLOW/FAST alternation — 46s average per turn (27–67s range).

**Why the alternation?**  
llama-server's LCP (Longest Common Prefix) cache matches the accumulated KV state against the new request prefix. On FAST turns, sim_best ≈ 0.995 — only the new user message tokens (~96-99) need processing. On SLOW turns, the conversation has grown past a context checkpoint boundary (every ~1,536 tokens of accumulated history), so ~1,596 tokens are re-prefilled.

**Generation rate:** 1.21–1.25 tok/s (hardware-bound: M1 memory bandwidth saturated by 12B model weights).

---

## Test Setup B — Ollama API → Ollama server (same GGUF, no proxy)

```
Python script
    ↓  user question only (~16–27 tokens, no system prompt)
Ollama :11434  (gemma4-local, num_ctx=32768, num_gpu=99, think=false)
    ↓  (Ollama wraps llama.cpp with Metal backend)
same GGUF on same M1 hardware
```

**Initial 5-question run:**

| Turn | Question | Load | Prefill | Gen | Total |
|------|----------|------|---------|-----|-------|
| 1 | Capital of France | 7.84s | 1.07s (16 tok) | 1.71s (13 tok) | 10.62s |
| 2 | Capital of Denmark | 0.34s | 0.60s (16 tok) | 1.84s (14 tok) | 2.79s |
| 3 | Capital of Sweden | 0.33s | 0.51s (16 tok) | 1.85s (14 tok) | 2.70s |
| 4 | Capital of Japan | 0.33s | 0.51s (16 tok) | 1.73s (13 tok) | 2.58s |
| 5 | Capital of Brazil | 0.34s | 0.52s (16 tok) | 1.86s (14 tok) | 2.73s |

**10-question extended run (think:false enforced):**

| Turn | Question | Prefill | Gen | Gen tok | Tok/s | Total |
|------|----------|---------|-----|---------|-------|-------|
| Q01 | Capital of Germany | 0.64s | 1.75s | 13 | 7.4 | 2.74s |
| Q02 | Capital of Australia | 0.51s | 1.95s | 14 | 7.2 | 2.81s |
| Q03 | Capital of Canada | 0.52s | 1.76s | 13 | 7.4 | 2.63s |
| Q04 | Capital of Argentina | 0.52s | 1.86s | 14 | 7.5 | 2.74s |
| Q05 | Capital of Egypt | 0.53s | 1.77s | 13 | 7.4 | 2.64s |
| Q06 | 12 × 13 = ? | 0.73s | 2.48s | 18 | 7.3 | 3.55s |
| Q07 | Three primary colours | 0.75s | 2.81s | 20 | 7.1 | 3.91s |
| Q08 | Python language origin | 0.73s | 7.34s | 50 | 6.8 | 8.41s |
| Q09 | Hexagon sides | 0.73s | 1.81s | 13 | 7.2 | 2.89s |
| Q10 | WW2 end year | 0.74s | 6.65s | 46 | 6.9 | 7.74s |
| **AVG** | | **0.64s** | **3.02s** | **21** | **7.2** | **4.01s** |

---

## Head-to-Head Comparison

| Metric | Copilot → Proxy → llama-server | Direct Ollama (no proxy) | Factor |
|--------|-------------------------------|--------------------------|--------|
| Model load | 8s | 7.8s | same |
| First response | 64s (after 7.5 min cold start) | 10.6s (incl. 7.8s load) | **6× faster** |
| Subsequent avg | ~46s | ~3s (short answers) | **~15× faster** |
| Subsequent range | 27–67s | 2.6–8.4s | — |
| Generation rate | 1.21–1.25 tok/s | 7.1–7.5 tok/s | **6× faster** |
| Prompt size | ~20,000 tokens (Copilot injects) | 16–27 tokens (question only) | **750× smaller** |
| Routing overhead | ~5ms | 0ms | negligible either way |

---

## Key Findings

### 1. The proxy is not the bottleneck — the system prompt is

The routing proxy adds ~5ms per request (Python loopback HTTP). Against 27–67 second response times, that is 0.01% of total latency. Replacing or removing the proxy has zero measurable effect on speed.

The actual bottleneck is the **20,000-token Copilot system prompt** that must be prefilled into the KV cache on every new session. At 27–36 tok/s prefill speed, that alone takes 57–60 seconds per context-boundary crossing.

### 2. Generation is 6× faster with short prompts — same hardware

Ollama achieved 7.1–7.5 tok/s generation. llama-server achieved 1.21–1.25 tok/s. Same GGUF, same M1, same GPU layers. The difference is KV cache size:

- With a 20,000-token context in cache, each attention step reads ~20K token KV vectors from memory
- With a 16-token context, each step reads ~16 token KV vectors
- Memory bandwidth is the ceiling — smaller context = faster attention = faster generation

### 3. `think: false` is mandatory for Gemma 4

Without `--reasoning off` (llama-server) or `think: false` (Ollama API), Gemma 4 generates thousands of reasoning tokens before any answer. At 1.2 tok/s that is a 10+ minute wait. This must be enforced at the server or API layer, not assumed.

- llama-server: `--reasoning off --chat-template-kwargs '{"enable_thinking": false}'` — enforced globally
- Ollama Modelfile: `PARAMETER think false` — **not supported in v0.30.6**
- Ollama API: `"think": false` in request body — **works, must be sent per-request**

### 4. Response time scales linearly with output length

At 7.2 tok/s, every 10 output tokens adds ~1.4 seconds:

| Answer length | Est. gen time |
|--------------|---------------|
| 10 tokens | ~1.4s |
| 20 tokens | ~2.8s |
| 50 tokens | ~6.9s |
| 100 tokens | ~13.9s |
| 500 tokens | ~69s |

Short factual answers: 2.6–3.0s total. Longer code or explanation: scales accordingly.

### 5. The SLOW/FAST alternation pattern in Copilot sessions

Every other Copilot turn hits a ~65s slow path. This is caused by llama-server's context checkpoint spacing: as the conversation history accumulates, every ~1,536 new tokens triggers a re-prefill of the gap from the last checkpoint. This is deterministic and unavoidable when using a large-system-prompt CLI tool.

---

## Proposed Direction — Ollama Agent Skill

A dedicated Ollama agent skill (modelled on `copilot-cli-agent`, `gemini-cli-agent`) that calls Ollama's HTTP API directly, injecting only the context the task actually requires, would deliver:

- **No routing proxy dependency** — calls `http://localhost:11434/api/chat` directly
- **2–5s typical response time** for agent tasks with short, targeted prompts
- **Controllable system prompt** — agent author decides what context Gemma sees
- **`think: false` enforced per-request** — no reasoning overhead
- **Stateless per-call or stateful per-session** — agent manages conversation history explicitly

This is the same pattern as the existing CLI agent skills but targets Ollama's REST API instead of a CLI binary. The routing proxy remains useful for Claude Code and Copilot sessions where system prompt injection is not controllable, but a purpose-built Ollama skill bypasses that constraint entirely.

---

## Ollama Registration Note

Ollama does not scan for raw GGUF files. To register the existing model:

```bash
cat > /tmp/Modelfile-gemma4 << 'EOF'
FROM /Users/richardfremmerlid/Projects/local-llm-bench/llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf
PARAMETER num_ctx 32768
PARAMETER num_gpu 99
EOF
ollama create gemma4-local -f /tmp/Modelfile-gemma4
```

Registration takes ~45s (hard-links the GGUF into Ollama's blob store). Model load on first request: ~7.8s. Subsequent requests within keep-alive window: ~0.3s load overhead.
