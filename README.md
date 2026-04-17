# Universal Agent Plugins & Skills Ecosystem

## Project Overview

A strictly cross-platform (Windows, Mac, Ubuntu) library that serves as the universal upstream source for reusable AI agent plugins and skills across multiple IDEs and agent frameworks:

- **Claude Code**, **GitHub Copilot**, **Gemini CLI**, **Antigravity**, **Roo Code**, **Windsurf**, **Cursor**, and other compliant integrations.
- *Now universally supporting the single `.agents/` folder standard (no duplicate copies needed for `.github`, `.gemini`, `.agent`, etc).*

**119 skills** across **27 plugins** — all maintained from a single hub-and-spoke source tree.

---

## Core Philosophy: Transitional Architectures & Decoupled Skills

This repository is built on a pragmatic acceptance of the current AI engineering landscape: **the ecosystem changes weekly, and workflows that were revolutionary six months ago are obsolete today.**

Frameworks like `agent-agentic-os` and `spec-kitty` are treated as **Transitional Architectures** — bridges between what agents need to do today and what native SDKs will eventually handle. When Anthropic, Google, and GitHub harden native memory persistence, execution safety, and multi-agent orchestration, large swaths of this tooling will be happily discarded.

**Skills are Applications; the SDK is the OS.** Individual skills must function in complete isolation — no hard dependencies on sibling plugins, no assumptions about which framework is running.

---

## Installation

> [!IMPORTANT]
> **Start here — fresh clone or first-time setup.** The single `.agents/` environment directory is **not committed** to your repo. It will be empty by default.
>
> All installation methods (**uvx**, **bootstrap.py**, **npx skills**, and **Marketplace / Extension CLI**) are now consolidated in a single authoritative guide:
>
> ### 👉 [Go to INSTALL.md](./INSTALL.md)

---

## Architecture Highlights

### Triple-Loop Autonomous Skill Improvement

The `agent-agentic-os` plugin implements a **Triple-Loop** architecture for continuous, autonomous skill improvement:

| Layer | Agent | Role |
|:---|:---|:---|
| **L0** | `triple-loop-architect` (Claude) | Interactive setup: scaffolds isolated sibling lab, seeds all files, launches L1 |
| **L1** | Gemini CLI (`gemini --yolo --model gemini-3-flash-preview`) | Headless orchestrator: reads `eval-instructions.md`, runs the loop, gates via `evaluate.py` |
| **L2** | Copilot CLI (`gpt-5-mini`) | Cheap mutation proposer: proposes SKILL.md edits using free Copilot quota |

The loop is autonomous and cost-effective: L2 uses GitHub Copilot's `gpt-5-mini` (free quota), enabling 20–80 mutation proposals per run at near-zero cost. L1 (Gemini Flash) orchestrates unattended overnight. `evaluate.py` is the absolute gate — exit 0 = KEEP, exit 1 = DISCARD + auto-revert.

**Not all skills are good candidates** — the best targets have clear, objective routing criteria and adversarial eval cases. Use [`eval-autoresearch-fit`](plugins/agent-plugin-analyzer/skills/eval-autoresearch-fit/SKILL.md) to score a skill before running a loop.

**To start a loop on any skill:**
```
@triple-loop-architect

Kick off a 10-iteration Triple-Loop optimization run targeting the `<skill-name>` skill
inside the `<plugin-folder>` plugin. Use gemini-3-flash-preview as L1 and gpt-5-mini as L2.
```
See the full sample prompt: [`references/sample-prompts/triple-loop-architect-prompt.md`](plugins/agent-agentic-os/references/sample-prompts/triple-loop-architect-prompt.md)

**Live example — `convert-mermaid` skill, 26 iterations across 2 rounds: 0.61 → 1.00**

![convert-mermaid eval progress](plugins/mermaid-to-png/skills/convert-mermaid/evals/eval_progress.png)

Each blue diamond is a baseline anchor (one per session). Green = new best score. Amber = kept but not a record. The two-segment shape shows a fresh re-baseline for round 2 — the plotter handles this automatically.

