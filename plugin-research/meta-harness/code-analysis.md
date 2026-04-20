# Meta-Harness Artifact — Code Analysis

**Artifact repo:** https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
**Local path:** `temp/repos/meta-harness-tbench2-artifact/`
**Related paper summary:** [summary.md](./summary.md)

This document analyzes the actual discovered harness code that achieved #2 on TerminalBench-2 (Opus 4.6) and #1 among all Haiku 4.5 agents.

---

## Structure

Remarkably lean — the entire harness is 5 files:

```
meta-harness-tbench2-artifact/
├── agent.py                    # Main harness — 1,321 lines, everything is here
├── anthropic_caching.py        # Prompt caching helper — 63 lines
├── prompt-templates/
│   └── terminus-kira.txt       # System prompt template
└── pyproject.toml              # Dependencies
```

This is the *output* of the Meta-Harness search process — a single self-contained Python harness that wraps Claude (via LiteLLM) and manages tool execution in a Linux sandbox environment (Terminal-Bench 2.0, powered by Harbor/Terminus2).

---

## Core Class: `AgentHarness`

Extends `Terminus2` (from the Harbor framework). The key innovations over the baseline (`Terminus-KIRA`) are:

### 1. Environment Bootstrapping (`_gather_env_snapshot`)

Before the first agent turn, runs a single compound bash command that gathers:
- Working directory (`pwd`)
- File listing (`ls -la /app/`)
- Available languages and tools (python, gcc, node, java, rustc, go)
- Package managers (pip3, apt-get, npm)
- Memory (`free -h`)

This is injected into the first prompt as a compact `[Environment Snapshot]` block. The result: **2–5 fewer early exploration turns** where the agent would otherwise just be running `ls` and `which python`. This is a classic harness-level optimization — moving context gathering out of the agent loop and into a deterministic pre-step.

### 2. Marker-Based Command Polling (`_execute_commands`)

Instead of waiting a fixed duration after each command, the harness:

1. Sends the command
2. Immediately sends `echo '__CMDEND__<seq>__'`
3. Polls every 0.5s for the marker to appear
4. Exits early if the marker arrives before the timeout

Commands that finish in 0.1s don't wait 1.0s. Fast sequences of reads/writes/compiles complete much faster. The harness tracks time saved for analysis. Output cleaning strips all marker lines before returning to the LLM.

### 3. Native Tool Calling (No Parsing)

The baseline Terminus-KIRA used XML/JSON parsing of raw LLM output. This harness uses Anthropic's `tools` parameter directly — the model emits structured tool calls natively. Three tools:

**`execute_commands`**
```json
{
  "analysis": "reasoning about what to do",
  "plan": "step-by-step plan",
  "commands": [
    { "keystrokes": "python script.py", "duration": 5.0 }
  ]
}
```
Duration is capped at 60s. The `analysis` and `plan` fields force the model to reason explicitly before acting — a structured chain-of-thought embedded in the tool schema.

**`task_complete`**
Two-call confirmation. First call triggers a multi-perspective checklist (test engineer, QA engineer, end-user). Second call actually terminates the episode. Prevents premature completion.

**`image_read`**
Reads local files, base64-encodes them, sends as multimodal messages. Supports PNG, JPG, JPEG, GIF, WEBP.

### 4. Context Management

Two layers:

**Reactive**: When `ContextLengthExceededError` fires, the harness unwinds messages, calls `_summarize()` to compress progress into a summary, and retries with a handoff prompt.

**Proactive**: `_check_proactive_summarization()` runs each episode. If context is filling up before hitting the limit, it summarizes early, preventing the harder recovery path.

Terminal output is capped at 30KB before being included in messages.

### 5. Anthropic Prompt Caching (`anthropic_caching.py`)

Adds `cache_control: {type: ephemeral}` to the last 3 messages in any Anthropic API call. Converts string content to array format with cache metadata. Cost reduction on repeated long-context turns.

---

## Harness Design Patterns

