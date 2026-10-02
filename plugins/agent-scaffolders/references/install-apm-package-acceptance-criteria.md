# Acceptance Criteria: install-apm-package

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
