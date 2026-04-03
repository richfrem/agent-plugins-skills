# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the **upstream source monorepo** for a cross-platform library of reusable AI agent plugins and skills. It is the hub in a hub-and-spoke model: plugins live here in canonical form and are deployed ("bridged") into target projects via installer scripts.

- **120 production skills** across **29 plugins** targeting Claude Code, GitHub Copilot, Gemini CLI, Roo Code, Windsurf, Cursor, and compatible integrations.
- Individual skills must function in complete isolation — no hard runtime dependencies on sibling plugins.

## Key Commands

### Install / Deploy Plugins

```bash
# Recommended: uvx (cross-platform, no clone needed)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y  # non-interactive
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --dry-run

# Zero-dep fallback (Mac/Linux)
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python3 -

# From a local clone (interactive TUI)
python plugins/plugin-manager/scripts/install_all_plugins.py

# Dry run preview
python plugins/plugin-manager/scripts/install_all_plugins.py --dry-run
```

> **Windows**: Never use `npx skills add` — Git symlinks check out as plain-text pointer files on Windows. Use `uvx` or `bootstrap.py` instead.

### Add/Update a Single Plugin (Interactive TUI)

```bash
# Interactive picker — select plugins to install from local repo
python plugins/plugin-manager/scripts/plugin_add.py

# Install from a remote GitHub repo
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills
```

### Regenerate the Autoresearch Fitness Report

```bash
python3 plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/scripts/update_ranked_skills.py \
  --json-path plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json \
  --morning-report
```

### Python Dependencies (per skill/plugin)

```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

Most skills require only Python 3.8+ standard library. Check `requirements.in` in the relevant plugin directory.

## Architecture

### Source → Deploy Flow

```
plugins/<plugin>/           ← canonical source (this repo)
  plugin.json
  skills/<skill>/
    SKILL.md                ← skill definition (agent routing prompt)
    evals/evals.json        ← routing eval suite (should_trigger boolean schema)
    evals/results.tsv       ← score history
    autoresearch/           ← optional: evaluate.py + golden tasks for improvement loops
    scripts/                ← file-level symlinks → ../../scripts/ (never directory symlinks)
  scripts/                  ← canonical scripts (shared via file-level symlinks only)
  agents/                   ← sub-agent .md definitions
  commands/                 ← slash command definitions

.agents/                    ← bridge installer output (hard copies, all symlinks resolved)
  skills/
  agents/
  workflows/

.claude/agents/             ← symlinks → .agents/agents/ (Claude Code routing)
```

The bridge installer resolves all file-level symlinks into physical copies so each deployed skill is self-contained regardless of which other plugins are present.

### Architecture Decision Records

See `ADRs/` for the authoritative rules governing this repo. Key ADRs:

- **ADR-001** — No cross-plugin script execution; use agent skill delegation at runtime
- **ADR-002** — Within-plugin multi-skill script sharing (hub-and-spoke)
- **ADR-003** — File-level symlinks only; scripts/assets/references at plugin root, never duplicated in skill subdirs
- **ADR-004** — Self-contained installed artifacts; no runtime cross-plugin dependencies

### Skill Standards

- Skill `name` must be kebab-case, match its parent directory exactly, contain no consecutive hyphens, and be 1–64 chars.
- Skill `description` is written in **third person** ("Extracts text", not "I extract text").
- `evals.json` must use `should_trigger: true/false` schema — the legacy `expected_behavior` string field produces 0% accuracy in the eval scorer.
- SKILL.md files must stay under ~500 lines; push detail into `references/` files.
- Python helper scripts only — never generate `.sh` bash scripts in skill scaffolding.

### Dual-Flywheel (agent-agentic-os)

The `agent-agentic-os` plugin runs continuous self-improvement:

- **OUTER flywheel** (`os-improvement-loop`): improves OS-level protocols between sessions
- **INNER flywheel** (`os-eval-runner` + `os-skill-improvement`): RED-GREEN-REFACTOR skill mutation gated by `evaluate.py` (exit 0 = KEEP, exit 1 = DISCARD)
- **`os-nightly-evolver`**: runs the INNER flywheel unattended overnight — Gemini CLI proposes mutations, `evaluate.py` gates them

### plugin-manager Scripts

All ecosystem management lives in `plugins/plugin-manager/scripts/`:

| Script | Purpose |
|---|---|
| `install_all_plugins.py` | Bulk bridge-install all plugins |
| `plugin_add.py` | Interactive TUI installer (local or remote GitHub repo) |
| `bridge_installer.py` | Low-level installer called by plugin_add.py |
| `update_agent_system.py` | Pull-based sync for installed environments |
| `clean_orphans.py` | Remove artifacts for deleted plugins |
| `audit_structure.py` | Validate plugin directory structure |
| `plugin_inventory.py` | List all plugins and their metadata |
| `sync_with_inventory.py` | Reconcile installed state with plugin_sources.json |
| `generate_readmes.py` | Regenerate plugin-level README files |

`skills-lock.json` at repo root tracks installed plugin hashes (analogous to a lockfile).

## Creating New Plugins and Skills

Use the scaffolding skills rather than hand-rolling structure:

- `/agent-scaffolders:create-plugin` — full plugin scaffold with discovery interview
- `/agent-scaffolders:create-skill` — skill scaffold with evals.json, references/, acceptance-criteria.md
- `/agent-scaffolders:audit-plugin` — validate structure after scaffolding

After scaffolding, run `plugin_add.py` to deploy.

## Scratch Output

Write any temporary files or analysis output to `temp/` at the repo root — never to the project root directly.
