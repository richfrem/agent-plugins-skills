---
concept: acceptance-criteria-plugin-installer
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/plugin-installer/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.189397+00:00
cluster: passed
content_hash: 32097a035f9ed35e
---

# Acceptance Criteria: plugin-installer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: plugin-installer

**Purpose**: Verify the Universal System Bridger executes and maps components accurately to appropriate agent environments.

## 1. Automatic Target Detection
- **[PASSED]**: The bridge auto-detects `DETECTABLE_AGENTS` present in the project (e.g., `.agent`, `.claude`, `.github`, `.gemini`) and sequentially bridges the plugin to all active environments, handling environment-specific syntaxes.
- **[FAILED]**: The bridge attempts to use a deprecated `--target` argument, or fails to detect an existing valid agent directory.

## 2. Directory and Component Separation 
- **[PASSED]**: Logic in `plugins/<name>/skills/` is deployed to central `.agents/skills/` and symlinked correctly. `plugins/<name>/commands/` is flattened into `.agents/workflows/` and mapped to individual agent files (e.g., `.prompt.md`, `.toml`, or symlinks).
- **[FAILED]**: Workflows are confused with skills, or nested directories break the installer.

## 3. Command Deployment edge-cases
- **[PASSED]**: The `deploy_commands()` function correctly ignores pointer files (files containing only a relative path, starting with `../` and having no newlines).
- **[FAILED]**: Pointer files are parsed as Markdown, causing parser errors or creating malformed target files.

## 4. Rule Merging and Deployment
- **[PASSED]**: Instructions in `plugins/<name>/rules/` are mapped dynamically. If the context requires monolithic rules (like Copilot instructions or Anthropic `CLAUDE.md`), the bridge creates/appends sections using the `<!-- BEGIN RULES -->` tags. For Antigravity, rules are kept separate in `.agents/rules/`.
- **[FAILED]**: Rule append logic corrupts the root file, inserts rules inside JSON arrays instead of Markdown tags, or fails to clean up old rules before appending new ones.

## 5. Lock File Management
- **[PASSED]**: A successful run updates `skills-lock.json` with the installed plugin's data and timestamp under `"locals"`.
- **[FAILED]**: The bridge fails to maintain the lock file or overwrites unrelated `"remotes"` in the file.


## See Also

- [[acceptance-criteria-analyze-plugin]]
- [[acceptance-criteria-audit-plugin]]
- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[acceptance-criteria-create-plugin]]
- [[acceptance-criteria-plugin-maintenance]]
- [[acceptance-criteria-analyze-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/plugin-installer/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.189397+00:00