Monitor a live run: `python3 plugins/agent-agentic-os/scripts/plot_eval_progress.py --tsv <lab>/evals/ --live`

**Flywheel layers:**
- **OUTER flywheel** (`os-improvement-loop`): improves OS-level protocols and session ledgers between sessions
- **INNER flywheel** (`os-eval-runner` + `os-skill-improvement`): improves individual skill routing accuracy within a session
- **Overnight** (`os-nightly-evolver`): runs the INNER flywheel unattended — see [`agents/os-nightly-evolver.md`](plugins/agent-agentic-os/agents/os-nightly-evolver.md)

### Karpathy Autoresearch Loop

Skills that score HIGH on the autoresearch viability rubric (objectivity + speed + frequency + utility) can run fully autonomous self-improvement loops:

```
mutate SKILL.md → evaluate.py → exit 0 (KEEP) or exit 1 (DISCARD) → repeat
```

**Ecosystem Fitness Sweep v1 is complete** — all 116/120 production skills scored for autoresearch viability. Results:

| Verdict | Count | Loop Type breakdown |
|---|---|---|
| HIGH | 9 | DETERMINISTIC: 41 · LLM_IN_LOOP: 59 · HYBRID: 16 |
| MEDIUM | 52 | |
| LOW | 42 | |
| NOT_VIABLE | 13 | |

Full ranked list: [`summary-ranked-skills.json`](plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json)
Top 20 opportunities with metrics + blockers: [`autoresearch-opportunities-report.md`](plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/autoresearch-opportunities-report.md)

**First live autoresearch loop**: `verification-before-completion` from `obra/superpowers` (35/40 HIGH) — golden task set + `evaluate.py` scaffolded, ready to run.

### Hub-and-Spoke ADR

All shared scripts live once at `plugins/<plugin>/scripts/`. Skills reference them via file-level symlinks (`skills/<skill>/scripts/script.py → ../../../scripts/script.py`). Directory-level symlinks are forbidden — `npx` drops them on install.

---

## Plugin Ecosystem (27 plugins · 119 skills)

### Agentic OS — Continuous Self-Improvement

The flagship operational framework. Implements the Dual-Flywheel architecture for autonomous skill evolution, memory management, eval-gated improvement loops, and session lifecycle protocols.

- [`os-guide`](plugins/agent-agentic-os/skills/os-guide/SKILL.md) — master orientation + skill taxonomy
- [`os-improvement-loop`](plugins/agent-agentic-os/skills/os-improvement-loop/SKILL.md) — OUTER flywheel: 7-step session improvement protocol
- [`os-eval-lab-setup`](plugins/agent-agentic-os/skills/os-eval-lab-setup/SKILL.md) — bootstrap eval experiment dir (evals.json, results.tsv, program.md)
- [`os-eval-runner`](plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md) — INNER flywheel gate: evaluate.py KEEP/DISCARD engine
- [`os-skill-improvement`](plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md) — RED-GREEN-REFACTOR skill mutation
- [`os-eval-backport`](plugins/agent-agentic-os/skills/os-eval-backport/SKILL.md) — backport approved improvements to master plugin sources
- [`os-memory-manager`](plugins/agent-agentic-os/skills/os-memory-manager/SKILL.md) — Phase 6/7 learning promotion to persistent memory
- [`os-improvement-report`](plugins/agent-agentic-os/skills/os-improvement-report/SKILL.md) — progress charts and score trajectory reports
- [`os-init`](plugins/agent-agentic-os/skills/os-init/SKILL.md) — OS bootstrap and kernel initialization
- [`os-clean-locks`](plugins/agent-agentic-os/skills/os-clean-locks/SKILL.md) — directory lock recovery
- [`todo-check`](plugins/agent-agentic-os/skills/todo-check/SKILL.md) — session TODO hygiene
- [`optimize-agent-instructions`](plugins/agent-agentic-os/skills/optimize-agent-instructions/SKILL.md) — audit and rewrite CLAUDE.md, GEMINI.md, and copilot-instructions.md; applies Karpathy's four behavioral principles, strips stale/foreign content, detects installed Super-RAG layers, adds platform-specific sections

