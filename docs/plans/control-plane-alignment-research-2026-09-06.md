# Control-Plane Alignment Research — 2026-09-06/07

Research/discovery only. No code changes. No control-plane task registered for this
document itself (this is pure research, not a gated engineering task).

**Issues touched or created by this research:**
- [#519](https://github.com/richfrem/agent-plugins-skills/issues/519) — control_plane.db durability. **Re-scoped and blocked on #536** (final state — see "FINAL DISPOSITION" section near the end of this document; the durability/verification/portability/concurrency reasoning elsewhere in this document below is superseded and kept only as a record of what was tested and rejected).
- [#523](https://github.com/richfrem/agent-plugins-skills/issues/523) — raw sqlite3 bypasses gate enforcement (existing, updated with corrected evidence; unaffected by the #519 correction — unchanged final disposition).
- [#536](https://github.com/richfrem/agent-plugins-skills/issues/536) — use control-plane history as training signal. **Elevated to highest priority** — #519 now depends entirely on this issue getting a real design.
- [#537](https://github.com/richfrem/agent-plugins-skills/issues/537) — self-evolution's `evolution_state.py` duplicates `agent_control.py`'s control plane, needs reconciliation decision. Unaffected by the #519 correction — unchanged final disposition.
- [#538](https://github.com/richfrem/agent-plugins-skills/issues/538) — `cmd_recover()` reads `cycle_manifests.jsonl` without filtering by `cycle_id`, stale entries can corrupt crash-recovery decisions. Unaffected by the #519 correction — unchanged final disposition.

**⚠️ Read the "FINAL DISPOSITION (2026-09-07)" section near the end of this document
before treating any earlier section's durability/verification/portability/concurrency
reasoning as this document's conclusion — it isn't. That reasoning was tested and
superseded; only one justification survived.**

---

## Part 1: agent-agentic-os skills/agents audit vs. the new SQLite control plane

Scope: `plugins/agent-agentic-os/skills/` (~24 skills) + `plugins/agent-agentic-os/agents/`
(4 agents), assessed against `agent_control.py`/`control_plane/` (built out across #524,
#529, #533, #535).

Criteria used: a skill is a MIGRATE candidate if it persists its own durable state
representing a task lifecycle, a decision, or an outcome (TSV/JSONL/markdown ledgers) that
overlaps with what `agent_control.py`'s tables already model (task phases, human decisions,
verification receipts, transitions). Pure read-only/reporting/config-cache skills are
NOT_APPLICABLE.

### MIGRATE (3)
- **`os-eval-runner`** — `results.tsv` KEEP/DISCARD (the exact file behind issue #460's
  race condition). Migrating gets transactional SQLite writes as a side effect. Highest
  blast-radius candidate — used by every improvement loop; treat as its own design pass.
- **`os-eval-backport`** — per-file ACCEPT/ADAPT/REJECT verdicts, currently only prose in a
  dated markdown file (`context/memory/YYYY-MM-DD.md`), no structured/queryable form.
- **`os-improvement-loop`** — explicitly "owns session lifecycle" in its own docs
  (KEEP/DISCARD, no-rollback rule, iteration ceiling) but implements that lifecycle ad hoc
  across three separate files (`improvement-ledger.md`, `os-experiment-log`, survey files)
  instead of one state machine.

### NEEDS_DESIGN_REVIEW (7)
- `os-evolution-planner` — plan-writing output overlaps with `interview-spec`'s
  `DRAFT_PLAN`/`write_plan_document.py`.
- `os-evolution-verifier` — PASS/FAIL verdicts are receipt-shaped but scenarios aren't 1:1
  with a single control-plane task.
- **`os-experiment-log`** — a fully separate, parallel flat-file "control plane" for
  run/decision/outcome history (5 source types: verifier/tester/orchestrator/planner/survey).
  `os-improvement-report`'s own docs already call it "the unified source of truth"
  superseding the legacy ledger — an in-progress, undocumented consolidation that never
  considered `agent_control.py` as the actual unification target.
- `os-skill-improvement` — genuine decision/outcome ledger
  (`context/memory/tests/registry.md`, hypothesis IN_PROGRESS/CONFIRMED/FALSIFIED), but
  keyed by test hypothesis, not by task.
- **`self-evolution`** — THE most consequential finding (see below).
- `improvement-intake-agent` — one-shot config, but its `HANDOFF_BLOCK` references an
  "improvement-lifecycle-orchestrator" with IDLE/RUNNING states that doesn't clearly map to
  anything else found in this audit — separate loose thread, not itself a control-plane
  question.

### NOT_APPLICABLE (~17)
Remaining skills/agents: pure reporting, diagnostics, config caches, locks, or genuinely
different state domains (knowledge stores, one-shot rewrites). Includes: `critical-auditor`,
`evo-smoketest`, `issue-resolution-reviewer`, `optimize-agent-instructions`, `os-clean-locks`,
`os-environment-probe`, `os-eval-lab-setup`, `os-guide`, `os-health-check`, `os-improvement-report`,
`os-init`, `os-memory-manager`, `repository-improvement`, `todo-check`, `agentic-os-setup`,
`os-architect-tester-agent`.

### ALREADY_ALIGNED (3)
`interview-spec`, the `os-architect` skill (delegates to the agent below),
`os-architect-agent` (correctly calls `agent_control.py init`/`log-prior-art`/`transition`
for `task_type=EVOLUTION` — a good template for future migrations).

### Single most important finding
**`self-evolution`'s `evolution_state.py` is a fully independent, complete 12-node state
machine** (TRIAGE→PLAN→AWAITING_APPROVAL→AUTHORIZED→CREATE_WORKTREE→EXECUTE→VERIFY_GATE→
PRE_COMMIT_RECEIPT→COMMIT→FINAL_RECEIPT→COMPLETED/ROLLBACK→ESCALATED) plus `record_trace.py`'s
hash-chained `cycle_manifests.jsonl` — covering nearly the same ground as `agent_control.py`'s
14-state machine (worktree isolation, verify gates, commit, rollback, escalation), built
entirely independently. Only integration point today: a single `log-prior-art` CLI call in
Phase 0.

**This is not a migration task — it's an architectural reconciliation decision** (two
competing control planes) that should be scoped and decided on its own *before* touching any
of the 3 MIGRATE candidates above, since migrating `os-improvement-loop` or `os-eval-runner`
without settling this first risks creating a third competing lifecycle model instead of
converging on one.

### Method note
First audit-fork attempt returned in <5s with 0 tool calls — a fabricated/empty response,
caught before being trusted. Re-run with an explicit instruction to actually `Read` every
file produced the real findings above (29 tool calls, ~3.5 min).

---

## Part 2: Unrequested `.agent/learning/` runtime artifacts — investigation (2026-09-07)

User flagged three local files/dirs they don't recall requesting and don't currently use:
- `.agent/learning/vector_wiki_db/` (contains a live `chroma.sqlite3`, 512KB)
- `.agent/learning/rlm_wiki_cache.lock` (empty)
- `.agent/learning/rlm_wiki_raw_sources_manifest.json`

**Status: untracked by git** (`.agent/learning/` is entirely gitignored — confirmed via
`git status --short` returning nothing and `git log --all` on these exact paths returning no
history). These are pure local runtime state, never committed.

**Timestamps:**
- `rlm_wiki_cache.lock` — created Apr 15 08:26, modified Apr 16 23:34, 2026
- `vector_wiki_db/` — created Apr 16 22:12, modified Apr 16 22:21, 2026
- `rlm_wiki_raw_sources_manifest.json` — created/modified Apr 26 22:20, 2026

**What auto-memory claims:** `project_super_rag_architecture.md` (origin session
`2cff826b-9629-4e0c-a990-42cfbd999bf5`, dated 2026-04-16) describes these as intentional
"Super-RAG Stack" config locations, attributing the design to "user's design philosophy —
each plugin must be independently valuable, but init agents surface the upside of combining
them without requiring it."

**Caveat — this claim is not independently verified.** The memory note is an agent's own
summary of a past session, not a transcript or a git-tracked decision record. It cannot be
taken as proof the user explicitly requested a *working, populated* instance of the stack in
*this* repo, only that the *plugins implementing the pattern* were being designed around that
time.

**More likely explanation, based on file contents:** `rlm_wiki_raw_sources_manifest.json`'s
`sources` config points at this repo's own `plugins/` and `plugin-research/` directories —
i.e., the RLM/vector-db/wiki tooling was run *against this very repo* as a working test of
the `obsidian-wiki-engine`/`vector-db`/`rlm-factory` plugins during their own development
(April 2026), not because the user asked to stand up a personal knowledge base for actual
use. Consistent with the user's own statement: "I do not use vector wiki db or rlm cache
right now."

**Update (2026-09-07, later same day): direct deep-read of `self-evolution`, superseding the
first fork attempt that returned empty (0 tool calls, fabricated response, caught and
discarded).** Read `SKILL.md`, `evolution_state.py` (764 lines), `verify_evolution_receipt.py`
(199 lines) directly rather than delegating — file count was small enough that a fork added
unnecessary indirection and risk (the same fork mechanism had already failed silently once
this session).

**Node sequence** (from `SKILL.md`): `PRIOR_ART_SCAN` (Phase 0, logs into `agent_control.py`)
→ `TRIAGE` → `PLAN` → `AWAITING_APPROVAL` (human gate) → `AUTHORIZED` → `CREATE_WORKTREE` →
`EXECUTE` → `VERIFY_GATE` → pass: `PRE_COMMIT_RECEIPT` → `COMMIT` → `FINAL_RECEIPT` →
`COMPLETED`, or fail: loop to `PLAN` (<3 attempts) or `ROLLBACK` → `FINAL_RECEIPT` →
`ESCALATED` (3rd fail).

**Docstring/code drift bug found:** `evolution_state.py`'s own module docstring (line 19)
claims per-cycle storage at `context/.evolution/<cycle-id>/state.json`. The actual code
(`_state_file_path()`, line 105) writes to one single global file:
`.agent/learning/evolution_state.json` — not per-cycle. `cmd_init()` (line ~248) checks this
one file's `status == "IN_PROGRESS"` to block starting a second cycle, meaning true
concurrent multi-cycle self-evolution isn't actually supported today, contradicting what the
docstring implies. Confirmed via `ls` that this file does not currently exist on disk (no
active cycle right now). Worth its own map-debt entry; not actioned here (research only).

**Key operational finding: `cycle_manifests.jsonl` is not pure audit trail — it's read back
mid-cycle.** `verify_evolution_receipt.py`'s `compute_receipt()` (lines 84, 93) reads this
file directly and folds an `ordered_events_digest` of the cycle's own trace events into the
cryptographic `EVO-INTEGRITY-...` receipt hash that gates the `COMMIT`/`FINAL_RECEIPT`
transitions (`preimage = manifest|ordered_digest|verifier_exit_code|initial_head|tree_sha`,
line 103). So for an *active* cycle, its trace entries are genuinely load-bearing, not just
historical.

**But safely scoped per-`cycle_id`:** `_compute_ordered_events_digest()` filters
`if ev.get("cycle_id") == cycle_id` (line 48) — entries from a different or dead cycle_id are
never read into a new cycle's receipt computation. Since `live-pass-1788153987`/
`live-pass2-1788154733` never reached a terminal state, have no corresponding
`evolution_state.json` (confirmed absent), and no future cycle will ever reuse those exact
IDs, **the 5 entries already investigated above are confirmed dead and safe to clear**, with
provably zero effect on any real cycle's receipt math.

**Retain / safe-to-clear verdict:**

| Artifact | Verdict |
|---|---|
| `.agent/learning/evolution_state.json` | RETAIN while a cycle is IN_PROGRESS (currently absent — nothing to retain right now) |
| `cycle_manifests.jsonl` entries for an active cycle_id | RETAIN — read back mid-cycle for receipt computation |
| `cycle_manifests.jsonl` entries for terminal/dead cycle_ids (incl. the 2 smoke-test ones) | SAFE TO CLEAR — audit-history only, never re-read |
| `traces/raw/<cycle_id>/` | SAFE TO CLEAR always — confirmed nothing reads it back |

**Correction (second-pass fork, more thorough than the direct read above):** a follow-up
fork read `evolution_state.py`'s `cmd_recover()` (lines 656-677) and
`references/evolution-graph-nodes.md`'s TRIAGE crash-recovery decision tree — files the
direct read above did not check. Finding: `cmd_recover()` scans `event_type` across
**every** event in `cycle_manifests.jsonl`, with **no `cycle_id` filter** — unlike
`compute_receipt()`, which is correctly scoped. This means the two dead smoke-test entries
(both containing `mutation.completed`) are not merely inert: as long as they remain in the
file, any future crash-recovery call risks wrongly concluding the *current* crashed cycle
already mutated something and jumping straight to `VERIFY_GATE`, even for a cycle that never
touched a file. **Upgrades the verdict from "safe to clear, no effect" to "safe to clear and
should be cleared — leaving them is an active latent correctness bug."** Also found: the
"6-node" language in `SKILL.md`'s frontmatter/references is stale — the actual DAG
(`evolution_state.py`'s `VALID_DAG`) has 14 canonical nodes. Both are documentation-drift
findings, not yet actioned (research only). Also confirmed: `.agent/learning/evolution.lock/`
is a second, previously-undiscussed state artifact (advisory PID-liveness-checked spinlock,
stale-lock auto-clearing built in) — currently absent, same as `evolution_state.json`.

**Relation to #519 confirmed and posted:** this is the same durability gap as #519
(`control_plane.db`), a second instance. Unlike `control_plane.db`, `cycle_manifests.jsonl`
already uses the hash-chained-append-only-log pattern that #519's design discussion converged
on as the right shape — recommending #519's eventual design adopt the same pattern for
consistency, without literally merging the two schemas (see comment posted to #519).

**Explicit answer: should skill-evolution proof-of-correctness and control-plane
state-change documentation share one logging model?** Yes, at the *pattern* level — one
shared "hash-chained append-only event log" mechanism, reused by both subsystems — not one
literal merged file/table (the two model genuinely different things: an arbitrary
general-purpose task DAG vs. one fixed, security-sensitive self-mutation workflow with its
own secret-scrubbing requirement). The `cmd_recover()` finding above is a concrete
illustration of *why* this needs careful design rather than a shortcut: it's an
unscoped-by-cycle_id query over a shared append-only log, which is exactly the class of bug
you get for free once two lifecycles share one log without per-lifecycle-id segmentation
being enforced consistently everywhere the log is read. A shared *pattern* — not shared
*storage* — carries that lesson forward into #519's eventual design without repeating the
same class of bug.

---

**Resolved (2026-09-07): deleted.** Before deleting, confirmed: no `rlm_profiles.json` or
`vector_profiles.json` exists (the "actively configured for use" files were never present,
only raw runtime artifacts); every repo-wide reference to these paths lives inside
`obsidian-wiki-engine`/`agent-memory`'s own plugin source (docs/init-agent scripts describing
where they'd write these files), not a live consumer; no symlinks, no cron/hooks depend on
them. Checked `vector_wiki_db/`'s internal timestamps in detail: all 8 UUID collection
directories (including `wiki_parent_v5/`'s 6 sub-collections and the standalone
`29654bc5-...` collection) were created/modified within one 8-minute window on Apr 16 2026
22:13-22:21 — a single contiguous ChromaDB ingest run, never touched again in the ~5 months
since. Confirms the "one-off dev-test run while building the plugin" explanation over
"adopted, ongoing personal use." Deleted `vector_wiki_db/`, `rlm_wiki_cache.lock`,
`rlm_wiki_raw_sources_manifest.json`. `git status` confirms zero diff (never tracked).
`.agent/learning/traces/` (the separate, currently-active self-evolution `cycle_manifests.jsonl`
audit trail) was left untouched — unrelated system, still in use.

---

## FINAL DISPOSITION (2026-09-07): supersedes the durability/verification/portability/concurrency reasoning above

Everything above this section that argues for `control_plane.db`/`cycle_manifests.jsonl`
durability on grounds of verification-of-agent-behavior, portability across clones,
concurrency safety, or "JSONL is a validated pattern, reuse it" **was tested and rejected**
in a later extended review the same day. Kept above only as a record of what was considered
and why it didn't hold up — not as this document's conclusion.

**What makes data actually valuable — the test that survived:** data has value only when an
actual, real consumer reads it back to change a future decision — not because it exists, not
because losing it would feel like a loss, not because a plausible-sounding future use can be
imagined for it.

**Why each rejected justification failed, specifically:**
- **Verification-of-agent-behavior** — grepping `control_plane/adapters.py` directly showed
  every read of `transition_decisions`/`task_transitions` is scoped to the *same task's own
  live gating* (duplicate-write prevention, a single-task `status` lookup) — never a
  look-back at a completed task for verification. No such consumer exists in the code.
- **Portability across clones** — "would survive a fresh clone" is a property, not a use.
  No task was ever named that requires reading this data from a different machine.
- **Concurrency safety ("Kafka-style" framing)** — at this repo's actual write volume (one
  developer, infrequent writes), the probability of two writers colliding is negligible;
  the safety property doesn't defend against a risk that exists at this scale.
- **"JSONL is the validated durable pattern, reuse it"** — the cited proof
  (`cycle_manifests.jsonl`) was itself never pushed to git. Citing an unproven example as
  proven was the error, not the format choice itself.

**The one justification that survived:** durability/export has value *if and only if* it
feeds a proven or concretely-planned self-improvement/training loop — the exact pattern
already confirmed working for `os-eval-runner`'s `results.tsv`/`evals.json`, which are
genuinely git-tracked (`git check-ignore` returns no match, `git log --all` shows real
commit history, `git ls-files` confirms tracked) specifically *because* they feed its
KEEP/DISCARD loop, not because of their file format.

### Final issue dispositions

| Issue | Disposition | Reasoning | Next step |
|---|---|---|---|
| [#519](https://github.com/richfrem/agent-plugins-skills/issues/519) | Rewritten, `status:blocked` | Every justification tested except one: feeding #536's proposed training loop | Wait for #536's design |
| [#536](https://github.com/richfrem/agent-plugins-skills/issues/536) | Elevated to highest priority | Now the dependency #519 is blocked on | Write a short design note: correlated decision/outcome pairs, SQLite-sufficiency question |
| [#460](https://github.com/richfrem/agent-plugins-skills/issues/460) | Unchanged | Real bug in a verified git-tracked, proven-valuable file; unrelated to the #519 correction | Triage independently |
| [#523](https://github.com/richfrem/agent-plugins-skills/issues/523) | Unchanged | Orthogonal to durability/export entirely | None — accepted residual risk |
| [#537](https://github.com/richfrem/agent-plugins-skills/issues/537) | Unchanged | Architectural-duplication question, independent of durability | Schedule as next big architecture decision |
| [#538](https://github.com/richfrem/agent-plugins-skills/issues/538) | Unchanged | Standalone correctness bug, evidence already in hand | Fix independently |

No code implemented for any of the above. All six issues carry their own disposition
comment on GitHub with this same reasoning, posted 2026-09-07.
