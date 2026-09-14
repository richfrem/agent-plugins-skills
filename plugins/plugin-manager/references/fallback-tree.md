# Procedural Fallback Tree: Plugin Manager

## 1. Terminal Environment Missing Curses / ANSI Support
- **Condition**: Running in automated CI/CD, subprocess pipe, or dumb terminal where interactive UI cannot render.
- **Action**: Automatically fallback to headless non-interactive mode (`-y` / `--all -y` / `--manifest`). Do not hang on raw keypress capture.

## 2. Retention Manifest Missing
- **Condition**: `plugin-retention.json` does not exist when executing pruning or retention-aware sync.
- **Action**: Generate template from `plugins/plugin-manager/assets/templates/plugin-retention.template.json` or fallback to all-retained default behavior with an informative warning.

## 3. Remote Repository / Network Unavailable
- **Condition**: GitHub or remote git server unreachable during remote plugin installation.
- **Action**: Report network failure, inspect local plugin cache in `.agents/` or `plugins/`, and suggest installing from local monorepo path.

## 4. Protected Core Skill Deletion Attempt
- **Condition**: Pruning or removal command targets protected core infrastructure (`plugin-manager`, bootstrap rules).
- **Action**: Abort operation or skip protected component with an explicit error message explaining retention guardrails.
