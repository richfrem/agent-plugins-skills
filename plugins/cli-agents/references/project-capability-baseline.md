# Capability Baseline (once per project setup)

## Contents

- [Load and reuse](#load-and-reuse)
- [Provider interview](#provider-interview)
- [Model preferences](#model-preferences)
- [Persistence and handoff](#persistence-and-handoff)

## Load and reuse

Deep analysis belongs in project setup. Complete the interview once per project
unless environment or preferences change. Load the caller project's
`context/agent-capability-profile.json` using `scripts/capability_profile.py`.
For a ready profile, summarize it and ask only about changes. Do not repeat deep
environment or model analysis during later plan and implementation review gates.
If the profile is missing or stale, route back to project setup before offering model choices.
Partial/invalid profiles need the same explicit remediation, not silent provider selection.

## Provider interview

Collect the user-confirmed provider inventory one question at a time. Reuse answers
already supplied. For Codex, Agy, Claude, Copilot and the configured local LLM:

1. Ask whether the provider is available for the project (available: Yes/No).
2. Ask about an active subscription, account, license or other access (Yes/No/Unknown).
3. For a work-account provider, ask the separate project authorization question.
4. Verify installation/callability with a safe, non-model probe of the selected binary.

Use the installed runtime's supported probe (for example, `codex --version`,
`claude --version`, `copilot --help` or `agy --help`); do not assume `gh copilot`
is the same executable used by the router. Probe the configured local runtime.
Installed alone never counts as available. Record installed, access_confirmed,
access_status, project_authorized and the derived available value. Enable availability
only when confirmed access, project authorization and the safe probe all succeed.
No subscription, unknown access, denied/pending project authorization or probe failure
means unavailable/unverified with a specific refresh action. Optional unavailable
providers do not block configuration of the available providers.

## Model preferences

Delegate model IDs, tiers, pricing and synchronization authority to update-cli-models.
Read current catalogs without automatically starting a refresh. For each available
provider, recommend proportionate low/medium/high model preferences and ask the user
to choose or confirm only selections not already authorized. Ask separately about
fallback order and non-secret workplace, privacy, network or quota constraints.
If catalog authority is unavailable, report the missing resource and refresh action;
do not invent choices. Model preferences and fallback order are preference metadata,
not authorization for a dispatch or silent provider switch.

## Persistence and handoff

Write and validate the complete JSON using the bundled write_profile/load_profile
interfaces and the profile contract. Record unavailable providers honestly.
Never store credentials, tokens, prompts or raw provider output.
The machine-readable profile is canonical. `context/memory/environment.md`, when
present in the selected project, is a summary/compatibility fallback only.
Pipeline stages must read the profile and must not repeat this setup interview.
Project setup does not authorize reviewer dispatch. Do not dispatch an internal reviewer
until the applicable gate has an authorized runtime/model/effort choice; reuse existing
authorization rather than repeatedly asking the same question.
