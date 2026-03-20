# Asynchronous Benchmark Metric Capture

**Pattern Name**: Asynchronous Benchmark Metric Capture
**Category**: Evaluation & Tuning
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
During parallel benchmark executions or deep subagent loops, critical telemetry (like `total_tokens` consumed and `duration_ms` elapsed) is emitted as one-time ephemeral notifications. This pattern mandates that the agent explicitly listens for these notifications and writes them to a persistent `timing.json` log immediately as each subagent task completes, preventing this critical benchmark data from being lost in the chat history.

## When to Use
- When executing the `Rigorous Benchmarking & Grading Loop` pattern across positive/negative prompt test cases.
- In multi-agent swarm environments where parallel workers consume highly variable token counts.
- When tracking the overhead cost of complex `././SKILL.md` contexts against a baseline.

## Implementation Example
```markdown
### Capture Timing Data (Required)
When each subagent task completes, you receive an asynchronous system notification containing `<total_tokens>` and `<duration_ms>`.
- You MUST save this data immediately to `timing.json` in the respective subagent's run directory.
- Do NOT batch process this at the end of the entire swarm execution, as the notifications may scroll out of the immediate context window.
```

## Anti-Patterns
- Benchmarking the "Success Rate" (pass/fail) of an iteration without tracking the Token / Time cost to achieve that success.
- Expecting a human to manually scroll through 10 Subagent trace logs to calculate total token latency.
