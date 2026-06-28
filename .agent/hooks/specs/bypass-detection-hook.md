# Bypass Detection Hook Spec

> **Status: DEFERRED** — spec only. Implement after 3–5 real cycles of friction-driven
> evolution have produced trace data showing which bypasses actually occur.
> See round 4 reviews for rationale (GPT Q2, Opus Q2).

## Purpose

Detect likely Tier 0 bypasses that agents may not self-report. Complements the Pre-Completion
Gate (which depends on self-reporting) with external verification at known high-risk operations.

## Integration Point

Repo-root `.agent/hooks/` — per ADR-004, must not be inside any plugin (would create a
cross-plugin runtime dependency). Hook fires as a PostToolUse or PreToolUse event on file
write operations.

## Canonical Capability Registry Format

```json
{
  "operations": [
    {
      "description": "Create a new skill",
      "canonical_path": "plugins/**/skills/*/SKILL.md",
      "required_capability": "create-skill",
      "detection": "wrote plugins/**/skills/*/SKILL.md without prior create-skill invocation"
    }
  ]
}
```

Registry location: `.agent/hooks/specs/bypass-capability-registry.json`

## Initial Detection Rules (7 high-confidence)

1. Wrote `plugins/**/skills/*/SKILL.md` for a **new** skill without invoking `create-skill`.
2. Modified `symlinks.json` or created symlinks without running `symlink_manager.py diagnose` first.
3. Wrote a `.sh` script despite the Python-only helper-script rule.
4. Edited `.agents/**` as if it were source of truth instead of `plugins/**`.
5. Modified `plugins/**/scripts/*.py` after a failure without updating `references/evolution-log.md`.
6. Added Map Debt in chat/output but did not write `<plugin>/references/map-debt.md`.
7. Deleted or moved any file under `plugins/**/skills/` without matching `skill-deletion-guard.md` gate.

## Implementation Notes (for when deferred work is picked up)

- Start with rules 2, 6, and 7 — highest signal, lowest false-positive risk.
- Rule 1 requires tracking whether `create-skill` was invoked this session (session state).
- Rules 3 and 4 are file-pattern checks — straightforward glob matching.
- Rule 5 requires correlating a script edit with an evolution-log append in the same session.
- Do not implement rules with high false-positive risk before running baseline session traces.
- When built: emit a `friction` event (not an error) so the friction-driven loop handles it.

## Prerequisite Before Implementation

Run 3–5 os-improvement-loop cycles with `friction.resolved` events active and review
`events.jsonl` to identify which bypass patterns actually appear vs. which are theoretical.
Design the hook against observed patterns, not anticipated ones.
