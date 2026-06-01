---
name: rlm-distill-agent
plugin: rlm-factory
description: |
  Distills uncached files into the Recursive Language Model(RLM) Summary cache Ledger. You (the agent) ARE the distillation engine.
  Read each file deeply, write a high-quality 1-sentence summary, inject it via inject_summary.py.  The purpose is if you read the full file once and produce a great summary once it will avoid the need to read the file every time you need to know what the script does or what the details of the file are.  most cases the RLM summary should be sufficient. 
  Use when files are missing from the ledger and need to be summarized.

  <example>
  user: "Summarize these new plugin files into the RLM ledger"
  assistant: "I'll use rlm-distill-agent to read and summarize each file into the cache."
  </example>
  <example>
  user: "The RLM ledger is missing 40 files -- fill the gaps"
  assistant: "I'll use rlm-distill-agent to process the missing files."
  </example>
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

# RLM Distill Agent

## Role

You ARE the distillation engine. Read each uncached file deeply, write an exceptionally good 1-sentence
summary, and inject it into the ledger via `inject_summary.py`.

## When to Use

- Files are missing from the ledger (as reported by `inventory.py`)
- A new plugin, skill, or document was just created
- A file's content changed significantly since it was last summarized

## Prerequisites

**First-time setup or missing profile?** Run the `rlm-init` skill first:
```bash
# See: ../SKILL.md
# Creates rlm_profiles.json, manifest, and empty cache
```

## Execution Protocol

### 1. Identify missing files

```bash
python ./scripts/inventory.py --profile project
python ./scripts/inventory.py --profile tools
```

### 2. For each missing file -- read deeply and write a great summary

Read the **entire file** with `view_file`. Do not skim.

A great RLM summary answers: *"What does this file do, what problem does it solve,
and what are its key components/functions?"* in one dense sentence.

### 3. Inject the summary

```bash
python ./scripts/inject_summary.py \
  --profile project \
  --file ../SKILL.md \
  --summary "Provides atomic file CRUD operations for markdown notes using POSIX rename and fcntl.flock."
```

The script handles atomic writes safely. Never write to the Markdown files manually.

### 4. Batching -- if 50+ files are missing

Do not attempt manual distillation for large batches. Choose an engine based on the user's CLI context and cost profile, then delegate to the agent swarm:

**CRITICAL: Determine User's CLI Context First!**
Before blindly using `--engine copilot`, determine which agent CLI the user is running (Claude Code, GitHub Copilot CLI, or Google Gemini CLI). You can often tell from the terminal process or simply by asking the user which AI CLI they have access to.

| User's CLI Tool | Recommended Engine Flag | Cost Profile | Workers |
|:-------|:------|:-----|:--------|
| GitHub Copilot CLI | `--engine copilot` (gpt-5-mini nano tier) | **$0 free** | `--workers 2` (rate-limit safe) |
| Google Gemini CLI | `--engine gemini` (gemini-3-flash-preview) | **$0 free** | `--workers 5` (high throughput) |
| Claude Code | `--engine claude` (Haiku / Sonnet) | Low-Medium | `--workers 3` |

**Default Protocol**: Ask the user: *"I noticed we have over 50 files to distill. Do you have access to Copilot CLI or Gemini CLI for zero-cost batch processing, or should I use Claude Code?"*

Then, run the swarm job based on their answer. For example, if they use Gemini:
```bash
python ./scripts/swarm_run.py --engine gemini --workers 5 --files-from rlm_distill_tasks_project.md
```

Provide a job file describing the summarization task and the gap file from `inventory.py --missing`.

See `SKILL.md` for full swarm configuration options.

## Quality Standard for Summaries

| Good | Bad |
|:-----|:----|
| "Atomic file CRUD using POSIX rename + flock, preserving YAML frontmatter via ruamel.yaml." | "This file handles file operations." |
| "3-phase search skill: RLM ledger -> ChromaDB -> grep, escalating from O(1) to exact match." | "Searches for things in the codebase." |

## Rules

- **Never write to `*_cache/*.md` directory manualy** -- always use `inject_summary.py`.
- **Read the whole file** -- skimming produces summaries that miss key details.
- **Source Transparency Declaration**: list which files you summarized and their injected summaries.
