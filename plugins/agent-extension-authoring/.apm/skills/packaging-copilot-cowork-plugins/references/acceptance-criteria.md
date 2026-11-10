# Acceptance Criteria: packaging-copilot-cowork-plugins

## Create or convert

- The output is a Microsoft 365 Copilot Cowork app package, not an APM bundle.
- The package ZIP has `manifest.json` at its root, required icons, and the intended
  skill folders registered in `agentSkills`.
- Any requested MCP connector is represented as a remote service reference; its server
  implementation is not described as bundled or locally executable.
- Existing Claude/Open Plugin conversion uses Microsoft's current route and reports
  unsupported source features and unresolved connector placeholders.

## Validate and package

- The exact WIQD version and supported command options are checked before use because
  WIQD is preview software.
- Static and deep validation results are reported separately; deep validation covers
  the final ZIP before upload.
- Manual local packaging is identified as a fallback and does not claim to replace
  Microsoft's App Validation Library.
- Existing outputs and source files are not overwritten without explicit approval.
- The final ZIP is checked for expected contents, integrity, symbolic links, hidden
  files, and likely credential files.

## Tenant actions

- Authentication, provisioning, sharing, publication, and deletion are treated as
  external side effects requiring explicit user approval for tenant and scope.
- Connector authorization is not claimed complete merely because the package declares
  a connector.
- The final report distinguishes local packaging from any tenant-side action actually
  completed.

## Local packager

- `package_cowork_plugin.py` accepts an explicit plugin path and output ZIP path.
- It refuses invalid package roots, malformed manifest references, missing skills or
  icons, wrong icon dimensions, symbolic links, and likely credential files.
- It preserves an existing destination unless `--overwrite` is explicitly supplied.
- It includes each skill's `SKILL.md`, `references/`, `assets/` and `scripts/`, and
  excludes only source-only `evals/` and `tests/` directories, reporting what was omitted.
- It rejects a skill with more than 20 companion files, any over 5 MB, or over 10 MB total.
- Focused tests cover successful packaging, path traversal, icon validation, and
  overwrite behavior.

## Scaffold, bundle and content checks

- `scaffold_cowork_package.py` takes explicit developer, privacy and terms values and never
  invents URLs; it refuses an existing output folder and produces a manifest, both icons and
  skill folders the packager accepts.
- `bundle_skill_companions.py` never modifies the source skill, leaves skills within the limit
  unchanged, rewrites every link when bundling, filters unsupported file types and excluded
  files with plain-text replacements, and fails with an actionable message if a skill still
  exceeds the limit.
- The packager fails on incomplete or out-of-range manifest metadata, mismatched or missing
  `SKILL.md` frontmatter, broken or folder-targeting relative links, and unsupported file types,
  and warns on missing heading anchors.
- Tests cover each behavior above in addition to the original packaging cases.
