# Universal Agent Plugins & Skills Ecosystem

Welcome to the central Open Standard Agent repository. This repository functions as a universal capability registry, fundamentally designed **for AI agents, by AI agents**. 

## Project Overview

This is a strictly cross-platform (Windows, Mac, Ubuntu) library that serves as a universal deployment source for multiple IDEs and agent frameworks, including:
- **Claude Code** (`.claude/`)
- **GitHub Copilot** (`.github/`)
- **Gemini CLI / Antigravity** (`.gemini/`, `.agent/`)
- **Roo Code**, **Windsurf**, **Cursor**, and other compliant integrations.

Instead of keeping documentation trapped in disparate folders, this site serves as the navigable master hub for all active agent skills and capabilities.

---

## Installation

Use the `npx skills` CLI to install plugins directly into your agent environment. It auto-detects installed agents (Claude Code, GitHub Copilot, Gemini, Cursor, and 30+ others) and wires everything up natively.

### Installing from GitHub

```bash
# Install all plugins from this repo
npx skills add richfrem/agent-plugins-skills

# Install a single plugin
npx skills add richfrem/agent-plugins-skills/plugins/rlm-factory
npx skills add richfrem/agent-plugins-skills/plugins/vector-db
npx skills add richfrem/agent-plugins-skills/plugins/spec-kitty-plugin

# Update all installed skills to latest
npx skills update
```

### Installing Locally (For Contributors / Local Dev)

If you are developing or modifying plugins locally, you can install them directly from the local filesystem instead of pulling from GitHub.

> [!WARNING]
> When testing local changes to a skill, `npx` may cache previous symlinks or encounter folder lock issues when overwriting. Before reinstalling your local changes, you **must remove the existing destination folders** first.

```bash
# First, remove the existing agent skills folder to prevent caching/lock issues

# remove a specific skill first check list 
npx skills list

#remove a specific skill 
npx skills remove skill-name

# Remove all skills from all agents
rm -rf .agents/
npx skills remove --all -y

# Install a specific local plugin
npx skills add ./plugins/rlm-factory --force

# Install the entire local plugins directory
npx skills add ./plugins/ --force
```

