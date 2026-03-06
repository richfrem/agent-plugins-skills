---
description: High-speed RLM distillation of project documentation using agentic intelligence.
---

# Agent-Driven Distillation Workflow (PROJECT)

Use this workflow to dramatically accelerate the summarization of documents (MD, TXT) or code for the RLM cache by utilizing frontier AI models instead of slow, low-power local models.

## 🧠 Distillation Efficiency Tiers (Why this exists)

RLM Distillation maps to three tiers of speed and scale:

1. **Tier 1 (Slowest): Local LLM via `distiller.py`**
   - *Use Case*: Offline or zero-cost background runs.
   - *Limitation*: Requires Ollama. Takes 3-5 minutes per file on M1 hardware. High failure rate on complex files.
2. **Tier 2 (Fast): Single Agent Injection (This Workflow)**
   - *Use Case*: On-the-fly gap-filling of 1-10 files.
   - *Advantage*: The agent (Claude/Gemini/Antigravity) simply reads the file, generates a perfect summary instantly, and uses `inject_summary.py` to bypass the slow local distiller.
3. **Tier 3 (Fastest/Scale): Multi-Agent Swarm**
   - *Use Case*: Mass gap-filling of dozens/hundreds of files (e.g., initial repository documentation).
   - *Advantage*: Delegates the exact same prompt to a parallel orchestrator (`swarm_run.py`) to hit API endpoints concurrently in seconds.

## 🚀 Execution Steps (Batch / Bulk)

For filling large gaps (e.g., repository documentation), the [Orchestrator](plugins/agent-loops/skills/orchestrator/SKILL.md) routes work to the **[Agent Swarm](plugins/agent-loops/skills/agent-swarm/SKILL.md)** pattern (Pattern 4). This pattern is implemented by the `swarm_run.py` script.

1.  **Locate or create a Job File** (e.g., `plugins/rlm-factory/resources/jobs/rlm_chronicle.job.md`).
2.  **Execute the Swarm Runner**:
    ```bash
    python3 plugins/agent-loops/skills/agent-swarm/scripts/swarm_run.py \
      --job plugins/rlm-factory/resources/jobs/rlm_chronicle.job.md \
      --dir 00_CHRONICLE/ENTRIES \
      --resume
    ```
    *Note: This script features built-in exponential backoff for rate limits and checkpointing to auto-resume.*
3.  **Check Progress**: Monitor the `✅` and `❌` status in the terminal. The runner persists state to a `.swarm_state_*.json` file.


## 🚀 Execution Steps (Single File)

1.  **Identify the document** (e.g., `docs/architecture_overview.md`).
2.  **Read the document** using `view_file`.
3.  **Read the summarization prompt** from [rlm_summarize_tool.md](plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_tool.md) or [rlm_summarize_general.md](plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_general.md).
4.  **Generate a high-quality summary** following the prompt's guidelines.
5.  **Execute the injector** to write your summary instantly into the cache:

```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py --profile project --file <path_to_doc> --summary "Your summary here"
```

6.  **Verify** that `rlm_summary_cache.json` is updated.


