# Acceptance Criteria: convert-plugin-to-apm

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
