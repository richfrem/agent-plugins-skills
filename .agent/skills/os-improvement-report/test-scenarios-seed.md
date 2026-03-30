# Test Scenario Bank — Agentic OS Plugin

Pre-designed hypotheses for the test registry. ORCHESTRATOR reads this at orientation
and selects the highest-priority untested scenario for each cycle. As scenarios are run,
move them to `context/memory/tests/registry.md` with their results.

**Status note**: All `results.tsv` baselines are empty. The first eval run for each
skill establishes the baseline. Tests 1-N per skill should be designed as
"establish baseline + identify first improvement opportunity" — not comparison tests.

---

## Registry Index (All 50 Scenarios)

| ID | Target | Hypothesis | Priority |
|----|--------|------------|----------|
| T01 | os-eval-runner | Baseline routing: eval triggers on correct phrases, not on explain/describe | HIGH |
| T02 | os-eval-runner | KEEP/DISCARD threshold: clearly improved skill scores KEEP, degraded scores DISCARD | HIGH |
| T03 | os-eval-runner | Adversarial coverage: eval catches prompts designed to bypass routing | MEDIUM |
| T04 | os-eval-runner | Edge case: graceful failure when evals.json is missing or malformed | MEDIUM |
| T05 | os-eval-runner | Survey completion: evaluator completes self-assessment after every eval run | HIGH |
| T06 | os-improvement-loop | Baseline 1-cycle smoke: all 14 mandatory loop steps execute in order | HIGH |
| T07 | os-improvement-loop | Friction emission: agents emit type:friction events when encountering ambiguity | HIGH |
| T08 | os-improvement-loop | Loop report written: report file created after every cycle regardless of outcome | HIGH |
| T09 | os-improvement-loop | Survey completion: both ORCHESTRATOR and INNER_AGENT complete survey after cycle | HIGH |
| T10 | os-improvement-loop | Memory persistence: at least one promoted fact in context/memory.md after cycle | MEDIUM |
| T11 | os-improvement-loop | Auto-trigger: os-learning-loop triggered when friction_events_total reaches 3 | HIGH |
| T12 | os-improvement-loop | Lock contention: second agent attempting same lock receives clear failure, not hang | HIGH |
| T13 | os-clean-locks | Baseline routing: triggers on /os-clean-locks and lock variants, not on list-locks | HIGH |
| T14 | os-clean-locks | Stale lock cleanup: lock with PID that no longer exists gets removed | HIGH |
| T15 | os-clean-locks | Active lock protection: lock held by running PID is preserved | HIGH |
| T16 | os-clean-locks | Post-clean verification: state_update clears active_agent field after cleanup | MEDIUM |
| T17 | os-clean-locks | Survey completion: os-clean-locks completes self-assessment after every run | MEDIUM |
| T18 | os-memory-manager | Baseline promotion: ephemeral state skipped, architectural decisions promoted | HIGH |
| T19 | os-memory-manager | Dedup detection: semantic duplicate caught and flagged before write | HIGH |
| T20 | os-memory-manager | Test registry preservation: registry.md skipped by archive logic, never deleted | HIGH |
| T21 | os-memory-manager | Conflict detection: <CONFLICT> marker emitted before any write with overlap | HIGH |
| T22 | os-memory-manager | Size enforcement: memory.md over 50KB triggers archive, not silent truncation | MEDIUM |
| T23 | os-memory-manager | Survey completion: memory manager completes self-assessment after every session | HIGH |
| T24 | os-memory-manager | Rollback protocol: rejected write triggers git stash pop, file reverted | MEDIUM |
| T25 | os-memory-manager | Falsified hypothesis: DO NOT RE-TEST entry added to memory.md when hypothesis falsified | HIGH |
| T26 | learning-loop | Baseline 3-phase completion: observe, hypothesize, test phases all execute | HIGH |
| T27 | learning-loop | Survey Phase V: survey completed and saved to retrospectives/ after every run | HIGH |
| T28 | learning-loop | Metrics Phase VI: post_run_metrics.py fires and emits metric event | HIGH |
| T29 | learning-loop | Memory Phase VII: os-memory-manager invoked before handoff | HIGH |
| T30 | learning-loop | Handoff gate: Phase VIII only starts after survey saved + metrics emitted + memory written | HIGH |
| T31 | dual-loop | Baseline handoff: outer loop assigns task, inner loop completes and signals back | HIGH |
| T32 | dual-loop | Survey both agents: outer loop AND inner loop both complete self-assessment | HIGH |
| T33 | dual-loop | Friction propagation: inner loop friction events visible to outer loop via event bus | MEDIUM |
| T34 | dual-loop | Result surfacing: inner loop eval result surfaced to outer loop before next iteration | HIGH |
| T35 | dual-loop | Auto-trigger: os-learning-loop flagged when same friction cause appears 3+ times across both loops | HIGH |
| T36 | os-learning-loop | Registry orientation: Phase 1 reads registry.md and lists prior confirmed/falsified hypotheses | HIGH |
| T37 | os-learning-loop | DO NOT RE-TEST respected: agent skips hypothesis already falsified in prior cycle | HIGH |
| T38 | os-learning-loop | Pre-eval documentation: scenario file written BEFORE eval_runner.py is called | HIGH |
| T39 | os-learning-loop | Registry close: registry.md row updated from IN PROGRESS to CLOSED after cycle | HIGH |
| T40 | os-learning-loop | Fast Path vs Full Loop: Fast Path halts before Phase 3, does not acquire lock | MEDIUM |
| T41 | kernel.py | PROTECTED_STATE_KEYS state_update guard: execution_mode rejects string overwrite | HIGH |
| T42 | kernel.py | PROTECTED_STATE_KEYS state_increment guard: execution_mode rejects integer increment | HIGH |
| T43 | kernel.py | Stale lock auto-cleanup: lock file with dead PID cleared automatically on next acquire | HIGH |
| T44 | kernel.py | Lock idempotency: same agent cannot acquire the same lock twice without releasing | MEDIUM |
| T45 | kernel.py | Agent permit list: emit_event from unlisted agent name is rejected | HIGH |
| T46 | hooks | Friction count: post_run_metrics.py correctly counts type:friction events from events.jsonl | HIGH |
| T47 | hooks | Metrics on Stop: metrics report written to disk on every Stop hook fire | HIGH |
| T48 | hooks | Auto-trigger threshold: friction_events_total >= 3 emits metric that triggers os-learning-loop | HIGH |
| T49 | os-init | Interview skip: init does not repeat questions already answered in conversation | MEDIUM |
| T50 | os-init | Survey completion: init completes self-assessment after every onboarding run | HIGH |

