# 0021 — Create `agent-finetuning` Plugin: Skills & Sub-Agents for Automated LLM Fine-Tuning

**Plugin:** agent-finetuning (new — does not exist yet)
**Effort:** XL — new plugin with 5 skills, 1 orchestrator sub-agent, 1 hook, config files
**Environment:** Windows PC + NVIDIA RTX 2000 Ada GPU, WSL2 + Ubuntu (primary), Python 3.11, CUDA 12.6 stable / 13.0 nightly

---

## Context

This plugin automates what is currently a fully manual fine-tuning pipeline documented in
`Project_Sanctuary/forge/CUDA-ML-ENV-SETUP.md` and `forge/README.md`. The existing
pipeline has 5 phases (~15 manual steps):

- **Phase 0:** WSL2 system setup + llama.cpp build (one-time)
- **Phase 1:** ML env creation (`setup_ml_env_wsl.sh`) + surgical strike installs (bitsandbytes, triton, xformers)
- **Phase 2:** Dataset forge (`forge_whole_genome_dataset.py`) + validate + base model download
- **Phase 3:** QLoRA fine-tune (`fine_tune.py` — 1–3h, Qwen2-7B-Instruct, 4-bit, LoRA r=16)
- **Phase 4:** Merge adapter (`merge_adapter.py` + `--skip-sanity`) → GGUF convert (`convert_to_gguf.py --quant Q4_K_M --force`) → create Modelfile → Ollama import → HuggingFace upload

**Key source scripts analyzed:**
- `fine_tune.py` — uses `AutoModelForCausalLM`, `BitsAndBytesConfig`, `SFTTrainer`, YAML config from `forge/config/training_config.yaml`, checkpoint resume, 7-step pipeline
- `forge_whole_genome_dataset.py` — relies on `mcp_servers.lib` (ContentProcessor, find_project_root); scans `ingest_manifest.json` then appends ADDITIONAL_DOCS; outputs `dataset_package/sanctuary_whole_genome_data.jsonl`; min 200 entries threshold
- `validate_dataset.py` — 3-step: JSONL syntax, schema (`instruction`/`output` required), duplicate check
- `merge_adapter.py` — CPU-load base, PeftModel.from_pretrained, merge_and_unload, applies Qwen2→llama.cpp compatibility patches (strips `use_flash_attn`, `sliding_window`, etc.)
- `convert_to_gguf.py` — locates `../llama.cpp/convert_hf_to_gguf.py` + `llama-quantize`, 3-step: f16→GGUF→quantize (Q4_K_M default)→verify with `gguf.GGUFReader`
- `create_modelfile.py` — reads `gguf_config.yaml`, auto-picks newest GGUF, writes Ollama 0.12.9-compatible Modelfile with GUARDIAN-01 system prompt + dual-mode template, stops `<|im_end|>`, temperature 0.7, num_ctx 4096
- `upload_to_huggingface.py` — delegates to `mcp_servers.lib.hf_utils.upload_to_hf_hub`, reads `.env` for `HUGGING_FACE_TOKEN`, repo default `richfrem/Sanctuary-Qwen2-7B-v1.0-GGUF-Final`

**ML-Env-CUDA13 key facts:**
- Foundation Layer: torch, tensorflow, nvidia-* managed by `setup_ml_env_wsl.sh` (not pip-tools)
- Application Layer: managed via `requirements.in` → `pip-compile` → `requirements.txt`
- Critical surgical strike sequence: purge nvidia packages → triton==3.1.0 → bitsandbytes==0.48.2 (CUDA 126) → xformers → fsspec≤2024.3.1
- Known gotchas: `ncclDevCommDestroy` symbol mismatch fixed by purging `nvidia-*-cu12` first; `evaluation_strategy` renamed to `eval_strategy` in newer transformers; `keep_torch_compile` error fixed by upgrading accelerate
- VENV at `~/ml_env` (Linux native FS, NOT `/mnt/c/` — major I/O performance difference)
- llama.cpp must be sibling dir: `../llama.cpp/` relative to Project_Sanctuary

