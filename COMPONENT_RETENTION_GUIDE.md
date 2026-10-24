# Repository Skill & Rule Configuration Guide

This guide lists which skills and rules to enable (`true`) or leave out (`false`) to keep agent context small, centred on the `running-control-plane` init workflow and core repository governance.

Skills are installed with APM from a materialized clone ([INSTALL.md](INSTALL.md), Option 1). The selection is APM's `--skill` list, saved in the global manifest `~/.apm/apm.yml` (or a project's `apm.yml`). Rules are not installed by APM: setup copies the enabled rules into a project's `.agent/rules/`, and `AGENTS.md` lists them there.

`--skill` selects skills only: APM still installs all of a plugin's agents (and hooks, for harnesses that support them).

Entries marked **not yet classified** are skills or rules that exist in the repository but have no recorded decision yet; review them and set `true` or `false`.

---

## 1. Quick Summary of Configuration Goals

- **Focus**: Maintain core repo governance, issue tracking, scaffolding, and the `running-control-plane` bootstrap.
- **De-bloat**: Leave out unused high-token agent patterns, RLM/vector stores, Obsidian wiki notes, and heavy prototyping pipelines until explicitly needed.

---

## 2. Skills Configuration (APM `--skill` selection)

### A. `agent-agentic-os` (control plane and skill lab)

| Skill | Status | Rationale |
|---|---|---|
| `running-control-plane` | **`true`** | Intake gateway, health check, transition simulator, worktree selection and the gating switch. Turn gating off per clone with `control_plane_mode.py disable` instead of uninstalling. |
| `setting-up-agentic-os` | **`true`** | Project init and retrofit, the agent's own simulation identity, and the human signing-key setup. Needs `running-control-plane` installed beside it. |
| `improving-skills-in-lab` | `false` | Opt-in: skill improvement lab (planning, isolated lab setup, improvement loop, KEEP/DISCARD scorer, log and charts, backport) and its session-memory mode. The evolution cycle in `running-control-plane` runs the lab's `evaluate.py`, so install both where evolution cycles are used. |

Install the enabled skills:

```bash
python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_consumer.py install --checkout . --global --plugins agent-agentic-os --skill running-control-plane --skill setting-up-agentic-os
```

---

### B. `agent-memory` (Agent Memory & Knowledge)

| Skill | Status | Rationale |
|---|---|---|
| `memory-management` | `false` | Filesystem memory and session continuity. |
| `managing-rlm-cache` | `false` | Summary ledger setup, search, distillation, audit, curation and cleanup. |
| `managing-vector-db` | `false` | ChromaDB setup, ingest, semantic query, audit, cleanup and server lifecycle. |
| `managing-obsidian-vaults` | `false` | Vault/Markdown/Bases/Canvas/graph operations and wiki build, distill, query and lint. |

Enable only the skills needed by the consumer. The former obsidian-wiki-engine
plugin is absorbed into agent-memory; standalone wiki installs select
`managing-obsidian-vaults` without vector or RLM dependencies.

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

### D. `agent-extension-authoring` (Authoring & APM Packaging)

| Skill | Status | Rationale |
|---|---|---|
| `authoring-skills` | **`true`** | Scaffolds, evaluates, and audits agent skills. |
| `authoring-plugins` | **`true`** | Scaffolds and audits whole plugins. |
| `authoring-subagents` | **`true`** | Scaffolds and audits sub-agents. |
| `authoring-instructions` | **`true`** | Scaffolds and audits governance instructions, AGENTS.md, rules, hooks. |
| `authoring-github-workflows` | **`true`** | Scaffolds GitHub workflows and Copilot custom agents. |
| `packaging-with-apm` | **`true`** | Packages, builds, and distributes via APM. |

Install the enabled skills:

```bash
python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_consumer.py install --checkout . --global --plugins agent-extension-authoring --skill authoring-skills --skill authoring-plugins --skill authoring-subagents --skill authoring-instructions --skill authoring-github-workflows --skill packaging-with-apm
```

---

### E. `cli-agents` (External CLI Bridges)

| Skill | Status | Rationale |
|---|---|---|
| `agt-security` | not yet classified |  |
| `cli-agent` | **`true`** | Dispatches tasks to Claude, Codex, Copilot, Agy and local llama CLIs; also covers local LLM setup, model catalog maintenance and project capability setup. |
| `maf-adapter` | `false` | Microsoft Agent Framework adapter. |

Install the enabled skills:

```bash
python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_consumer.py install --checkout . --global --plugins cli-agents --skill cli-agent
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
python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_consumer.py install --checkout . --global --plugins dev-utils --skill context-bundler --skill github-issue-agent --skill github-issue-backlog-agent --skill github-issue-pr-lifecycle-agent --skill github-issue-prioritizer --skill github-issue-worktree-agent --skill symlink-manager
```

---

### H. `agent-exploration-cycle` (Business Discovery & Prototyping)

| Skill | Status | Rationale |
|---|---|---|
| `running-exploration-cycle` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `capturing-business-requirements` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `building-interactive-prototypes` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `handing-off-to-engineering` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |
| `reengineering-vibe-code` | `false` | Off for lean development; enable only for product discovery or prototype reverse-engineering. |

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
3. **Undo the last change**: `python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_consumer.py rollback` (every `apm_consumer.py install` takes a backup first).
4. **Change a rule**: copy it into, or delete it from, the project's `.agent/rules/` and update the rules list in `AGENTS.md`.
