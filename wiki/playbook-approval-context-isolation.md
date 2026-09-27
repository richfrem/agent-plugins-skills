# Playbook: Approval context isolation and evidence completeness

**Status**: CONFIRMED
**Discovered**: 2026-09-27

## Hard invariants

- Production tasks use the human approval context; simulations use a separate database and agent key.
- One task uses one approving key, beginning with its first signed gate.
- A genuine DONE signature alone is insufficient: consumers must authenticate every proof-bearing
  history transition, its consumed request, and the exact content-bound challenge.
- Missing legacy signatures fail closed. Never manufacture evidence from unsigned receipts.
- An account existing does not prove the agent runs under it or lacks access to human trust files.
- Same-account hostile modification requires deployment isolation, not another writable database flag.
- Shared diagram masters belong to the plugin; public docs paths and skill spokes are managed links.

## Canonical verification flow

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest plugins/agent-agentic-os/tests/test_approver_isolation.py plugins/agent-agentic-os/tests/test_dual_identity_onboarding.py -q -p no:cacheprovider
python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-agentic-os
```

Run from the source checkout. Installed-skill tests materialize symlinks as hard copies and execute
the simulator outside the source tree. Signing remains human-controlled for production.

## Negative constraints

Do not equate a passing happy path with an adversarial boundary; deletion and metadata alteration
tests must exercise real SQLite files, hooks, and signatures. Do not advertise historical CIBA/FIDO
design sketches as deployed mechanisms. Repository-domain replay and runtime privilege isolation
must not be claimed solved merely by validating a database stamp.
