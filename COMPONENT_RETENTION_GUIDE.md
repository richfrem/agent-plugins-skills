# Repository Skill & Rule Configuration Guide

This guide lists which skills and rules to enable (`true`) or leave out (`false`) to keep agent context small, centred on `os-control-init` workflows and core repository governance.

Skills are installed with APM from a materialized clone ([INSTALL.md](INSTALL.md), Option 1). The selection is APM's `--skill` list, saved in the global manifest `~/.apm/apm.yml` (or a project's `apm.yml`). Rules are not installed by APM: setup copies the enabled rules into a project's `.agent/rules/`, and `AGENTS.md` lists them there.

`--skill` selects skills only: APM still installs all of a plugin's agents (and hooks, for harnesses that support them).

Entries marked **not yet classified** are skills or rules that exist in the repository but have no recorded decision yet; review them and set `true` or `false`.

---

## 1. Quick Summary of Configuration Goals

- **Focus**: Maintain core repo governance, issue tracking, scaffolding, and the `os-control-init` bootstrap suite.
- **De-bloat**: Leave out unused high-token agent patterns, RLM/vector stores, Obsidian wiki notes, and heavy prototyping pipelines until explicitly needed.

---

## 2. Skills Configuration (APM `--skill` selection)

### A. `agent-agentic-os` (OS Kernel & Bootstrap)

| Skill | Status | Rationale |
|---|---|---|
| `os-control-health` | **`true`** | Verification gate required by `os-control-init` Phase 5 to confirm DB, memory, and substrate health. |
| `os-control-init` | **`true`** | Core skill to bootstrap and retrofit Agentic OS, 3-Layer memory, and repo structure. |
| `os-control-intake` | `false` | Control-plane interview state machine; disable if doing direct/manual tasking. |
| `os-control-mode` | `false` | Control-plane database mode switcher. |
| `os-control-signing-setup` | **`true`** | Guides SSH cryptographic human approval gate enrollment and verification. |
| `os-control-simulator` | `false` | Control-plane transition dry-run simulator. |
| `os-control-worktree` | `false` | Worktree orchestration engine; turn on if using automated isolated task worktrees. |
| `os-lab-backport` | `false` | Skill improvement lab: isolated lab setup, improvement loop, KEEP/DISCARD scorer, backport review, run log and charts. |
| `os-lab-log` | `false` | Skill improvement lab: isolated lab setup, improvement loop, KEEP/DISCARD scorer, backport review, run log and charts. |
| `os-lab-loop` | `false` | Skill improvement lab: isolated lab setup, improvement loop, KEEP/DISCARD scorer, backport review, run log and charts. |
| `os-lab-memory` | **`true`** | Manages memory tiers (`MEMORY.md`, `context/memory.md`, session logs). |
| `os-lab-planner` | `false` | Architectural synthesis subagent; disable if doing manual architecture review. |
| `os-lab-scorer` | `false` | Skill improvement lab: isolated lab setup, improvement loop, KEEP/DISCARD scorer, backport review, run log and charts. |
| `os-lab-setup` | `false` | Skill improvement lab: isolated lab setup, improvement loop, KEEP/DISCARD scorer, backport review, run log and charts. |

