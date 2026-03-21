# HuggingFace Utils Plugin 🤗

Integration utilities for syncing the consuming project's remote dataset with the HuggingFace Hub.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install huggingface-utils
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/huggingface-utils
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/huggingface-utils

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install huggingface-utils
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/huggingface-utils
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

