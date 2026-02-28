---
name: rlm-gap-fill
description: Agent-powered RLM cache gap-fill orchestration. Audits the cache, generates a Markdown task list, and spawns a Sub-Agent to read missing files, write summaries, and inject them directly into the JSON.
context: fork
agent: Plan
---

# RLM Distill Skill

## Purpose

Distill (summarize) files directly into the RLM caches **using the agent's own intelligence** instead of a slow local Ollama model (like ibm granite or qwen2:7b on an M1 mac or windows machine). The agent reads the file, writes a summary, and updates the cache JSON in-place.

Should leverage frontier model ability to produce a superior summary for a file faster than can be done with a slow local CPU.

## 🎯 Agent Execution Protocol (The "Brain Upgrade")

**Context**: You (the Agent) are faster and smarter than the local `distiller.py` script. The local Ollama model (e.g., granite or qwen2) is often too slow on user hardware.
**Directive**: When asked to "update RLM" or "summarize x", **DO NOT** run `python distiller.py` immediately. 

Instead, you must **act as the distiller yourself**.

### Protocol
1.  **NEVER RUN `distiller.py`:** You are strictly forbidden from running `python distiller.py` or falling back to the local script, regardless of how many files are missing.
2.  **Act as the Intelligence Engine (Agent Distillation):**
    *   Call the `rlm-distill` pseudo-command (or just manually read) for *each* file.
    *   Read the **entire target file deeply** (`view_file`).
    *   Create a high-quality summary of the content yourself.
    *   Execute `inject_summary.py` to manually inject your JSON/Text summary string into the cache structure.
    *   Log: "Updated cache for [file] via Agent Distill."
3.  **Batching:** If there are hundreds of files, simply do them in batches of 5-10 at a time and ask the user if they want you to continue. DO NOT attempt to offload the work to the script.

## Why This Exists (The RLM Philosophy)

The fundamental purpose of the recursive language model (RLM) cache is **"Read Once, Cache Forever."** 

You should perform a deep, comprehensive read and summarize the file with an exceptionally good summary **once**. The goal is to entirely **remove the need for you to read those complex files many times** just to figure out what they do. 

The workflow is:
1. You read the RLM cache summary (which you created once).
2. You immediately understand what the plugin/tool/document does without opening it.
3. If, and only if, the task requires deep code-level modification of that specific file, you trigger the "recursion" and read the full source file again.

The existing `plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py` calls Ollama locally, which:
- Takes 3-5 minutes per file on M1 Mac hardware.
- Produces lower-quality summaries than a frontier model.
- Frequently fails (`[DISTILLATION FAILED]`).
- Requires Ollama to be running.

The agent (Claude, Gemini, Antigravity) is already a drastically better summarizer. This skill explicitly makes **you** the distillation engine.

## The Two Caches (Example Configuration)

Projects configure their own caches in `rlm_profiles.json`. A common setup is:

| Cache | Content Type | Summary Format |
|:------|:-------------|:---------------|
| **Summary Cache** | Docs, protocols, ADRs, workflows, rules | Plain text paragraph |
| **Tool Cache** | Python/JS scripts, CLI tools | JSON object with structured fields |

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
  "plugins/path/to/script.py": {
    "hash": "<content_hash_or_manual_marker>",
    "summary": "{\"purpose\": \"...\", \"layer\": \"...\", \"usage\": [...], \"args\": [...], \"inputs\": [...], \"outputs\": [...], \"dependencies\": [...], \"key_functions\": [...], \"consumed_by\": [...]}",
    "file_mtime": 1234567890.0,
    "summarized_at": "2026-02-11T18:30:00Z"
  }
}
```

**Note:** The tool cache `summary` field is a JSON **string** (not a nested object), matching the existing distiller's output format.

## The Agent Gap-Fill Workflow (Procedure)

When the user asks you to "audit and update the RLM cache" or "distill missing files", follow this exact cyclical workflow.

### 1. Identify Gaps & Generate Task List

First, run the RLM Auditor to generate an actionable checklist of all files missing from the cache.

```bash
# Generate the full checklist of missing files for the target profile
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile <profile_name> --tasks
```

This generates `rlm_distill_tasks_<profile_name>.md` in the project root, containing checkboxes and pre-written `inject_summary.py` commands for every missing file.

### 2. Deep File Analysis

Open the `rlm_distill_tasks_*.md` file and begin working through the checklist. For each file:

1. Open and thoroughly read the source file (e.g. using `view_file` or `cat`).
2. Do not skip or skim. You must understand the file's purpose, architecture, inputs, and outputs.

### 3. Generate Summary & Exact Prompt Alignment

Before writing the summary, you **MUST** align your output exactly with the rigorous standards defined in the official RLM prompts. 

**For code/scripts (Tool Cache / tools profile):**
Read and strictly adhere to the JSON schema demanded in:
> `plugins/tool-inventory/resources/prompts/rlm/rlm_summarize_tool.md`
Your output must be the raw, stringified JSON object matching that exact schema.

**For docs/markdown (Summary Cache / project profile):**
Read and strictly adhere to the high-fidelity architectural criteria demanded in:
> `plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_general.md`
Your output must be a dense, signal-heavy text summary.

### 4. Inject Summary & Track Progress

Execute the pre-written `inject_summary.py` command found in your task list for that file, replacing the placeholder with your generated string:

```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py --profile <profile_name> --file "path/to/file.py" --summary "YOUR COMPLETE SUMMARY TEXT OR JSON"
```

1. After the injection succeeds, **update the checkbox** (`[x]`) in the `rlm_distill_tasks_*.md` file to track your progress.
2. Proceed to the next missing file on the list.

### 5. Verify & Re-Audit

Once you have completed the checklist (or if you are ending your session), run the auditor again without the `--tasks` flag to prove the gap has been closed:

```bash
python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile <profile_name>
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
