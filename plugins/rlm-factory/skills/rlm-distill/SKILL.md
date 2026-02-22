---
name: rlm-distill
description: Agent-powered RLM cache distillation. Replaces the slow local Ollama distiller with the agent's own summarization capability for both rlm_summary_cache.json and rlm_tool_cache.json.
---

# RLM Distill Skill

## Purpose

Distill (summarize) files directly into the RLM caches **using the agent's own intelligence** instead of the slow local Ollama model (qwen2:7b on M1 Mac). The agent reads the file, writes a summary, and updates the cache JSON in-place.

Should leverage frontier model ability to produce a superior summary for a file faster than can be done with a slow local CPU.

## 🎯 Agent Execution Protocol (The "Brain Upgrade")

**Context**: You (the Agent) are faster and smarter than the local `distiller.py` script.
**Directive**: When asked to "update RLM" or "summarize x", **DO NOT** run `python distiller.py` immediately.

### Protocol
1.  **Check**: Is the request for < 10 files?
2.  **Action**: If YES -> **Read & Write Manually**.
    *   Read the target file (`view_file`).
    *   Generate the summary (Mental Step).
    *   Edit `rlm_summary_cache.json` or `rlm_tool_cache.json` directly (`replace_file_content` or `ed`).
    *   Log: "Updated cache for [file] via Agent Distill."
3.  **Fallback**: If NO (Batch > 10 files) -> Run `python distiller.py` (The script is better for bulk/boring work).

## Why This Exists

The existing `plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py` calls Ollama locally, which:
- Takes 3-5 minutes per file on M1 Mac
- Produces lower-quality summaries than a frontier model
- Frequently fails (`[DISTILLATION FAILED]` — currently 31 entries)
- Requires Ollama to be running

The agent (Claude, Gemini, Antigravity) is already a better summarizer. This skill cuts the middleman.

## The Two Caches

| Cache | Path | Content Type | Summary Format |
|:------|:-----|:-------------|:---------------|
| **Summary Cache** | `.agent/learning/rlm_summary_cache.json` | Docs, protocols, ADRs, workflows, rules | Plain text paragraph |
| **Tool Cache** | `.agent/learning/rlm_tool_cache.json` | Python/JS scripts, CLI tools | JSON object with structured fields |

### First Run?

If no cache exists yet, use the [`rlm-init`](../rlm-init/SKILL.md) skill to interactively set up cache location, manifest, and `.env` config before distilling.

## Cache Entry Schema

### Summary Cache Entry (docs/markdown)
```json
{
  "path/to/file.md": {
    "hash": "<content_hash_or_manual_marker>",
    "summary": "Plain text summary of the document...",
    "file_mtime": 1234567890.0,
    "summarized_at": "2026-02-11T18:30:00Z"
  }
}
```

### Tool Cache Entry (code/scripts)
```json
{
  "tools/path/to/script.py": {
    "hash": "<content_hash_or_manual_marker>",
    "summary": "{\"purpose\": \"...\", \"layer\": \"...\", \"usage\": [...], \"args\": [...], \"inputs\": [...], \"outputs\": [...], \"dependencies\": [...], \"key_functions\": [...], \"consumed_by\": [...]}",
    "file_mtime": 1234567890.0,
    "summarized_at": "2026-02-11T18:30:00Z"
  }
}
```

**Note:** The tool cache `summary` field is a JSON **string** (not a nested object), matching the existing distiller's output format.

## Procedure

### 1. Identify Files to Distill

Choose one of:

**A. Fix failed entries:**
```bash
# Find all DISTILLATION FAILED entries
grep -n "DISTILLATION FAILED" .agent/learning/rlm_summary_cache.json
```

**B. Distill new/changed files:**
```bash
# Find files modified in last N hours not yet in cache
find . -name "*.md" -mmin -120
```

**C. Distill specific files the user requests.**

### 2. Read the Source File

Read the file content using `view_file` or equivalent.

### 3. Write the Summary

**For docs/markdown (summary cache):** Write a concise, information-dense paragraph that captures:
- What the document is (purpose)
- Key architectural components or decisions
- Status and relationships to other documents
- NO filler phrases like "This document..." — go straight to substance

**For code/scripts (tool cache):** Write a JSON string with these fields:
- `purpose`: One-sentence description
- `layer`: Where it fits (e.g., "Curate / RLM", "Orchestrator")
- `usage`: Array of example commands
- `args`: Array of CLI arguments
- `inputs`: Array of input files/sources
- `outputs`: Array of output files/artifacts
- `dependencies`: Array of script dependencies
- `key_functions`: Array of important functions
- `consumed_by`: Array of consumers

### 4. Update the Cache JSON

Edit the cache file directly using file editing tools. Set:
- `hash`: Use `"agent_distilled_<date>"` as the hash marker (e.g., `"agent_distilled_2026_02_11"`)
- `summary`: Your summary text
- `summarized_at`: Current ISO timestamp
- `file_mtime`: (optional) File modification time if available

### 5. Verify

After editing, spot-check that the JSON is still valid:
```bash
python3 -c "import json; json.load(open('.agent/learning/rlm_summary_cache.json')); print('✅ Valid JSON')"
```

## Quality Guidelines

### Signal Over Noise
- Every summary should be **Signal**: a reader should learn the essential purpose and architecture from the summary alone
- Avoid **Noise**: don't pad with obvious observations, don't repeat the filename as the description
- A good summary lets the agent decide whether to read the full file without actually reading it

### Conciseness
- Summary cache: Target 2-5 sentences for simple docs, up to a paragraph for complex protocols
- Tool cache: Keep `purpose` to 1-2 sentences. Let the structured fields carry the detail.

### First Principles
- Summarize what the file **actually does**, not what it says it does
- If the file has a grand description but trivial implementation, note the gap
- Cross-reference related documents where architecturally significant

## Incremental vs Full

- **Incremental (preferred)**: Fix `[DISTILLATION FAILED]` entries and distill new files only
- **Full**: Only needed if the cache is severely stale or corrupted

## Integration with Existing Distiller

This skill **complements** the Ollama-based distiller — it doesn't replace the script. The script is still useful for:
- Batch processing hundreds of files unattended
- CI/CD pipelines where no agent is available
- Content hash tracking for change detection

The agent distillation is better for:
- Fixing failed entries quickly
- Distilling complex documents that need frontier-model comprehension
- On-demand updates during active sessions
- M1 Mac environments where Ollama is too slow

## Related

- `plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py` — Original Ollama-based distiller
- `plugins/rlm-factory/skills/rlm-curator/scripts/rlm_config.py` — Configuration and cache utilities
- `plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py` — Search the cache
- `plugins/rlm-factory/resources/rlm_manifest.json` — Defines which directories get distilled
