# Local LLM CLI Dispatch

Dispatches bounded tasks directly to local inference runners — either `llama-server` at `http://localhost:8089` or native Apple Silicon MLX (`mlx-lm`) at `http://127.0.0.1:8080/v1` — with no routing proxy, no cloud API, and 2–5s typical response.

> **Apple Silicon Reference**: For native Apple Silicon Metal acceleration using MLX (`mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`, 4.43 GB RAM footprint), see [local-mlx-apple-silicon.md](local-mlx-apple-silicon.md).

## Constraints & Requirements

- **Prerequisites**: Server must be active (`curl -s http://localhost:8089/health` for llama-server, or `curl -s http://127.0.0.1:8080/v1/models` for MLX).
- **Latency Threshold**: Mode B validation requires sub-5s latency for typical bounded prompts.
- **Token Budget**: Keep prompts lean (<2,000 tokens) and instructions specific; default `max_tokens=120`.
- **Sub-Agent Isolation**: Because `--cli llama` dispatches HTTP requests directly without CLI-level sandboxing, you must append the verbatim isolation instruction to the prompt:
  > "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

## Workflow

1. **Health Check**: `curl -s http://localhost:8089/health` must return `{"status":"ok"}`; otherwise start `python3 scripts/run_server.py`.
2. **Select Persona**: Choose a persona file from `<personas>/` (see SKILL.md *Personas*), or `/dev/null` for none.
3. **Dispatch**: Run `scripts/run_agent.py` with `--cli llama` and a bounded `--max-tokens`.
4. **Inspect**: Verify exit 0 and that the output file contains the completed response.

## Dispatch Syntax

```bash
python3 scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" --cli llama
```

## Verification & Smoke Test

Validate server health and run the `/dev/null` smoke test:

```bash
# 1. Health check
curl -s http://localhost:8089/health

# 2. Smoke test (/dev/null inputs, expect fast response <= 5s)
python3 scripts/run_agent.py /dev/null /dev/null /tmp/test.md "Say hello in one word." --cli llama
cat /tmp/test.md
```

## Example

```bash
python3 scripts/run_agent.py <personas>/refactor-expert.md target.py review.md "List top 3 issues concisely." --cli llama
```
