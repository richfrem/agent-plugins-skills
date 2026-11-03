# Apple Silicon MLX Local LLM Reference (Zero-Swap Inference)

Native Apple Silicon Metal execution guide for local sovereign model inference using Apple's MLX framework (`mlx-lm`).

---

## 1. Architectural Overview & Hardware Boundary

On Apple Silicon (M1/M2/M3/M4) systems with unified memory (e.g. 16GB RAM):
- **Local Inference (`mlx-lm`)**: Highly optimized via unified memory and Apple Silicon GPU cores. A 4-bit quantized 7B model (`mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`) consumes only **~4.43 GB of RAM**, leaving plenty of headroom for macOS and IDE tasks with **zero swap-thrashing**.
- **Local Fine-Tuning Boundary**: Fine-tuning 7B models on 16GB M-series Macs causes severe memory exhaustion and thrashing. Fine-tuning/training is strictly reserved for dedicated NVIDIA CUDA/WSL2 rigs (Phoenix Forge), while Apple Silicon serves as the premier zero-latency, private local inference engine.

---

## 2. Canonical Model Selection

- **Repository**: `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`
- **Cache Location**: `~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-7B-Instruct-4bit`
- **Quantization**: 4-bit Group-Wise Quantization (MLX format)
- **Peak RAM**: ~4.43 GB
- **Measured Throughput (Apple M1 16GB)**:
  - Prompt processing: **~83.7 tokens/second**
  - Generation speed: **~14.3 tokens/second**

---

## 3. Server Mode: OpenAI-Compatible Endpoint

Run `mlx_lm.server` as a persistent background or dedicated daemon serving standard OpenAI API endpoints:

```bash
# Launch OpenAI-compatible server on port 8080
uvx --from mlx-lm mlx_lm.server \
  --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
  --port 8080
```

### Health Check & Model Discovery Gate

To verify the server is live and responsive:

```bash
curl -s http://127.0.0.1:8080/v1/models
```

**Expected JSON Output:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
      "object": "model",
      "created": 1741000000,
      "owned_by": "mlx-lm"
    }
  ]
}
```

### Direct HTTP Chat Completion Test

```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
    "messages": [
      {"role": "system", "content": "You are a concise engineering assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 50
  }'
```

---

## 4. On-Demand CLI & Interactive Modes

When a persistent server is not desired, execute ad-hoc prompts directly without keeping background memory occupied:

### One-Shot Generation

```bash
uvx --from mlx-lm mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
  --prompt "What is the capital of France?" \
  --max-tokens 50 \
  --verbose True
```

**Output:**
```
The capital of France is Paris.
==========
Prompt: 36 tokens, 83.681 tokens-per-sec
Generation: 8 tokens, 14.348 tokens-per-sec
Peak memory: 4.431 GB
```

### Interactive Terminal Chat

```bash
uvx --from mlx-lm mlx_lm.chat \
  --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
```

---

## 5. Sub-Agent Task Delegation Integration

To route bounded sub-agent tasks or Mode B delegations to the local MLX server:

1. **Environment Variables**:
   ```bash
   export OPENAI_BASE_URL="http://127.0.0.1:8080/v1"
   export OPENAI_API_KEY="none"
   export LOCAL_LLM_MODEL="mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
   ```

2. **Sub-Agent Isolation Guard**:
   Always append bounded isolation rules when dispatching:
   > "You are operating as an isolated local sub-agent. Do NOT use tools. Do NOT access filesystem. Only return the final answer concisely."

3. **Fallback Topology**:
   - Primary: Persistent MLX Server (`http://127.0.0.1:8080/v1`)
   - Fallback 1: Local Ollama (`http://127.0.0.1:11434`)
   - Fallback 2: One-shot CLI `mlx_lm.generate`
   - Fallback 3: Cloud cheapest-tier model (Haiku / Gemini Flash)
