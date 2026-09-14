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

## Native orchestration facilities (verified September 2026)

This Codex CLI provides sandboxed execution (`--sandbox`), approval policy, non-interactive
`exec`, dedicated `review`, session resume/fork, and browsing sessions through `codex agents`.
Its documented CLI surface does **not** expose a native plan mode, a command that creates Git
worktrees, or a CLI flag to delegate subagents. Do not infer any of those from the model or from
an outer host's collaboration tools. Use the Agentic OS portable worktree and its orchestration
layer for those functions; then run Codex in that selected worktree.

```bash
# Bounded review on the current portable worktree
codex review --uncommitted "Review only correctness and regression risks."

# Restricted execution inside a selected worktree
codex exec --sandbox workspace-write "Implement the approved task and run focused tests."
```

Use `--dangerously-bypass-approvals-and-sandbox` only with explicit authorization and external
containment. When a host does provide collaboration tools, record that host runtime separately
rather than claiming the Codex CLI itself supplied native delegation.

---

## Orchestration Pattern: `run_agent.py`

```bash
python ./scripts/run_agent.py \
  <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  --cli codex --model gpt-5-codex
```

The prompt is piped to `codex exec` via stdin — not passed as a positional arg — to avoid OS ARG_MAX limits and process listing exposure.

### Example

```bash
python ./scripts/run_agent.py \
  agents/refactor-expert.md \
  target.py \
  refactor.md \
  "Refactor this function and explain the top 3 changes." \
  --cli codex
```

### With a different model

```bash
python ./scripts/run_agent.py \
  agents/security-auditor.md \
  target.py \
  security.md \
  "Find vulnerabilities. Rate severity: CRITICAL / MODERATE / MINOR." \
  --cli codex --model gpt-4o
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
echo "Say hello in one sentence." | codex exec --model gpt-5-codex -
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Summarize this file." --cli codex
```

---

## Health Check

```bash
echo $OPENAI_API_KEY   # must be set
which codex            # must be on PATH
codex --version
codex exec --help      # verify exec subcommand and available flags
```