**Agents:**
- [`os-learning-loop`](plugins/agent-agentic-os/agents/os-learning-loop.md) — retrospective + friction analysis sub-agent
- [`os-nightly-evolver`](plugins/agent-agentic-os/agents/os-nightly-evolver.md) — bounded autonomous overnight skill evolution (Gemini CLI mutations + evaluate.py gate)
- [`os-health-check`](plugins/agent-agentic-os/agents/os-health-check.md) — OS liveness metrics
- [`agentic-os-setup`](plugins/agent-agentic-os/agents/agentic-os-setup.md) — OS initialization agent

### Agent Loops — Execution Patterns

Routing architecture unifying state management across complex agent executions with shared closure.

- [`orchestrator`](plugins/agent-loops/skills/orchestrator/SKILL.md) — intelligent task router and lifecycle manager
- [`learning-loop`](plugins/agent-loops/skills/learning-loop/SKILL.md) — research, contextual integration, memory persistence
- [`dual-loop`](plugins/agent-loops/skills/dual-loop/SKILL.md) — inner execution / outer verification for multi-step tasks
- [`agent-swarm`](plugins/agent-loops/skills/agent-swarm/SKILL.md) — parallelized concurrent sub-agents on independent worktrees
- [`red-team-review`](plugins/agent-loops/skills/red-team-review/SKILL.md) — adversarial multi-agent evaluation

### Execution Disciplines — Safety & Quality

