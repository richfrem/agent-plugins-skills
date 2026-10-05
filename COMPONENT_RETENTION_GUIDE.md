# Repository Skill & Rule Configuration Guide

This document catalogs which skills, rules, and agents should be enabled (`true`) versus disabled (`false`) when configuring this repository for minimal overhead, specifically centering around `os-init` workflows and core repository governance.

---

## 1. Quick Summary of Configuration Goals

- **Focus**: Maintain core repo governance, issue tracking, scaffolding, and the `os-init` bootstrap suite.
- **De-bloat**: Disable unused high-token agent patterns, RLM/vector stores, obsidian wiki notes, and heavy prototyping pipelines until explicitly needed.

---

## 2. Skills Configuration (`should_install: true / false`)

### A. `agent-agentic-os` (OS Kernel & Bootstrap)
| Skill | Status | Rationale |
|---|---|---|
| `os-init` | **`true`** | Core skill to bootstrap and retrofit Agentic OS, 3-Layer memory, and repo structure. |
| `os-health-check` | **`true`** | Verification gate required by `os-init` Phase 5 to confirm DB, memory, and substrate health. |
| `os-guide` | **`true`** | Architectural knowledge base and reference mappings used during `os-init`. |
| `os-signing-setup` | **`true`** | Guides SSH cryptographic human approval gate enrollment and verification. |
| `os-memory-manager` | **`true`** | Manages memory tiers (`MEMORY.md`, `context/memory.md`, session logs). |
| `critical-auditor` | `false` | Deep adversarial auditor loop; disabled for lean setup. |
| `work-intake` | `false` | Control-plane interview state machine; disable if doing direct/manual tasking. |
| `self-evolution` | `false` | Autonomous state-machine autoresearch loop; turn on only when mutating skills. |
| `worktree-manager` | `false` | Worktree orchestration engine; turn on if using automated isolated task worktrees. |
| `os-architect` | `false` | Architectural synthesis subagent; disable if doing manual architecture review. |
| `os-control-plane-mode` | `false` | Control-plane database mode switcher. |
| `os-environment-probe` | `false` | Standalone probe script (probed internally by `os-init`). |
| `os-evolution-verifier` | `false` | Receipt validation for autonomous evolution. |
| `os-clean-locks` | `false` | Standalone lock cleaner (handled by `os-health-check`). |
| `todo-check` | `false` | TODO comment scanner. |
| `transition-simulator` | `false` | Control-plane transition dry-run simulator. |
| `repository-improvement`| `false` | Automated friction cluster synthesizer. |
| `evo-smoketest` | `false` | Smoke test harness for evolution runs. |
| `os-eval-*` (5 skills) | `false` | Autoresearch headless lab runner and eval backporters. |

---

### B. `agent-memory` (Cognitive Memory & Retrieval)
*All components disabled unless building semantic / vector-search indexes.*

| Skill | Status | Rationale |
|---|---|---|
| `memory-management` | `false` | Standalone memory helper (covered by `os-memory-manager`). |
| `rlm-*` (6 skills) | `false` | Recursive Language Model summary ledger distillation & curation. |
| `vector-db-*` (6 skills)| `false` | ChromaDB vector storage, ingestion, and search. |

---

### C. `agent-orchestration` (Execution Topologies)
*All execution loop patterns disabled if operating directly through host agent.*

| Skill | Status | Rationale |
|---|---|---|
| `orchestrator` | `false` | Autonomous pattern router. |
| `select-loop-strategy` | `false` | DAG vs. swarm strategy classifier. |
| `graph-execution` | `false` | Deterministic DAG runner with join barriers. |
| `graph-planner` | `false` | Multi-agent DAG planner. |
| `agent-swarm` | `false` | Parallel multi-agent worker runner. |
| `co-pilot-loop` | `false` | QA Director + Worker companion loop. |
| `dual-loop` | `false` | Strategy packet worker delegation. |
| `learning-loop` | `false` | Autonomous research loop. |
| `triple-loop-learning` | `false` | Autoresearch mutation benchmark loop. |
| `red-team-review` | `false` | Multi-agent red-team review loop. |

---

### D. `dev-utils` (Core Developer Utilities)
| Skill | Status | Rationale |
|---|---|---|
| `symlink-manager` | **`true`** | **Critical**: Audits and restores repository symlinks across Windows/Linux. |
| `github-issue-agent` | **`true`** | Logs GitHub issues for bugs and friction events. |
| `github-issue-prioritizer` | **`true`** | Ranks issue priorities. |
| `context-bundler` | **`true`** | Bundles documentation/code for LLM context. |
| `github-issue-backlog-agent`| **`true`** | Backlog triage. |
| `github-issue-pr-lifecycle-agent`| **`true`** | PR lifecycle automation. |
| `github-issue-worktree-agent`| **`true`** | Worktree issue association. |
| `adr-management` | `false` | Architecture decision record scaffolding (optional). |
| `convert-mermaid` | `false` | Headless Mermaid to PNG renderer. |
| `humanize` | `false` | AI-to-human text rewriter. |
| `link-checker-agent` | `false` | Markdown URL link integrity checker. |
| `hf-*` (3 skills) | `false` | HuggingFace upload/download primitives. |

