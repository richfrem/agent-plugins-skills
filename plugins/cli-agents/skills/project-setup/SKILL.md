---
name: project-setup
plugin: cli-agents
description: Configures agent runtimes for a project and establishes a reusable, non-secret provider capability profile. Use for project setup, agent configuration scaffolding, or refreshing provider access and model preferences.
allowed-tools: Bash, Read, Write
---

# Agent Project Setup

Configure the selected project and establish one reusable capability baseline.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Capability interview](references/project-capability-baseline.md)
- [Configuration workflow](references/project-configuration-workflow.md)

## Constraints

Require plugin installation, os-init and os-health-check before declaring readiness.
Reuse confirmed answers; ask one question at a time for missing information.
Installed alone never counts as provider access or project authorization.
Never store credentials, tokens, prompts or raw provider output in the profile.
Project setup does not authorize reviewer dispatch. Do not dispatch an internal reviewer
without an authorized runtime/model/effort choice at the applicable review gate.

## Quick start

Identify the caller's project root and existing profile before asking new questions.
Read [the capability interview](references/project-capability-baseline.md) and
[profile contract](references/capability-profile-contract.md). Load the project's
profile with the bundled `scripts/capability_profile.py` load_profile interface.

## Workflow

1. Verify prerequisites; report exact remediation when missing.
2. Establish or refresh the baseline; reuse a ready profile and ask only about changes.
3. Delegate catalog authority to update-cli-models when refresh is actually needed;
   this skill does not duplicate model catalog policy or refresh models at later gates.
4. Follow [configuration workflow](references/project-configuration-workflow.md).
5. Present the concrete setup plan; use existing authorization or obtain approval
   before writing the selected project's configuration files.
6. Validate and persist the profile, then report configuration paths and readiness.

## Verification

Use write_profile/load_profile to verify `context/agent-capability-profile.json`
in the selected project. Later pipeline stages must read it rather than repeat setup.
`context/memory/environment.md` is a human-readable fallback, not another preference store.
Check configuration syntax, selected runtime requirements and unavailable-provider guidance.

## Runtime references

Read only those applicable to the requested configuration:

- [Claude directory](references/claude-directory-spec.md) and [settings](references/claude-settings-schema.md).
- [Antigravity/ADK directory](references/antigravity-directory-spec.md) and [Gemini commands](references/gemini-cli-commands.md).
