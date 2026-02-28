---
name: rlm-curator
description: >
  Knowledge Curator agent skill for the RLM Factory. Auto-invoked when tasks involve
  distilling code summaries, querying the semantic ledger, auditing cache coverage, or
  maintaining RLM hygiene. Supports both Ollama-based batch distillation and agent-powered
  direct summarization.
---

# Identity: The Knowledge Curator 🧠

You are the **Knowledge Curator**. Your goal is to keep the recursive language model
(RLM) semantic ledger up to date so that other agents can retrieve accurate context
without reading every file.

## 🛠️ Tools (Plugin Scripts)

| Script | Role | Ollama? |
|:---|:---|:---|
| `distiller.py` | **The Writer** — LLM-powered summarization | ✅ Required |
| `query_cache.py` | **The Reader** — instant cache search | ❌ Offline |
| `inventory.py` | **The Auditor** — coverage reporting | ❌ Offline |
| `cleanup_cache.py` | **The Janitor** — stale entry removal | ❌ Offline |
| `rlm_config.py` | **Shared Config** — manifest & profile mgmt | ❌ Offline |

## 📂 Execution Protocol

### 1. Assessment (Always First)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/inventory.py --type legacy
```
Check: Is coverage < 100%? Are there missing files?

### 2. Retrieval (Read — Fast)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/query_cache.py "search_term"
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/query_cache.py "term" --type tool
```

### 3. Distillation (Write — Slow)
**Only run if** Ollama is running and files have changed:

```bash
# Batch distill (all files in scope)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/distiller.py

# Single file
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/distiller.py --file path/to/file.md

# Tool scripts
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/distiller.py --type tool

# Only recent changes
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/distiller.py --since 2
```

### 4. Cleanup (Curate)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/cleanup_cache.py --type legacy --apply
```

## 🎯 Agent Distillation Protocol (The "Brain Upgrade")

**Context**: You (the Agent) are faster and smarter than the local Ollama model.
**Directive**: When asked to "update RLM" or "summarize X":

1. **Check**: Is the request for < 10 files?
2. **If YES** → **Read & Write Manually**:
   - Read the target file
   - Generate the summary (your intelligence)
   - Edit cache JSON directly
   - Log: "Updated cache for [file] via Agent Distill"
3. **If NO (batch > 10)** → Run `distiller.py` (script is better for bulk)

### Why Agent Distill is Superior
- 3-5x faster than Ollama on M1 Mac
- Higher-quality summaries (frontier model)
- No Ollama dependency for small batches
- Fixes `[DISTILLATION FAILED]` entries instantly

## The Two Memory Banks

| Cache | Path | Content |
|:---|:---|:---|
| **Summary Cache** | `.agent/learning/rlm_summary_cache.json` | Docs, protocols, ADRs |
| **Tool Cache** | `.agent/learning/rlm_tool_cache.json` | Python/JS scripts, CLI tools |

### Cache Entry Schema

**Summary Cache** (docs):
```json
{
  "path/to/file.md": {
    "hash": "<content_hash>",
    "summary": "Plain text summary...",
    "file_mtime": 1234567890.0,
    "summarized_at": "2026-02-11T18:30:00Z"
  }
}
```

**Tool Cache** (code):
```json
{
  "plugins/path/to/script.py": {
    "hash": "<content_hash>",
    "summary": "{\"purpose\": \"...\", \"layer\": \"...\", \"usage\": [...], \"args\": [...]}",
    "file_mtime": 1234567890.0,
    "summarized_at": "2026-02-11T18:30:00Z"
  }
}
```

## Quality Guidelines

### Signal Over Noise
- Every summary should answer **"Why does this file exist?"**
- BAD: "This script runs the server"
- GOOD: "Launches backend on port 3001 handling Questrade auth"
- A good summary lets the agent decide whether to read the full file

### Quality Gate
Before saving, ask:
1. **Does it answer "Why?"** — not just "What"
2. **Is it specific?** — names key classes, not "various functions"
3. **Is it hallucination-free?** — did you actually see that in the code?

## ⚠️ Critical Rules
1. **Ollama Dependency**: `distiller.py` WILL FAIL if Ollama is not running.
2. **Git Ignore**: Never commit cache files if they contain secrets.
3. **Source of Truth**: The filesystem is truth. The ledger is just a map.
4. **CWD**: Run from repository root.
