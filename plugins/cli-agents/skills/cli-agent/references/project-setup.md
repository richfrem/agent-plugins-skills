# Agent Project Setup Reference

Configures agent runtimes for a project and establishes a reusable, non-secret provider capability profile in `context/agent-capability-profile.json`.

## Constraints

- Require plugin installation, os-control-init and os-control-health before declaring readiness.
- Reuse confirmed answers; ask one question at a time for missing information.
- Installed alone never counts as provider access or project authorization.
- Never store credentials, tokens, prompts or raw provider output in the profile.
- Project setup does not authorize reviewer dispatch without an authorized runtime/model/effort choice at the applicable review gate.

## Quick Start

Identify the caller's project root and existing profile before asking new questions.
Read [the capability interview](project-capability-baseline.md) and [profile contract](capability-profile-contract.md).
Load the project's profile using `scripts/capability_profile.py`:
```python
from capability_profile import load_profile, write_profile
profile = load_profile(project_root)
```

## Workflow

1. **Verify Prerequisites**: Ensure environment and plugin readiness; report exact remediation when missing.
2. **Capability Interview**: Follow [project-capability-baseline.md](project-capability-baseline.md) to inventory installed CLIs, subscriptions, and authorized project providers. Reuse a ready profile and ask only about changes.
3. **Catalog Authority**: Delegate catalog authority to [model-catalog-maintenance.md](model-catalog-maintenance.md) when refresh is actually needed; project-setup does not duplicate model catalog policy or refresh models at later gates.
4. **Configuration**: Follow [project-configuration-workflow.md](project-configuration-workflow.md) to generate runtime configs.
5. **Concrete Plan & Approval**: Present the concrete setup plan; use existing authorization or obtain approval before writing the selected project's configuration files.
6. **Persist Baseline**: Validate and persist `context/agent-capability-profile.json` using `write_profile()`, then report configuration paths and readiness.

## Verification & Handoff

Use `write_profile()` / `load_profile()` to verify `context/agent-capability-profile.json` in the selected project.
Later pipeline stages must read it rather than repeat setup.
`context/memory/environment.md` is a human-readable fallback, not another preference store.
Check configuration syntax, selected runtime requirements and unavailable-provider guidance.

## Runtime References

Read only those applicable to the requested configuration:
- [Claude directory](claude-directory-spec.md) and [settings](claude-settings-schema.md).
- [Antigravity/ADK directory](antigravity-directory-spec.md) and [Gemini commands](gemini-cli-commands.md).
