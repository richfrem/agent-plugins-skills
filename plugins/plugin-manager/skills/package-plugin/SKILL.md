---
name: package-plugin
description: Package a plugin directory into a distributable ZIP archive with correct flags for symlink preservation, exclusion of build artifacts, and manifest validation before packaging.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Package Plugin

Package a plugin into a distributable `.zip` archive suitable for importing into Claude Code
or sharing with other teams.

## When to Use

- Exporting a plugin for Claude Code import (`claude --plugin-dir`)
- Sharing a plugin with another developer or repository
- Creating a release artifact for distribution

## Execution Steps

### 1. Validate the Plugin

Before packaging, verify the plugin has a valid manifest:

```bash
python3 ./package.py \
  --validate-only --plugin <path-to-plugin>
```

This checks:
- `./plugin.json` exists and is valid JSON
- `name` is kebab-case
- `version` is semver
- `author` is an object (not a string)
- At least one `skills/*/SKILL.md` exists

### 2. Package the Plugin

```bash
python3 ./package.py \
  --plugin <path-to-plugin> --output <destination>
```

**Default output:** `~/Desktop/<plugin-name>-v<version>.zip`

### 3. Verify the Package (Optional)

```bash
python3 ./package.py \
  --verify <path-to-zip>
```

Extracts to `/tmp/package-verify/` and confirms the structure is intact.

## What the Packager Does

1. Preserves symlinks (`--symlinks` flag) for `agents/` and `commands/` directories
2. Excludes: `.DS_Store`, `__pycache__`, `.history/`, `node_modules/`, `*.pyc`, `.git/`
3. Names output as `<plugin-name>-v<version>.zip`
4. Validates `plugin.json` schema before packaging

## Rules

- **Always validate before packaging.** Catch manifest issues before they reach consumers.
- **Never manually zip a plugin.** Always use this script to ensure correct flags.
- **Source Transparency Declaration**: state which plugin was packaged and the output path.
