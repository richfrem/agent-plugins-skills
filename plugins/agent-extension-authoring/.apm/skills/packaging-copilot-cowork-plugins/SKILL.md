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
- Keep each skill portable and self-contained. Packaged `scripts/` travel with the skill
  but Cowork is not guaranteed to execute them; expose runtime functionality that must
  reliably run through a remote MCP connector.
- WIQD is preview software. Check its current official documentation and exact
  installed version, then pin the tested version in repository or CI setup. Do not
  guess a version or assume command compatibility.
- Do not authenticate, provision, share, publish, or delete tenant resources without
  explicit user approval for the target tenant and scope. Never request or store
  passwords, tokens, or client secrets in skill files or package artifacts.
- Inspect existing files before editing. Do not overwrite source skills, manifests,
  icons, or environment configuration without approval.

## Quick start

Identify whether the source is a new WIQD project, an existing WIQD project, or an
existing Claude/Open Plugin project. Read
[the package lifecycle](references/cowork-package-lifecycle.md) for the applicable
creation, conversion, validation, or sharing route. To zip an existing `appPackage/`
locally, run `python scripts/package_cowork_plugin.py --plugin-path <path> --output-path
<output.zip>` (details in the lifecycle reference).

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

## Verification

Check that the ZIP has a valid manifest, required icons, and exactly the intended skill
folders and connector declarations; ensure it contains no credentials, local secrets,
or unintended files. Verify deep validation applies to the final artifact, not only an
earlier draft. Do not report tenant sharing or publication as complete unless it was
explicitly approved and confirmed. See
[acceptance criteria](references/acceptance-criteria.md) for the completion contract.
