# Acceptance Criteria: authoring-plugins

Merged from the retired skills; one section per mode.

## Mode: create-plugin

**Purpose**: Verify the system generates compliant APM-native and `.claude-plugin` architectures.

## 1. Directory Structure
- **[PASSED]**: Generates `.apm/skills/`, `.claude-plugin/plugin.json`, `apm.yml`, `README.md`, and (when `--with-hooks` is set) `.apm/hooks/hooks.json`.
- **[FAILED]**: Fails to create `.apm/skills/` or puts shared scripts at the plugin root.

## 2. Configuration Files
- **[PASSED]**: Generates `apm.yml`, `.claude-plugin/plugin.json` (with an `author` object and no `skills`/`agents`/`hooks` arrays), and (when `--with-mcp` is set) `.mcp.json`.
- **[FAILED]**: Names the file `mcp.json` (missing dot) or fails to generate valid manifests.

## Mode: audit-plugin

**Purpose**: Verify the system auditor accurately detects specification failures.

## 1. File & Primitive Detection
- **[PASSED]**: Auditor flags missing `.claude-plugin/plugin.json`, duplicate primitive directories outside `.apm/`, and invalid `lsp.json` structures.
- **[FAILED]**: Auditor silently passes a plugin that stores its `hooks.json` in the root directory instead of `.apm/hooks/hooks.json` (or `hooks/hooks.json`).

## 2. Self-Contained Skill Enforcement
- **[PASSED]**: Auditor strictly rejects raw filesystem symlinks (`SF-2`), nested `SKILL.md` files, and duplicate plugin-root files inside `.apm/skills/*/`.
- **[FAILED]**: Auditor allows raw symlinks or nested `SKILL.md` files inside a skill's resource directories.
