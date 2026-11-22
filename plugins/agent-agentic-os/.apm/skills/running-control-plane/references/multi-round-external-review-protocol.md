# Multi-Round External Review Protocol

Applies at both `PLAN_REVIEW` (plan) and `WORKTREE_REVIEW` (implementation) gates
whenever the user opts into external review rather than waiving it via `signed_decisions`. Builds on
`bundling-context`'s generic Multi-Persona Fan-Out mechanics (per-persona `responses/` subfolder,
regenerate-in-place per round) with the review-specific judgment calls those generic mechanics
deliberately don't encode.

## Persona selection is content-driven, not fixed

The Graph Planning Phase 1 Fan-Out Trio (Architecture Skeptic, Security/Edge-Case Auditor, TDD
Contract Reviewer) is a default, not a mandate. Add or drop personas based on what the round
actually touched:
- A round that added significant new test coverage warrants `tdd-contract-reviewer.md` even if
  it wasn't in an earlier round.
- A round that's purely cosmetic/docs may warrant only one persona, or skip this gate entirely
  (see Path B in `SKILL.md`).
- A round touching security-sensitive logic (auth, injection surfaces, gate enforcement) always
  warrants `adversarial-security-auditor.md`.

## Folding prior rounds' findings into the next round's brief

Before regenerating `prompt.md` for round N+1, update the leading context brief to state round
N's findings **in past tense as already-fixed** (or explicitly deferred, with why), not silently
dropped:
- List each finding with a `[FIXED]` or `[DEFERRED — reason]` tag and one line on what changed.
- Ask reviewers to verify the fix closed the gap, not rediscover the original finding — explicitly
  say "don't re-litigate finding N unless something about *how* it was fixed looks wrong."
- Carry forward anything genuinely still open (e.g. a finding whose real fix needs its own design
  pass) as an explicit "still open" item, not silently.

This keeps review rounds convergent — each round narrows toward genuinely new findings instead
of re-discovering the same ones.

## Plan review and implementation review are not interchangeable

Skipping plan review inside `PLAN_REVIEW` and only running code review inside `WORKTREE_REVIEW`
after the fact is not equivalent to running the plan gate — it's post-hoc auditing of already-
built work, which is more expensive to act on than catching a design flaw before implementation.
Both review points are independent; treat a waiver of either as a real human-signed decision
(recorded via `signed_decisions`), not a default.

## Reference

See `plugins/dev-utils/skills/bundling-context/SKILL.md`'s Multi-Persona Fan-Out Mode section for
the underlying generic folder/regeneration mechanics this protocol builds on.