| Pattern | Implementation |
|---|---|
| **Pre-turn environment injection** | `_gather_env_snapshot()` runs once, injects before turn 1 |
| **Early command exit** | Marker polling reduces fixed-wait overhead |
| **Native tool schema as CoT** | `analysis` + `plan` fields force structured reasoning |
| **Double-confirmation completion** | Two `task_complete` calls with checklist between |
| **Layered context management** | Proactive summarization before reactive recovery |
| **Full trajectory logging** | Every step: prompt, response, tool calls, tokens, cost |

---

## System Prompt (terminus-kira.txt)

Key behavioral constraints baked into the system prompt:
- Standalone execution — no human will intervene
- Must verify task completion from multiple perspectives (test engineer, QA, user)
- Warns against side effects and state pollution
- Checklist before `task_complete`: re-read the task, verify output, check for regressions

---

## How the Agent Loop Works

```
AgentHarness.run()
│
├── _gather_env_snapshot()     # once, pre-loop
│
└── _run_agent_loop()          # up to max_episodes
    │
    ├── _check_proactive_summarization()
    ├── _handle_llm_interaction()
    │   ├── Build messages from chat history
    │   ├── Apply prompt caching
    │   ├── litellm.acompletion() with tools=
    │   └── Extract tool_calls from response
    │
    ├── _parse_tool_calls()
    │   ├── execute_commands  →  _execute_commands()   # marker polling
    │   ├── task_complete     →  confirmation loop
    │   └── image_read        →  _execute_image_read() # multimodal
    │
    ├── Record Step(metrics, trajectory)
    └── Loop or exit
```

---

## Error Handling

```python
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4s),
    # No retry on: BadRequest, AuthError, ContextLength, OutputLength, Cancelled
)
```

- API timeout: 900s (15 min)
- Block detection: 600s (10 min)
- Output length exceeded: request shorter response, retry
- Parsing failure: send feedback, retry

---

## What the Meta-Harness Search Actually Discovered

Comparing this artifact to the Terminus-KIRA baseline, the search process discovered these specific improvements:

1. **Environment snapshot injection** — eliminates boilerplate exploration turns
2. **Marker-based polling** — replaces fixed-duration waits with adaptive polling
3. **Native tool calling** — removes parsing failures as a failure mode
4. **Forced structured reasoning** (`analysis`/`plan` fields) — reduces poorly-planned action sequences
5. **Proactive summarization** — prevents hard context-length failures
6. **Double-confirmation task completion** — reduces false-completion errors
7. **Multi-perspective completion checklist** — catches regressions before exit

These aren't obvious prompt hacks — they're architectural decisions about control flow, information presentation, and error recovery. This is exactly what the paper claims: code-space search finds structural improvements that text-space optimizers cannot.

---

## Performance Characteristics

| Metric | Value |
|---|---|
| Pass rate (Opus 4.6) | 76.4% |
| Easy tasks | 100.0% |
| Medium tasks | 81.1% |
| Hard tasks | 64.7% |
| TerminalBench-2 rank (Opus 4.6) | #2 overall |
| TerminalBench-2 rank (Haiku 4.5) | #1 overall |
| Context per step (max) | 10M tokens of diagnostic info available to the search proposer |

---

## Relevance to This Repo

The Meta-Harness artifact is directly analogous to what the `os-eval-runner` + `os-skill-improvement` flywheel in `agent-agentic-os` does:

| Meta-Harness concept | This repo equivalent |
|---|---|
| Harness = code wrapping an LLM | SKILL.md + scripts = skill wrapping an agent |
| Outer search loop | `os-improvement-loop` (OUTER flywheel) |
| Filesystem of all prior candidates + traces | `.agent/learning/` + eval results |
| Proposer reads filesystem, writes new harness | `os-skill-improvement` RED-GREEN-REFACTOR loop |
| `evaluate.py` gates mutations | `evaluate.py` exit 0 = KEEP, exit 1 = DISCARD |
| Environment snapshot injection | Pre-context patterns in SKILL.md |
| Marker-based early exit | Verification-before-completion skill |

The key capability this repo currently lacks: **raw execution trace storage and selective retrieval** by the proposer. Meta-Harness's advantage comes from the proposer reading `grep`/`cat` over full execution logs rather than summarized scores. The `os-eval-runner` passes scores and diffs — adding structured execution trace logs to the filesystem would move the flywheel significantly closer to the Meta-Harness approach.
