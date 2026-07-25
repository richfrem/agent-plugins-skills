# Architecture Overview

This document gives agents a fast, accurate understanding of this repository's structure and
architectural rules. **`plugins/` is the single source of truth** — `.agents/`, the Claude Code
marketplace, and any other installed-copy location are outputs, never authoritative. Update this
document when the plugin count, ADR set, or top-level layout changes.

## 1. What This Repo Is

`agent-plugins-skills` is the **upstream source monorepo** for a cross-platform library of reusable
AI agent plugins and skills. Plugins are authored here and deployed into *other* target projects via
a bridge installer (`bootstrap.py` / `plugin_add.py`). It is not an application with a frontend and
backend — it is a **plugin ecosystem + installer**, consumed by Claude Code, GitHub Copilot, Gemini
CLI, Antigravity, and other compliant agent frameworks.

Current scale (read from `plugins/` — verify with `find plugins/*/skills -mindepth 1 -maxdepth 1 -type d | wc -l` before quoting a number elsewhere):
- **11 plugins**
- **128 skills** (SKILL.md definitions)
- **46 agent definitions** (`agents/*.md` across plugins)

## 2. Project Structure

```
[Project Root]/
├── plugins/                        # CANONICAL SOURCE — authoritative for all skills/agents
│   ├── agent-agentic-os/           # OS improvement loop, memory, evolution planning (19 skills)
│   ├── agent-loops/                # OS-decoupled execution primitives (6 skills)
│   ├── agent-memory/               # RLM summary cache + ChromaDB vector store (13 skills)
│   ├── agent-scaffolders/          # Plugin/skill/agent scaffolding tools (30 skills)
│   ├── cli-agents/                 # Multi-LLM CLI dispatch (Claude/Copilot/Gemini/Agy) (12 skills)
│   ├── dependency-management/      # pip-compile / dependency tier workflow (1 skill)
│   ├── dev-utils/                  # ADR mgmt, symlinks, context bundling, GitHub issues, worktrees (16 skills)
│   ├── exploration-cycle-plugin/   # Business discovery workflow + SQLite control plane (20 skills)
│   ├── obsidian-wiki-engine/       # Karpathy-style LLM wiki over the codebase (10 skills)
│   ├── plugin-manager/             # Install/remove/sync plugins into target projects (3 skills)
│   └── spec-kitty-plugin/          # DEPRECATED pointer — see plugins/spec-kitty-plugin/README.md
│       <plugin>/
│       ├── skills/<skill>/SKILL.md # Skill definition (evals.json lives alongside)
│       ├── agents/                 # Sub-agent definitions
│       ├── commands/               # Slash commands
│       ├── scripts/                # Shared scripts (file-level symlinks only — ADR-003)
│       ├── references/             # Extra detail kept out of SKILL.md (>~500 line rule)
│       └── .claude-plugin/         # plugin.json manifest
│
├── .agents/                         # INSTALLED COPIES ONLY — bridge installer output
│   ├── skills/ agents/ workflows/  # What actually runs at runtime (hard copies, symlinks resolved)
│   └── hooks/ ownership/
│
├── ADRs/                            # Authoritative architecture decision records (001–007)
├── .agent/rules/                    # Full rule text (CLAUDE.md carries only the summary)
├── docs/                            # MAF research, ADR support docs, superpowers specs
├── context/                         # events.jsonl, experiment-log, memory (OS runtime state)
├── tasks/                           # backlog/ and done/ — task tracking artifacts
├── bootstrap.py                     # Entry point for uvx / curl-pipe zero-clone install
├── plugin.yaml                      # Root manifest listing all skills_dirs
├── plugin-sources.json              # Tracks which plugins are installed where
├── symlinks.json                    # Manifest for symlink_manager.py (cross-platform symlinks)
├── skills-lock.json                 # Lockfile for installed skill versions
├── pyproject.toml                   # setuptools packaging; exposes plugin-add/-remove/-sync CLIs
├── README.md                        # Ecosystem overview, version history, install guide
└── CLAUDE.md                        # Behavioral guidelines + project-specific rules (this repo's law)
```

## 3. High-Level Flow: Author → Install → Run

```
[plugins/<plugin>/skills/*, agents/*, scripts/*]   (authored here, source of truth)
              │
              │  plugin_add.py / bootstrap.py (uvx or local)
              ▼
[.agents/skills/, .agents/agents/, .agents/workflows/]   (installed hard copies, symlinks resolved)
              │
              │  consumed at runtime by
              ▼
[Claude Code | GitHub Copilot | Gemini CLI | Antigravity | MAF adapter]
```

