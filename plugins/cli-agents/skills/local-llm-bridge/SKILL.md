---
name: local-llm-bridge
plugin: cli-agents
description: >
  Local Gemma 4 12B sub-agent. Routes bounded tasks directly to the optimized llama-server
  at localhost:8089 — no routing proxy, no cloud API, 2–5s typical response.
  Use for fast, private, cost-free subtask delegation from any cloud primary agent.
  Part of the run_agent.py multi-LLM task router — cli=llama target.
allowed-tools: Bash, Read, Write
---

## Identity: The Local Gemma Sub-Agent Dispatcher

Dispatches bounded tasks directly to the optimized local Gemma 4 12B server at `http://localhost:8089/v1/chat/completions`. No routing proxy involved. Uses the `run_agent.py` task router with `cli=llama`.

> [!IMPORTANT]
> **Requires llama-server running on port 8089.** Check: `curl http://localhost:8089/health`
> Start: `./run_server.sh` in the local-llm-bench workspace.
> Thinking is disabled server-side (`--reasoning off`) — no special flags needed.

---

## Why This Is Fast

The routing proxy (Mode A) carries ~29K tokens of Claude Code system prompt — at ~30 tok/s prefill that costs 60+ seconds per context boundary crossing.

This skill (Mode B) sends **only the task prompt** — typically 50–500 tokens. At 7+ tok/s generation on M1 Metal with a small context:

| Output length | Typical response time |
|---------------|-----------------------|
| 50 tokens | ~7s |
| 100 tokens | ~14s |
| 200 tokens | ~28s |

Default `max_tokens=120` keeps responses terse. Override via code if needed.

---

## Orchestration Pattern: `run_agent.py`

```bash
python ./scripts/run_agent.py \
  <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  llama
```

### Example — code review

```bash
python ./scripts/run_agent.py \
  agents/refactor-expert.md \
  target.py \
  review.md \
  "List the top 3 issues in this code. Be terse." \
  llama
```

### Example — summarize a diff

```bash
python ./scripts/run_agent.py \
  /dev/null \
  changes.diff \
  summary.md \
  "Summarize this diff in 2 sentences. Focus on risk." \
  llama
```

### Example — instruction only (no input file)

```bash
python ./scripts/run_agent.py \
  /dev/null /dev/null \
  answer.md \
  "What is the capital of France? One word." \
  llama
```

---

## Prompt Budget Guidelines

Keep prompts lean — this is the primary performance lever:
- Persona: 100–300 tokens (enough to set role and tone)
- Source file: keep under 2,000 tokens where possible; trim to the relevant section
- Instruction: 1–3 sentences; specific and bounded
- Expected output: terse — list form, not prose paragraphs

Avoid: pasting full file trees, long conversation histories, or open-ended "analyze everything" instructions.

---

## Hardware Details (M1 Mac, 16GB)

| Parameter | Value |
|-----------|-------|
| Server | llama-server :8089 |
| Model | Gemma 4 12B UD-Q4_K_XL |
| GPU offload | `-ngl 99` (full Metal) |
| Flash Attention | `-fa on` |
| Batch sizes | `-b 2048 -ub 512` |
| KV cache quant | `-ctk q8_0 -ctv q8_0` |
| Thinking | disabled (`--reasoning off`) |
| Context | 32768 tokens (1 slot) |

---

## Persona Registry (`agents/`)

| Persona | Use For |
|---------|---------|
| `security-auditor.md` | Vulnerability review, risk assessment |
| `refactor-expert.md` | Code cleanup, readability, DRY |
| `architect-review.md` | Design review, modularity check |

---

## Co-located Scripts (`scripts/`)

All scripts are symlinked from the canonical `plugins/cli-agents/scripts/` so the skill is self-contained when installed in isolation.

| Script | Purpose |
|--------|---------|
| `run_agent.py` | Task router — `cli=llama` dispatches here |
| `kv_cache_orchestrator.py` | KV slot save/restore for repeated persona calls |
| `run_server.py` | Start llama-server with authoritative parameters |
| `test_run_agent.py` | 28 tests for the task router |

> `routing_proxy.py` is NOT included — it is the Mode A API compatibility shim and is not part of this skill's execution path.

---

## Smoke Test

```bash
curl http://localhost:8089/health
python ./scripts/run_agent.py /dev/null /dev/null /tmp/test.md "Say hello in one word." llama
cat /tmp/test.md
```

---

## Health Check

```bash
curl http://localhost:8089/health          # must return {"status":"ok"}
# If down: python ./scripts/run_server.py
```
