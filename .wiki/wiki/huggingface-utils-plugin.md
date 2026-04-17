---
concept: huggingface-utils-plugin
source: plugin-code
source_file: huggingface-utils/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.614846+00:00
cluster: plugin-code
content_hash: a13617b30b95f44d
---

# HuggingFace Utils Plugin 🤗

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# HuggingFace Utils Plugin 🤗

Integration utilities for syncing the consuming project's remote dataset with the HuggingFace Hub.

## Dependencies

The `hf-upload` skill requires `huggingface_hub`:

```bash
pip install -r requirements.txt
# or: pip install huggingface_hub
```

## Overview
This plugin provides the necessary skills and scripts to persist cognitive continuity data, RLM cache states, and deterministic traces up to a remote HuggingFace repository (the "Soul"), ensuring no agent learnings are lost between sessions.

## Core Capabilities
| Skill | Purpose |
| :--- | :--- |
| **hf-init** | Initialization script to validate connection and repo structure. |
| **forge-soul-exporter** | Gathers local traces and snapshot files and uploads them to the Hub. |

## Usage
These utilities are primarily invoked autonomously by the primary agent during the session closure configuration.

## Plugin Components

### Skills
- `hf-init`
- `hf-upload`

### Scripts
- `scripts/hf_config.py`



## See Also

- [[adr-manager-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[agent-plugin-analyzer]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `huggingface-utils/README.md`
- **Indexed:** 2026-04-17T06:42:09.614846+00:00
