---
name: reengineering-vibe-code
plugin: agent-exploration-cycle
description: >
  Rescues an existing vibe-coded prototype: audits the running app, builds a characterization test
  safety net, consolidates specs/REQS.md, extracts a pure domain layer and migrates vertical slices
  with independent certification. Use when the user says "harden our local prototype", "rescue this
  vibe-coded app", "I have a running prototype at localhost", "audit the UI", "capture
  characterization tests", "extract the domain", "migrate a slice" or "prepare this for enterprise
  delivery". Not for starting from an idea with no code (use running-exploration-cycle).
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Reengineering Vibe Code

Path 2: [vibe-reengineering.mmd](references/vibe-reengineering.mmd). Router: [vibe-orchestrator-agent.md](references/vibe-orchestrator-agent.md).

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Truth order**: `specs/REQS.md` > `tests/characterization/` > `/domain` > derived specs > prototype code ([rules](references/architecture-rules.md)). A conflict is `HUMAN_REQUIRED`.
- **Never autonomously rewrite** auth, billing, cryptography or compliance logging; they need a hash-bound `human-approval.json`.
- Characterization tests assert legacy behavior verbatim; fixtures contain no absolute paths or secrets.
- Only the four independent agents decide: `domain-purity-auditor`, `semantic-drift-auditor`, `certification-verifier` (sole authority for `slice-certified`) and `business-rule-audit-agent`. After two rejections for the same issue, escalate to the user.
- Do destructive work in an isolated workspace (`os-control-worktree` skill). Register the task through `os-control-intake` only when the user runs a control plane.
- Ask the five architecture questions one at a time. Pick runtime and model through the `cli-agent` skill.

## Quick start

```bash
test -f exploration/captures/DISCOVERY_REPORT.md || echo "start at phase 1"
ls specs/REQS.md tests/characterization 2>/dev/null
```

## Workflow

Seven phases ([guide](references/vibe-reengineer-guide.md)): browser audit, safety net, five questions, REQS and risk gate (full architecture package optional), domain extraction with purity audit, target scaffolding (ADR, ports, session memory), slice migration with drift audit and certification. Finish by handing to `handing-off-to-engineering`.

## Verification

Run the characterization suite (100 percent parity), the purity and drift reports, and the certification report in `temp/`.

Acceptance criteria: [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Absorbed skills: [vibe-reengineer.md](references/vibe-reengineer.md) • [vibe-browser-audit.md](references/vibe-browser-audit.md) • [vibe-behavioral-test-capture.md](references/vibe-behavioral-test-capture.md) • [vibe-domain-extractor.md](references/vibe-domain-extractor.md) • [vibe-slice-migrator.md](references/vibe-slice-migrator.md) • [vibe-spec-packager.md](references/vibe-spec-packager.md) • [vibe-togaf-architect.md](references/vibe-togaf-architect.md) (full spec package) • [vibe-to-engineering-handoff.md](references/vibe-to-engineering-handoff.md) (10-step pipeline) • [runtime-observer-agent.md](references/runtime-observer-agent.md) (telemetry, fixture portability)
- Criteria: [reengineer](references/vibe-reengineer-acceptance-criteria.md) • [audit](references/vibe-browser-audit-acceptance-criteria.md) • [tests](references/vibe-behavioral-test-capture-acceptance-criteria.md) • [domain](references/vibe-domain-extractor-acceptance-criteria.md) • [migrator](references/vibe-slice-migrator-acceptance-criteria.md) • [packager](references/vibe-spec-packager-acceptance-criteria.md) • [togaf](references/vibe-togaf-architect-acceptance-criteria.md)
- Templates: [domain classification](assets/domain-classification-template.md) • [session memory](assets/session-memory-template.md) • [ADR](assets/adr-template.md)
