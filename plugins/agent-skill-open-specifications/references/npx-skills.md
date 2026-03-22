# Installation & Management (npx skills)

This document captures our accumulated knowledge and definitive specifications for installing, updating, and managing Agent Skills using the universal `npx skills` CLI.

## Overview
The `npx skills` CLI is the official open standard package manager for AI agent skills. It auto-detects installed agents (Claude Code, GitHub Copilot, Gemini CLI, Cursor, Roo Code, etc.) and seamlessly wires up the requested skills into their respective configuration environments.

## Installing from Remote Repositories
You can install single skills or entire curated collections directly from GitHub and other Git providers.

### Commands
- **Install a specific skill:**
  ```bash
  npx skills add <github-user>/<repo>/plugins/<plugin-name>
  ```
- **Install a full collection (entire repository):**
  ```bash
  npx skills add <github-user>/<repo>
  ```

### Notable Open Skill Collections
- **Agent Plugins (This Repo):** `npx skills add richfrem/agent-plugins-skills`
- **Anthropic Official:** `npx skills add anthropics/skills`
- **Microsoft Official:** `npx skills add microsoft/skills`

## Updating Skills
To universally update all installed skills across all of your agent environments to their latest available remotes:
```bash
npx skills update
```

## Local Development & Reinstallation
For skill developers and contributors, it is necessary to install and test skills from the local filesystem rather than a remote repository.

### Local Installation Commands
```bash
# Install a specific local plugin
npx skills add ./plugins/my-plugin --force

# Install the entire local plugins directory
npx skills add ./plugins/ --force
```

### CRITICAL: Avoiding Cache and Folder Lock Issues
When running `npx skills add` locally, the tool dereferences symlinks and packages the skills for the target environments. However, when attempting to overwrite an *existing* local installation, `npx` may encounter symlink caching issues or folder lock constraints (particularly with Python scripts or deeply nested resources).

To guarantee a clean local reinstallation during iterative development, you **must manually wipe the destination environment first**.

**Example (Antigravity/Universal Agents):**
```bash
# 1. Remove the existing agent skills folder
rm -rf .agents/

# 2. Perform a fresh forced installation
npx skills add ./plugins/my-plugin --force
```
Failing to remove the `.agents/` directory prior to a forced local overwrite will often result in silently skipped files or broken relative paths.
