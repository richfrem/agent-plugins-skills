---
description: High-speed RLM distillation of project documentation using agentic intelligence.
---

# Agent-Driven Distillation Workflow

Use the `rlm-distill` agent to summarize files into the RLM Summary Ledger
using frontier AI instead of slow local Ollama.

> For full protocol, quality standards, and swarm delegation: see [`rlm-distill` agent](../../plugins/rlm-factory/agents/rlm-distill.md)

## Steps

1. Run audit to find missing files:
```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile project
```

2. For each missing file -- read it deeply, generate a 1-sentence dense summary, inject:
```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py \
  --profile project \
  --file <path_to_file> \
  --summary "Your summary here."
```

3. For 50+ files -- delegate to the swarm (see rlm-distill agent for details).