> **Why this works**: each plugin in `plugins/` contains a `SKILL.md` following the [open agent skills standard](https://skills.sh/docs). The CLI reads it and configures your IDE automatically.

Browse all available plugins and their install status at:
**[skills.sh/richfrem/agent-plugins-skills](https://skills.sh/richfrem/agent-plugins-skills)**


---

## Core Architecture: Agent Loops

The system relies heavily on the **[Agent Loops](plugins/agent-loops/README.md)** architecture, a sophisticated routing system that unifies state management across complex agent executions. 

Agent Loops ensure **shared closure** across all operations, which means no session terminates without saving memory (persisting context snapshots), formalizing learnings (distillation), and sealing its actions. The architectural flows are categorized into 5 core behavior patterns:

1. **[Orchestrator](plugins/agent-loops/skills/orchestrator/SKILL.md)**: The intelligent task router and lifecycle administrator that initiates and concludes sessions.
2. **[Simple Learning Loop](plugins/agent-loops/skills/learning-loop/SKILL.md)**: The foundational pattern for research, contextual integration, and continuous memory persistence.
3. **[Red Team Review](plugins/agent-loops/skills/red-team-review/SKILL.md)**: An adversarial, multi-agent evaluation framework used to stress-test designs and catch architectural drift.
4. **[Dual-Loop](plugins/agent-loops/skills/dual-loop/SKILL.md)**: An inner execution / outer verification paradigm for complex, multi-step engineering assignments requiring ongoing correction.
5. **[Agent Swarm](plugins/agent-loops/skills/agent-swarm/SKILL.md)**: A parallelized execution framework enabling concurrent sub-agents to process distinct tasks simultaneously on independent worktrees.

---

## Site Navigation & Plugin Ecosystem

This repository currently hosts **28 distinct plugin packages** containing over extensive modular agent skills. Below is the complete manifest of capabilities, each linked to its respective definition document (`SKILL.md`).

### Architecture & Design
- **ADR Manager** — Automatically draft and syndicate Architecture Decision Records.
  ↳ [`adr-management`](plugins/adr-manager/skills/adr-management/SKILL.md)

### Agent Operations & Management
- **Agent Scaffolders** — Interactive creators to scaffold exact file hierarchies for plugins, skills, hooks, Azure API wrappers, GitHub workflows, and MCP configurations.
  ↳ [`audit-plugin`](plugins/agent-scaffolders/skills/audit-plugin/SKILL.md)
  ↳ [`create-agentic-workflow`](plugins/agent-scaffolders/skills/create-agentic-workflow/SKILL.md)
  ↳ [`create-azure-agent`](plugins/agent-scaffolders/skills/create-azure-agent/SKILL.md)
  ↳ [`create-github-action`](plugins/agent-scaffolders/skills/create-github-action/SKILL.md)
  ↳ [`create-hook`](plugins/agent-scaffolders/skills/create-hook/SKILL.md)
  ↳ [`create-legacy-command`](plugins/agent-scaffolders/skills/create-legacy-command/SKILL.md)
  ↳ [`create-mcp-integration`](plugins/agent-scaffolders/skills/create-mcp-integration/SKILL.md)
  ↳ [`create-plugin`](plugins/agent-scaffolders/skills/create-plugin/SKILL.md)
  ↳ [`create-skill`](plugins/agent-scaffolders/skills/create-skill/SKILL.md)
  ↳ [`create-sub-agent`](plugins/agent-scaffolders/skills/create-sub-agent/SKILL.md)
- **Plugin Manager** — The authoritative suite for ensuring ecosystem health, synchronization, garbage collection, and artifact bootstrapping.
  ↳ [`ecosystem-cleanup-sync`](plugins/plugin-manager/skills/ecosystem-cleanup-sync/SKILL.md)
  ↳ [`plugin-bootstrap`](plugins/plugin-manager/skills/plugin-bootstrap/SKILL.md)
  ↳ [`plugin-maintenance`](plugins/plugin-manager/skills/plugin-maintenance/SKILL.md)
  ↳ [`plugin-replicator`](plugins/plugin-manager/skills/plugin-replicator/SKILL.md)
- **Plugin Mapper** — Intelligent transpiler that maps universal `.md` tasks to IDE-specific rule configurations (e.g. converting prompts for `.claude/`).
  ↳ [`agent-bridge`](plugins/plugin-mapper/skills/agent-bridge/SKILL.md)

### Standards & Hygiene
- **Agent Skill Open Specifications** — The canonical documentation for agents on how to construct compliant skills and directory architectures.
  ↳ [`ecosystem-authoritative-sources`](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/SKILL.md)
  ↳ [`ecosystem-standards`](plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md)
- **Coding Conventions** — Centralized rules engine for standardizing file headers and `snake_case/camelCase/PascalCase` semantics across multiple languages.
  ↳ [`coding-conventions`](plugins/coding-conventions/skills/coding-conventions/SKILL.md)
  ↳ [`conventions-agent`](plugins/coding-conventions/skills/conventions-agent/SKILL.md)
- **JSON Hygiene** — Agentic scanner detecting broken configuration values (e.g., duplicated keys masked by standard JSON parsers).
  ↳ [`json-hygiene-agent`](plugins/json-hygiene/skills/json-hygiene-agent/SKILL.md)

### Data & Code Manipulation
- **Context Bundler** — Tooling to package deep directory contexts and code traces into single readable files.
  ↳ [`context-bundling`](plugins/context-bundler/skills/context-bundling/SKILL.md)
- **Dependency Management** — Handles cross-platform pip-compile workflows securely.
  ↳ [`dependency-management`](plugins/dependency-management/skills/dependency-management/SKILL.md)
- **Excel to CSV** — Flat file extraction module for ingestion and parsing.
  ↳ [`excel-to-csv`](plugins/excel-to-csv/skills/excel-to-csv/SKILL.md)

### Agent Persona CLI Interfaces
Sub-systems allowing fresh, isolated model context spaces for advanced tasks (audits, QA, external validation).
- **Claude CLI Agent**
  ↳ [`claude-cli-agent`](plugins/claude-cli/skills/claude-cli-agent/SKILL.md)
- **Copilot CLI Agent**
  ↳ [`copilot-cli-agent`](plugins/copilot-cli/skills/copilot-cli-agent/SKILL.md)
- **Gemini CLI Agent**
  ↳ [`gemini-cli-agent`](plugins/gemini-cli/skills/gemini-cli-agent/SKILL.md)

### Artificial Constraints & Vectors
- **Environment Helper** — Universal resolver for constant integration values across environments.
  ↳ [`env-helper`](plugins/env-helper/skills/env-helper/SKILL.md)
- **HuggingFace Utils** — Snapshot persistence and HuggingFace Soul repository lifecycle actions.
  ↳ [`hf-init`](plugins/huggingface-utils/skills/hf-init/SKILL.md)
  ↳ [`hf-upload`](plugins/huggingface-utils/skills/hf-upload/SKILL.md)
- **Memory Management** — Orchestrates multi-tiered cognition and context caching between long-term persistent storage and active memory files.
  ↳ [`memory-management`](plugins/memory-management/skills/memory-management/SKILL.md)

### Authoring & Documentation
- **Doc Coauthoring** — Iterative and collaborative tech specification drafting.
  ↳ [`doc-coauthoring`](plugins/doc-coauthoring/skills/doc-coauthoring/SKILL.md)
- **Link Checker** — Continuous markdown hyperlink validation.
  ↳ [`link-checker-agent`](plugins/link-checker/skills/link-checker-agent/SKILL.md)
- **Markdown to MSWord Converter** — Interoperability translator for non-technical stakeholders.
  ↳ [`markdown-to-msword-converter`](plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/SKILL.md)
- **Mermaid to PNG** — Diagram exporter and renderer.
  ↳ [`convert-mermaid`](plugins/mermaid-to-png/skills/convert-mermaid/SKILL.md)

### Feature Driven Engineering
- **Spec Kitty Suite** — The massive enterprise-grade Spec-Driven Development implementation layer handling the `Spec -> Plan -> Tasks -> Implement -> Merge` workflow autonomously.
  ↳ [`spec-kitty-accept`](plugins/spec-kitty-plugin/skills/spec-kitty-accept/SKILL.md)
  ↳ [`spec-kitty-agent`](plugins/spec-kitty-plugin/skills/spec-kitty-agent/SKILL.md)
  ↳ [`spec-kitty-analyze`](plugins/spec-kitty-plugin/skills/spec-kitty-analyze/SKILL.md)
  ↳ [`spec-kitty-checklist`](plugins/spec-kitty-plugin/skills/spec-kitty-checklist/SKILL.md)
  ↳ [`spec-kitty-clarify`](plugins/spec-kitty-plugin/skills/spec-kitty-clarify/SKILL.md)
  ↳ [`spec-kitty-constitution`](plugins/spec-kitty-plugin/skills/spec-kitty-constitution/SKILL.md)
  ↳ [`spec-kitty-dashboard`](plugins/spec-kitty-plugin/skills/spec-kitty-dashboard/SKILL.md)
  ↳ [`spec-kitty-implement`](plugins/spec-kitty-plugin/skills/spec-kitty-implement/SKILL.md)
  ↳ [`spec-kitty-init`](plugins/spec-kitty-plugin/skills/spec-kitty-init/SKILL.md)
  ↳ [`spec-kitty-merge`](plugins/spec-kitty-plugin/skills/spec-kitty-merge/SKILL.md)
  ↳ [`spec-kitty-plan`](plugins/spec-kitty-plugin/skills/spec-kitty-plan/SKILL.md)
  ↳ [`spec-kitty-research`](plugins/spec-kitty-plugin/skills/spec-kitty-research/SKILL.md)
  ↳ [`spec-kitty-review`](plugins/spec-kitty-plugin/skills/spec-kitty-review/SKILL.md)
  ↳ [`spec-kitty-specify`](plugins/spec-kitty-plugin/skills/spec-kitty-specify/SKILL.md)
  ↳ [`spec-kitty-status`](plugins/spec-kitty-plugin/skills/spec-kitty-status/SKILL.md)
  ↳ [`spec-kitty-sync-plugin`](plugins/spec-kitty-plugin/skills/spec-kitty-sync-plugin/SKILL.md)
  ↳ [`spec-kitty-tasks`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks/SKILL.md)
  ↳ [`spec-kitty-update`](plugins/spec-kitty-plugin/skills/spec-kitty-update/SKILL.md)
  ↳ [`spec-kitty-workflow`](plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md)
- **Task Manager** — Kanban board synchronization and task lane transitions.
  ↳ [`task-agent`](plugins/task-manager/skills/task-agent/SKILL.md)

### Knowledge Base / Vector Stores
- **Obsidian Integration** — Bi-directional sync translating standard codebase folders into fully operational Graph Vaults inside Obsidian.
  ↳ [`obsidian-bases-manager`](plugins/obsidian-integration/skills/obsidian-bases-manager/SKILL.md)
  ↳ [`obsidian-canvas-architect`](plugins/obsidian-integration/skills/obsidian-canvas-architect/SKILL.md)
  ↳ [`obsidian-graph-traversal`](plugins/obsidian-integration/skills/obsidian-graph-traversal/SKILL.md)
  ↳ [`obsidian-init`](plugins/obsidian-integration/skills/obsidian-init/SKILL.md)
  ↳ [`obsidian-markdown-mastery`](plugins/obsidian-integration/skills/obsidian-markdown-mastery/SKILL.md)
  ↳ [`obsidian-vault-crud`](plugins/obsidian-integration/skills/obsidian-vault-crud/SKILL.md)
- **RLM Factory** — Reverse Language Modeling engine generating high-speed offline functional cache representations of code.
  ↳ [`ollama-launch`](plugins/rlm-factory/skills/ollama-launch/SKILL.md)
  ↳ [`rlm-curator`](plugins/rlm-factory/skills/rlm-curator/SKILL.md)
  ↳ [`rlm-distill`](plugins/rlm-factory/agents/rlm-distill.md) *(agent)*
  ↳ [`rlm-cleanup`](plugins/rlm-factory/agents/rlm-cleanup.md) *(agent)*
  ↳ [`rlm-init`](plugins/rlm-factory/skills/rlm-init/SKILL.md)
  ↳ [`tool-inventory-init`](plugins/rlm-factory/skills/tool-inventory-init/SKILL.md)
- **Tool Inventory** — Vector-search registry for all python scripts making them accessible to agents without hard-coded rules.
  ↳ [`tool-inventory`](plugins/tool-inventory/skills/tool-inventory/SKILL.md)
- **Vector DB** — ChromaDB driven continuous semantic embedding indexing module for native codebase integration search.
  ↳ [`vector-db-search`](plugins/vector-db/skills/vector-db-agent/SKILL.md) *(read-only skill)*
  ↳ [`vdb-ingest`](plugins/vector-db/agents/vdb-ingest.md) *(agent)*
  ↳ [`vdb-cleanup`](plugins/vector-db/agents/vdb-cleanup.md) *(agent)*
  ↳ [`vector-db-init`](plugins/vector-db/skills/vector-db-init/SKILL.md)
  ↳ [`vector-db-launch`](plugins/vector-db/skills/vector-db-launch/SKILL.md)

### Utilities
- **Migration Utils** — Standard scripts utilized during extensive codebase restructuring architectures.
  ↳ [`migration-utils`](plugins/migration-utils/skills/migration-utils/SKILL.md)

---
*Generated autonomously via Agent Extensions.*
