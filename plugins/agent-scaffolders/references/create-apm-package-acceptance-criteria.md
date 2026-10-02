# Acceptance Criteria: create-apm-package

- [ ] Successfully validates that the package name is kebab-case.
- [ ] Refuses to scaffold into an existing plugin directory (unless `--allow-hybrid` is set).
- [ ] Creates a valid `apm.yml` with metadata and governance lane.
- [ ] Creates the full `.apm/` source tree for primitives.
- [ ] Creates `docs/governance.md` matching the selected lane.
- [ ] Creates a boilerplate `README.md` and `.gitignore`.
- [ ] Runs `validate_apm_package.py` and reports results.
- [ ] Handles `--dry-run` without making any filesystem changes.
- [ ] Provides a clear "Next Steps" summary for the user.