Install the enabled skills:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --checkout . --global --plugins agent-agentic-os --skill os-control-health --skill os-control-init --skill os-control-signing-setup --skill os-lab-memory
```

---

### B. `agent-memory` (Cognitive Memory & Retrieval)

| Skill | Status | Rationale |
|---|---|---|
| `memory-management` | `false` | Standalone memory helper (covered by `os-lab-memory`). |
| `rlm-audit` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `rlm-cleanup-agent` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `rlm-curator` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `rlm-distill-agent` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `rlm-init` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `rlm-search` | `false` | Recursive Language Model summary ledger distillation & curation. |
| `vector-db-audit` | `false` | ChromaDB vector storage, ingestion, and search. |
| `vector-db-cleanup` | `false` | ChromaDB vector storage, ingestion, and search. |
| `vector-db-ingest` | `false` | ChromaDB vector storage, ingestion, and search. |
| `vector-db-init` | `false` | ChromaDB vector storage, ingestion, and search. |
| `vector-db-launch` | `false` | ChromaDB vector storage, ingestion, and search. |
| `vector-db-search` | `false` | ChromaDB vector storage, ingestion, and search. |

No skills enabled: do not install this plugin.

---

### C. `agent-orchestration` (Execution Topologies)

| Skill | Status | Rationale |
|---|---|---|
| `agent-swarm` | `false` | Parallel multi-agent worker runner. |
| `co-pilot-loop` | `false` | QA Director + Worker companion loop. |
| `dual-loop` | `false` | Strategy packet worker delegation. |
| `graph-execution` | `false` | Deterministic DAG runner with join barriers. |
| `graph-planner` | `false` | Multi-agent DAG planner. |
| `learning-loop` | `false` | Autonomous research loop. |
| `orchestrator` | `false` | Autonomous pattern router. |
| `red-team-review` | `false` | Multi-agent red-team review loop. |
| `select-loop-strategy` | `false` | DAG vs. swarm strategy classifier. |
| `triple-loop-learning` | `false` | Autoresearch mutation benchmark loop. |

No skills enabled: do not install this plugin.

---

### D. `agent-scaffolders` (Scaffolding, Auditing & APM)

| Skill | Status | Rationale |
|---|---|---|
| `audit-agents-md` | not yet classified |  |
| `audit-plugin` | **`true`** | Audits plugin layout and `.claude-plugin/plugin.json`. |
| `audit-rule` | not yet classified |  |
| `audit-skill` | **`true`** | Validates skill structure and compliance. |
| `audit-sub-agent` | not yet classified |  |
| `compile-apm-package` | `false` | APM bundle compiler. |
| `convert-plugin-to-apm` | `false` | APM converter. |
| `create-agentic-workflow` | `false` | GitHub Agentic Workflow scaffolder. |
| `create-agents-md` | not yet classified |  |
| `create-apm-package` | `false` | APM package scaffolder. |
| `create-azure-agent` | `false` | Azure AI Foundry deployment scaffolder. |
| `create-docker-skill` | `false` | Docker skill environment scaffolder. |
| `create-github-action` | `false` | CI/CD GitHub Action scaffolder. |
| `create-hook` | `false` | Hook scaffolder. |
| `create-mcp-integration` | `false` | MCP integration scaffolder. |
| `create-plugin` | **`true`** | Scaffolds top-level plugins. |
| `create-rule` | **`true`** | Scaffolds standard rules. |
| `create-skill` | **`true`** | Scaffolds standard skills. |
| `create-stateful-skill` | not yet classified |  |
| `create-sub-agent` | not yet classified |  |
| `ecosystem-authoritative-sources` | `false` | Reference specs. |
| `ecosystem-standards` | `false` | Reference specs. |
| `install-apm-package` | `false` | APM package installer. |
| `manage-marketplace` | **`true`** | Manages catalog manifests. |

Install the enabled skills:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --checkout . --global --plugins agent-scaffolders --skill audit-plugin --skill audit-skill --skill create-plugin --skill create-rule --skill create-skill --skill manage-marketplace
```

---

### E. `cli-agents` (External CLI Bridges)

| Skill | Status | Rationale |
|---|---|---|
| `agent-file-synchronization` | not yet classified |  |
| `agt-security` | not yet classified |  |
| `agy-cli-agent` | **`true`** | Dispatches tasks via Antigravity CLI. |
| `claude-cli-agent` | **`true`** | Dispatches sub-tasks to Claude CLI. |
| `codex-cli-agent` | **`true`** | Dispatches sub-tasks to OpenAI Codex CLI. |
| `copilot-cli-agent` | **`true`** | Dispatches sub-tasks to Copilot CLI. |
| `local-llm-bridge` | `false` | Local Gemma/llama-server bridge. |
| `local-llm-setup` | `false` | Local inference stack setup wizard. |
| `maf-adapter` | `false` | Microsoft Agent Framework adapter. |
| `project-setup` | **`true`** | Configures model capability profiles. |
| `update-cli-models` | `false` | CLI model catalog updater. |

Install the enabled skills:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --checkout . --global --plugins cli-agents --skill agy-cli-agent --skill claude-cli-agent --skill codex-cli-agent --skill copilot-cli-agent --skill project-setup
```

---

### F. `dependency-management` (Dependency Workflow)

| Skill | Status | Rationale |
|---|---|---|
| `dependency-management` | not yet classified |  |

No skills enabled: do not install this plugin.

---

### G. `dev-utils` (Core Developer Utilities)

| Skill | Status | Rationale |
|---|---|---|
| `adr-management` | `false` | Architecture decision record scaffolding (optional). |
| `coding-conventions-agent` | not yet classified |  |
| `context-bundler` | **`true`** | Bundles documentation/code for LLM context. |
| `convert-mermaid` | `false` | Headless Mermaid to PNG renderer. |
| `github-issue-agent` | **`true`** | Logs GitHub issues for bugs and friction events. |
| `github-issue-backlog-agent` | **`true`** | Backlog triage. |
| `github-issue-pr-lifecycle-agent` | **`true`** | PR lifecycle automation. |
| `github-issue-prioritizer` | **`true`** | Ranks issue priorities. |
| `github-issue-refactor-proposer` | `false` | Automated friction cluster synthesizer. |
| `github-issue-resolution-reviewer` | not yet classified |  |
| `github-issue-worktree-agent` | **`true`** | Worktree issue association. |
| `hf-download` | `false` | HuggingFace upload/download primitives. |
| `hf-init` | `false` | HuggingFace upload/download primitives. |
| `hf-upload` | `false` | HuggingFace upload/download primitives. |
| `humanize` | `false` | AI-to-human text rewriter. |
| `link-checker-agent` | `false` | Markdown URL link integrity checker. |
| `optimize-context` | not yet classified |  |
| `symlink-manager` | **`true`** | **Critical**: Audits and restores repository symlinks across Windows/Linux. |
| `todo-check` | not yet classified |  |

Install the enabled skills:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --checkout . --global --plugins dev-utils --skill context-bundler --skill github-issue-agent --skill github-issue-backlog-agent --skill github-issue-pr-lifecycle-agent --skill github-issue-prioritizer --skill github-issue-worktree-agent --skill symlink-manager
```

