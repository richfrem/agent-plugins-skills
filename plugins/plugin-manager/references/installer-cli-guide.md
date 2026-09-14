# Plugin Installer CLI & Architecture Guide

## CLI Reference

### plugin_add.py (Interactive & Batch Installer)
```bash
python3 plugins/plugin-manager/scripts/plugin_add.py [SOURCE] [OPTIONS]
```
- `SOURCE`: GitHub repository shorthand (`owner/repo`), URL, or local path. If omitted, prompts with interactive menu.
- `--source`, `-s`: Explicit source argument.
- `--all`, `-a`: Install all discovered plugins in the source repository.
- `--yes`, `-y`: Non-interactive mode, skip confirmation prompts.
- `--dry-run`: Preview file operations without modifying disk.
- `--plugins <p1,p2>`: Comma-separated list of plugins to install.
- `--select-skills`: Interactively select and customize specific skills within each plugin.
- `--no-install-rules`: Skip installing plugin rules into `.agent/rules/`.
- `--no-append-rules-to-ide-files`: Skip injecting rule content into IDE instruction files (e.g. `CLAUDE.md`).

### plugin_installer.py (Engine)
```bash
python3 plugins/plugin-manager/scripts/plugin_installer.py --plugin <PATH> [OPTIONS]
```
- `--plugin <PATH>`: Absolute or relative path to a plugin directory.
- `--skills <s1,s2>`: Comma-separated subset of skills to install.
- `--dry-run`: Preview actions without writing files or symlinks.
- `--no-install-rules`: Skip installing rules into `.agent/rules/`.
- `--no-append-rules-to-ide-files`: Skip appending rules to IDE instruction files.

## Target Environments & Symlink Mapping

The installer deploys artifacts centrally into `.agents/` and creates IDE-specific symlinks:

| Target | Skills Directory | Workflows / Commands | Rules Directory |
|---|---|---|---|
| Central (`.agents/`) | `.agents/skills/<name>` | `.agents/workflows/<plugin>_<cmd>.md` | `.agent/rules/<rule>.md` |
| Claude Code (`.claude/`) | `.claude/skills/<name>` | `.claude/commands/<plugin>_<cmd>.md` | Appended or linked |
| Gemini CLI (`.gemini/`) | `.gemini/skills/<name>` | `.gemini/commands/<plugin>_<cmd>.md` | Appended or linked |
| GitHub Copilot (`.github/`) | `.github/skills/<name>` | `.github/prompts/<plugin>_<cmd>.md` | Appended or linked |

## Rules Merge Protocol

When `deploy_rules()` runs, it performs a non-destructive merge:
- New rules are installed into `.agent/rules/`.
- Existing rules are diff-merged to preserve downstream customizations.
- IDE files (such as `CLAUDE.md`) have rule sections injected or appended unless `--no-append-rules-to-ide-files` is passed.
