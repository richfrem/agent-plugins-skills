# Agentic OS Init & Retrofit Guide (the `init` mode)

Bootstrap or retrofit the Agentic OS and 3-Layer Memory architecture in any repository. Supports fresh setup as well as retrofitting established projects to comply with autonomous evolution standards.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Trigger: "set up agentic OS", "initialize agent harness", "init my project for AI agents", "retrofit repository", "upgrade project for evolution", "sync instruction files", "where do I put CLAUDE.md", "create my agent environment", "set up persistent memory". Guides users through discovery, initializes/retrofits 3-Layer Memory, keeps AGENTS.md as the sole canonical instruction file, and guides plugin installation.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Read-Only Preflight**: Always run probe first to classify repo state; never blindly overwrite existing instructions.
2. **Canonical Instructions**: `AGENTS.md` is the sole canonical source; `CLAUDE.md` must be a short pointer.
3. **Preserve User Rules**: During retrofits, preserve custom user instructions and never destroy existing configurations without confirmation.

## Quick start

Probe installation state before taking action:

```bash
python3 ../running-control-plane/scripts/control_plane/installation_probe.py --target <project-path>
```

## Workflow

1. **Preflight**: Run `installation_probe.py` to classify target as `FRESH`, `COMPLETE`, or `PARTIAL_OR_DRIFTED`.
2. **Discovery**: Interview stack, AI platforms, and package manager.
3. **Synthesize Instructions**: Keep `AGENTS.md` canonical per [instruction-blending.md](../instruction-blending.md).
4. **Execute Provisioning**:
   - Fresh: `python3 scripts/init_agentic_os.py --target <project-path> --sync-instructions`
   - Retrofit: `python3 scripts/init_agentic_os.py --target <project-path> --retrofit`
5. **Agent Simulation Identity** (creation, validation and healthcheck: [agent-identity.md](../agent-identity.md)): Ensure agent simulation identity (`context/simulation/identity/`) is initialized so the `simulator` mode of `running-control-plane` can run state validations without human production keys:
   ```bash
   python3 -c "from pathlib import Path; from control_plane.simulation_identity import ensure_simulation_identity; ensure_simulation_identity(Path('.'))"
   ```
6. **Verify Substrate**: Confirm 3-Layer Memory structure, identity status, and run health check ([setup-healthcheck-validation.md](../setup-healthcheck-validation.md)).

## Verification

Confirm Layer 2 `wiki/`, `context/control_plane.db`, and run the `health` mode:

```bash
python3 ../running-control-plane/scripts/control_plane/installation_probe.py --target <project-path>
```

## References

- [detailed-reference.md](../init-detailed-reference.md) — Phase specifications and identity enrollment details.
- [acceptance-criteria.md](../acceptance-criteria.md#mode-init) — QA scenarios and pass/fail matrix.
- [fallback-tree.md](../fallback-tree.md#mode-init) — Remediation pathways for failed initializations or drift.
