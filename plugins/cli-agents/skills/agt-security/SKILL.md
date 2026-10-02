---
name: agt-security
plugin: cli-agents
description: >-
  Provides sandboxing validation, HMAC key rotation, and budget verification to 
  manage security boundaries under Agentic Group Theory (AGT).
allowed-tools: Bash, Read, Write
---

# Agentic Group Theory Security (agt-security)

Manages local execution sandboxes, verifies process hygiene limits, and rotates cryptographic HMAC bus keys under Agentic Group Theory (AGT).

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Environment Hygiene**: Ensure banned execution variables (`PYTHONPATH`, `PYTHONHOME`, `LD_PRELOAD`, `DYLD_LIBRARY_PATH`) are scrubbed before subprocess launch.
- **Path Containment**: Ensure filesystem operations outside declared root boundaries raise explicit `PermissionError` exceptions.
- **Key Permission Enforcement**: HMAC session keys must be created exclusively with `0600` permissions inside protected secret storage (`context/exploration/.secrets/`).
- **Zero Key Leakage**: Never print, log, or leak raw HMAC key bytes to stdout, telemetry, or conversational outputs.

## Quick start

```bash
# Verify sandbox hygiene and path containment
python3 plugins/cli-agents/scripts/agt_ops.py verify-sandbox

# Rotate local HMAC session signing key
python3 plugins/cli-agents/scripts/agt_ops.py rotate-key
```

## Workflow

1. **Phase 1: Environment Hygiene Check**: Run `agt_ops.py verify-sandbox` to verify environment variable sanitization in subprocess runners.
2. **Phase 2: Boundary Containment Verification**: Confirm that path containment rules trigger `PermissionError` when accessing out-of-bounds directories.
3. **Phase 3: Cryptographic Key Rotation**: Execute `agt_ops.py rotate-key` to generate a 32-byte cryptographically secure HMAC session key with `0600` mode.
4. **Phase 4: Permission Verification**: Verify file mode permissions on `session_hmac.key` to ensure unauthorized read access is prevented.

## Verification

```bash
# Run sandbox verification
python3 plugins/cli-agents/scripts/agt_ops.py verify-sandbox

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/cli-agents/skills/agt-security --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - AGT operational security criteria.
