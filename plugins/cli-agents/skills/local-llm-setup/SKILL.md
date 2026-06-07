---
name: local-llm-setup
plugin: cli-agents
description: >
  Cross-platform setup wizard for the local Gemma 4 12B inference stack. Automates
  llama-server installation (binary download or Metal/CUDA/Vulkan/ROCm compile),
  model download, routing proxy daemon install (launchd/systemd/NSSM), and
  Mode A/B validation. Covers Day 1 bootstrap and Day 2+ reconfiguration.
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User wants to set up local Gemma 4 for the first time on a Mac.</commentary>
User: Set up local LLM with Gemma 4 on my M1 Mac
Agent: Detects Metal GPU, compiles llama-server from source, downloads gemma-4-12b-UD-Q4_K_XL.gguf,
  starts server, installs routing proxy via launchd, validates with a Mode B timing test (~2s).
</example>

<example>
<commentary>User wants to test Mode B task delegation speed vs Mode A proxy.</commentary>
User: Compare Mode B vs Mode A speed for local Gemma
Agent: Runs `time python3 scripts/run_agent.py /dev/null /dev/null /tmp/t.md "hello" --cli llama`
  (~2s), then `time claude --model gemma-4-12b -p "hello"` (~30–60s cold), reports the delta.
</example>

## Primary Use Case: Mode B Task Delegation

**Mode B is the fast path.** `run_agent.py` sends a lean prompt directly to llama-server — no proxy overhead, no 29K system prompt. Measured: ~2s wall clock for a typical bounded task.

```bash
# Start llama-server (required for cli=llama)
python3 scripts/run_server.py
curl http://localhost:8089/health   # must return {"status":"ok"}

# Mode B task delegation — fast path (~2s)
time python3 scripts/run_agent.py agents/refactor-expert.md target.py output.md \
  "List the top 3 issues." --cli llama

# Mode B with custom max tokens
python3 scripts/run_agent.py /dev/null /dev/null /tmp/out.md \
  "Summarize this architecture decision." --cli llama --max-tokens 300
```

**Available agent personas** (pass as PERSONA_FILE):

| Persona | Role |
|---------|------|
| `agents/refactor-expert.md` | Code quality — SOLID/DRY smell taxonomy |
| `agents/security-auditor.md` | OWASP vulnerability audit |
| `agents/architect-review.md` | C4/SOLID structural review |
| `agents/red-team-reviewer.md` | Adversarial exploit analysis |
| `agents/compliance-reviewer.md` | Coding standards drift detection |
| `agents/pr-reviewer.md` | Diff review — ship/hold decision |
| `agents/test-writer.md` | Unit test generation |
| `agents/debate-synthesizer.md` | Multi-perspective synthesis |
| `agents/output-validator.md` | Output guardrail / hallucination check |
| `agents/self-critic.md` | Reflection loop — task-fit check |
| `agents/performance-analyst.md` | Bottleneck and scale analysis |

## Mode A (Optional — Interactive Proxy)

Mode A routes Claude Code itself through Gemma via a proxy. It carries ~29K tokens of system prompt overhead per session, making the first turn 30–60s. **Not recommended for task delegation** — use Mode B instead.

```bash
python3 scripts/enable_global_routing.py   # install launchd/systemd/NSSM daemon
python3 scripts/disable_global_routing.py  # remove daemon
```

## Co-located Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `run_server.py` | Start llama-server (authoritative params) |
| `run_agent.py` | Task router — Mode B, 6 backends |
| `enable_global_routing.py` | Install Mode A proxy daemon |
| `disable_global_routing.py` | Remove Mode A proxy daemon |
| `routing_proxy.py` | Mode A API compatibility proxy (port 4000) |