Skills **run from `.agents/`**, never from `plugins/` directly — files under `plugins/` are inert
until installed. This split is intentional: it lets the same skill be authored once and deployed,
unmodified, into any number of target projects.

## 4. Core Components

### 4.1. Installer / Bridge (root-level)
- `bootstrap.py` — zero-clone entry point for `uvx --from git+... plugin-add`; downloads installer scripts to an ephemeral dir and runs them.
- `plugins/plugin-manager/scripts/plugin_add.py` / `plugin_installer.py` / `plugin_remove.py` / `sync_with_inventory.py` — interactive and scripted install/remove/sync of individual or bulk plugins into a target project's `.agents/` folder.
- `pyproject.toml` exposes these as console scripts: `plugin-add`, `plugin-remove`, `plugin-sync`.

### 4.2. Plugin: agent-agentic-os (v1.7.0)
The self-improvement kernel. Core loop: `os-architect → os-improvement-loop → os-eval-runner →
os-eval-backport → os-experiment-log`. Also owns memory management (`os-memory-manager`), evolution
planning (`os-evolution-planner`/`os-evolution-verifier`), and setup (`os-init`,
`agentic-os-setup` agent).

### 4.3. Plugin: agent-loops (v2.1.0)
Six OS-decoupled execution primitives (orchestrator, learning-loop, dual-loop, agent-swarm,
red-team-review, triple-loop-learning). Provides execution patterns only — no eval gate, no memory;
`os-improvement-loop` delegates its inner loop to `triple-loop-learning` as substrate.

### 4.4. Plugin: agent-memory (v1.0.0)
Two retrieval subsystems consolidated from former rlm-factory / vector-db / memory-management
plugins: RLM (dense-summary keyword cache, O(1) lookup, zero deps) and vector-db (ChromaDB semantic
embeddings). Can run standalone or combined as part of a "Super-RAG" stack with
`obsidian-wiki-engine`.

### 4.5. Plugin: agent-scaffolders (30 skills)
Tooling for creating and validating new ecosystem components: `create-plugin`, `create-skill`,
`create-sub-agent`, `audit-plugin`, plus APM package conversion, marketplace management, and
ecosystem-index maintenance.

### 4.6. Plugin: cli-agents (v1.1.0)
Multi-LLM task router (`run_agent.py`) consolidated from claude-cli/copilot-cli/gemini-cli.
6 backends, `--isolated` security contract, 11 expert-persona sub-agents (architect-review,
security-auditor, red-team-reviewer, etc.). Model selection driven by
`references/copilot-models.json` cost tiers. Gemini CLI consumer access ends June 18, 2026 —
`agy-cli-agent` is the forward path for frontier models.

### 4.7. Plugin: exploration-cycle-plugin (20 skills) — security-sensitive
Business discovery workflow (Path 1: pre-build discovery; Path 2: vibe-coded-prototype
migration). Backed by a hardened Python control plane in `scripts/`: `dispatch.py`,
`state_engine.py` (SQLite, transactional, WAL), `sandbox_runner.py` (process sandboxing, HMAC-signed
envelopes, approval gating). v1.3 hardened this to stdlib-only; v1.4 work is in progress. Any change
to these three files requires reading `ADRs/007_maf_adapter_runtime_decision.md` and the v1.4 spec
first — no casual convenience bypasses to the authorization gate or path enforcement.

### 4.8. Plugin: obsidian-wiki-engine (10 skills)
Karpathy-style LLM wiki generation over the codebase; standalone or combined with agent-memory as
the third leg of the Super-RAG stack.

### 4.9. Plugin: dev-utils (v1.1.0, 14 skills)
Consolidated from 9 former standalone plugins: ADR management, coding-conventions enforcement,
context bundling, mermaid conversion, HuggingFace init/upload, humanize, link-checking, context
optimization, `symlink-manager` (the only sanctioned way to create symlinks in this repo),
task-agent.

### 4.10. Plugin: dependency-management (1 skill)
Enforces the `pip-compile requirements.in → requirements.txt` workflow per plugin; no manual `pip
install`.

### 4.11. Plugin: plugin-manager (3 skills)
Wraps the install/remove/sync scripts above as invokable skills (`plugin-installer`,
`plugin-remover`, `plugin-syncer`).

### 4.12. Plugin: spec-kitty-plugin — DEPRECATED
Contains only a `README.md` pointer. As of Spec Kitty v3.2.2+, functionality moved to the
natively-managed upstream `Priivacy-ai/spec-kitty` package (installed separately, not sourced from
`plugins/` here). Do not add skills under this directory.

## 5. Architectural Rules (ADRs) — binding, not advisory