---

## Scenario Details

---

### T01 — os-eval-runner: Baseline Routing Accuracy

- **Target**: os-eval-runner
- **Hypothesis**: The skill triggers correctly on "evaluate this skill" and related phrases,
  but does NOT trigger on "explain this skill", "describe this skill", or "show me the eval results".
- **Why now**: All results.tsv baselines are empty. This establishes routing accuracy baseline.
- **Prior results**: None — first test of this target.
- **Acceptance criteria**: Eval triggers on 3/3 positive phrases; does NOT trigger on 3/3 negative phrases.
- **Failure criteria**: Any false positive or false negative routing.
- **Known weaknesses**: Routing is inferred from description text, not a real execution test.
- **Recommended next test**: T02 (KEEP/DISCARD threshold), or T05 (survey completion).

---

### T02 — os-eval-runner: KEEP/DISCARD Threshold

- **Target**: os-eval-runner
- **Hypothesis**: The evaluator correctly assigns KEEP to a skill with an added positive example
  and DISCARD to a skill with a removed description keyword.
- **Why now**: Without a working KEEP/DISCARD signal the entire flywheel cannot function.
- **Prior results**: None.
- **Acceptance criteria**: KEEP returned for +1 positive example change; DISCARD for -1 keyword.
- **Failure criteria**: KEEP/DISCARD swapped, or STATUS: BASELINE returned for both.
- **Known weaknesses**: eval_runner.py may return BASELINE if score delta is within noise band.
- **Recommended next test**: T03 (adversarial coverage) to check eval quality after baseline confirmed.

---

### T03 — os-eval-runner: Adversarial Prompt Coverage

- **Target**: os-eval-runner
- **Hypothesis**: The current evals.json contains enough adversarial prompts to catch a skill
  that has been manipulated to trigger on unrelated keywords.
- **Why now**: Adversarial coverage gap was identified in prior session as a known weakness.
- **Prior results**: None.
- **Acceptance criteria**: DISCARD returned when skill is patched with unrelated trigger keywords.
- **Failure criteria**: KEEP returned despite adversarial manipulation.
- **Known weaknesses**: Only tests evals.json coverage, not the quality of the eval scoring rubric.
- **Recommended next test**: Add 2 adversarial prompts to evals.json and re-run T02.

---

### T04 — os-eval-runner: Graceful Failure on Missing evals.json

- **Target**: os-eval-runner
- **Hypothesis**: eval_runner.py exits with a clear error message (not a Python traceback) when
  evals.json is absent or malformed.
- **Why now**: Agents calling eval_runner.py during os-learning-loop Phase 3 should get
  actionable errors, not crashes.
- **Prior results**: None.
- **Acceptance criteria**: Exit code non-zero, stderr contains human-readable error, no traceback.
- **Failure criteria**: Python traceback printed to stdout, or silent exit code 0 on failure.
- **Known weaknesses**: Does not test partial corruption (truncated JSON).
- **Recommended next test**: Test with truncated JSON to check partial corruption handling.

---

### T05 — os-eval-runner: Self-Assessment Survey Completion

- **Target**: os-eval-runner
- **Hypothesis**: The evaluator saves a survey file to retrospectives/ after every eval run,
  including runs that return DISCARD.
- **Why now**: Survey was added to Phase 5 in this session. Needs first-run verification.
- **Prior results**: None — new phase, first test.
- **Acceptance criteria**: File `retrospectives/survey_[DATE]_[TIME]_os-eval-runner.md`
  exists with all 4 qualitative sections populated.
- **Failure criteria**: File missing, or sections left blank ("N/A").
- **Known weaknesses**: Does not verify survey quality, only existence.
- **Recommended next test**: Read survey content and check if Improvement Recommendation leads to actionable T-next entry.

---

### T06 — os-improvement-loop: Baseline 1-Cycle Smoke Test

- **Target**: os-improvement-loop (SKILL.md v0.5.0)
- **Hypothesis**: A single loop cycle with 1 ORCHESTRATOR + 1 INNER_AGENT completes all
  14 mandatory steps listed in the CRITICAL section.
