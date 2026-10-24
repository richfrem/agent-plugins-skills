---
name: packaging-with-apm
plugin: agent-extension-authoring
description: >-
  Packages, installs and distributes agent extensions with APM (Agent Package Manager). Use when the user wants to create a new APM package, convert or migrate an existing plugin to APM and check it installs cleanly, compile a package into AGENTS.md, CLAUDE.md or GEMINI.md, install, update, pin or roll back packages globally or per project, or create a plugin marketplace catalog (marketplace.json). Not for authoring a single skill, plugin, sub-agent or rule (use the authoring-* skills).
argument-hint: "[create|convert|compile|install|marketplace] [target]"
allowed-tools: Bash, Read, Write, Glob
---

# Packaging with APM (`packaging-with-apm`)

Packages agent extensions for [APM](https://github.com/microsoft/apm) without changing their source layout, installs them with backup and rollback, and publishes marketplace catalogs. Behaviour below was verified with APM `0.33.0`.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Never change the source plugin to package it.** Staging, manifests and bundles go under `build/`; APM does not need an `apm.yml` inside the plugin.
2. **Pin APM** (`apm-cli==0.33.0`, see `requirements-dev.in`) and pin every install to `#<tag>` or `#<commit-sha>`.
3. **Compiled files are outputs.** Never edit a generated `AGENTS.md` or `GEMINI.md` when `.apm/` sources exist; change the source and recompile.
4. **No overwrites** of an existing package directory without explicit confirmation.
5. **Never edit deployed files** in harness folders; change the source and reinstall.

## Modes

Pick the mode from the request, then read its reference before running anything.

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `create` | New APM-native package from scratch | `scripts/scaffold_apm.py` | [create-apm-package.md](references/modes/create-apm-package.md) |
| `convert` | Existing plugin to APM, or an install check | `scripts/apm_build_pipeline.py` | [convert-plugin-to-apm.md](references/modes/convert-plugin-to-apm.md) |
| `compile` | Single-file context hosts (Codex, Gemini, OpenCode) | `apm compile` | [compile-apm-package.md](references/modes/compile-apm-package.md) |
| `install` | Install, update, roll back, remove | `scripts/apm_consumer.py` | [install-apm-package.md](references/modes/install-apm-package.md) |
| `marketplace` | Marketplace catalog and Gemini extension | `scripts/audit_marketplace_sources.py` | [manage-marketplace.md](references/modes/manage-marketplace.md) |

If the target harness supports native skill directories, prefer `install` over `compile`.

## Quick start

Install the pinned APM CLI once (APM does not install skill dependencies):

```bash
python3 -m pip install -r requirements-dev.txt   # run in this skill folder; installs apm-cli==0.33.0
apm --version
```

```bash
python3 scripts/scaffold_apm.py --name <package-name>                       # create
python3 scripts/apm_build_pipeline.py --plugin plugins/<name> --apm <path>   # convert
python3 scripts/apm_consumer.py install --plugins <name> --ref <tag-or-sha> --global   # install
```

## Workflow

1. Choose the mode and read its reference (the pipeline findings and their standard fixes are in [apm-alignment-fixes.md](references/apm-alignment-fixes.md)).
2. Run the mode's entry point; dry-run first where the script offers it.
3. Re-run until the mode's verification passes, then report the generated files or installed targets.
4. On any failure follow that mode's section in [fallback-tree.md](references/fallback-tree.md).

`materialize_copies.py` and `convert_symlinks_to_manifest.py` stay in `scripts/` while any plugin still uses a copy manifest; `decouple_agent_paths.py` rewrites hardcoded install-folder paths.

## Verification

```bash
python3 scripts/validate_apm_package.py --path ./<package-name>   # create
apm compile --validate                                            # compile
python3 scripts/apm_consumer.py list-backups                      # install
python3 scripts/audit_marketplace_sources.py .                    # marketplace
```

Run the tests with `python3 -m pytest tests` (set `APM_BIN` to include the install and pack cases). Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create](references/modes/create-apm-package.md) • [convert](references/modes/convert-plugin-to-apm.md) • [compile](references/modes/compile-apm-package.md) • [install](references/modes/install-apm-package.md) • [marketplace](references/modes/manage-marketplace.md)
- Detail: [legacy-plugin-conversion-guide.md](references/legacy-plugin-conversion-guide.md) • [apm-alignment-fixes.md](references/apm-alignment-fixes.md) • [agent-package-manager-overview.md](references/agent-package-manager-overview.md) • [marketplace.md](references/marketplace.md) • [marketplace-schema.md](references/marketplace-schema.md) • [marketplace-architecture.md](references/marketplace-architecture.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
- Example: [marketplace.json](examples/marketplace.json) • Diagram: [packaging-with-apm-flow.mmd](references/diagrams/packaging-with-apm-flow.mmd)
