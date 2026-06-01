---
name: agt-security
plugin: cli-agents
description: >-
  Provides sandboxing validation, HMAC key rotation, and budget verification to 
  manage security boundaries under Agentic Group Theory (AGT).
allowed-tools: Bash, Read, Write
---

# Agentic Group Theory (AGT) Security Control

This skill contains tools and reference materials to manage secure local execution sandboxes, verify process hygiene limits, and rotate cryptographic bus keys.

---

## 1. Sandbox Verification

To verify that the sub-agent execution environment complies with AGT process hygiene or containerized sandboxing:
```bash
python3 plugins/cli-agents/scripts/agt_ops.py verify-sandbox
```

This performs:
1. Validating that high-risk environment variables (e.g. `ANTHROPIC_API_KEY`, `PYTHONPATH`) are scrubbed inside subprocesses.
2. Confirming that allowed path boundaries throw exceptions on out-of-bounds access.
3. Checking container status (if Docker/Podman isolation is active).

---

## 2. HMAC Key Rotation

To generate or rotate the HMAC symmetric key used to sign messages across the local control plane:
```bash
python3 plugins/cli-agents/scripts/agt_ops.py rotate-key
```

Keys are rotated dynamically and written to `${CLAUDE_PROJECT_DIR}/context/exploration/.secrets/session_hmac.key` with restricted `0600` permissions.