- **Why now**: v0.5.0 added 7 new mandatory steps. First full validation needed.
- **Prior results**: Earlier smoke test only validated transport (kernel signal exchange).
- **Acceptance criteria**: All 14 steps logged in events.jsonl; loop report written to disk.
- **Failure criteria**: Any mandatory step absent from event stream.
- **Known weaknesses**: Two-session test requires manual coordination; hard to automate fully.
- **Recommended next test**: T07 (friction events) — use same test harness, inject ambiguity.

---

### T07 — os-improvement-loop: Friction Event Emission

- **Target**: os-improvement-loop
- **Hypothesis**: When an INNER_AGENT encounters an ambiguous task description, it emits a
  `type: friction` event before requesting human rescue.
- **Why now**: Friction events are the primary signal for os-learning-loop auto-trigger.
  If agents don't emit them, the flywheel is broken.
- **Prior results**: None — friction event protocol is new.
- **Acceptance criteria**: At least 1 `type: friction` event in events.jsonl during the cycle.
- **Failure criteria**: Agent requests human rescue without a prior friction event.
- **Known weaknesses**: Requires deliberately ambiguous task to trigger the friction path.
- **Recommended next test**: T11 (auto-trigger at 3 friction events) — inject 3 ambiguous tasks.

---

### T08 — os-improvement-loop: Loop Report Written Every Cycle

- **Target**: os-improvement-loop
- **Hypothesis**: A loop report is written to `context/memory/loop-reports/report_[CYCLE_ID].md`
  after every cycle, including cycles that end with DISCARD.
- **Why now**: Report is always written, never auto-displayed. Needs first verification.
- **Prior results**: None.
- **Acceptance criteria**: Report file exists with all 4 sections (agent summaries, baseline vs result,
  survey summaries, artifacts checklist).
- **Failure criteria**: File missing, or only written on KEEP cycles.
- **Known weaknesses**: Does not test report content quality.
- **Recommended next test**: Review report quality against the 4-section template.

---

### T09 — os-improvement-loop: Survey Completion by Both Agents

- **Target**: os-improvement-loop
- **Hypothesis**: Both ORCHESTRATOR and INNER_AGENT complete and save self-assessment surveys
  after every cycle, not just the one that ran evals.
- **Why now**: Survey is mandatory per v0.5.0. If only one agent surveys, flywheel data is incomplete.
- **Prior results**: None.
- **Acceptance criteria**: Two survey files in retrospectives/ after 1 cycle, one per agent role.
- **Failure criteria**: Only 1 survey file, or no survey files.
- **Known weaknesses**: Agent roles may be played by same Claude session; test may not distinguish.
- **Recommended next test**: T35 (dual-loop survey) — verify in proper 2-session setup.

---

### T10 — os-improvement-loop: Memory Persistence After Cycle

- **Target**: os-improvement-loop
- **Hypothesis**: At least one fact is promoted to context/memory.md after a cycle that
  produces a KEEP verdict.
- **Why now**: Memory persistence was missing from v0.3.0/v0.4.0. First test of new v0.5.0 behavior.
- **Prior results**: None.
- **Acceptance criteria**: context/memory.md modified; new fact has dedup ID assigned.
- **Failure criteria**: No modification to context/memory.md after a KEEP cycle.
- **Known weaknesses**: Does not verify fact quality or dedup correctness.
- **Recommended next test**: Run T19 (dedup detection) to verify the promoted fact would be caught on re-run.

---

### T11 — os-improvement-loop: os-learning-loop Auto-Trigger at 3 Friction Events

- **Target**: os-improvement-loop
- **Hypothesis**: When 3 friction events of the same type accumulate in events.jsonl,
  the ORCHESTRATOR flags os-learning-loop to run at next session start.
- **Why now**: Auto-trigger is the primary mechanism for systemic improvement. Unverified.
- **Prior results**: None.
- **Acceptance criteria**: After injecting 3 same-type friction events, os-learning-loop intent
  event appears in events.jsonl on next session, OR a flag file is written.
- **Failure criteria**: No os-learning-loop invocation after 3 friction events.
- **Known weaknesses**: "Next session start" is hard to test in a single session.
- **Recommended next test**: Test with friction_events_total >= 3 in post_run_metrics output (T48).

---

### T12 — os-improvement-loop: Lock Contention Handling

- **Target**: os-improvement-loop (kernel.py)
- **Hypothesis**: When two agents attempt to acquire the same lock simultaneously, the second
  receives a clear failure message and does not hang or corrupt the lock file.
- **Why now**: Lock contention is the main correctness risk in multi-session setup.
- **Prior results**: None — PID-lease locking is new in v3.
- **Acceptance criteria**: Second acquire_lock returns non-zero exit within 5 seconds;
  lock file still valid after race.
- **Failure criteria**: Deadlock, corruption of lock file, or silent success for second agent.
- **Known weaknesses**: Hard to create true simultaneity in test; sequential near-miss is easier.
- **Recommended next test**: Test stale lock auto-cleanup (T43) — related failure path.

---

### T13 — os-clean-locks: Baseline Routing

- **Target**: os-clean-locks
- **Hypothesis**: The skill triggers on "/os-clean-locks", "clear all locks", "reset agent locks",
  but does NOT trigger on "list locks", "show me the lock files", "what is locked".
