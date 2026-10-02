---
name: obsidian-init
description: Initializes and onboards a new project repository as an Obsidian Vault. Configures vault settings, exclusion filters, and agent discovery.
---

# Obsidian Init (obsidian-init)

Initializes project repositories as Obsidian Vaults with baseline configuration, developer exclusions, and agent discovery.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Frontmatter operations must preserve formatting and comments using `ruamel.yaml`.
- Never index machine-generated context snapshots (`.worktrees/`, `node_modules/`, `*.json`, `*_packet.md`) to prevent graph pollution.
- All vault initialization mutations must be verified with `--validate-only` prior to state application.

## Dependencies

Requires Python 3.8+ and standard library modules.

## Quick start
```bash
# 1. Initialize vault with default exclusions
python3 plugins/obsidian-wiki-engine/scripts/init_vault.py --vault-root <path-to-project>

# 2. Export vault path for downstream tools
export VAULT_PATH=<path-to-project>
```

## Workflow
1. **Prerequisites Verification**: Check Obsidian Desktop, Obsidian CLI, and Python packages.
2. **Vault Initialization**: Create `.obsidian/app.json` with baseline configurations and `.gitignore` entries.
3. **Exclusion Setup**: Apply exclusion rules for build artifacts, dependencies, and vector stores.
4. **Post-Init Validation**: Verify wikilink resolution and folder hierarchy within Obsidian.
5. **Discovery Registration**: Initialize source registry (`rlm_wiki_raw_sources_manifest.json`).

## Verification
```bash
# Validate vault configuration and exclusion rules
python3 plugins/obsidian-wiki-engine/scripts/init_vault.py --vault-root <path-to-project> --validate-only

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-init --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Vault initialization gates and verification criteria.
- [fallback-tree.md](references/fallback-tree.md) - Recovery procedures for missing prerequisites or corrupted config.
- [obsidian-vault-onboarding-guide.md](references/obsidian-vault-onboarding-guide.md) - Complete vault lifecycle and schema guide.
