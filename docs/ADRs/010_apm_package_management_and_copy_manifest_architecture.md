# ADR-010: APM Package Management & Copy Manifest Architecture

## Status
Accepted (2026-10-23)

## Context
Previously, plugins in this monorepo relied on custom tooling (`plugins/plugin-manager/scripts/plugin_add.py`, `plugin_installer.py`, `plugin-syncer`) and filesystem symlinks to share scripts across skills (ADR-002, ADR-003, ADR-006).

This architecture suffered from several critical points of friction:
1. **Windows Symlink Fragility**: Git on Windows checkouts without Developer Mode checks out symlinks as 30–50 byte text files containing paths. When consumed or packaged, skills broke because the "scripts" were plain text stubs rather than executable Python code.
2. **Proprietary Ecosystem Lock-in**: Downstream projects had to rely on custom `uvx ... plugin-add` commands and non-standard ownership manifests (`.agents/ownership/*.json`).
3. **Multi-Target Inconsistency**: Modern AI workflows run across multiple client tools (Claude Code, GitHub Copilot, OpenAI Codex, Google Antigravity). Manually copying and syncing files across disparate runtime directories (`.claude/`, `.github/`, `.agents/`, `.codex/`) was brittle and prone to drift.

## Decision
We mandate **Microsoft APM (Agent Package Manager)** as the universal package manager for all plugins and skills, coupled with a declarative **Copy Manifest (`symlinks.json`, `strategy: "copy"`)**:

1. **APM-Native Packaging**:
   - Every plugin is an APM package governed by an `apm.yml` manifest.
   - Deploys natively across all targets in one operation:
     - **Claude Code**: `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.claude/settings.json`
     - **GitHub Copilot**: `.agents/skills/`, `.github/agents/*.agent.md`, `.github/hooks/`
     - **OpenAI Codex**: `.agents/skills/`, `.codex/agents/*.toml`, `.codex/hooks.json`
     - **Antigravity (Agy)**: `.agents/skills/`, `.agents/hooks.json`
2. **Authoritative Copy Manifest (`symlinks.json`)**:
   - Filesystem symlink objects are eliminated across all source plugins.
   - Canonical files reside strictly at the plugin root (`plugins/<plugin>/scripts/`, etc.).
   - `symlinks.json` lists canonical source paths and destination paths with `strategy: "copy"`.
   - `materialize_copies.py` writes physical copies into skill folders after clone/pull and records them in local git excludes (`.git/info/exclude`), ensuring git stays clean while local test execution and APM packaging find real files.
3. **Decommissioning of `plugin-manager`**:
   - `plugins/plugin-manager` is completely retired and deleted.
   - Legacy ownership files (`.agents/ownership/*.json`) are removed; APM lockfiles (`apm.lock.yaml`) manage deployment state and file ownership deterministically.

## Consequences

**Positive:**
- **Cross-Platform Immunity**: Fully immune to Windows symlink degradation.
- **Standards-Compliant**: Uses industry-standard package manifests (`apm.yml`) and reproducible lockfiles (`apm.lock.yaml`).
- **Zero Drift**: `materialize_copies.py --check` guarantees 100% deterministic copy alignment (2,289 files verified with 0 drift).
- **Client Agnostic**: Installs seamlessly into Claude, Copilot, Codex, and Antigravity.

**Negative / Trade-offs:**
- Requires running `materialize_copies.py` once after cloning or checking out branches before running local tests.
- Consuming repositories must migrate from `plugin_add.py` / `uvx` to `apm install`.