- **Why now**: Routing baseline is empty. Must confirm skill is reached before testing its logic.
- **Prior results**: None.
- **Acceptance criteria**: 3/3 positive phrases route to skill; 3/3 negative phrases do not.
- **Failure criteria**: Any mis-routing in either direction.
- **Known weaknesses**: Routing is inferred, not directly observable.
- **Recommended next test**: T14 (stale lock cleanup) — test core function after routing confirmed.

---

### T14 — os-clean-locks: Stale Lock Cleanup

- **Target**: os-clean-locks
- **Hypothesis**: A lock file referencing a PID that no longer exists is removed by os-clean-locks.
- **Why now**: Stale locks from crashed sessions are the primary production failure mode.
- **Prior results**: None.
- **Acceptance criteria**: After creating a lock with PID 99999 (likely dead), os-clean-locks
  removes it and emits a cleanup event.
- **Failure criteria**: Lock preserved despite dead PID, or removed without event emission.
- **Known weaknesses**: PID 99999 may theoretically exist on some systems.
- **Recommended next test**: T15 (active lock protection) — opposite path with live PID.

---

### T15 — os-clean-locks: Active Lock Protection

- **Target**: os-clean-locks
- **Hypothesis**: A lock file referencing the current session's PID is NOT removed by os-clean-locks.
- **Why now**: Cleaning an active lock mid-session would corrupt the running agent's state.
- **Prior results**: None.
- **Acceptance criteria**: Lock with current PID preserved after os-clean-locks runs.
- **Failure criteria**: Active lock removed.
- **Known weaknesses**: Tests only the agent's own PID; multi-session scenario harder.
- **Recommended next test**: T16 (post-clean state verification) — check state_update behavior.

---

### T16 — os-clean-locks: Post-Clean State Verification

- **Target**: os-clean-locks
- **Hypothesis**: After cleanup, kernel state active_agent field is cleared via state_update.
- **Why now**: If active_agent is not cleared after lock cleanup, next session reads stale state.
- **Prior results**: None.
- **Acceptance criteria**: os-state.json active_agent field is null/empty after clean run.
- **Failure criteria**: active_agent still set to previous agent name after clean.
- **Known weaknesses**: Does not test mode or other state fields.
- **Recommended next test**: T17 (survey completion).

---

### T17 — os-clean-locks: Survey Completion

- **Target**: os-clean-locks
- **Hypothesis**: os-clean-locks completes self-assessment survey after every run,
  including trivial no-op runs where no locks were found.
- **Why now**: Survey was not in the original skill. Added in this session's audit. First test.
- **Prior results**: None.
- **Acceptance criteria**: Survey file in retrospectives/ after run.
- **Failure criteria**: No survey file, or survey skipped on no-op run.
- **Known weaknesses**: Survey quality not tested.
- **Recommended next test**: T14 again with survey quality review.

---

### T18 — os-memory-manager: Baseline Promotion Decision Accuracy

- **Target**: os-memory-manager
- **Hypothesis**: The manager correctly promotes architectural decisions and skips ephemeral state
  at a rate of 80%+ agreement with human judgment on a standard 10-item test set.
- **Why now**: Promotion accuracy is the core function. Baseline must be established first.
- **Prior results**: None.
- **Acceptance criteria**: 8/10 promotion decisions match human expectation on prepared test set.
- **Failure criteria**: Fewer than 7/10 correct; or system promotes ephemeral state consistently.
- **Known weaknesses**: "Human expectation" must be defined before running — prepare ground truth.
- **Recommended next test**: T19 (dedup detection) — second-most-critical function.

---

### T19 — os-memory-manager: Semantic Deduplication Detection

- **Target**: os-memory-manager
- **Hypothesis**: The manager catches a semantically duplicate fact (same meaning, different words)
  and emits <CONFLICT> before writing.
- **Why now**: Semantic dedup is the core "dementia defense". If it fails, memory fills with
  contradicting facts over time.
- **Prior results**: None.
- **Acceptance criteria**: <CONFLICT> emitted when a paraphrased version of an existing fact is promoted.
- **Failure criteria**: Paraphrase written as new fact without conflict detection.
- **Known weaknesses**: LLM semantic matching is probabilistic. May need 3 test cases to confirm.
- **Recommended next test**: T21 (conflict detection with overlapping rules).

---

### T20 — os-memory-manager: Test Registry Preservation

- **Target**: os-memory-manager
- **Hypothesis**: The archive logic in Phase 4 never archives context/memory/tests/registry.md,
  even when memory.md exceeds 50KB and archive is triggered.
- **Why now**: Registry preservation is a new explicit rule in Phase 3 (added this session).
  Must verify it cannot be accidentally archived.
- **Prior results**: None.
- **Acceptance criteria**: registry.md present after a forced archive operation.
- **Failure criteria**: registry.md moved to archive/ during memory size enforcement.
- **Known weaknesses**: Test requires large memory.md to trigger archive path.
- **Recommended next test**: T22 (size enforcement) uses same trigger — combine.

---

### T21 — os-memory-manager: Conflict Detection Before Write

- **Target**: os-memory-manager
- **Hypothesis**: When a proposed promoted fact overlaps with an existing rule in skills/,
  the manager emits <CONFLICT> rather than silently writing.
- **Why now**: Cross-skill conflict detection was added to Phase 4. Unverified.
- **Prior results**: None.
- **Acceptance criteria**: <CONFLICT> marker appears before write when grep finds match in skills/.
- **Failure criteria**: Write completes silently despite skill overlap found by grep.
- **Known weaknesses**: grep match quality determines sensitivity.
- **Recommended next test**: Test with a fact that partially overlaps (lower confidence case).

