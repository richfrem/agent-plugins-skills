---
description: Distill repository files into the RLM Summary Ledger using agentic intelligence (fast) or Swarm Workers (offline batch)
argument-hint: "[--profile project|tools] [--file path/to/file]"
---

# /rlm-factory:distill

Summarize files into the RLM Summary Ledger. Two paths depending on context:

> **For detailed execution protocol, see agent:** `rlm-distill-agent`

## Path 1 -- Agent Distillation (default, fast, single file)

The agent reads each file and writes a high-quality summary via `inject_summary.py`.
Use for 1-10 files. The agent is faster for small batches.

```bash
python ./scripts/inject_summary.py \
  --profile project \
  --file path/to/file.md \
  --summary "Your agent-generated summary here."
```

## Path 2 -- Automated Swarm Batch (offline, bulk, 10+ files)

Delegates to `swarm_run.py` to fan-out processing across Copilot/Gemini.
> **Note:** Limit `--workers 2` when using `gpt-5-mini` on the free tier to avoid API throttling.

```bash
# All files in profile scope
python ./scripts/swarm_run.py --engine copilot --files-from rlm_distill_tasks_project.md

```

| Profile | Flag | Cache Location |
|:--------|:-----|:-----------|
| Docs / protocols | `--profile project` | `rlm_summary_cache/*.md` |
| Plugins / scripts | `--profile tools` | `rlm_tool_cache/*.md` |
