---
name: convert-plugin-to-apm
description: >-
  Activate when the user wants to convert an existing Claude/Copilot/agent plugin to APM,
  add APM package management to a plugin without changing its layout, migrate a plugin
  to APM-native format, or check that a plugin packages and installs cleanly with APM.
allowed-tools: Bash, Read, Write, Glob
---

# Convert Plugin to APM (`convert-plugin-to-apm`)

Packages an existing agent plugin for [APM](https://github.com/microsoft/apm) without changing its source layout, verifies the install, and reports every misalignment with its standard fix. Behaviour below was verified with APM `0.33.0`.

## Contents

- [Critical Constraints](#critical-constraints)
- [What APM Does With a Plugin](#what-apm-does-with-a-plugin)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Authoring Rules for APM](#authoring-rules-for-apm)
- [Verification](#verification) · [References](#references)

## Critical Constraints

1. **Never change the source plugin to package it.** Staging, manifests, fixtures and bundles go under `build/`. APM does not need an `apm.yml` inside the plugin.
2. **Fix misalignments as reviewed source changes**, using the finding's standard fix (SF-1 to SF-11). Do not copy files in, repoint symlinks, or add new symlinks.
3. **Pin APM** to the repository's version (`apm-cli==0.33.0`, `plugins/agent-scaffolders/requirements-dev.in`) and pin installs to a ref (`#<tag>` or `#<commit-sha>`).

## What APM Does With a Plugin

- **Reads the plugin as-is**: `apm install ./plugins/<plugin>` (or `owner/repo/plugins/<plugin>#<ref>`) installs skills, agents and hooks from the existing layout.
- **Copies each skill folder whole.** Symlinks inside the package are turned into physical copies; a symlink pointing outside the package aborts the install. On a Windows checkout without symlink support, each symlink is a text stub and APM installs the stub as the file.
- **Rewrites markdown links** that leave a skill to point into its package cache (`apm_modules/`, or `~/.apm/apm_modules/` for global installs), so links to sibling skills and plugin-root files resolve. Paths in code blocks, inline code or plain text are **not** rewritten, and links that leave the plugin break.
- **Deploys per harness** (targets `claude,copilot,agy,codex`): skills to `.claude/skills/` and the shared `.agents/skills/`; agents to `.claude/agents/`, `.github/agents/`, `.codex/agents/`; hooks merged into each harness's hook settings with `${CLAUDE_PLUGIN_ROOT}/...` rewritten to a copied script. Global installs use the user-level folders (`~/.claude/skills/`, `~/.agents/skills/`, `~/.gemini/antigravity-cli/skills/`) and write nothing into repositories.
- **Does not deploy** a plugin's `rules/` folder (instructions come only from `.apm/instructions/`). Global installs give agy no hooks or agents.

## Quick start

Run the build pipeline on one plugin from the repository root:

```bash
python3 scripts/apm_build_pipeline.py --plugin plugins/<plugin-name> --apm <path-to-apm>
```

Add `--pack` to build the installable bundle, or `--skip-deploy` to validate without APM.

## Workflow

1. **Run the pipeline.** Stages: inspect, normalize, validate, package, test deploy, and (with `--pack`) pack.
   - Symlinks are read from the git index, so Windows checkouts are handled.
   - `symlinks.json` entries with `strategy: "copy"` become per-skill physical copies in staging only. This is how one canonical script is shared by several skills without symlinks.
2. **Read the report** (`build/staging/<plugin>.report.json`). Each finding has a `fix` id; apply it as described in [apm-alignment-fixes.md](references/apm-alignment-fixes.md).
3. **Re-run until validation and test deploy pass.** Test deploy installs into `build/test-deploy/<plugin>/`, checks every deployed skill against staging, then uninstalls.
4. **Install from a materialized clone** (`apm install <clone>/plugins/<plugin>`); the raw git path lacks copy-manifest files. `--pack` builds a bundle for whole-plugin installs (no `--skill`).

Related tools in `scripts/`: `convert_symlinks_to_manifest.py` (symlinks to copy entries, dry-run by default), `materialize_copies.py` (write copies after cloning; `--check` for drift), `decouple_agent_paths.py` (rewrite hardcoded `.agents/` references, dry-run by default).

## Authoring Rules for APM

| Reference to | Write it as |
|---|---|
| Another skill or agent | Its name: "use the `managing-adrs` skill" |
| A file in the same skill | A path relative to the skill folder (`references/`, `scripts/`) |
| A document elsewhere in the plugin | A markdown link with a `../` path inside the plugin |
| A script the skill runs | Keep it inside the skill (a copy-manifest entry if it is shared) |
| A hook script | `${CLAUDE_PLUGIN_ROOT}/hooks/x.py` in `hooks/hooks.json` |
| Another plugin's files | The other plugin's skill by name, never a path |

Never name an install folder (`.agents/`, `.claude/`, `~/.apm/`) in instructions; it differs by harness and by project versus global install.

## Verification

Run the pipeline with `--pack`. It passes when validation reports 0 errors, test deploy installs and uninstalls cleanly, and the bundle is written. Tests: `plugins/agent-scaffolders/tests/test_apm_build_pipeline.py` (set `APM_BIN` to include the APM install and pack cases).

## References

- [apm-alignment-fixes.md](references/apm-alignment-fixes.md) — Standard fix for every pipeline finding (SF-1 to SF-11), with applied examples.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for the earlier overlay, hybrid and full conversion modes of `migrate_to_apm.py`.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for mapping errors and validation rejections.
