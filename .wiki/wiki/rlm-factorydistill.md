---
concept: rlm-factorydistill
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_distill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.324143+00:00
cluster: ollama
content_hash: 9c3fe7545e3132f6
---

# /rlm-factory:distill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Distill repository files into the RLM Summary Ledger using agentic intelligence (fast) or Ollama (offline batch)
argument-hint: "[--profile project|tools] [--file path/to/file] [--since N]"
---

# /rlm-factory:distill

Summarize files into the RLM Summary Ledger. Two paths depending on context:

> **For detailed execution protocol, see agent:** `rlm-distill`

## Path 1 -- Agent Distillation (default, fast, no Ollama)

The agent reads each file and writes a high-quality summary via `inject_summary.py`.
Use for 1-50 files. The agent is faster and produces better summaries than local Ollama.

```bash
python ./scripts/inject_summary.py \
  --profile project \
  --file path/to/file.md \
  --summary "Your agent-generated summary here."
```

## Path 2 -- Ollama Batch (offline, bulk, 50+ files)

Requires Ollama running locally (`ollama serve`, model: `granite3.2:8b`).

```bash
# All files in profile scope
python ./scripts/distiller.py --profile project

# Single file
python ./scripts/distiller.py --profile project --file path/to/file.md

# Changed in last 2 hours
python ./scripts/distiller.py --profile project --since 2
```

| Profile | Flag | Cache file |
|:--------|:-----|:-----------|
| Docs / protocols | `--profile project` | `rlm_summary_cache.json` |
| Plugins / scripts | `--profile tools` | `rlm_tool_cache.json` |


## See Also

- [[obsidian-rlm-distiller]]
- [[rlm-factory-plugin]]
- [[rlm-core-philosophy-summarize-once-reuse-many]]
- [[rlm-core-philosophy-summarize-once-reuse-many]]
- [[audit-rlm-inventory]]
- [[rlm-factorycleanup]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_distill.md`
- **Indexed:** 2026-04-17T06:42:10.324143+00:00
