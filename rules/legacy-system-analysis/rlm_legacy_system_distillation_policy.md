---
trigger: manual
---

# Knowledge Sync Rule (RLM + Vector DB)

## Core Principle

**Every file change = immediate single-file sync.**

Do NOT wait to batch updates. When you create or modify a documentation file, immediately sync that ONE file to both caches. This prevents stale knowledge and eliminates big-bang rebuilds.

```bash
# Right after creating/editing a file:
python plugins/rlm-factory/scripts/distiller.py --file docs/ADRs/014-ai-assisted-prototyping.md
python plugins/vector-db/scripts/ingest.py --file docs/ADRs/014-ai-assisted-prototyping.md
```

## Trigger Conditions

Run sync when you have created or modified files in:
- `docs/` - ADRs, guides, analysis documents
- `legacy-system/` - Form overviews, business rules
- `plugins/` - Tool documentation (READMEs)
- `.agent/` - Rules, workflows, prompts

---

## Prerequisites

### Start Ollama (Required for RLM)
RLM distillation requires Ollama to be running. In a **separate WSL terminal**:
```bash
ollama serve
```

Then verify the model is available:
```bash
ollama list  # Should show granite3.2:8b or similar
```

If the model isn't installed:
```bash
ollama pull granite3.2:8b
```

---

## Part 1: RLM Distillation

### Quick Update (Specific Folders)
```bash
# WSL terminal - activate venv first
source .venv/bin/activate
# Update specific folders
python plugins/rlm-factory/scripts/distiller.py --target docs/ADRs
python plugins/rlm-factory/scripts/distiller.py --target docs/oracle-forms-visualizer
python plugins/rlm-factory/scripts/distiller.py --target plugins/context-bundler
python plugins/rlm-factory/scripts/distiller.py --target .agent/rules
```

### Full Rebuild (All Default Targets)
```bash
python plugins/rlm-factory/scripts/distiller.py
```

### Single File Update
```bash
python plugins/rlm-factory/scripts/distiller.py --file docs/ADRs/014-ai-assisted-prototyping.md
```

### Check Coverage
```bash
python plugins/rlm-factory/scripts/inventory.py
```

---

## Part 2: Vector DB Incremental Ingest

### Incremental Folder Update (Recommended)
```bash
# Ingest specific folders incrementally (no purge)
python plugins/vector-db/scripts/ingest.py --folder docs/ADRs
python plugins/vector-db/scripts/ingest.py --folder docs/oracle-forms-visualizer
python plugins/vector-db/scripts/ingest.py --folder plugins/context-bundler
python plugins/vector-db/scripts/ingest.py --folder .agent/rules
```

### Single File Ingest
```bash
python plugins/vector-db/scripts/ingest.py --file docs/ADRs/014-ai-assisted-prototyping.md
```

### Check Stats
```bash
python plugins/vector-db/scripts/query.py --stats
```

### Full Rebuild (Only if necessary)
```bash
# WARNING: Purges and rebuilds entire index (~10 min)
python plugins/vector-db/scripts/ingest.py --full
```

---

## Post-Creation Checklist

After creating documentation files:
- [ ] Run `distiller.py --target <folder>` for RLM updates
- [ ] Run `ingest.py --folder <folder>` for Vector DB updates
- [ ] Verify with `inventory.py` and `query.py --stats`

## Example: Today's Session

After adding multiple ADRs and docs:
```bash
# RLM updates
python plugins/rlm-factory/scripts/distiller.py --target docs/ADRs --target docs/oracle-forms-visualizer --target plugins/context-bundler --target .agent/rules

# Vector DB updates (incremental)
python plugins/vector-db/scripts/ingest.py --folder docs/ADRs
python plugins/vector-db/scripts/ingest.py --folder docs/oracle-forms-visualizer
python plugins/vector-db/scripts/ingest.py --folder plugins/context-bundler
python plugins/vector-db/scripts/ingest.py --folder .agent/rules
```

## AI Agent Automation Note

After creating multiple files in a single session, **always** provide the user with both commands:

```
To sync the knowledge caches with today's changes, run:

# RLM Cache
python plugins/rlm-factory/scripts/distiller.py --target docs/ADRs --target docs/oracle-forms-visualizer

# Vector DB
python plugins/vector-db/scripts/ingest.py --folder docs/ADRs
python plugins/vector-db/scripts/ingest.py --folder docs/oracle-forms-visualizer
```

---

## Cache Locations

| Cache | Location | Size |
|-------|----------|------|
| RLM | `.agent/learning/rlm_summary_cache.json` | ~200KB |
| Vector DB | `~/.agent/learning/chroma_db/` | ~50MB |

Both should be kept in sync. RLM updates are fast (~1s/file). Vector DB is slower (~2-5s/file) but enables semantic search.