---
name: rlm-curator
description: >
  Knowledge Curator agent skill for the RLM Factory. Auto-invoked when tasks involve
  distilling code summaries, querying the semantic ledger, auditing cache coverage, or
  maintaining RLM hygiene. Supports both Ollama-based batch distillation and agent-powered
  direct summarization. V2 enforces Concurrency Safety constraints.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Identity: The Knowledge Curator 🧠

You are the **Knowledge Curator**. Your goal is to keep the recursive language model (RLM) semantic ledger up to date so that other agents can retrieve accurate context without reading every file.

## Tools (Plugin Scripts)

| Script | Role |
|:---|:---|
| `swarm_run.py` | **The Writer (Swarm)** — automated batch summarization |
| `inject_summary.py` | **The Writer (Single)** -- direct agent-generated injection |
| `inventory.py` | **The Auditor** -- coverage reporting |
| `cleanup_cache.py` | **The Janitor** -- stale entry removal |
| `rlm_config.py` | **Shared Config** -- manifest & profile mgmt |

> **Searching the cache?** Use the [`rlm-search` skill](../rlm-search/SKILL.md) and its `query_cache.py` script.

## Architectural Constraints (The "Electric Fence")

The RLM Cache is an optimized architecture producing isolated Markdown files per component.

### ❌ WRONG: Manual Cache Manipulation (Negative Instruction Constraint)
**NEVER** manually create the `.agent/learning/rlm_summary_cache/*.md` files using raw bash or tool blocks. Doing so could result in skipped indexing or lost metadata fields.

### ✅ CORRECT: Curatorial Scripts
**ALWAYS** use `inject_summary.py` or `swarm_run.py` to write to the cache directories. These scripts handle the atomic file writing and schema consistency perfectly.

---

## 📂 Execution Protocol

### 1. Assessment (Always First)
```bash
python ./scripts/inventory.py --type legacy
```
Check: Is coverage < 100%? Are there missing files?

### 2. Retrieval (Read -- Fast)
Use the **`rlm-search`** skill for all cache queries:
```bash
python ./scripts/query_cache.py --profile plugins "search_term"
python ./scripts/query_cache.py --profile tools --list
```

### 3. Distillation (Write)

#### Option B: Zero-Cost Swarm (Preferred for bulk > 10 files)
Use the Copilot swarm (free, gpt-5-mini) or Gemini swarm (free).

Delegate to the `agent-loops:agent-swarm` skill, providing:
- Engine: `copilot` (free default) or `gemini` (higher throughput)
- Job: provide a job file describing the summarization task
- Files: gap list from `inventory.py --missing`
- Workers: `2` for copilot (rate-limit safe), `5` for gemini


#### Option C: Manual Agent Injection (< 5 files)
```bash
python ./scripts/inject_summary.py \
  --profile project \
  --file path/to/file.md \
  --summary "Your dense summary here..."
```

### 4. Cleanup (Curate)
```bash
python ./scripts/cleanup_cache.py --profile project --apply
```

## Quality Guidelines
Every summary injected should answer **"Why does this file exist?"**
- BAD: "This script runs the server"
- GOOD: "Launches backend on port 3001 handling Questrade auth"