Behavioural guardrails enforcing best practices on every coding session. These skills come from [`obra/superpowers`](https://github.com/obra/superpowers) — install that plugin to get them. This ecosystem builds on superpowers rather than duplicating it.

**Install:** `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add obra/superpowers`

Skills available via superpowers: `verification-before-completion` · `test-driven-development` · `using-git-worktrees` · `systematic-debugging` · `finishing-a-development-branch` · `requesting-code-review`

### Agent Scaffolders — Boilerplate Generators

Interactive creators for exact file hierarchies across all plugin/skill types.

- [`create-plugin`](plugins/agent-scaffolders/skills/create-plugin/SKILL.md) · [`create-skill`](plugins/agent-scaffolders/skills/create-skill/SKILL.md) · [`create-sub-agent`](plugins/agent-scaffolders/skills/create-sub-agent/SKILL.md)
- [`create-command`](plugins/agent-scaffolders/skills/create-command/SKILL.md) · [`create-hook`](plugins/agent-scaffolders/skills/create-hook/SKILL.md) · [`create-github-action`](plugins/agent-scaffolders/skills/create-github-action/SKILL.md)
- [`create-agentic-workflow`](plugins/agent-scaffolders/skills/create-agentic-workflow/SKILL.md) · [`create-azure-agent`](plugins/agent-scaffolders/skills/create-azure-agent/SKILL.md)
- [`create-docker-skill`](plugins/agent-scaffolders/skills/create-docker-skill/SKILL.md) · [`create-mcp-integration`](plugins/agent-scaffolders/skills/create-mcp-integration/SKILL.md)
- [`create-stateful-skill`](plugins/agent-scaffolders/skills/create-stateful-skill/SKILL.md) · [`manage-marketplace`](plugins/agent-scaffolders/skills/manage-marketplace/SKILL.md)

### Agent Plugin Analyzer — Plugin Quality Audits

Structured audit framework for assessing plugin architectural maturity and compliance.

- [`l5-red-team-auditor`](plugins/agent-plugin-analyzer/skills/l5-red-team-auditor/SKILL.md) — 39-point L5 maturity matrix audit
- [`audit-plugin`](plugins/agent-plugin-analyzer/skills/audit-plugin/SKILL.md) · [`audit-plugin-l5`](plugins/agent-plugin-analyzer/skills/audit-plugin-l5/SKILL.md)
- [`analyze-plugin`](plugins/agent-plugin-analyzer/skills/analyze-plugin/SKILL.md) · [`self-audit`](plugins/agent-plugin-analyzer/skills/self-audit/SKILL.md) *(32/40 HIGH)*
- [`mine-skill`](plugins/agent-plugin-analyzer/skills/mine-skill/SKILL.md) · [`mine-plugins`](plugins/agent-plugin-analyzer/skills/mine-plugins/SKILL.md)
- [`path-reference-auditor`](plugins/agent-plugin-analyzer/skills/path-reference-auditor/SKILL.md) · [`synthesize-learnings`](plugins/agent-plugin-analyzer/skills/synthesize-learnings/SKILL.md)
- [`eval-autoresearch-fit`](plugins/agent-plugin-analyzer/skills/eval-autoresearch-fit/SKILL.md) — score any skill for Karpathy autoresearch loop viability; update `summary-ranked-skills.json` *(25/40 MEDIUM)*

### CLI Sub-Agents — Isolated Model Contexts

Dispatch specialized analysis to fresh model contexts via CLI tools (security audits, architecture review, QA).

- [`claude-cli-agent`](plugins/claude-cli/skills/claude-cli-agent/SKILL.md) · [`claude-project-setup`](plugins/claude-cli/skills/claude-project-setup/SKILL.md)
- [`copilot-cli-agent`](plugins/copilot-cli/skills/copilot-cli-agent/SKILL.md) — GPT-5 mini via Copilot CLI; used in autoresearch mutation delegation
- [`gemini-cli-agent`](plugins/gemini-cli/skills/gemini-cli-agent/SKILL.md) · [`antigravity-project-setup`](plugins/gemini-cli/skills/antigravity-project-setup/SKILL.md)

### Coding Conventions

Centralized rules engine for file headers, naming conventions, and linting across Python, TypeScript, and C#. *(autoresearch score: 34/40 HIGH)*

- [`coding-conventions-agent`](plugins/coding-conventions/skills/coding-conventions-agent/SKILL.md)

### Context Bundler — Context Packaging

Package deep directory contexts and code traces into single payloads for external LLM review.

- [`context-bundler`](plugins/context-bundler/skills/context-bundler/SKILL.md) *(29/40 MEDIUM)*
- [`red-team-bundler`](plugins/context-bundler/skills/red-team-bundler/SKILL.md) — structured red team review payload generator

### Dependency Management

Cross-platform pip-compile workflows with strict `.in` → `.txt` lockfile discipline.

- [`dependency-management`](plugins/dependency-management/skills/dependency-management/SKILL.md)

### Excel to CSV

Headless batch conversion of Excel workbooks to CSV for data pipeline ingestion.

- [`excel-to-csv`](plugins/excel-to-csv/skills/excel-to-csv/SKILL.md)

### Exploration Cycle — Discovery & Requirements

Autonomous discovery loop for idea framing, business requirements, user stories, prototyping, and handoff into formal engineering specs.

- [`exploration-workflow`](plugins/exploration-cycle-plugin/skills/exploration-workflow/SKILL.md) · [`exploration-session-brief`](plugins/exploration-cycle-plugin/skills/exploration-session-brief/SKILL.md)
- [`business-requirements-capture`](plugins/exploration-cycle-plugin/skills/business-requirements-capture/SKILL.md) · [`business-workflow-doc`](plugins/exploration-cycle-plugin/skills/business-workflow-doc/SKILL.md)
- [`user-story-capture`](plugins/exploration-cycle-plugin/skills/user-story-capture/SKILL.md) · [`exploration-handoff`](plugins/exploration-cycle-plugin/skills/exploration-handoff/SKILL.md)
- [`exploration-optimizer`](plugins/exploration-cycle-plugin/skills/exploration-optimizer/SKILL.md)

*Deferred (scaffolded, not yet active):*
- [`exploration-orchestrator`](plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/SKILL.md) — full-cycle orchestrator coordinating discovery agents end-to-end
- [`prototype-builder`](plugins/exploration-cycle-plugin/skills/deferred/prototype-builder/SKILL.md) — builds exploratory prototypes to make ambiguous product direction concrete

### Feature-Driven Engineering — Spec Kitty Suite

Enterprise-grade Spec-Driven Development: `Spec → Plan → Tasks → Implement → Review → Merge`.

- [`spec-kitty-specify`](plugins/spec-kitty-plugin/skills/spec-kitty-specify/SKILL.md) · [`spec-kitty-plan`](plugins/spec-kitty-plugin/skills/spec-kitty-plan/SKILL.md) · [`spec-kitty-tasks`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks/SKILL.md)
- [`spec-kitty-implement`](plugins/spec-kitty-plugin/skills/spec-kitty-implement/SKILL.md) · [`spec-kitty-review`](plugins/spec-kitty-plugin/skills/spec-kitty-review/SKILL.md) · [`spec-kitty-merge`](plugins/spec-kitty-plugin/skills/spec-kitty-merge/SKILL.md)
- [`spec-kitty-analyze`](plugins/spec-kitty-plugin/skills/spec-kitty-analyze/SKILL.md) · [`spec-kitty-accept`](plugins/spec-kitty-plugin/skills/spec-kitty-accept/SKILL.md) · [`spec-kitty-clarify`](plugins/spec-kitty-plugin/skills/spec-kitty-clarify/SKILL.md)
- [`spec-kitty-research`](plugins/spec-kitty-plugin/skills/spec-kitty-research/SKILL.md) · [`spec-kitty-dashboard`](plugins/spec-kitty-plugin/skills/spec-kitty-dashboard/SKILL.md) · [`spec-kitty-status`](plugins/spec-kitty-plugin/skills/spec-kitty-status/SKILL.md)
- [`spec-kitty-checklist`](plugins/spec-kitty-plugin/skills/spec-kitty-checklist/SKILL.md) · [`spec-kitty-constitution`](plugins/spec-kitty-plugin/skills/spec-kitty-constitution/SKILL.md)
- [`spec-kitty-tasks-outline`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks-outline/SKILL.md) · [`spec-kitty-tasks-finalize`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks-finalize/SKILL.md) · [`spec-kitty-tasks-packages`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks-packages/SKILL.md)
- [`spec-kitty-workflow`](plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md) · [`spec-kitty-sync-plugin`](plugins/spec-kitty-plugin/skills/spec-kitty-sync-plugin/SKILL.md)

### Link Checker — Documentation Hygiene

Continuous markdown hyperlink validation with multi-stage pipeline (inventory → extract → audit → fix).

- [`link-checker-agent`](plugins/link-checker/skills/link-checker-agent/SKILL.md)

### Markdown to MSWord

Interoperability translator for non-technical stakeholders.

- [`markdown-to-msword-converter`](plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/SKILL.md)

### Memory Management

Multi-tiered cognition and context caching between long-term persistent storage and active memory.

- [`memory-management`](plugins/memory-management/skills/memory-management/SKILL.md)

### Mermaid to PNG

Diagram exporter and renderer using headless browser.

- [`convert-mermaid`](plugins/mermaid-to-png/skills/convert-mermaid/SKILL.md) *(autoresearch score: 30/40 MEDIUM — Triple-Loop eval run complete: 0.61 → 1.00 in 26 iterations)*

### Obsidian Wiki Engine — Karpathy LLM Wiki + Super-RAG

Karpathy-style LLM wiki with cross-source concept synthesis and 3-tier Super-RAG retrieval (RLM keyword → vector semantic → grep exact). Transforms raw markdown sources into structured, queryable concept nodes. Includes full Obsidian vault CRUD, canvas, and graph traversal.

**Super-RAG stack:** `rlm-factory` (O(1) keyword) + `vector-db` (O(log N) semantic) + wiki nodes (full concept)

Each plugin works **standalone** (Mode A) or combined for full Super-RAG power. Init agents detect what is actually installed in `.agents/skills/` and configure only the available layers — any combination works.

**Wiki skills:**
- [`obsidian-wiki-builder`](plugins/obsidian-wiki-engine/skills/obsidian-wiki-builder/SKILL.md) — build Karpathy nodes (ingest → concept synthesis → format)
- [`obsidian-rlm-distiller`](plugins/obsidian-wiki-engine/skills/obsidian-rlm-distiller/SKILL.md) — generate RLM summary layers per concept
- [`obsidian-query-agent`](plugins/obsidian-wiki-engine/skills/obsidian-query-agent/SKILL.md) — 3-phase query with `--save-as` (file outputs back)
- [`obsidian-wiki-linter`](plugins/obsidian-wiki-engine/skills/obsidian-wiki-linter/SKILL.md) — semantic health check (inconsistencies, gaps, stale articles)

**Vault skills:**
- [`obsidian-init`](plugins/obsidian-wiki-engine/skills/obsidian-init/SKILL.md) · [`obsidian-vault-crud`](plugins/obsidian-wiki-engine/skills/obsidian-vault-crud/SKILL.md)
- [`obsidian-canvas-architect`](plugins/obsidian-wiki-engine/skills/obsidian-canvas-architect/SKILL.md) · [`obsidian-graph-traversal`](plugins/obsidian-wiki-engine/skills/obsidian-graph-traversal/SKILL.md)
- [`obsidian-markdown-mastery`](plugins/obsidian-wiki-engine/skills/obsidian-markdown-mastery/SKILL.md) · [`obsidian-bases-manager`](plugins/obsidian-wiki-engine/skills/obsidian-bases-manager/SKILL.md)

**Setup agents:** `wiki-init-agent` (guided init, Modes A–D) · `rlm-factory-init-agent` (guided init, Modes A–D) · `vector-db-init-agent` (guided init, Modes A–D) · `super-rag-setup-agent` (full 3-plugin orchestrator)

### Plugin Manager — Ecosystem Sync

Authoritative suite for ecosystem health, synchronization, and artifact bootstrapping.

- [`plugin-installer`](plugins/plugin-manager/skills/plugin-installer/SKILL.md) — local symlink deployment from source to agent environments
- [`auto-update-plugins`](plugins/plugin-manager/skills/auto-update-plugins/SKILL.md) — pull-based sync via SessionStart hook
- [`maintain-plugins`](plugins/plugin-manager/skills/maintain-plugins/SKILL.md)
- [`replicate-plugin`](plugins/plugin-manager/skills/replicate-plugin/SKILL.md)

### RLM Factory — Reverse Language Modeling

O(1) keyword search over dense per-file summaries. Zero external dependencies — works standalone or as Phase 1 of the Super-RAG stack.

- [`rlm-init`](plugins/rlm-factory/skills/rlm-init/SKILL.md) · [`rlm-curator`](plugins/rlm-factory/skills/rlm-curator/SKILL.md) · [`rlm-search`](plugins/rlm-factory/skills/rlm-search/SKILL.md)
- [`rlm-distill-agent`](plugins/rlm-factory/skills/rlm-distill-agent/SKILL.md) · [`rlm-distill-ollama`](plugins/rlm-factory/skills/rlm-distill-ollama/SKILL.md) · [`rlm-cleanup-agent`](plugins/rlm-factory/skills/rlm-cleanup-agent/SKILL.md)
- [`ollama-launch`](plugins/rlm-factory/skills/ollama-launch/SKILL.md)

**Setup agent:** `rlm-factory-init-agent` (guided setup, Modes A–D: standalone → partial → full Super-RAG)

### RSVP Speed Reader

Token-stream speed reading with pause/resume, comprehension check-ins, and session management.

- [`rsvp-reading`](plugins/rsvp-speed-reader/skills/rsvp-reading/SKILL.md) · [`rsvp-comprehension-agent`](plugins/rsvp-speed-reader/skills/rsvp-comprehension-agent/SKILL.md)

### Agent Skill Open Specifications

Canonical documentation for compliant skill and directory architecture construction.

- [`ecosystem-standards`](plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md)
- [`ecosystem-authoritative-sources`](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/SKILL.md)

### Task Manager

Kanban board synchronization and task lane transitions.

- [`task-agent`](plugins/task-manager/skills/task-agent/SKILL.md)



### Vector DB

ChromaDB-driven semantic embedding indexing with Parent-Child retrieval. Works standalone or as Phase 2 of the Super-RAG stack. Supports In-Process mode (zero server setup) and HTTP Server mode. Profile-driven via `.agent/learning/vector_profiles.json`.

- [`vector-db-init`](plugins/vector-db/skills/vector-db-init/SKILL.md) · [`vector-db-launch`](plugins/vector-db/skills/vector-db-launch/SKILL.md)
- [`vector-db-ingest`](plugins/vector-db/skills/vector-db-ingest/SKILL.md) · [`vector-db-search`](plugins/vector-db/skills/vector-db-search/SKILL.md)
- [`vector-db-cleanup`](plugins/vector-db/skills/vector-db-cleanup/SKILL.md)

**Setup agent:** `vector-db-init-agent` — guided wizard (Modes A–D), detects installed Super-RAG layers, provisions only what's present

### Voice Writer

Tone mapping and humanization for AI-generated content.

- [`humanize`](plugins/voice-writer/skills/humanize/SKILL.md)

### HuggingFace Utils

Snapshot persistence and HuggingFace repository lifecycle.

- [`hf-init`](plugins/huggingface-utils/skills/hf-init/SKILL.md) · [`hf-upload`](plugins/huggingface-utils/skills/hf-upload/SKILL.md)

### ADR Manager

Automatically draft and syndicate Architecture Decision Records.

- [`adr-management`](plugins/adr-manager/skills/adr-management/SKILL.md)

---

## Completed Experiments

### Ecosystem Fitness Sweep v1 — COMPLETE (`temp/ecosystem-fitness-sweep-v1/`)

Scored all 116/120 production skills for **Karpathy autoresearch loop viability** using GPT-5 mini via Copilot CLI.
Each skill scored on: objectivity (can a shell command measure it?), execution speed, frequency of use, and potential utility (max 40).

**Top HIGH candidates:**

| Rank | Skill | Score | Loop |
|---|---|---|---|
| 1 | superpowers/verification-before-completion | 35/40 | LLM_IN_LOOP |
| 2 | superpowers/test-driven-development | 35/40 | LLM_IN_LOOP |
| 3 | coding-conventions/coding-conventions-agent | 34/40 | HYBRID |
| 4 | superpowers/using-git-worktrees | 33/40 | DETERMINISTIC |
| 5 | spec-kitty-plugin/spec-kitty-status | 33/40 | DETERMINISTIC |
| 6 | agent-agentic-os/os-eval-runner | 32/40 | DETERMINISTIC |

Full ranked results: [`summary-ranked-skills.json`](plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json)
Top 20 opportunities with metrics + blockers: [`autoresearch-opportunities-report.md`](plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/autoresearch-opportunities-report.md)

Regenerate report:
```bash
python3 plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/scripts/update_ranked_skills.py \
  --json-path plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json \
  --morning-report
```

---

## Repository Structure

```
plugins/                    ← upstream source (27 plugins, 119 skills)
  <plugin>/
    plugin.json
    skills/<skill>/
      SKILL.md              ← skill definition (mutation target for autoresearch loops)
      evals/evals.json      ← routing evaluation suite (should_trigger boolean schema)
      evals/results.tsv     ← per-experiment score history
      autoresearch/         ← optional: evaluate.py + golden task set for improvement loops
      scripts/              ← file-level symlinks → ../../scripts/
    scripts/                ← canonical scripts (shared via symlinks, never duplicated)
    agents/                 ← sub-agent .md definitions
    assets/diagrams/        ← architecture diagrams

.agents/                    ← deployed skill copies (bridge installer output)
  skills/
  agents/

plugin-research/            ← experiments and autoresearch infrastructure
  experiments/
    analyze-candidates-for-auto-reseaarch/

temp/                       ← local scratch (gitignored except scripts)
  ecosystem-fitness-sweep-v1/
```

---

*119 skills · 27 plugins · Dual-Flywheel architecture · Karpathy autoresearch loops · Super-RAG 3-tier retrieval*