---

### T22 — os-memory-manager: Memory Size Limit Enforcement

- **Target**: os-memory-manager
- **Hypothesis**: When context/memory.md exceeds 50KB, the manager archives the oldest lines
  rather than silently allowing unbounded growth.
- **Why now**: Unbounded memory.md degrades context quality and model performance.
- **Prior results**: None.
- **Acceptance criteria**: After padding memory.md to 51KB, archive/YYYY-MM.md is created
  with the oldest facts.
- **Failure criteria**: No archive created; or memory.md truncated without archive.
- **Known weaknesses**: Test requires large synthetic memory.md — use a copy, not production file.
- **Recommended next test**: T20 (registry preservation) — run simultaneously with same padded file.

---

### T23 — os-memory-manager: Survey Completion

- **Target**: os-memory-manager
- **Hypothesis**: The memory manager completes Phase 5 self-assessment survey after every
  session close, including sessions with zero promotions.
- **Why now**: Survey is new (added this session). First test.
- **Prior results**: None.
- **Acceptance criteria**: Survey file saved to retrospectives/ with all 4 qualitative sections.
- **Failure criteria**: Survey absent or incomplete.
- **Known weaknesses**: Does not test whether survey insights feed back into future runs.
- **Recommended next test**: Check if survey improvement recommendation leads to a registry entry.

---

### T24 — os-memory-manager: Rollback on Rejected Write

- **Target**: os-memory-manager
- **Hypothesis**: When the user rejects a proposed write during the git stash + diff preview,
  git stash pop restores the original file correctly.
- **Why now**: Safe Write Protocol is critical for non-destructive memory updates.
- **Prior results**: None.
- **Acceptance criteria**: After rejection, memory.md byte count unchanged from pre-write state.
- **Failure criteria**: File modified despite user rejection, or git stash pop fails.
- **Known weaknesses**: Requires a real git stash state; hard to automate cleanly.
- **Recommended next test**: Test Post-Write Verification path (T19 related).

---

### T25 — os-memory-manager: Falsified Hypothesis Entry

- **Target**: os-memory-manager
- **Hypothesis**: When a test registry entry is falsified (DISCARD verdict), the manager adds
  a "DO NOT RE-TEST" entry to context/memory.md with the cycle ID as evidence.
- **Why now**: Without DO NOT RE-TEST entries, os-learning-loop will re-test the same
  hypotheses indefinitely, wasting cycles.
- **Prior results**: None.
- **Acceptance criteria**: DO NOT RE-TEST entry with cycle ID appears in memory.md after falsification.
- **Failure criteria**: No entry added, or entry added without cycle ID reference.
- **Known weaknesses**: Requires a real falsified cycle to test.
- **Recommended next test**: Verify T37 (os-learning-loop respects DO NOT RE-TEST) after this.

---

### T26 — learning-loop: Baseline 3-Phase Completion

- **Target**: learning-loop (plugins/agent-loops)
- **Hypothesis**: A full learning loop run executes all 3 core phases: observe (Phase I),
  hypothesize + design (Phase II-III), test (Phase IV) in order without skipping.
- **Why now**: Baseline needed before testing the new Phases V-VIII added this session.
- **Prior results**: None.
- **Acceptance criteria**: Events for all 3 phases present in events.jsonl.
- **Failure criteria**: Any phase absent from event stream.
- **Known weaknesses**: Phase presence in events doesn't guarantee correct execution.
- **Recommended next test**: T27 (survey Phase V) once baseline confirmed.

---

### T27 — learning-loop: Survey Completion at Phase V

- **Target**: learning-loop
- **Hypothesis**: Phase V (self-assessment survey) executes after Phase IV and saves a survey file
  to retrospectives/ before Phase VI begins.
- **Why now**: Phase V is new — added this session. First verification needed.
- **Prior results**: None.
- **Acceptance criteria**: Survey file saved; Phase VI event appears AFTER survey_completed event.
- **Failure criteria**: Phase VI starts before survey_completed; or survey absent.
- **Known weaknesses**: Event ordering in JSONL doesn't guarantee causal ordering.
- **Recommended next test**: T28 (metrics Phase VI) — continue sequence.

---

### T28 — learning-loop: Metrics Emission at Phase VI

- **Target**: learning-loop
- **Hypothesis**: post_run_metrics.py fires during Phase VI and emits a metric event with
  all required fields (human_interventions, friction_events_total, etc.).
- **Why now**: Phase VI is new — added this session.
- **Prior results**: None.
- **Acceptance criteria**: Metric event in events.jsonl with all 6 required fields populated.
- **Failure criteria**: Metric event missing, or fields null/zero when they should have values.
- **Known weaknesses**: Fields may all be 0 on a clean run — hard to distinguish from failure.
- **Recommended next test**: Inject a deliberate friction event and verify friction_events_total = 1.

---

### T29 — learning-loop: Memory Written at Phase VII

- **Target**: learning-loop
- **Hypothesis**: os-memory-manager is invoked during Phase VII and writes a session log
  before the handoff in Phase VIII.
- **Why now**: Phase VII is new — added this session.
- **Prior results**: None.
- **Acceptance criteria**: Session log file created in context/memory/YYYY-MM-DD.md before Phase VIII event.
- **Failure criteria**: No session log; or Phase VIII starts before memory write.
- **Known weaknesses**: Requires os-memory-manager to work correctly (dependency).
- **Recommended next test**: T30 (Phase VIII gate) — full sequence validation.

