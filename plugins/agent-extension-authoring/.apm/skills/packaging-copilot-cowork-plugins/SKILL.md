---
name: packaging-copilot-cowork-plugins
plugin: agent-extension-authoring
description: >-
  Creates, validates and prepares Microsoft 365 Copilot Cowork plugin App Packages
  containing Agent Skills and optional remote MCP connectors. Use when scaffolding,
  converting, validating, provisioning, packaging or sharing a Cowork plugin. Not for
  APM package creation or installation (use packaging-with-apm).
argument-hint: "[create|convert|validate|package|share] [plugin path]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Packaging Copilot Cowork Plugins

Creates and validates Microsoft 365 app packages for Copilot Cowork plugins. A package
contains the plugin manifest, icons, and one or more skills; it may also declare remote
MCP connectors.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Constraints

- Package the plugin as an M365 App Package `.zip`; do not treat each skill as a
  separate app package.
- Keep each skill portable and self-contained. In tests, Cowork and Microsoft 365 Copilot
  Chat ran a packaged Python script and returned its output file; Microsoft does not
  guarantee this. Prefer scripts that write files (a local server is unreachable) and put
  must-run functionality behind a remote MCP connector.
- Publish rejects some file types (e.g. `.mmd`) and allows 20 companion files per skill; use the scripts.
- WIQD is preview software. Check its current official documentation and exact
  installed version, then pin the tested version in repository or CI setup. Do not
  guess a version or assume command compatibility.
- Do not authenticate, provision, share, publish, or delete tenant resources without
  explicit user approval for the target tenant and scope. Never request or store
  passwords, tokens, or client secrets in skill files or package artifacts.
- Inspect existing files before editing. Do not overwrite source skills, manifests,
  icons, or environment configuration without approval.

## Quick start

Identify whether the source is a WIQD project or a Claude/Open Plugin project, and read
[the package lifecycle](references/cowork-package-lifecycle.md) for the route. Without
WIQD, build locally from an APM plugin in two steps:

```bash
python scripts/scaffold_cowork_package.py --apm-plugin <plugin> --output <dir>/appPackage \
  --developer-name <name> --website-url <url> --privacy-url <url> --terms-url <url>
python scripts/package_cowork_plugin.py --plugin-path <dir>/appPackage --output-path <output.zip>
```

The scaffold bundles over-limit skills and filters unsupported file types; the packager
checks the manifest, `SKILL.md` frontmatter, links and file types.

## Workflow

1. Reuse supplied requirements. Confirm the plugin name, skills to include, connector
   endpoint and auth expectations, privacy/terms URLs for conversion when needed, and
   whether the user wants only a local ZIP or tenant-side actions.
2. Follow the relevant lifecycle route in
   [the package lifecycle](references/cowork-package-lifecycle.md). When building
   from scratch, follow its source-authoring route before creating the M365 package.
   Keep generated package files under the selected project; do not copy server
   executables into the app package.
3. Validate the built ZIP and inspect its contents before delivery. Report the exact
   artifact path, validation result, tool version, and any unperformed tenant actions.
4. If publish validation rejects something the checks missed, fix the tools here and rebuild.

## Verification

Check that the ZIP has a valid manifest, required icons, and exactly the intended skill
folders and connector declarations; ensure it contains no credentials, local secrets,
or unintended files. Verify deep validation applies to the final artifact, not only an
earlier draft. Do not report tenant sharing or publication as complete unless it was
explicitly approved and confirmed. See
[acceptance criteria](references/acceptance-criteria.md) for the completion contract.
