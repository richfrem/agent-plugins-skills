---
description: Distill repository files into semantic summaries using Ollama (requires Ollama running)
argument-hint: "[--type legacy|tool] [--file path/to/file] [--model <model_name>] [--since N]"
---

# Distill Files into RLM Cache

Process files with a local LLM (Ollama) to generate one-sentence semantic summaries.
These summaries are stored in the RLM ledger for instant context retrieval.

## Prerequisites
- **Ollama must be running**: `ollama serve`
- **Model pulled**: `ollama pull granite3.2:8b` (default) or your preferred model

> [!TIP]
> `granite3.2:8b` is highly recommended for RLM distillation as it excels at generating concise, dense technical summaries.

## Configuration
The default model can be configured via a `.env` file in the **project root**:

```bash
# Configuration in <project_root>/.env
OLLAMA_MODEL=granite3.2:8b
OLLAMA_HOST=http://localhost:11434
```

## Usage
```bash
# Distill all files in default scope (legacy docs)
python3 plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile project

# Distill tool scripts
python3 plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile tools

# Distill a single file
python3 plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile project --file path/to/new_file.py

# Only files changed in the last 2 hours
python3 plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile project --since 2
```

## Memory Banks
| Type | Flag | Cache File |
|:---|:---|:---|
| Project Docs | `--profile project` | `rlm_summary_cache.json` |
| Tool Scripts | `--profile tools` | `rlm_tool_cache.json` |

## ⚠️ This is the WRITE operation — it calls Ollama and is expensive/slow.
For READ operations, use `/rlm-factory:query` instead.