| ADR | Rule |
|---|---|
| 001 | No cross-plugin script execution — delegate via agent skill at runtime, never import another plugin's script directly |
| 002 | Within-plugin multi-skill script sharing goes through hub-and-spoke: shared scripts live in the plugin root `scripts/`, individual skills get file-level symlinks to them |
| 003 | Resource sharing uses mirrored folder structure + **file-level symlinks only** — never directory symlinks, never duplicated files |
| 004 | Installed artifacts (`.agents/`) must be self-contained — no runtime cross-plugin paths |
| 005 | Plugins must maintain separation of concerns and loose coupling |
| 006 | Python-native bootstrap installer (`bootstrap.py`) replaces the old `npx skills add` path |
| 007 | MAF (Microsoft Agent Framework) is an optional certified runtime adapter, never the primary orchestration kernel — `.md` manifests remain the portable source of truth across Claude Code / Copilot CLI / Gemini CLI / MAF |

Full rule text (rationale, examples, enforcement detail) lives in `.agent/rules/` — CLAUDE.md only
carries the summary. Key files: `coding-conventions.md`, `dependency-management.md`,
`plugin-architecture-policy.md`, `self-evolution-policy.md`, `symlink-cross-platform.md`,
`test-driven-development.md`, `destructive-action-guard.md`, `git-operations.md`,
`skill-deletion-guard.md`.

## 6. Skill & Plugin Authoring Standards

- Skill `name`: kebab-case, matches directory name exactly, 1–64 chars.
- Skill `description`: third person.
- `evals.json`: routing criteria use `should_trigger: true/false` — the legacy `expected_behavior`
  schema silently produces 0% routing accuracy.
- `SKILL.md`: under ~500 lines; overflow detail goes to `references/`.
- Helper scripts: Python only — never bash (`.sh`).
- New plugins/skills should be scaffolded via `create-plugin` / `create-skill`, then validated with
  `audit-plugin`, then deployed with `plugin_add.py` — not hand-rolled.

## 7. Symlink System

`symlinks.json` (root manifest, ~2,800 lines) tracks every shared-script symlink across all plugins,
managed exclusively through `symlink-manager` (`.agents/skills/symlink-manager/scripts/symlink_manager.py`).
Never run `ln -s` by hand. Workflow: `diagnose` → fix manifest → `restore` → `diagnose` again to
confirm zero BROKEN entries before committing. A broken symlink in `plugins/` fails silently at
install time, so this check is not optional.

## 8. Runtime State & Memory

- `context/events.jsonl`, `context/experiment-log/`, `context/memory/` — the Agentic OS's own runtime
  state (event bus, experiment tracking, promoted memories), maintained by `agent-agentic-os` skills.
- `tasks/backlog/`, `tasks/done/` — task-tracking artifacts used by `dev-utils:task-agent` and the OS
  improvement loop.
- This is distinct from the *user's* Claude Code memory system (`~/.claude/projects/.../memory/`),
  which is a separate, cross-project persistence layer, not part of this repo's tracked state.

## 9. Deployment Model

There is no build/deploy pipeline in the traditional sense — "deployment" means running the
installer against a *target* repository:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

This populates the target's `.agents/` directory. `build/` at the repo root is a Python
setuptools artifact (from `pip install -e .` / packaging), not an application build output.

## 10. Testing & Validation

- Plugin structural validation: `audit-plugin` skill.
- Control-plane smoke tests: `plugins/exploration-cycle-plugin/scripts/smoke_test.py`.
- `cli-agents` router: 76 TDD tests across 3 files (per README v1.5 notes).
- No single top-level test runner — tests are scoped per plugin, colocated with the plugin's
  `scripts/`.

## 11. Known Architectural Evolution (see README.md for full history)

- **v1.3** — SQLite-backed hardened control plane for exploration-cycle-plugin.
- **v1.4** — MAF synthesis: hybrid architecture, MAF adopted as certified optional adapter (ADR-007),
  not a kernel replacement.
- **v1.5** — cli-agents promoted to a full multi-LLM task router with adversarial agent personas.

## 12. Glossary

- **Plugin**: A directory under `plugins/` bundling related skills, agents, commands, and scripts around one capability area.
- **Skill**: A `SKILL.md`-defined capability, self-contained, no runtime cross-plugin dependencies.
- **Bridge installer**: The `bootstrap.py` / `plugin_add.py` mechanism that copies `plugins/` content into a target project's `.agents/`.
- **RLM**: Dense-summary keyword cache used for fast O(1) file lookup (agent-memory plugin).
- **MAF**: Microsoft Agent Framework — optional certified runtime adapter per ADR-007, not the primary kernel.
- **Control plane**: The SQLite/HMAC-hardened state and sandboxing layer in exploration-cycle-plugin (`state_engine.py`, `sandbox_runner.py`, `dispatch.py`).
