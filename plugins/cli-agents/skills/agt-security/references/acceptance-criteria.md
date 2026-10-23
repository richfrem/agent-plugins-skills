# Acceptance Criteria: Agent Governance Toolkit Security (`agt-security`)

Verification criteria for Microsoft Agent Governance Toolkit (AGT) security boundaries.

## 1. Environment Sanitization & Hygiene
- [ ] Subprocess execution environment is stripped of banned injection variables (`PYTHONPATH`, `PYTHONHOME`, `LD_PRELOAD`, `DYLD_LIBRARY_PATH`).
- [ ] `agt_ops.py verify-sandbox` exits 0 with no detected dirty variables.

## 2. Filesystem Boundary Containment
- [ ] Filesystem access outside declared project roots raises explicit `PermissionError`.
- [ ] Relative traversals (`../`) outside boundaries are blocked deterministically.

## 3. Cryptographic Key Lifecycle & Secrets
- [ ] HMAC session key is generated with cryptographically secure random bytes (32 bytes).
- [ ] Key file permissions are strictly enforced to `0600` (`-rw-------`).
- [ ] Secrets directory `context/exploration/.secrets/` is protected and excluded from version control.
- [ ] Raw key bytes and HMAC tokens are never printed to stdout, console logs, or agent conversation context.
