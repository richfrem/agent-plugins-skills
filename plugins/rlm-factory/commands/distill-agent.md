---
description: High-speed RLM distillation of project documentation using agentic intelligence.
---

# Agent-Driven Distillation Workflow

Use this workflow to bypass slow local Ollama models when summarizing files for the RLM
Summary Ledger. The agent reads the file itself, generates a high-quality summary, and
injects it via `inject_summary.py`.

> For full protocol, quality standards, and swarm delegation: see the `rlm-distill` agent

## Steps

1. Identify missing files:
```bash
python3 ./scripts/inventory.py --profile project
```

2. For each missing file -- read it deeply, generate a 1-sentence dense summary, inject:
```bash
python3 ./scripts/inject_summary.py \
  --profile project \
  --file <path_to_file> \
  --summary "Your summary here."
```

3. For 50+ files -- delegate to the swarm (see `rlm-distill` agent for details).
