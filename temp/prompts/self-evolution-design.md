# Self-Evolution Architecture — Round 5 Review

## What Was Changed (this session — Round 4 feedback implemented)

Both GPT and Opus reviewed round 4. Strong convergence on all five Q answers. All changes now
implemented. Prior GPT and Opus round 4 reviews are in this bundle.

### Change 1 — `friction.resolved` event protocol (both Q1 — highest priority)

Added `### Friction Resolution Event` subsection to `os-improvement-loop/SKILL.md` immediately
after the Friction Event Protocol block. Every `type: friction` event must be closed by a
`friction.resolved` event before `task.complete` or `loop.close`.

Event shape: `--type friction --action friction.resolved` with `friction-id`, `outcome`, and
`artifact` in summary. Valid outcomes: `FIX`, `MAP_DEBT`, `ESCALATE`.

Stage 4.0 previously referenced `friction.resolved` as the verification target but the event
type was not defined anywhere. Now defined.

### Change 2 — INNER_AGENT obligation: close friction before task.complete (GPT Q5.3, Opus Q1)

INNER_AGENT execution obligations in Stage 3 now has step 8: "Before emitting `task.complete`,
close every friction event emitted this cycle with a `friction.resolved` event." Step 9 is the
existing `task.complete`. Stage 4.0 remains the backstop gate; this makes enforcement earlier.

### Change 3 — Bypass detection spec created, not implemented (both Q2)

Created `.agent/hooks/specs/bypass-detection-hook.md` with 7 initial detection rules,
registry format, integration point, and prerequisites for implementation. Deferred until
3–5 real cycles produce trace data showing which bypasses actually occur.

### Change 4 — Map Debt aging: Cycle ID + Status fields (GPT Q3 over Opus)

`map-debt.md` schema updated in both `self-evolution/SKILL.md` and `self-evolution-policy.md`:
- Added `Cycle ID` column (from `events.jsonl`)
- Added `Status` column: `OPEN / RESOLVED / ESCALATED`

Aging rule updated: "count completed cycles since entry's Cycle ID; if OPEN entry is older
than 3 completed cycles, auto-escalate." Date-based aging (Opus) deferred — dates are a proxy
for cycles; Cycle ID is the actual invariant.

### Change 5 — Globs broadened to `**/*` (Opus Q4 Scenario B)

`self-evolution-policy.md` globs changed from
`["plugins/**/SKILL.md", "plugins/**/scripts/*.py", "plugins/**/agents/*.md"]`
to `["**/*"]`. The friction model was only loading on plugin file edits. Most user tasks
don't touch those paths, so the Pre-Completion Gate and No Silent Bypass Rule weren't firing.

### Change 6 — PRE-COMPLETION GATE: capability check prefix added (GPT Q4)

Gate now opens with:
`Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]`

This closes the "I didn't know a capability existed" loophole before the three attestation
questions. Light-touch — one extra line, not a full audit.

### Change 7 — Stale body trigger text fixed (both Q5.1)

`self-evolution/SKILL.md` body text "Trigger: Any tool call or subprocess returns a failure..."
replaced with version that includes workaround/bypass/guess scenarios. The frontmatter trigger
was already correct; the body was still failure-only from before round 3.

### Change 8 — Tier 0 Map Debt wording fixed (both Q5.2)

`self-evolution-policy.md` Tier 0 section: "log as Map Debt in the evolution log" →
"record Map Debt in `<plugin>/references/map-debt.md` and append an audit row to the
evolution log." Round 4 separated the two concepts; the Tier 0 bullet hadn't been updated.

### Change 9 — Skill count fixed, third and final time (Opus Q5.3 + GPT Q5)

CLAUDE.md, GEMINI.md, copilot-instructions.md all updated:
- Old: "Active skills (17):" list of 17 + separate callout for os-skill-improvement (implied 18th)
- New: "Active skills (17):" list of 17 + "Reference skills (1): os-skill-improvement — methodology/reference only; prefer os-improvement-loop. Do not delete."
- Removed duplicate os-skill-improvement callout below the agents line.

Two sources of truth → one explicit label. The tripwire from the April 2026 incident is removed.

---

## Questions for Round 5

**Q1 — Is the `friction.resolved` protocol actually implementable with the current kernel?**
The new protocol says `--type friction --action friction.resolved`. The existing kernel
(`emit_event`) accepts arbitrary `type` and `action` strings — there's no schema validation.
But `read_events --type friction` would return BOTH `friction.encountered` and `friction.resolved`
events, making Stage 4.0's "verify exactly one resolution per friction" check ambiguous.
Does Stage 4.0 need to filter by `--action friction.resolved` separately from `--action encountered`?
Or should the type be `friction.resolved` (not `friction`) so they're distinct event types?

**Q2 — Session boundary: can the Cycle ID aging work across sessions?**
Cycle IDs come from `events.jsonl`, which is per-session (the event bus resets). If a Map Debt
entry is logged in cycle CID-001 of session A, and session B starts fresh with new CIDs, Phase 0
can read the map-debt.md but has no way to count "3 completed cycles since CID-001" without
cross-session event history. Does the architecture need a persistent cycle counter? Or should
we fall back to calendar-day aging (Opus's suggestion) for cross-session entries?

**Q3 — Tier 0 duplication (Opus Q5.1, deferred):**
Tier 0 signal list appears identically in `self-evolution-policy.md` AND `self-evolution/SKILL.md`
Phase 1. Opus flagged this as a drift risk — when one is updated, the other won't be.
Is the right fix: keep iron-law version in the rule file, replace Phase 1 list with a pointer?
Or is the duplication acceptable as a redundancy (both files load in different contexts)?

**Q4 — Evolution log header location (Opus Q5.2):**
The evolution log creation logic appears in both Phase 0 (bootstrap profile mentions the path)
and Phase 7 (creates the file with header if missing). Is this acceptable or should Phase 7
be the single owner of "create evolution log with header"?

**Q5 — Is this architecture now complete enough to close the branch and ship?**
After 5 rounds of multi-LLM review, the architecture covers: friction-driven triggering (Tier 0),
mandatory self-reporting (Pre-Completion Gate + friction.resolved), persistent debt tracking
(map-debt.md with Cycle ID + Status), external bypass spec (deferred), and deletion guard.
Is there a remaining structural gap that would justify a round 6, or is the right next step
to merge and run real sessions against it?
