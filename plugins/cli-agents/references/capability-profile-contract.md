# Local Capability Profile

`project-setup` may collect a local, non-secret capability profile after the
consuming repository has completed plugin installation, `os-init`, and
`os-health-check`.

Store it at `context/agent-capability-profile.json`; the path is gitignored by
default.

The profile is JSON and must validate against schema version `1`. It records
only installation status, user-confirmed access status, derived provider
availability, user-selected low/medium/high model IDs, fallback order,
non-secret constraints, source, and an update timestamp. It must never
contain credentials, API keys, access tokens, private prompts, or raw provider
output.

For each provider, `installed` records the deterministic CLI probe result,
`access_confirmed` records the user's explicit subscription/account answer,
`access_status` records a non-secret state such as `confirmed`,
`no_subscription`, `not_authenticated`, `not_confirmed`, or `unknown`, and
`project_authorized` records the user's explicit authorization to use the
provider for this project. `available` may be true only when the user confirms
access, the user confirms project authorization, and the CLI probe succeeds.
An installed CLI without a subscription is therefore recorded as installed but
unavailable; a work account without project authorization is also unavailable.
Installation alone never authorizes use.

Use `scripts/capability_profile.py` to classify the profile as:

- `unconfigured` — file is absent;
- `partial` — structurally valid but required fields are not complete;
- `invalid` — unreadable or schema-invalid;
- `stale` — a supplied plugin/catalog snapshot no longer matches;
- `ready` — valid and current.

An unavailable optional provider is recorded as unavailable and does not block
setup. A missing, partial, invalid, or stale profile must produce remediation
guidance rather than silently selecting a provider.

`fallback_order` is retained as user preference metadata for setup and future
orchestration. `run_agent.py` does not silently change an explicitly requested
`--cli` backend; when that backend is selected but unavailable in the profile,
it uses that backend's catalog default or reports the backend's normal runtime
failure. Provider switching requires an explicit orchestration decision.

Snapshot-bearing profiles are also treated as stale when the caller cannot
provide the corresponding current snapshot. This prevents routing from trusting
an unverifiable profile after an installation or catalog update.
