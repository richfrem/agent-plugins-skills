# Acceptance Criteria: packaging-with-apm

Merged verbatim from the five retired APM skills; one section per mode.

## Mode: create-apm-package

- [ ] Successfully validates that the package name is kebab-case.
- [ ] Refuses to scaffold into an existing plugin directory (unless `--allow-hybrid` is set).
- [ ] Creates a valid `apm.yml` with metadata and governance lane.
- [ ] Creates the full `.apm/` source tree for primitives.
- [ ] Creates `docs/governance.md` matching the selected lane.
- [ ] Creates a boilerplate `README.md` and `.gitignore`.
- [ ] Runs `validate_apm_package.py` and reports results.
- [ ] Handles `--dry-run` without making any filesystem changes.
- [ ] Provides a clear "Next Steps" summary for the user.

## Mode: convert-plugin-to-apm

- [ ] Correctly identifies the source plugin by looking for `.claude-plugin/plugin.json`.
- [ ] Defaults to **Overlay mode** to prevent primitive movement.
- [ ] In **Overlay mode**, adds `apm.yml` and `docs/governance.md` without moving files.
- [ ] In **Full mode**, creates a new directory and migrates all primitives to `.apm/`.
- [ ] Correctly maps `commands/` to `.apm/prompts/`.
- [ ] Preserves existing plugin primitives untouched in overlay and hybrid modes; only APM overlay files are added.
- [ ] Generates a `docs/governance.md` file matching the selected lane.
- [ ] Runs `validate_apm_package.py` on the result.
- [ ] Flags "Dual Manifest" risk if both `plugin.json` and `apm.yml` exist without hybrid documentation.
- [ ] Handles `--dry-run` without making any filesystem changes.

## Mode: compile-apm-package

- [ ] Explained the difference between `install` and `compile` to the user.
- [ ] Verified package integrity before execution.
- [ ] Correctly identified that the target harness requires a top-level context file.
- [ ] Executed `apm compile` successfully.
- [ ] Verified the presence of generated artifacts (AGENTS.md, GEMINI.md, etc.).
- [ ] Warned the user that compiled files are not the canonical source of truth.

## Mode: install-apm-package

- [ ] Verified `apm.yml` presence before proceeding.
- [ ] Successfully executed `validate_apm_package.py` with 0 errors.
- [ ] Correctly auto-detected the harness target or exited with code 2 if ambiguous.
- [ ] Verified converged skill materialization into `.agents/skills/<package-name>/` by default.
- [ ] Supported `--target agent-skills` and `--target all,agent-skills` combinations.
- [ ] Supported `--legacy-skill-paths` for per-client skill deployment.
- [ ] Executed `apm install --dry-run` for preview when requested.
- [ ] Verified that `apm.lock.yaml` was updated or already present.
- [ ] Reminded the user of the "Source in .apm/" rule after materialization.
- [ ] Explains that `all,agent-skills` is a broad routing test, not always the recommended runtime install.
- [ ] Warns that installing both `.agents/skills/` and target-specific skill folders can cause duplicate skill discovery.
- [ ] Recommends the smallest target set needed for the user’s active runtime.
- [ ] Distinguishes install verification from runtime-discovery hygiene.

## Mode: manage-marketplace

To verify the skill correctly guides the user in setting up and managing a marketplace.

| Scenario | Expected Result | Pass/Fail |
|----------|-----------------|-----------|
| **Setup location** | The guide directs the user to place `marketplace.json` inside a `.claude-plugin/` directory at root. | **PASS** |
| **Owner field** | The `owner` field is created and defined as an object: `{"name": "Owner Name"}`. | **PASS** |
| **Name Field** | The `name` field strictly uses **kebab-case** validation. | **PASS** |
| **CLI Directives** | The guide references addition using `/plugin marketplace add` TUI behavior directives. | **PASS** |
| **Variables mapping** | The guide lists `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` absolute references mapped safely for author hooks. | **PASS** |

## Failure Patterns (FAIL)

| Scenario | Incorrect Result |
|----------|-----------------|
| **Wrong file location** | Agent places `marketplace.json` at the repo root without a `.claude-plugin/` parent directory. |
| **String `owner` field** | Generated catalog uses `"owner": "Acme Corp"` instead of `"owner": {"name": "Acme Corp"}`. |
| **Non-kebab-case name** | Generated catalog uses names with spaces or mixed case (e.g., `"My Plugin"` or `"MyPlugin"`). |
| **Wrong CLI command** | Skill tells consumers to run `claude plugins add-marketplace` or any other non-canonical command. |
| **Hardcoded paths in hooks** | Plugin author guidance uses absolute host paths (e.g., `/home/user/.claude/plugins/my-plugin/run.sh`) instead of `${CLAUDE_PLUGIN_ROOT}`. |
