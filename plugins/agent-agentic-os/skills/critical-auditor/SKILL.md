---
name: critical-auditor
description: Conducts a full-system adversarial audit of agent plugins, skills, specifications, and orchestration against enforced runtime contracts using deep reasoning.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Critical Auditor (`critical-auditor`)

Conducts failure-seeking adversarial system audits designed to uncover boundary violations, unverified assumptions, and enforcement loopholes.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Output Requirements](#output-requirements)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Unforgiving Mandate**: Treat guarantees as unenforced unless mathematically or programmatically verified by code and tests.
2. **Exploit Reproduction**: Every finding must include a concrete exploit reproduction scenario.
3. **No Muted Severity**: Never downgrade security or boundary findings without empirical proof of remediation.

## Quick start

Audit a target skill for boundary violations and contract enforcement:

```bash
python3 scripts/audit_skill.py <path/to/skill> --strict
```

## Workflow

1. **Map Target Surface**: Identify boundaries, evaluation suites, and state mutators in target skill or plugin.
2. **Adversarial Pass**: Probe execution enforcement, mutation integrity, eval coverage, and sandbox isolation.
3. **Draft Exploitation Scenarios**: Construct minimal repro steps illustrating how checks can be bypassed.
4. **Document Findings**: Assign severity (P0-P2), explain root failure cause, and propose remediation.

## Output Requirements

For each finding, specify:
- **Severity**: P0 (Critical), P1 (Major), P2 (Minor).
- **Reproduction**: Concrete exploit path with shell/code snippet.
- **Root Failure**: Exact reason why existing checks failed to catch it.
- **Remediation**: Structural patch or invariant enforcement.

## Verification

Confirm audit findings are documented and reproducible:

```bash
git status --short
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for adversarial audits.
- [fallback-tree.md](references/fallback-tree.md) — Failure resolution and audit escalation paths.
