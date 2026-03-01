---
description: High-speed RLM distillation of project documentation using agentic intelligence.
---

# Agent-Driven Distillation Workflow (PROJECT)

Use this workflow to bypass slow local Ollama models when summarizing **documentation** (MD, TXT) for the RLM project cache. The agent (Claude, Gemini, Antigravity, etc.) reads the file itself, generates a high-quality summary, and injects it into the cache.

## 🚀 Execution Steps (Batch / Bulk)

For filling large gaps (e.g., Chronicle entries), the [Orchestrator](plugins/agent-loops/skills/orchestrator/SKILL.md) routes work to the **[Agent Swarm](plugins/agent-loops/skills/agent-swarm/SKILL.md)** pattern (Pattern 4). This pattern is implemented by the `swarm_run.py` script.

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
3.  **Read the summarization prompt** from [rlm_summarize_tool.md](plugins/tool-inventory/resources/prompts/rlm/rlm_summarize_tool.md) or [rlm_summarize_general.md](plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_general.md).
4.  **Generate a high-quality summary** following the prompt's guidelines.
5.  **Execute the injector** to write your summary instantly into the cache:

```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py --profile project --file <path_to_doc> --summary "Your summary here"
```

6.  **Verify** that `rlm_summary_cache.json` is updated.


