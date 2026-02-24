---
description: High-speed RLM distillation of project documentation using agentic intelligence.
---

# Agent-Driven Distillation Workflow (PROJECT)

Use this workflow to bypass slow local Ollama models when summarizing **documentation** (MD, TXT) for the RLM project cache. The agent (Claude, Gemini, Antigravity, etc.) reads the file itself, generates a high-quality summary, and injects it into the cache.

## 🚀 Execution Steps

1.  **Identify the document** (e.g., `docs/architecture_overview.md`).
2.  **Read the document** using `view_file`.
3.  **Read the summarization prompt** from [rlm_summarize_legacy.md](${CLAUDE_PLUGIN_ROOT}/resources/prompts/rlm/rlm_summarize_legacy.md).
4.  **Generate a high-quality summary** following the prompt's guidelines.
5.  **Execute the distiller** to inject your summary into the cache:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/distiller.py --file <path_to_doc> --type project --summary '<summary_text>'
```

6.  **Verify** that `rlm_summary_cache.json` is updated.

