# Session Debrief: Issue #523 (SQLite Trigger-Based Transition Enforcement) — 2026-09-07

**Scope of this debrief:** the full session that started with re-evaluating #523's accepted-risk
disposition, through interview-spec, spec-stage review, implementation, two rounds of code
review, and finishing with two clean, unpushed local branches (`feature/issue-523-trigger-enforcement`,
`fix/review-gate-method-choice`). Written before either branch was pushed or PR'd.

---

## What went well

**Empirical-first debugging, not assumption-first.** Every non-obvious SQLite behavior in this
session was discovered by actually running code against a real (or `/tmp` prototype) database,
not by reasoning from documentation alone:
- `RAISE(ABORT)`/`FAIL`/`IGNORE` rolling back an earlier trigger's audit-log `INSERT` — disproven
  a "log then abort" design that looked correct on paper, via a 3-line `/tmp` SQLite test before
  any production code was written.
- The INSERT-trigger/UPDATE-trigger cross-trigger cascade — found by actually inserting an
  illegal row and inspecting the resulting `transition_violations` table, not by static analysis.
- `_rebuild_schema_transactional()` silently destroying `enforce_valid_transition` — found by
  actually calling the rebuild method and querying `sqlite_master` for surviving triggers.
- `_sync_valid_transitions()`'s race window — proven with a forced mid-batch constraint violation
  in a real TDD RED test (17/53 rows survived), not merely inferred from reading the diff.

This is the single strongest pattern of the session: every fix traces to a reproduced failure,
not a hypothesized one. Zero of the four real bugs found tonight were caught by design review
alone — all four needed code to actually run.

