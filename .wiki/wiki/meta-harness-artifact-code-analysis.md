---
concept: meta-harness-artifact-code-analysis
source: research-docs
source_file: meta-harness/code-analysis.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.454660+00:00
cluster: before
content_hash: 97f24faf9caa5307
---

# Meta-Harness Artifact — Code Analysis

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


*(content truncated)*

## See Also

- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement]]
- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[meta-harness-enhancement-task-tracker]]
- [[agent-harness-learning-layer-formerly-agentic-os]]

## Raw Source

- **Source:** `research-docs`
- **File:** `meta-harness/code-analysis.md`
- **Indexed:** 2026-04-17T06:42:10.454660+00:00
