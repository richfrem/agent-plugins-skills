---
name: vector-db-launch
plugin: agent-memory
description: Start the Native Python ChromaDB background server when concurrent multi-agent read/writes are required.
allowed-tools: Bash, Read, Write
---

# Vector DB Launch (`vector-db-launch`)

Starts and verifies the ChromaDB background HTTP service for multi-agent concurrency.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Critical Constraints

1. **Localhost-Only Binding**: NEVER bind `--host` to `0.0.0.0` or any public interface due to CVE-2026-45829/45830/45831; binding MUST remain `127.0.0.1`.
2. **In-Process Preference**: Default to in-process mode unless concurrent writer access is explicitly required.

## Quick start

Check whether the ChromaDB background server is already active:

```bash
curl -sf http://127.0.0.1:8110/api/v1/heartbeat > /dev/null && echo "ChromaDB running" || echo "ChromaDB stopped"
```

## Workflow

1. **Check Existing Service**: Query heartbeat to confirm port 8110 availability.
2. **Launch Daemon**: Start ChromaDB background server binding strictly to localhost:
   ```bash
   chroma run --host 127.0.0.1 --port 8110 --path .vector_data &
   ```
3. **Verify Heartbeat**: Poll heartbeat endpoint until healthy.
4. **Report Status**: State daemon PID, host binding, port, and storage path.

## Verification

Confirm service health via heartbeat response:

```bash
curl -sf http://127.0.0.1:8110/api/v1/heartbeat
```

## Troubleshooting

- `chroma: command not found`: Ensure dependencies are installed in virtualenv.
- `Port 8110 already in use`: Check running process with `lsof -i :8110`.
- `Permission Denied`: Confirm write access to `.vector_data`.

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for vector database launch and lifecycle.
- [vector-db-bootstrap-guide.md](references/vector-db-bootstrap-guide.md) — Initialization manual and configuration details.