**Disciplined scoping — 10 issues filed rather than absorbed.** Multiple genuinely interesting,
adjacent problems surfaced during #523's work (audit.py's 45 pre-existing findings, the
pre-existing `_rebuild_schema_transactional()` atomicity bug, the review-gate UX idea, three
separate architecture-level ideas about self-improvement/reflection). Every one of them was
filed as its own issue or comment rather than folded into #523's diff. The clearest test of this
discipline: `_rebuild_schema_transactional()`'s atomicity bug was found *during a review of
#523's own code*, sits inside the exact function #523's new triggers were added to, and was
still filed separately (#552) rather than fixed inline — because the bug itself predates #523
and wasn't caused by it. That's a harder scoping call than filing the unrelated audit findings,
and it held.

**Two-round review process, both rounds finding real things.** The spec-stage single-agent
security review (before any code was written) found the INSERT/DELETE+INSERT bypass and the
legitimate-caller-drift residual risk — genuine gaps in a design that had already been through
several rounds of interview-spec discussion. The implementation-stage review (after code was
committed) found the `_sync_valid_transitions()` race and the `_rebuild_schema_transactional()`
atomicity bug — neither visible from the spec alone, only from reading the actual SQL. Neither
review was a rubber stamp; both returned REVISE/"proceed with changes," and both sets of
findings were empirically verified (not just accepted on the auditor's word) before being acted
on.

---

## What was inefficient

**Process overhead exceeded task size at multiple points, and this was flagged mid-session
rather than caught in retrospect.** Concretely:
- The review-gate template redesign (5-way question structure) required three back-and-forth
  rounds (propose 2-axis idea → clarify coordinator's flat-question-list constraint → wording
  tweak → approve) for what is, in the end, a YAML text edit to two option lists. The underlying
  design constraint (coordinator has no conditional-question support) could have been checked
  and stated up front in the first proposal, collapsing two rounds into one.
- Several GitHub issues were filed reactively, in small batches, as they were noticed mid-turn
  (#543/#544 while #523 was already mid-review; #545/#546/#550 while #523 was already
  mid-implementation; #551 while #523 was already mid-commit). Each one was handled correctly
  in isolation, but the constant context-switching between "advance #523" and "file this
  unrelated thing right now" added real overhead — a single end-of-session sweep would have
  produced the same 10 issues with less thread-juggling, at the cost of losing some findings if
  they weren't written down immediately. Given how many of tonight's findings were genuinely
  time-sensitive (discovered mid-debugging, easy to forget), immediate filing was probably still
  the right call *for this session* — but it's worth naming as overhead, not pretending it was
  free.
- The Finding-1-vs-Finding-2 disposition question (rebuild atomicity vs. sync race) took two
  full question/answer round-trips to resolve, including one where the user had to explicitly
  restate that the two findings were different in kind (pre-existing vs. #523's-own-new-code)
  after an initial answer was deferred. The distinction was correct and important, but it could
  have been stated as the recommendation up front instead of presented as a symmetric two-way
  choice needing separate resolution for each.

**Net assessment:** none of the overhead produced wrong outcomes — every deferred/blocked/fixed
decision that came out of the back-and-forth was correct. The inefficiency was in the *shape* of
the process (more round-trips than strictly necessary), not its *conclusions*.

---

## Every issue filed tonight

| # | Title | Status |
|---|---|---|
| [#543](https://github.com/richfrem/agent-plugins-skills/issues/543) | Verify/refresh `cheapest_models.json` pricing (Sept 2026) | Ready-to-work — mechanical verification/refresh task |
| [#544](https://github.com/richfrem/agent-plugins-skills/issues/544) | Review-persona dispatch doesn't consult `cheapest_models.json` | Ready-to-work — well-scoped, no open design questions |
| [#545](https://github.com/richfrem/agent-plugins-skills/issues/545) | map-debt/evolution-log ↔ GitHub issue bidirectional cross-referencing | Needs-user-decision — mechanism (schema field vs. convention) not yet chosen |
| [#546](https://github.com/richfrem/agent-plugins-skills/issues/546) | Periodic issue-hygiene capability (staleness/silent-fix detection) | Needs-user-decision — session-start check vs. standalone skill vs. both |
| [#547](https://github.com/richfrem/agent-plugins-skills/issues/547) | Pipeline-close self-reflection step at `DONE` | Blocked — explicitly subsumed by #548's broader design pass; should not be worked independently |
| [#548](https://github.com/richfrem/agent-plugins-skills/issues/548) | Two-tier evolution/improvement architecture design (skill-level vs. pipeline-level) | Blocked — needs its own dedicated design pass before any of #519/#536/#547 proceed; three rounds of guidance already added via comments, no design doc written yet |
| [#549](https://github.com/richfrem/agent-plugins-skills/issues/549) | Control-plane pipeline architecture overview document | Ready-to-work — pure documentation task, no design questions |
| [#550](https://github.com/richfrem/agent-plugins-skills/issues/550) | Installed plugin copies file verified bug reports upstream | Needs-user-decision — capability 1+2 scoped, but implementation approach (new skill vs. extend `github-issue-agent`) not chosen |
| [#551](https://github.com/richfrem/agent-plugins-skills/issues/551) | 45 pre-existing audit findings across ~24 skills | Ready-to-work — mechanical (line-trimming, adding missing links), strong batch-PR candidate |
| [#552](https://github.com/richfrem/agent-plugins-skills/issues/552) | `_rebuild_schema_transactional()` broken atomicity | Ready-to-work — root cause fully diagnosed and reproduced, fix approach specified (either split `executescript` into individual `execute()` calls, or correct the docstring) |
| [#536 comment](https://github.com/richfrem/agent-plugins-skills/issues/536) | Broadened scope to include eval.json/skill-evolution review | Deferred — folded into #536's existing blocked-on-design status, no new action |

---

## Recommended merge order (not acted on — recommendation only)

**`fix/review-gate-method-choice` first, then `feature/issue-523-trigger-enforcement`.**

Reasoning:
1. `fix/review-gate-method-choice` is smaller, fully independent, and touches shared
   infrastructure (`transition_templates.yaml`) that other in-flight or future work may also
   touch — merging it first reduces the chance of a rebase conflict against `main` moving further
   ahead of it while it sits unmerged.
2. `feature/issue-523-trigger-enforcement` is the larger, security-relevant change; merging it
   second means its final pre-merge rebase (if any conflicts arise) happens against a `main` that
   already includes the review-gate change, rather than needing a second rebase after the fact
   if the order were reversed.
3. The two branches touch almost entirely disjoint files (only `skills-lock.json` and
   `evolution-log.md` overlap, both of which are low-conflict-risk — timestamp noise and
   append-only log entries respectively), so the order has low practical stakes either way; this
   recommendation is about minimizing rebase churn, not resolving any real dependency between
   the two.