---

### T30 — learning-loop: Phase VIII Handoff Gate

- **Target**: learning-loop
- **Hypothesis**: Phase VIII (handoff) only begins after survey is saved AND metrics are emitted
  AND memory is written — all three gates must pass.
- **Why now**: The gate is defined in the SKILL but there's no enforcement mechanism tested.
- **Prior results**: None.
- **Acceptance criteria**: Interrupt after Phase VII (before memory write); Phase VIII does not proceed.
- **Failure criteria**: Phase VIII proceeds despite incomplete prior phases.
- **Known weaknesses**: Hard to simulate partial completion without modifying the skill.
- **Recommended next test**: Test with post_run_metrics.py absent (failure injection).

---

### T31 — dual-loop: Baseline Outer-Inner Handoff

- **Target**: dual-loop (plugins/agent-loops)
- **Hypothesis**: Outer loop assigns task to inner loop via event bus; inner loop completes
  and signals back; outer loop receives result before iteration 2.
- **Why now**: Baseline transport test needed before testing flywheel additions.
- **Prior results**: Smoke test in prior session validated kernel transport; this validates the
  dual-loop SKILL coordination layer specifically.
- **Acceptance criteria**: task.assigned event followed by task.completed in events.jsonl;
  outer loop reads result before emitting next task.assigned.
- **Failure criteria**: Outer loop emits task.assigned twice without reading result from first.
- **Known weaknesses**: Requires 2 Claude sessions running simultaneously.
- **Recommended next test**: T32 (survey both agents).

---

### T32 — dual-loop: Survey Completion by Both Agents

- **Target**: dual-loop
- **Hypothesis**: Both outer loop and inner loop agents complete self-assessment surveys after
  a full cycle, not just the inner loop that ran the eval.
- **Why now**: Step 7 (survey) is new in dual-loop SKILL. Both agents must contribute.
- **Prior results**: None.
- **Acceptance criteria**: Two survey_completed events in events.jsonl, one from each agent role.
- **Failure criteria**: Only 1 survey_completed, or surveys only from inner loop.
- **Known weaknesses**: In single-session simulation, both "agents" may be same model instance.
- **Recommended next test**: T33 (friction propagation) using the same 2-session setup.

---

### T33 — dual-loop: Inner Loop Friction Propagation

- **Target**: dual-loop
- **Hypothesis**: Friction events emitted by the inner loop are visible to the outer loop
  via the shared events.jsonl before the outer loop decides the next iteration strategy.
- **Why now**: Friction propagation is necessary for outer loop to adapt task strategy.
- **Prior results**: None.
- **Acceptance criteria**: Outer loop reads events.jsonl after inner loop completes;
  friction event count influences next task description.
- **Failure criteria**: Outer loop ignores friction events; repeats same task without adaptation.
- **Known weaknesses**: "Influences task description" is hard to verify mechanically.
- **Recommended next test**: T34 (result surfacing).

---

### T34 — dual-loop: Inner Loop Eval Result Surfaced to Outer Loop

- **Target**: dual-loop
- **Hypothesis**: The inner loop's eval.result event (KEEP/DISCARD + score delta) is read by
  the outer loop and included in the strategy for iteration 2.
- **Why now**: Without this, outer loop cannot learn from inner loop results — flywheel breaks.
- **Prior results**: None.
- **Acceptance criteria**: Outer loop's iteration 2 strategy packet references the KEEP/DISCARD
  verdict from iteration 1.
- **Failure criteria**: Outer loop treats iteration 2 as fresh start, ignoring iter 1 result.
- **Known weaknesses**: Strategy packet content is text; hard to verify mechanically.
- **Recommended next test**: T35 (auto-trigger after 3 friction events).

---

### T35 — dual-loop: os-learning-loop Auto-Trigger After 3 Same-Cause Friction Events

- **Target**: dual-loop
- **Hypothesis**: When the same friction cause appears 3+ times across both outer and inner loop
  survey responses, a flag or event triggers os-learning-loop before the next session.
- **Why now**: This is the primary systemic improvement signal from the dual-loop.
- **Prior results**: None.
- **Acceptance criteria**: os-learning-loop:intent event or flag file after 3 same-cause friction items.
- **Failure criteria**: No trigger despite 3 matching friction causes.
- **Known weaknesses**: "Same cause" requires semantic matching — hard to verify mechanically.
- **Recommended next test**: T36 (os-learning-loop reads registry) — full loop if T35 triggers it.

---

### T36 — os-learning-loop: Registry Orientation at Phase 1

- **Target**: os-learning-loop
- **Hypothesis**: Phase 1 reads context/memory/tests/registry.md and the agent lists
  confirmed/falsified hypotheses before proposing any new change.
- **Why now**: Registry read was added to Phase 1 in this session. First test.
- **Prior results**: None.
- **Acceptance criteria**: Agent outputs a summary of prior registry entries before Phase 2.
- **Failure criteria**: Agent proposes changes without mentioning prior test results.
- **Known weaknesses**: Requires a pre-populated registry.md to verify the read.
- **Recommended next test**: T37 (DO NOT RE-TEST respected) — requires T36 to pass first.

---

### T37 — os-learning-loop: DO NOT RE-TEST Entries Respected