---

### H. `exploration-cycle-plugin` (Business Discovery & Prototyping)

| Skill | Status | Rationale |
|---|---|---|
| `business-requirements-capture` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `business-workflow-doc` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `discovery-planning` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `exploration-handoff` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `exploration-optimizer` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `exploration-session-brief` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `exploration-workflow` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `prototype-builder` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `subagent-driven-prototyping` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `user-story-capture` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `using-exploration-cycle` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-behavioral-test-capture` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-browser-audit` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-domain-extractor` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-reengineer` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-slice-migrator` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-spec-packager` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-to-speckit-superpowers` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `vibe-togaf-architect` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `visual-companion` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |

No skills enabled: do not install this plugin.

---

### I. `obsidian-wiki-engine` (Obsidian Vault & Wiki)

| Skill | Status | Rationale |
|---|---|---|
| `obsidian-bases-manager` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-canvas-architect` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-graph-traversal` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-init` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-markdown-mastery` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-query-agent` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-rlm-distiller` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-vault-crud` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-wiki-builder` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |
| `obsidian-wiki-linter` | `false` | Off for lean development; enable only when integrating directly with an Obsidian vault. |

No skills enabled: do not install this plugin.

---

### J. `plugin-manager` (Decommissioned)

> Legacy `uvx` / `plugin-add` installer has been fully retired and removed following the APM migration (plan Section 9). Replaced entirely by Microsoft APM CLI (`apm install`).

| Skill | Status | Rationale |
|---|---|---|
| `plugin-installer` | **retired** | Replaced by `apm install`. |
| `plugin-remover` | **retired** | Replaced by `apm uninstall`. |
| `plugin-syncer` | **retired** | Replaced by `apm install` / `apm update`. |

---

## 3. Rules Configuration (`.agent/rules/`)

Rules stay outside APM. Setup copies each enabled rule from its plugin's `rules/` folder (or keeps the repository copy) into the project's `.agent/rules/`, and `AGENTS.md` links it.

| Rule File | Status | Purpose |
|---|---|---|
| `adversarial-reasoning-before-agreement-rule.md` | **`true`** | Prevents sycophancy; forces stress-testing of major technical proposals. |
| `background-document-priority.md` | not yet classified |  |
| `coding-conventions.md` | **`true`** | Standardizes Python and markdown formatting. |
| `config-driven-constants-over-hardcoding.md` | `false` | Optional rule for externalizing constant values. |
| `cryptographic-human-gates.md` | not yet classified |  |
| `dependency-management.md` | **`true`** | Governs virtual environment and requirements hygiene. |
| `deployment-decision-principles.md` | not yet classified |  |
| `destructive-action-guard.md` | **`true`** | **Hard invariant**: Prevents accidental deletion of skills, files, and stand-in references. |
| `engineering-lifecycle-policy.md` | **`true`** | **Hard invariant**: Defines the 4-phase lifecycle and cryptographic approval human gate. |
| `git-operations.md` | **`true`** | Prohibits unverified pushes and direct commits to main. |
| `github-issue-logging-policy.md` | **`true`** | Standardizes friction and bug reporting to GitHub issues. |
| `graph-planning-superpowers-policy.md` | not yet classified |  |
| `plugin-architecture-policy.md` | not yet classified |  |
| `pre-push-audit.md` | not yet classified |  |
| `schema-driven-sharepoint-deployment.md` | not yet classified |  |
| `self-evolution-policy.md` | **`true`** | Enforces the 3-attempt ceiling and pre-completion checklist gate. |
| `skill-deletion-guard.md` | not yet classified |  |
| `spec-driven-development-policy.md` | not yet classified |  |
| `state-transition-guidance-compliance.md` | `false` | Specialized state machine transition rule. |
| `symlink-cross-platform.md` | **`true`** | Enforces file-level symlink rules across Windows and POSIX. |
| `test-driven-development.md` | `false` | Detailed TDD red-green-refactor loop guidance. |
| `test-driven-wave-deployment.md` | not yet classified |  |
| `worktree-lifecycle-management.md` | `false` | Worktree vocabulary rule (needed if automated worktrees enabled). |
| `worktree-subagent-leak-detection.md` | `false` | Post-subagent leak detection rule. |

---

## 4. How to Apply Changes

1. **Change a skill selection**: add skills with another install command (`--skill` adds to the selection), or edit the `skills:` list for that plugin in `~/.apm/apm.yml` and run:
   ```bash
   apm install --global
   ```
2. **Leave a plugin out entirely**: `apm uninstall <path-to-clone>/plugins/<plugin> --global`.
3. **Undo the last change**: `python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py rollback` (every `apm_consumer.py install` takes a backup first).
4. **Change a rule**: copy it into, or delete it from, the project's `.agent/rules/` and update the rules list in `AGENTS.md`.
