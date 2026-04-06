# Copilot instructions for agent-plugins-skills (from CLAUDE.md)

This file reproduces the key operational and architectural guidance present in CLAUDE.md so Copilot/AI sessions can act consistently with the repo's intent.

## Repository purpose

This repo is the upstream monorepo for a cross-platform library of reusable AI agent plugins and skills. Plugins here are canonical sources that are "bridged" into target environments by installer scripts. Individual skills must be self-contained and not depend at runtime on sibling plugins.

## Key commands

### Install / Deploy Plugins

- Recommended (uvx, cross-platform):
  - uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
  - uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y
  - uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --dry-run

- Zero-dep fallback (macOS / Linux):
  - curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python3 -

- From a local clone (interactive TUI):
  - python plugins/plugin-manager/scripts/plugin_add.py
  - python plugins/plugin-manager/scripts/install_all_plugins.py
  - python plugins/plugin-manager/scripts/install_all_plugins.py --dry-run

### Regenerate autoresearch report (example)

- python3 plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/scripts/update_ranked_skills.py \
  --json-path plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json \
  --morning-report

### Python dependency workflow (per-plugin)

- pip-compile ./requirements.in
- pip install -r ./requirements.txt

Notes: Most skills require only Python 3.8+ standard library. Check requirements.in in the relevant plugin directory.

Windows note: Never use `npx skills add` on Windows; Git symlinks check out as plain-text pointer files. Use `uvx` or `bootstrap.py` instead.

## High-level architecture (Source → Deploy)

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

- The bridge installer resolves file-level symlinks into physical copies so deployed skills are self-contained.
- Management scripts live in plugins/plugin-manager/scripts/ (install_all_plugins.py, plugin_add.py, bridge_installer.py, audit_structure.py, plugin_inventory.py, generate_readmes.py, etc.).

## Architecture Decision Records

See ADRs/ for authoritative rules. Relevant ADRs called out in CLAUDE.md:
- ADR-001: No cross-plugin script execution; use agent skill delegation at runtime
- ADR-002: Within-plugin multi-skill script sharing (hub-and-spoke)
- ADR-003: File-level symlinks only; no directory symlinks
- ADR-004: Self-contained installed artifacts; no runtime cross-plugin dependencies

## Skill standards and conventions

- Skill naming: kebab-case, directory-matching, no consecutive hyphens, 1–64 chars
- SKILL.md: keep under ~500 lines; push longer detail to references/
- evals/evals.json: use `should_trigger: true|false` schema (do not use legacy `expected_behavior` strings)
- Scripting: use Python helper scripts only; do not create `.sh` scaffolding in skills
- Symlinks: file-level symlinks only; installer resolves them into .agents/
- Lockfile: skills-lock.json tracks installed plugin hashes
- Temp outputs: write analysis/temporary files to temp/ (do not write to repo root)

## Plugin-manager scripts (from CLAUDE.md)

- install_all_plugins.py — Bulk bridge-install all plugins
- plugin_add.py — Interactive TUI installer (local or remote)
- bridge_installer.py — Low-level installer
- update_agent_system.py — Pull-based sync for installed environments
- clean_orphans.py — Remove artifacts for deleted plugins
- audit_structure.py — Validate plugin directory structure
- plugin_inventory.py — List plugins and metadata
- sync_with_inventory.py — Reconcile installed state with plugin_sources.json
- generate_readmes.py — Regenerate plugin-level README files

## Creating new plugins & skills (scaffolding)

- Use scaffolders rather than hand-rolling structure:
  - /agent-scaffolders:create-plugin
  - /agent-scaffolders:create-skill
  - /agent-scaffolders:audit-plugin
- After scaffolding run plugin_add.py to deploy and audit_structure.py to validate.

## Scratch output

- Write temporary files or analysis output to temp/ at repo root — never to the project root directly.

---

This file is now aligned with CLAUDE.md. If you want additional CLAUDE.md sections incorporated or per-plugin details added, say which plugin(s).

Would you like an MCP server configured (for example Playwright) for this repository?