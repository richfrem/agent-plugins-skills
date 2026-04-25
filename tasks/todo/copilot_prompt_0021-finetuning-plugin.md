# Copilot Task Delegation Prompt

Generate all files for the new `agent-finetuning` plugin and extend `huggingface-utils` exactly as specified below. Use your write/edit tools to create or update files directly.

## Rules
1. **Generic and Reusable**: The `agent-finetuning` plugin MUST NOT contain any Project Sanctuary terminology (e.g., "Soul", "Genome", "Guardian", "Sanctuary"). It must be a generic, reusable plugin for fine-tuning LLMs on any dataset.
2. **Separation of Concerns**: `agent-finetuning` handles environment setup, dataset preparation, fine-tuning, merging, and GGUF conversion. `huggingface-utils` handles all interactions with the Hugging Face Hub (init, upload, download).
3. **Paths**: Scaffold the plugin in `plugins/agent-finetuning/`. Update `huggingface-utils` in `plugins/huggingface-utils/`.
4. **Behavioral**: No Bash script generation (except when strictly necessary for setup instructions within SKILL.md). All new code should be Python. Follow the `evals.json` boolean routing schema (`should_trigger: true/false`).

---

## 1. Scaffold `agent-finetuning` Shell

Create `plugins/agent-finetuning/.claude-plugin/plugin.json`:
```json
{
    "name": "agent-finetuning",
    "version": "1.0.0",
    "description": "A comprehensive plugin for automating the LLM fine-tuning pipeline on CUDA environments. Features skills for WSL2/Ubuntu ML environment setup, JSONL dataset preparation, QLoRA fine-tuning orchestration, and GGUF conversion/merging.",
    "author": {"name": "Richard Fremmerlid"},
    "repository": "https://github.com/richfrem/agent-plugins-skills",
    "license": "MIT",
    "keywords": ["finetuning", "qlora", "cuda", "wsl2", "llm", "gguf", "llama.cpp"],
    "capabilities": ["model-finetuning", "dataset-preparation", "environment-setup"],
    "skills": ["setup-cuda-env", "forge-dataset", "run-finetuning", "merge-and-export"],
    "agents": ["finetuning-orchestrator"],
    "commands": ["finetune-init", "finetune-start"],
    "hooks": true
}
```

Create `plugins/agent-finetuning/README.md` summarizing the generic fine-tuning pipeline (Setup -> Dataset -> Train -> Export).

---

## 2. Create `setup-cuda-env` Skill
Path: `plugins/agent-finetuning/skills/setup-cuda-env/SKILL.md`
Path: `plugins/agent-finetuning/skills/setup-cuda-env/evals.json`

**Description:** Guides the user through validating a WSL2 Ubuntu environment with an NVIDIA GPU. Must check `nvidia-smi` and Python 3.11. Detail a "surgical strike" protocol for installing dependencies in a strict order:
1. Purge existing nvidia packages.
2. Install PyTorch with specific CUDA tag.
3. Install `triton`.
4. Install `bitsandbytes`.
5. Install `xformers`.
6. Mention compiling `llama.cpp` as a sibling directory.
Provide the generic bash commands required to execute this setup. Do NOT use Sanctuary terms.

---

## 3. Create `forge-dataset` Skill
Path: `plugins/agent-finetuning/skills/forge-dataset/SKILL.md`
Path: `plugins/agent-finetuning/skills/forge-dataset/evals.json`

**Description:** A generic skill for processing raw data into a `training_data.jsonl` format suitable for fine-tuning. 
- Must explain the required schema (`instruction` and `output` keys).
- Must include a sub-step for validating the JSONL (syntax, schema, duplicates).
- Expect the user to provide **any content directories** (Markdown, code, text dumps) to parse into the JSONL format.
- Should write a generic `prepare_dataset.py` script to the host project to handle chunking and dataset preparation.
- Includes steps to download a **small base model** suitable for local fine-tuning.

---

## 4. Create `run-finetuning` Skill
Path: `plugins/agent-finetuning/skills/run-finetuning/SKILL.md`
Path: `plugins/agent-finetuning/skills/run-finetuning/evals.json`

**Description:** Executes a QLoRA fine-tuning run on the small base model within the created CUDA environment.
- Must detail the creation of a generic `training_config.yaml` with parameters for 8GB+ VRAM optimization (max_seq_length=256, load_in_4bit=true, bnb_4bit_quant_type=nf4, lora r=16, paged_adamw_8bit, gradient_checkpointing).
- Must provide guidance on executing the fine-tuning script (assume a script like `fine_tune.py` exists in the host project, or provide a generic one).
- **Explicit Goal:** Include a dedicated path to **test Unsloth** (`unsloth.FastLanguageModel`) to see if it is faster and uses less VRAM for this workload.
- Emphasize checkpoint resumption.

---

## 5. Create `merge-and-export` Skill
Path: `plugins/agent-finetuning/skills/merge-and-export/SKILL.md`
Path: `plugins/agent-finetuning/skills/merge-and-export/evals.json`

**Description:** Handles the post-training pipeline.
- Merging the LoRA adapter into the base model using CPU loading.
- Applying necessary compatibility patches for `llama.cpp` (e.g., stripping `use_flash_attn`).
- Converting to GGUF format (Q4_K_M) using the `llama.cpp` conversion tools.
- Generating a generic Ollama `Modelfile`.
- **Local Testing:** Test the compiled model locally via Ollama to ensure it works.
- **CRITICAL DELEGATION:** Explicitly state that after a successful local test, uploading the final artifacts to Hugging Face MUST be delegated to the `huggingface-utils` plugin (`hf-model-upload` skill). Do not include HF upload logic here.

---

## 6. Create `finetuning-orchestrator` Sub-Agent
Path: `plugins/agent-finetuning/agents/finetuning-orchestrator.md`

**Description:** A **full-cycle orchestrator agent** that guides the user through the end-to-end process.
- Phase 0 gate: Environment Validation -> delegates to `setup-cuda-env`.
- Phase 1 gate: Parse content to JSONL & base model download -> delegates to `forge-dataset`.
- Phase 2 gate: Test Unsloth & execute training -> delegates to `run-finetuning`.
- Phase 3 gate: Merge, GGUF conversion & **local testing** -> delegates to `merge-and-export`.
- Phase 4 gate: Hub Deployment (after successful local test) -> delegates to `huggingface-utils` / `hf-model-upload`.
Must maintain state between phases so a user can resume after long training runs.

---

## 7. Extend `huggingface-utils` Plugin
We need to ensure `huggingface-utils` has generic capabilities for uploading models, separate from project-specific "Soul" persistence.

1. **Review/Update `hf-init`**: Ensure `plugins/huggingface-utils/skills/hf-init/SKILL.md` is generic enough to initialize repo paths for model uploads, not just datasets.
2. **Create `hf-model-upload` Skill**:
   - Path: `plugins/huggingface-utils/skills/hf-model-upload/SKILL.md`
   - Path: `plugins/huggingface-utils/skills/hf-model-upload/evals.json`
   - **Description**: A generic skill to upload model artifacts (GGUF, Safetensors, Modelfiles, READMEs) to a Hugging Face model repository. It should accept arguments for repo name and file paths. It must not contain Sanctuary-specific hardcoded paths. Update `plugin.json` to include this new skill.

---

## Execution
Generate all files exactly as specified. Ensure `evals.json` files use the `should_trigger` schema.