- **Target**: os-learning-loop
- **Hypothesis**: When registry.md contains a "DO NOT RE-TEST" entry for a hypothesis,
  the agent skips that hypothesis and proposes the next untested one.
- **Why now**: Without this, cycles are wasted re-testing confirmed failures.
- **Prior results**: None.
- **Acceptance criteria**: Agent reads DO NOT RE-TEST entry and proposes a different hypothesis;
  never proposes the blocked one.
- **Failure criteria**: Agent proposes the blocked hypothesis.
- **Known weaknesses**: Requires a pre-seeded DO NOT RE-TEST entry — use T25 result.
- **Recommended next test**: T38 (pre-eval documentation).

---

### T38 — os-learning-loop: Test Scenario Documented BEFORE Eval

- **Target**: os-learning-loop
- **Hypothesis**: The scenario file is written to context/memory/tests/ BEFORE eval_runner.py
  is called in Phase 3.
- **Why now**: Protocol requires this ordering. If reversed, no pre-test documentation exists
  if eval crashes.
- **Prior results**: None.
- **Acceptance criteria**: Scenario file with Status: IN PROGRESS present before any eval event.
- **Failure criteria**: Scenario file created after eval.result event.
- **Known weaknesses**: Timestamp comparison requires millisecond precision in events.jsonl.
- **Recommended next test**: T39 (registry close after cycle).

---

### T39 — os-learning-loop: Registry Row Closed After Cycle

- **Target**: os-learning-loop
- **Hypothesis**: After Phase 5 (test registry close), the registry.md row is updated from
  IN PROGRESS to CLOSED with the verdict.
- **Why now**: Phase 5 is new. Unclosed rows pollute future orientation reads.
- **Prior results**: None.
- **Acceptance criteria**: registry.md row for the cycle shows CLOSED before Phase 6 begins.
- **Failure criteria**: Row remains IN PROGRESS; or verdict field is blank.
- **Known weaknesses**: Requires reading registry.md mid-execution.
- **Recommended next test**: T36 again with the newly closed entry — verify next cycle reads it.

---

### T40 — os-learning-loop: Fast Path vs Full Loop Selection

- **Target**: os-learning-loop
- **Hypothesis**: Fast Path mode completes Phases 0-2 and outputs FINDINGS: block, then stops
  without acquiring the kernel lock or running evals.
- **Why now**: Fast Path / Full Loop selection is documented but unverified.
- **Prior results**: None.
- **Acceptance criteria**: Fast Path run does not emit acquire_lock:kernel event;
  Full Loop run does emit it.
- **Failure criteria**: Fast Path acquires lock; or Full Loop skips lock.
- **Known weaknesses**: Mode selection logic is in the agent prompt — hard to force a specific mode.
- **Recommended next test**: Test Fast Path -> "apply those changes" upgrade to Full Loop.

---

### T41 — kernel.py: PROTECTED_STATE_KEYS Guard on state_update

- **Target**: kernel.py
- **Hypothesis**: state_update --key execution_mode --value untrusted rejects the write
  and exits non-zero.
- **Why now**: This is the primary protection against agent misconfiguration. Must be verified.
- **Prior results**: None.
- **Acceptance criteria**: Exit code 1; stderr contains "Protected key: execution_mode".
- **Failure criteria**: state update succeeds; or exit 0 returned.
- **Known weaknesses**: Tests only execution_mode; hook_sample_rate not separately tested.
- **Recommended next test**: T42 (same guard on state_increment — the bug just fixed).

---

### T42 — kernel.py: PROTECTED_STATE_KEYS Guard on state_increment (Bug Regression Test)

- **Target**: kernel.py
- **Hypothesis**: state_increment --key execution_mode exits non-zero with "Protected key" message.
  This is a regression test for the bug fixed in this session.
- **Why now**: Bug was just patched. Regression test must be run and recorded before this fix
  could be accidentally reverted.
- **Prior results**: Bug confirmed present before patch. Patch applied in this session.
- **Acceptance criteria**: Exit code 1; "Protected key: execution_mode" in stderr.
- **Failure criteria**: Any exit code 0, or integer written to execution_mode.
- **Known weaknesses**: Tests only the patched path; does not test hook_sample_rate.
- **Recommended next test**: T41 (state_update guard) for symmetry; then T43 (stale lock).

---

### T43 — kernel.py: Stale Lock Auto-Cleanup

- **Target**: kernel.py
- **Hypothesis**: acquire_lock automatically removes a lock file referencing a dead PID
  before attempting to acquire.
- **Why now**: Stale locks from crashed sessions are the primary production failure mode.
- **Prior results**: None.
- **Acceptance criteria**: After creating a lock with PID 99999, the next acquire_lock call
  from any agent succeeds (removes stale lock and acquires fresh).
- **Failure criteria**: acquire_lock fails despite stale lock; or stale lock preserved.
- **Known weaknesses**: PID 99999 may exist on some systems. Use a confirmed dead PID.
- **Recommended next test**: T44 (lock idempotency).

---

### T44 — kernel.py: Lock Idempotency (No Double-Acquire)

- **Target**: kernel.py
- **Hypothesis**: The same agent cannot acquire the same lock twice without releasing it first.
  Second acquire_lock from same PID fails with a clear error.
