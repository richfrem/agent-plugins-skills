---
name: codex-cli-agent
plugin: cli-agents
description: >
  Codex CLI sub-agent for dispatching tasks to OpenAI-compatible models via the `codex` binary.
  Use for code-focused tasks routed to GPT-5 Codex or any OpenAI-compatible endpoint.
  Part of the run_agent.py multi-LLM task router — cli=codex target.
allowed-tools: Bash, Read, Write
---

## Identity: The Codex Sub-Agent Dispatcher (Standard: gpt-5-codex)

Dispatches bounded tasks to the Codex CLI (`codex` binary). Uses the `run_agent.py` task router with `cli=codex`.

> [!IMPORTANT]
> **Default model: `gpt-5-codex`.** Requires `OPENAI_API_KEY` in environment. The `codex` binary must be on PATH.

---

## Orchestration Pattern: `run_agent.py`

```bash
python ./scripts/run_agent.py \
  <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  codex [model=gpt-5-codex]
```

### Example

```bash
python ./scripts/run_agent.py \
  agents/refactor-expert.md \
  target.py \
  refactor.md \
  "Refactor this function and explain the top 3 changes." \
  codex
```

### With a different model

```bash
python ./scripts/run_agent.py \
  agents/security-auditor.md \
  target.py \
  security.md \
  "Find vulnerabilities. Rate severity: CRITICAL / MODERATE / MINOR." \
  codex gpt-4o
```

---

## When to Use codex-cli-agent

| Use Case | Why codex |
|----------|-----------|
| Code review / refactor | GPT-5 Codex is code-optimized |
| OpenAI endpoint routing | Use any `OPENAI_BASE_URL`-compatible target |
| Isolated sub-task to GPT-5 | No main agent context bleed |

---

## Persona Registry (`agents/`)

| Persona | Use For |
|---------|---------|
| `security-auditor.md` | Red team, vulnerability scanning |
| `refactor-expert.md` | Code optimization, DRY, readability |
| `architect-review.md` | System design, modularity |

---

## Smoke Test

```bash
codex exec --model gpt-5-codex "Say hello in one sentence."
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Summarize this file." codex
```

---

## Health Check

```bash
echo $OPENAI_API_KEY   # must be set
which codex            # must be on PATH
codex --version
codex exec --help      # verify exec subcommand and available flags
```