---

### E. `agent-scaffolders` & `plugin-manager`
| Skill | Status | Rationale |
|---|---|---|
| `create-skill` | **`true`** | Scaffolds standard skills. |
| `create-rule` | **`true`** | Scaffolds standard rules. |
| `create-plugin` | **`true`** | Scaffolds top-level plugins. |
| `audit-skill` | **`true`** | Validates skill structure and compliance. |
| `audit-plugin` | **`true`** | Audits plugin layout and `.claude-plugin/plugin.json`. |
| `manage-marketplace` | **`true`** | Manages catalog manifests. |
| `plugin-installer` | **`true`** | Deploys new plugins from local or GitHub sources. |
| `plugin-syncer` | **`true`** | Syncs desired-state manifests and cleans orphans. |
| `plugin-remover` | **`true`** | Uninstalls plugins cleanly. |
| `create-azure-agent` | `false` | Azure AI Foundry deployment scaffolder. |
| `create-docker-skill` | `false` | Docker skill environment scaffolder. |
| `create-agentic-workflow`| `false` | GitHub Agentic Workflow scaffolder. |
| `create-github-action` | `false` | CI/CD GitHub Action scaffolder. |
| `create-hook` | `false` | Hook scaffolder. |
| `create-mcp-integration`| `false` | MCP integration scaffolder. |
| `compile-apm-package` | `false` | APM bundle compiler. |
| `convert-plugin-to-apm` | `false` | APM converter. |
| `create-apm-package` | `false` | APM package scaffolder. |
| `install-apm-package` | `false` | APM package installer. |
| `ecosystem-*` | `false` | Reference specs. |

---

### F. `cli-agents` (External CLI Bridges)
| Skill | Status | Rationale |
|---|---|---|
| `claude-cli-agent` | **`true`** | Dispatches sub-tasks to Claude CLI. |
| `copilot-cli-agent` | **`true`** | Dispatches sub-tasks to Copilot CLI. |
| `codex-cli-agent` | **`true`** | Dispatches sub-tasks to OpenAI Codex CLI. |
| `agy-cli-agent` | **`true`** | Dispatches tasks via Antigravity CLI. |
| `project-setup` | **`true`** | Configures model capability profiles. |
| `local-llm-bridge` | `false` | Local Gemma/llama-server bridge. |
| `local-llm-setup` | `false` | Local inference stack setup wizard. |
| `maf-adapter` | `false` | Microsoft Agent Framework adapter. |
| `update-cli-models` | `false` | CLI model catalog updater. |

---

### G. `exploration-cycle-plugin` & `obsidian-wiki-engine`
*Turn all **`false`** for lean development.*
- **`exploration-cycle-plugin`**: 20 skills for business exploration and prototype reverse-engineering (`vibe-*`, `exploration-*`, `discovery-*`). Keep `false` unless doing product discovery.
- **`obsidian-wiki-engine`**: 10 skills for managing Obsidian canvas/bases/markdown notes. Keep `false` unless integrating directly into an Obsidian vault.

---

## 3. Rules Configuration (`.agent/rules/`)

| Rule File | Status | Purpose |
|---|---|---|
| `destructive-action-guard.md` | **`true`** | **Hard invariant**: Prevents accidental deletion of skills, files, and stand-in references. |
| `engineering-lifecycle-policy.md` | **`true`** | **Hard invariant**: Defines the 4-phase lifecycle and cryptographic approval human gate. |
| `adversarial-reasoning-before-agreement-rule.md`| **`true`** | Prevents sycophancy; forces stress-testing of major technical proposals. |
| `github-issue-logging-policy.md` | **`true`** | Standardizes friction and bug reporting to GitHub issues. |
| `self-evolution-policy.md` | **`true`** | Enforces the 3-attempt ceiling and pre-completion checklist gate. |
| `git-operations.md` | **`true`** | Prohibits unverified pushes and direct commits to main. |
| `symlink-cross-platform.md` | **`true`** | Enforces file-level symlink rules across Windows and POSIX. |
| `coding-conventions.md` | **`true`** | Standardizes Python and markdown formatting. |
| `dependency-management.md` | **`true`** | Governs virtual environment and requirements hygiene. |
| `config-driven-constants-over-hardcoding.md` | `false` | Optional rule for externalizing constant values. |
| `state-transition-guidance-compliance.md` | `false` | Specialized state machine transition rule. |
| `worktree-lifecycle-management.md` | `false` | Worktree vocabulary rule (needed if automated worktrees enabled). |
| `worktree-subagent-leak-detection.md` | `false` | Post-subagent leak detection rule. |
| `test-driven-development.md` | `false` | Detailed TDD red-green-refactor loop guidance. |

---

## 4. How to Apply Changes

Whenever you edit `.agents/ownership/<plugin>.json` or `plugin-retention.json`:
```bash
python plugins/plugin-manager/scripts/sync_with_inventory.py
```
This automatically prunes newly disabled items from `.agents/` and preserves enabled items.
