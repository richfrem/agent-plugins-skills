# Acceptance Criteria: Obsidian Init

## 1. Prerequisite Check
- [ ] Agent verifies Obsidian app, obsidian-cli, and ruamel.yaml before running init.
- [ ] Missing prerequisites are reported individually with install commands.

## 2. Vault Initialization
- [ ] `.obsidian/app.json` is created with default exclusion filters.
- [ ] `.gitignore` is updated to exclude `.obsidian/`.
- [ ] `--validate-only` makes NO filesystem changes.

## 3. Safety
- [ ] Agent does NOT initialize a directory with no `.md` files without explicit user confirmation.
- [ ] Init script is idempotent — re-running on an already-initialized vault does not corrupt config.