- **Why now**: Double-acquire could cause lock accounting corruption.
- **Prior results**: None.
- **Acceptance criteria**: Second acquire_lock from same PID returns non-zero exit.
- **Failure criteria**: Second acquire succeeds; or lock file corrupted.
- **Known weaknesses**: PID-based locking allows any process with same PID to acquire.
- **Recommended next test**: T45 (agent permit list).

---

### T45 — kernel.py: Agent Permit List Enforcement

- **Target**: kernel.py
- **Hypothesis**: emit_event from an agent name not listed in context/agents.json is rejected
  with a non-zero exit code.
- **Why now**: Unlisted agents bypassing the permit list is a security risk.
- **Prior results**: None.
- **Acceptance criteria**: Emit from "unknown-agent-xyz" returns non-zero; no event written to JSONL.
- **Failure criteria**: Event written to events.jsonl despite unlisted agent name.
- **Known weaknesses**: Fail-open vs fail-closed behavior depends on kernel version — verify.
- **Recommended next test**: Add the agent to agents.json and verify emit succeeds after.

---

### T46 — hooks: Friction Event Counting in post_run_metrics.py

- **Target**: hooks/post_run_metrics.py
- **Hypothesis**: The script correctly counts type:friction events from events.jsonl and
  reports the count in friction_events_total.
- **Why now**: Friction count is the trigger for os-learning-loop auto-trigger. If counting
  is wrong, the trigger fires at wrong thresholds.
- **Prior results**: None.
- **Acceptance criteria**: With 5 friction events in events.jsonl, friction_events_total = 5.
- **Failure criteria**: Count is 0, or counts non-friction events, or off-by-one.
- **Known weaknesses**: Requires pre-seeded events.jsonl with known friction count.
- **Recommended next test**: T48 (auto-trigger threshold) — dependent on T46 passing.

---

### T47 — hooks: Metrics Written on Every Stop Hook

- **Target**: hooks/post_run_metrics.py
- **Hypothesis**: post_run_metrics.py runs on every Stop hook and writes a metric report
  regardless of session length or outcome.
- **Why now**: If metrics are only written on long sessions, short diagnostic sessions
  produce no signal.
- **Prior results**: None.
- **Acceptance criteria**: Metric report present after a 1-turn "hello" session.
- **Failure criteria**: No metric report after short session; or report only written on error.
- **Known weaknesses**: Stop hook may not fire in all Claude Code environments.
- **Recommended next test**: T46 (friction counting) — verify report content after T47 confirms writing.

---

### T48 — hooks: Auto-Trigger Threshold for os-learning-loop

- **Target**: hooks/post_run_metrics.py + os-learning-loop
- **Hypothesis**: When post_run_metrics.py emits a metric event with friction_events_total >= 3,
  os-learning-loop runs in Full Loop mode at next session start.
- **Why now**: Auto-trigger is the primary autonomous improvement mechanism. Unverified end-to-end.
- **Prior results**: None.
- **Acceptance criteria**: After seeding events.jsonl with 3 friction events, Stop hook fires,
  metric event shows friction_events_total = 3, os-learning-loop intent event appears.
- **Failure criteria**: No os-learning-loop invocation; or metric not emitted; or wrong count.
- **Known weaknesses**: "Next session start" timing hard to test in single session.
- **Recommended next test**: Verify os-learning-loop runs in Full Loop mode (not Fast Path) per T40.

---

### T49 — os-init: Interview Skip for Already-Answered Questions

- **Target**: os-init
- **Hypothesis**: When the user has already stated their project type and use case in conversation,
  the init interview skips those questions and only asks what is still unclear.
- **Why now**: Redundant questioning is friction. Phase 1 says to skip answered questions but
  this is never tested.
- **Prior results**: None.
- **Acceptance criteria**: After "I'm building a Python CLI tool solo" context, init does not ask
  "What kind of project is this?" or "Who is using it?".
- **Failure criteria**: Init asks questions already answered in conversation.
- **Known weaknesses**: LLM context extraction is probabilistic — test 3 cases to confirm.
- **Recommended next test**: T50 (survey completion).

---

### T50 — os-init: Survey Completion After Onboarding

- **Target**: os-init
- **Hypothesis**: Phase 5 self-assessment survey is completed and saved after every init run,
  including partial inits that stop after the interview phase.
- **Why now**: Phase 5 is new — added this session.
- **Prior results**: None.
- **Acceptance criteria**: Survey file in retrospectives/ with all sections populated,
  including Improvement Recommendation.
- **Failure criteria**: Survey absent after init; or sections blank.
- **Known weaknesses**: Survey may not be saved if init is interrupted mid-phase.
- **Recommended next test**: Review whether the improvement recommendation from T50
  leads to an update of the os-init SKILL.md — closing the flywheel.

---

## Usage Instructions for ORCHESTRATOR

1. Read this file at orientation (Phase 0 / Stage 0).
2. Cross-reference with `context/memory/tests/registry.md` — skip any scenario already IN PROGRESS or CLOSED.
3. Select the highest-priority untested scenario that targets the skill under active improvement.
4. Follow `references/test-registry-protocol.md` to document the scenario BEFORE running.
5. After completing, update `context/memory/tests/registry.md` and follow the promotion rules.
6. Use the "Recommended next test" field from this scenario to choose the next cycle's test.

Priority ordering within a target: start with HIGH, then MEDIUM.
Cross-target ordering: run kernel.py and hooks tests first (foundational infrastructure),
then os-memory-manager and os-learning-loop (most impactful for flywheel),
then os-improvement-loop and dual-loop (integration tests).
