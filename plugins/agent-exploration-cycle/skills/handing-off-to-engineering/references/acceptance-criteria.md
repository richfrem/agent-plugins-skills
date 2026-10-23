# Acceptance Criteria: handing-off-to-engineering

## 1. Routing
- [ ] Triggers on "prepare the handoff", "what risk tier is this", "hand this to engineering", "diagnose this codebase before we change it", "we hit an unknown during the build".
- [ ] Does not write the specification or implement; those belong to the receiving team.

## 2. Risk tier
- [ ] The five questions are asked and each answer carries a one-sentence evidence note; a missing or vague answer blocks finalization.
- [ ] One rule applies: Tier 3 when Q3 or Q4 is "yes", or Q1 and Q2 are both "yes"; Q5 alone is Tier 2 with ethics review; all "no" is Tier 1.
- [ ] Tier 3 writes `exploration/handoffs/tier3-risk-summary.md` first, repeats the canonical Tier-3 redirect without softening, and never lets the expert deploy directly.

## 3. Package
- [ ] The package lands at `exploration/handoffs/handoff-package.md` (never a singular `handoff/` folder) with a `## Risk Assessment` block and `**Tier:**`.
- [ ] It contains no `[NEEDS HUMAN INPUT]`; unresolved items become `[UNCONFIRMED]` with a reason and are listed once in `## Deferred Gaps`.
- [ ] Every readiness check has an evidence sentence; every major claim cites its source capture.
- [ ] Three blocker questions for the named consumer are predicted and resolved inline or listed under `## Unresolved Ambiguity`.
- [ ] `python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 4` passes; the skill ends with `PHASE 4 COMPLETE`.

## 4. Technical discovery
- [ ] `python3 scripts/technical_diagnostic_engine.py --task-id <id> --title "<title>" --output exploration/DIAGNOSTIC_BRIEF.md` is read-only and writes the brief with a handoff contract section.
- [ ] Source files outside `exploration/` are never modified.

## 5. Control plane and re-entry
- [ ] The structured-engineering route names the `os-control-intake` skill; no path or Python import into `agent-agentic-os` is used.
- [ ] A re-entry brief quotes the engineering ambiguity verbatim before rephrasing it.

## 6. Code
- [ ] `python3 -m pytest scripts -q` passes from the skill folder.