**Unsloth optimization target (task #151):**
- Replace `AutoModelForCausalLM.from_pretrained` with `unsloth.FastLanguageModel.from_pretrained`
- Patch `SFTTrainer` with Unsloth's custom Triton kernels
- Goal: 2x+ speed, 80–90% VRAM reduction
- Requires: `unsloth`, `xformers`, `triton` — alternative training path, not replace existing

---

## Gaps Identified

- ❌ No `agent-finetuning` plugin exists — everything is manual documentation
- ❌ No skill guides WSL2 system pre-checks and the surgical strike installation protocol (the exact bitsandbytes/triton/xformers ordering is critical and fragile)
- ❌ No skill automates the full dataset forge+validate cycle; `forge_whole_genome_dataset.py` depends on `mcp_servers.lib` which won't be in path without guidance
- ❌ No skill for fine-tuning run with checkpoint-resume awareness and environment pre-checks
- ❌ No Unsloth alternative training path skill
- ❌ No skill for merge→GGUF→Modelfile→Ollama→HF pipeline with proper Qwen2 compatibility patches
- ❌ No sub-agent guides the complete session with phase-gate checkpoints
- ❌ No `evals.json` routing criteria for any of the above
- ❌ No `hooks/session_end.py` to persist phase progress between interrupted runs
- ❌ Plugin has no `plugin.json`, no `README.md`, no `CHANGELOG.md`

---

## Workstreams

| WS | Scope | Output file(s) |
|----|-------|----------------|
| WS-A | Scaffold plugin shell | `plugins/agent-finetuning/README.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `evals/evals.json` |
| WS-B | `setup-cuda-env` skill | `plugins/agent-finetuning/skills/setup-cuda-env/SKILL.md`, `evals.json` |
| WS-C | `forge-dataset` skill | `plugins/agent-finetuning/skills/forge-dataset/SKILL.md`, `evals.json` |
| WS-D | `run-finetuning` skill | `plugins/agent-finetuning/skills/run-finetuning/SKILL.md`, `evals.json` |
| WS-E | `merge-and-export` skill | `plugins/agent-finetuning/skills/merge-and-export/SKILL.md`, `evals.json` |
| WS-F | `finetuning-orchestrator` sub-agent | `plugins/agent-finetuning/agents/finetuning-orchestrator.md` |
| WS-G | `hooks/session_end.py` | `plugins/agent-finetuning/hooks/session_end.py` |

**WS ordering rule:** WS-A scaffold first. Skills WS-B through WS-E built before orchestrator WS-F. Hook WS-G last.

---

## Key Content Requirements Per Workstream

### WS-B: `setup-cuda-env` skill
Must cover in SKILL.md:
- Pre-flight: `nvidia-smi` GPU check, WSL2 detection, Python 3.11 check
- `bash setup_ml_env_wsl.sh` (stable) or `--cuda13` flag
- Activate: `source ~/ml_env/bin/activate`
- Surgical strike protocol (ordered exactly): purge → triton 3.1.0 → bitsandbytes 0.48.2 → xformers → fsspec≤2024.3.1
- llama.cpp sibling clone + cmake build with `GGML_CUDA=ON`
- `CMAKE_ARGS="-DGGML_CUDA=on" pip install --force-reinstall --no-cache-dir llama-cpp-python --no-deps`
- Verification suite: `test_torch_cuda.py`, `test_xformers.py`, `test_llama_cpp.py`
- HuggingFace `.env` setup: `HUGGING_FACE_TOKEN=...`
- **Gotchas section**: ncclDevCommDestroy fix, evaluation_strategy→eval_strategy rename, accelerate upgrade for keep_torch_compile error, `/mnt/c/` I/O penalty

### WS-C: `forge-dataset` skill
Must cover:
- Activate env first: `source ~/ml_env/bin/activate`
- Must accept generic user-provided directories containing Markdown, text, or code files.
- `python generic_forge_dataset.py --input_dirs <paths> --output training_data.jsonl` — parses any of the user's content into the required format.
- `python generic_validate_dataset.py training_data.jsonl` — validates JSONL syntax, `instruction`+`output` schema, duplicates.
- `bash download_model.sh <model_name>` — Downloads a small base model for fine-tuning.
- **Gotchas**: Ensure the parser handles chunking long documents properly so the dataset fits within context windows.

### WS-D: `run-finetuning` skill
Must cover two paths:

**Standard QLoRA path:**
- Focus on fine-tuning a small base model within the optimized CUDA environment.
- Config: `training_config.yaml` — key params: max_seq_length=256, load_in_4bit=true, bnb_4bit_quant_type=nf4, lora r=16, epochs=3, batch=1, grad_accum=8, paged_adamw_8bit, fp16=true
- `python fine_tune.py` — auto-resumes from checkpoint in `outputs/checkpoints/`
- Monitor: log output shows step/loss; adapter saved to `models/adapter/`
- Verify: `ls models/adapter/` → `adapter_model.safetensors` + `adapter_config.json`

**Unsloth testing path:**
- **Explicit Goal:** Test if Unsloth is significantly faster for this workload.
- Install: `pip install unsloth xformers triton`
- Swap `AutoModelForCausalLM` → `unsloth.FastLanguageModel.from_pretrained`
- Patch `SFTTrainer` with Unsloth wrapper
- Target: Validate the expected 2x+ speed and 80–90% VRAM reduction.

### WS-E: `merge-and-export` skill
Must cover ordered pipeline:
1. `python merge_adapter.py --skip-sanity` — CPU load, applies llama.cpp patches, atomically saves to `models/merged/`
2. Sentencepiece prereq: `pip install sentencepiece protobuf`
3. `python convert_to_gguf.py --quant Q4_K_M --force` — locates `llama.cpp` tools; f16 cleaned up; verifies with `gguf.GGUFReader`
4. `python create_modelfile.py` — auto-detects newest GGUF, writes `Modelfile`
5. **Local Testing:** `ollama create My-Finetune-Model -f Modelfile`; rigorously test locally via `ollama run My-Finetune-Model` to confirm behavior before pushing.
6. **Upload:** Delegate to `huggingface-utils` after local testing is verified.
- **Gotchas**: `--force` needed if GGUF exists; sanity check skipped for memory safety; `../llama.cpp` must exist as sibling; quantization metadata stripped from config.json before conversion

### WS-F: `finetuning-orchestrator` sub-agent
Phase-gate design for a **full cycle agent** — user confirms before each phase, moving from raw environment to published model:
- Phase 0 gate: "Has `nvidia-smi` been run and confirmed? Is WSL2 active?" → calls setup-cuda-env skill
- Phase 1 gate: "Is env active? Parse user content to JSONL? Download small model?" → calls forge-dataset skill
- Phase 2 gate: "Dataset validated? Test Unsloth and start training run?" → calls run-finetuning skill
- Phase 3 gate: "Merge+GGUF+Ollama? Test model locally?" → calls merge-and-export skill
- Phase 4 gate: "Local test passed? Push to Hugging Face?" → delegates to `huggingface-utils`
- Session persistence: reads/writes `context/finetuning_session.json` for phase state

### WS-G: `hooks/session_end.py`
- Writes phase progress to `context/finetuning_session.json`: `{phase: N, step: "...", last_checkpoint: "...", timestamp: "..."}`
- Reads existing session on start to support resume

---

## Delegation Plan

1. Delegation prompt at `tasks/todo/copilot_prompt_0021-finetuning-plugin.md`
2. Dispatch via `run_agent.py` with `claude-sonnet-4.6` when on CUDA machine
3. Review: verify each skill file exists, evals.json has ≥6 entries, plugin.json lists all skills
4. `python plugins/plugin-manager/scripts/plugin_add.py` to install into `.agents/`
5. Commit and PR on `feat/agent-finetuning-plugin` branch

> **⚠️ Execution note:** This plugin is authored on Mac. All skills reference WSL2/Windows
> NVIDIA CUDA paths. Execute skill workflows only on Windows PC with NVIDIA GPU.

---

## Status

- [ ] WS-A: Plugin scaffold
- [ ] WS-B: `setup-cuda-env` skill
- [ ] WS-C: `forge-dataset` skill
- [ ] WS-D: `run-finetuning` skill
- [ ] WS-E: `merge-and-export` skill
- [ ] WS-F: `finetuning-orchestrator` sub-agent
- [ ] WS-G: `hooks/session_end.py`
