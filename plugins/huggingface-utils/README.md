# HuggingFace Utils Plugin 🤗

Integration utilities for syncing the consuming project's remote dataset with the HuggingFace Hub.

## Installation
### Option 1: Skills Only (End Users)
```bash
npx skills add ./plugins/huggingface-utils
```
This installs the skills from this plugin.

### Option 2: Full Deployment (Skills + Commands + Agents)
For complete access to all components, use the bridge-plugin skill:
```bash
# Use the bridge-plugin skill to deploy all components
# python ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/huggingface-utils
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

