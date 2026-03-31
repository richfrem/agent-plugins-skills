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
