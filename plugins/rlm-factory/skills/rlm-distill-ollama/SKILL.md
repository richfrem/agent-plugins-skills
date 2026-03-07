---
description: Distill repository files into the RLM Summary Ledger using agentic intelligence (fast) or Ollama (offline batch)
argument-hint: "[--profile project|tools] [--file path/to/file] [--since N]"
---

# /rlm-factory:distill

Summarize files into the RLM Summary Ledger. Two paths depending on context:

> **For detailed execution protocol, see agent:** [`rlm-distill-agent`](../rlm-distill-agent/SKILL.md)

## Path 1 -- Agent Distillation (default, fast, no Ollama)

The agent reads each file and writes a high-quality summary via `inject_summary.py`.
Use for 1-50 files. The agent is faster and produces better summaries than local Ollama.

```bash
python3 plugins/rlm-factory/skills/rlm-distill-agent/scripts/inject_summary.py \
  --profile project \
  --file path/to/file.md \
  --summary "Your agent-generated summary here."
```

## Path 2 -- Ollama Batch (offline, bulk, 50+ files)

Requires Ollama running locally (`ollama serve`, model: `granite3.2:8b`).

```bash
# All files in profile scope
python3 plugins/rlm-factory/skills/rlm-distill-ollama/scripts/distiller.py --profile project

# Single file
python3 plugins/rlm-factory/skills/rlm-distill-ollama/scripts/distiller.py --profile project --file path/to/file.md

# Changed in last 2 hours
python3 plugins/rlm-factory/skills/rlm-distill-ollama/scripts/distiller.py --profile project --since 2
```

| Profile | Flag | Cache file |
|:--------|:-----|:-----------|
| Docs / protocols | `--profile project` | `rlm_summary_cache.json` |
| Plugins / scripts | `--profile tools` | `rlm_tool_cache.json` |
