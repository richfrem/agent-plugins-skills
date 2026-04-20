---
concept: agent-driven-distillation-workflow
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_distill-agent.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323957+00:00
cluster: files
content_hash: 63c58815ae5ad454
---

# Agent-Driven Distillation Workflow

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
python ./scripts/inventory.py --profile project
```

2. For each missing file -- read it deeply, generate a 1-sentence dense summary, inject:
```bash
python ./scripts/inject_summary.py \
  --profile project \
  --file <path_to_file> \
  --summary "Your summary here."
```

3. For 50+ files -- delegate to the swarm (see `rlm-distill` agent for details).


## See Also

- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_distill-agent.md`
- **Indexed:** 2026-04-17T06:42:10.323957+00:00
