# Acceptance Criteria: plugin-syncer

## Functional Requirements
1. **Full Synchronization**: The skill must be able to sync all plugins strictly recorded in `plugin-sources.json` by invoking the underlying script safely.
2. **Selective Execution**: It must accurately relay user requests for `--dry-run` and `--cleanup-only` modes.
3. **Canonical Alignment**: It must respect the canonical separation of duties where addition and deletion are handled by the installer and remover skills respectively.

## Non-Functional Requirements
1. **Idempotence**: Running the underlying script multiple times must leave the system in exactly the same valid state.
2. **Zero Dependencies**: Must leverage standard Python libraries exclusively without needing Node.js or `npmi` installs to ensure Windows compatibility.
