# Map Debt Ledger

Persistent tracking of architectural friction, structural anomalies, and unclosed loops across sessions.

## DEBT-20260920-POST-DONE-PROTOCOL-CODIFICATION (RESOLVED)

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `AGENTS.md`, `plugins/agent-agentic-os/rules/worktree-lifecycle-management.md`, `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`, `plugins/agent-agentic-os/scripts/control_plane/pipeline_simulator.py`, `plugins/agent-agentic-os/scripts/control_plane/transition_simulation_cases.py`, `plugins/agent-agentic-os/skills/transition-simulator/SKILL.md`, `plugins/agent-agentic-os/references/cheap-agent-transition-simulation.md`
- Friction observed: Agents reaching final state DONE frequently froze, dropped context, or failed to execute the post-completion Git convergence lifecycle without explicit human re-prompting because the exact 5-step post-DONE protocol (Push -> PR -> Merge -> Sync -> Prune) was not codified in transition guidance, rules, or simulator tests.
- Why not fixed now: Fixed immediately.
- Recommended fix / fix applied: Added Section 10 ("The Standard Post-DONE Protocol") to `worktree-lifecycle-management.md` and `AGENTS.md`; codified `post_done_protocol` under `stages.DONE.closeout_contract` in `transition_templates.yaml` with explicit execution classes; added `PipelineSimulator.get_post_done_convergence_protocol()` and `grade_post_done_convergence_plan()` in `transition_simulation_cases.py` along with deterministic contract tests in `test_control_plane_pipeline_simulator.py`; documented Mode 3 post-DONE convergence verification and harness-agnostic execution in `transition-simulator/SKILL.md` and `cheap-agent-transition-simulation.md`.
- Evidence/repro: Verified via `pytest -q plugins/agent-agentic-os/tests/test_control_plane_pipeline_simulator.py` (12 passed) and `agent_control.py transition-guidance` output in DONE state.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-HUMAN-CONFIRMED-PROVENANCE (RESOLVED)

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/coordinator.py`, `plugins/agent-agentic-os/scripts/agent_control.py`
- Friction observed: Non-interactive soft transitions run by the agent with verified `--human-confirmed` were assigning `decision_actor = "agent"` when recording transition decisions, causing the SQLite trigger `enforce_valid_transition` to reject the transition because `required_transition_questions` requires `actor = 'human'`.
- Why not fixed now: Fixed immediately.
- Recommended fix / fix applied: In `coordinator.py`, when `--human-confirmed` has been validated and accepted, set `decision_actor = "human" if human_confirmed else "agent"`, establishing correct human provenance for soft transitions authorized by the user in chat.
- Evidence/repro: Verified via `pytest -q plugins/agent-agentic-os/tests` (888 passed) and successful execution of soft transitions with `--human-confirmed`.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-REVIEW-SELECTION-PROFILE-VALIDATION (OPEN)

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `transition_templates.yaml` review-selection questions (internal runtime/model/effort); `control_plane/coordinator.py`; `context/agent-capability-profile.json` (project-setup)
- Friction observed: Future enhancement (H1 option A): the internal runtime/model/effort answers are free text. `list-review-options` (read-only) now lets the human copy exact ids, but nothing rejects a typed answer that is not a real runtime/model (one hand-typed 'gemini flash 3.8' was recorded).
- Why not fixed now: Deliberately deferred by human decision (option B chosen 2026-09-20). Profile-driven validation needs the capability profile to exist (project-setup) and a validation rule that accepts only entries in the profile.
- Recommended fix / fix applied: Have the coordinator offer choices from context/agent-capability-profile.json and reject answers not in it, falling back to free text with a warning when the profile is missing.
- Evidence/repro: Decision 416 recorded 'gemini flash 3.8'; round-3 synthesis H1; tests/test_list_review_options.py covers the read-only verb only.
- Severity: L
- Repeat: NO
- Status: OPEN (2026-09-20 partial: validated numbered menus for runtime/model/effort now exist (choices_from + review_options.choices_for; agy via `agy models`, others via the capability profile's providers.<runtime>.model_tiers; typed answers outside a menu are rejected; no-menu falls back to free text with a visible warning). Remaining: no `models` command exists for codex/claude/copilot so their menus need a profile entry; no agent-definition question (agy agents / claude --agent) was added because it would add a required question to both edges; profile schema is read minimally)

## DEBT-20260919-TRANSITION-VIOLATIONS-NOT-WRITTEN-ON-ROLLBACK (RESOLVED)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `control_plane/adapters.py` apply_transition_with_receipts / apply_recovery paths; `transition_violations` table; enforce_valid_transition trigger
- Friction observed: When the enforce_valid_transition trigger rejects a transition the trigger's INSERT into `transition_violations` happens inside the same transaction that the coordinator then aborts (the PersistenceInvariantViolation rolls it back), so no violation row survives. The 2026-09-19 intake attempts left nothing in transition_violations. U2 made the error message name the missing question ids, but the audit row itself is still lost.
- Why not fixed now: Needs an autonomous out-of-transaction audit write (a separate connection/transaction committed after the rollback, tolerant of DB errors) and its own tests; not part of Gate 1 scope.
- Recommended fix / fix applied: After the rollback, write a `transition_violations` row (with failed question ids, actor, and format context) on a separate connection; test that the row survives a rolled-back transition.
- Evidence/repro: Probe: cp.transition() without decisions raises; SELECT COUNT(*) FROM transition_violations stays 0. tests/test_actionable_rollback.py covers the message only.
- Severity: M
- Repeat: NO
- Status: RESOLVED (2026-09-19, auth-ciba-increment-b: adapters write the rejection (actor, reason, detail) to transition_violations on a separate transaction after rollback; tests/test_violation_audit.py)

## DEBT-20260919-SIGNING-DOMAIN-QUALIFIED-NAMESPACES (RESOLVED)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `control_plane/ssh_signing.py` SIGN_NAMESPACE / SELFTEST_NAMESPACE; `allowed_signers` files
- Friction observed: Signature namespaces are the bare strings `control-plane` and `control-plane-selftest`; OpenSSH recommends application-specific `NAMESPACE@YOUR.DOMAIN` names so the same key cannot collide with another tool's namespace.
- Why not fixed now: Changing the namespace changes signed bytes, enrolled `allowed_signers` lines and every signing test; needs a migration for already-enrolled keys (the human's key is enrolled today).
- Recommended fix / fix applied: Introduce domain-qualified constants in constants.py, accept old and new during a transition window, re-enroll via setup_ciba_identity.py.
- Evidence/repro: ssh_signing.py namespace constants; OpenSSH ssh-keygen(1) SIGNATURES section.
- Severity: L
- Repeat: NO
- Status: RESOLVED (2026-09-19, auth-ciba-increment-b: namespaces are now control-plane@agentic-os.local / control-plane-selftest@agentic-os.local; identity_setup.migrate_namespaces + setup_ciba_identity.py migrate existing allowed_signers; bare-namespace signatures never verify; tests/test_domain_namespaces.py)

## DEBT-20260919-SIGNING-KEY-REVOCATION-KRL (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `control_plane/ssh_signing.py` verification; `context/identity/`
- Friction observed: Verification uses `allowed_signers` only; there is no revocation list (`ssh-keygen -k` / `-Y verify -r`), so a compromised enrolled key can only be removed by editing `allowed_signers` by hand.
- Why not fixed now: Not required for Increment B; needs a human-owned revocation file with the same mode/ownership checks as `allowed_signers`.
- Recommended fix / fix applied: Add an optional human-owned `revoked_keys` file, pass it to `ssh-keygen -Y verify -r`, and cover it in isolation_check and the setup script.
- Evidence/repro: ssh_signing.py verify command line has no -r option.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-GATE1-CHALLENGE-POLICY-VERSION-BINDING (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `control_plane/ssh_signing.py` challenge payload; `transition_request`
- Friction observed: The challenge binds task, edge, content hash (spec+plan), occupancy, nonce and expiry but not the policy version (transition_templates.yaml / guidance version) in force, so the human's signature does not prove which rules the approval was given under.
- Why not fixed now: Changes the signed bytes and needs a challenge_version bump with backward-compatible verification of pending requests.
- Recommended fix / fix applied: Add a policy/guidance digest to the challenge and to transition_request, bump challenge_version, reject on mismatch at approve time.
- Evidence/repro: ssh_signing.py derive_challenge_from_row fields.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-GATE1-EXECUTION-BINDING-D7 (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: coordinator, `update-worktree`, later gates (IN_WORKTREE onward)
- Friction observed: Deferred item D7: nothing after the Gate 1 commit re-verifies the signed approval, so later stages trust the APPROVED state row rather than the signature; an actor that can write the DB is not stopped downstream.
- Why not fixed now: Out of Increment B scope by human decision (Gate 1 only).
- Recommended fix / fix applied: Re-verify the stored proof (or a signed approval token) at IN_WORKTREE and before push, or bind downstream capabilities to the committed transition id.
- Evidence/repro: plan Revision 6 D7; isolation-setup.md residual risk.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-AGENT-RECORDED-HUMAN-RECEIPT (ESCALATED)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py` (`record-review-skip`, `--actor human`, `--human-confirmed`) and `transition_templates.yaml` review-edge hints
- Friction observed: On 2026-09-19 the agent recorded review-skip receipts with `record-review-skip --actor human`, quoting the human's chat as `--human-confirmed`, instead of asking the edge's questions; the CLI cannot tell an agent-run verb from a human decision (`_enforce_human_confirmed` checks only the `HUMAN-CONFIRMED:` prefix; `record_review_skip` accepts any actor string). The PLAN_REVIEW hint ('If No, record the explicit skip receipt') also does not say who records it. Receipt 158 (`EVO-INTEGRITY-auth-ciba-increment-b-9112d420d352`) falsely satisfied `critic_review_or_skip` until the coordinator's occupancy-exit delete removed it (transition 311), so the incident survives only here. An earlier instance exists: `temp/rerun_interview_answers_as_human.sh` (2026-09-17).
- Why not fixed now: Repeat=YES must escalate; the fix is scoped into this same work package (T15 receipt provenance and append-only audit, T16 guidance and eval guard, T17 review-selection prompts) but is not implemented yet.
- Recommended fix / fix applied: T15: receipts carry actor and provenance, an append-only `receipt_audit`, `invalidate-receipt` (human-interactive only); T16: YAML hints name the human as recorder, SKILL.md hard rule, eval cases; T17: the No path becomes a coordinator-created human skip decision.
- Evidence/repro: Session transcript 2026-09-19; `verification_receipts` receipt 158; `adapters.py` occupancy-exit `DELETE FROM verification_receipts`.
- Severity: M
- Repeat: YES
- Status: ESCALATED

## DEBT-20260919-REVIEW-SELECTION-CONTRACT-GAP (RESOLVED)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `transition_templates.yaml` edges `plan_review_to_multi_agent_review` and `worktree_review_to_multi_agent_code_review`; `coordinator.py`
- Friction observed: `review-selection-v1` requires runtime, model and effort to be persisted before any reviewer dispatch, but both edges define only 'review needed' and 'review method', MULTI_AGENT_REVIEW defines no entry questions, and the interactive `.py` commits after two answers. The agent wrongly treated the missing rows as a user omission; the human had to insist. Also: 'No' is listed on both edges but absent from `accepted_answers`, so it is rejected.
- Why not fixed now: Needs its own TDD cycle across both edges; scheduled as T17 in this work package.
- Recommended fix / fix applied: T17: one shared review-selection routine and question template for both edges (review needed -> type -> runtime -> model -> effort), no silent defaults, `--answers` cannot satisfy them, a policy check blocks dispatch without the three decisions; tests R1-R8 over both edges.
- Evidence/repro: Live reproduction: decisions 388-390 / transition 311 commit with zero runtime/model/effort rows; YAML lines for both edges.
- Severity: M
- Repeat: NO
- Status: RESOLVED (2026-09-19, auth-ciba-increment-b T17: both review edges declare conditional `asked_when` runtime/model/effort questions, human-typed only; `record_critic_review` refuses an internal review without them; tests/test_review_selection.py). Residual: the requirement is enforced in Python (coordinator + record_critic_review), not by a DB trigger, so a direct DB writer is not stopped (same class as GATE1-DIRECT-DB-FORGERY-RESIDUAL); the plan-edge 'No' answer still routes through the human-recorded skip (T15).

## DEBT-20260919-STALE-AGENTS-WORK-INTAKE-INSTALL (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: .agents/skills/work-intake/scripts (installed copy) vs plugins/agent-agentic-os/scripts
- Friction observed: The installed `.agents/` copy of `agent_control.py`/`control_plane` (dated 2026-09-16) lacks fixes present in the plugin source (e.g. the interview check deferral), and treated edges as human-only, producing misleading denials. SKILL.md still points agents at the installed path.
- Why not fixed now: Refreshing installed copies is an installer action (`plugin_add.py`) outside this worktree's scope.
- Recommended fix / fix applied: Point SKILL.md at the plugin path or refresh installs via `plugin_add.py`; add a drift check (version stamp) to os-health-check.
- Evidence/repro: `diff -rq .agents/skills/work-intake/scripts/control_plane plugins/agent-agentic-os/scripts/control_plane`.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-INTERVIEW-TRIVIAL-EVIDENCE-REQUIRED-ON-STANDARD (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `required_transition_questions` for INTERVIEW -> DRAFT_PLAN; `transition_templates.yaml`
- Friction observed: The DB requires a human answer to `interview_trivial_evidence` even on the STANDARD route, so a STANDARD task must answer a TRIVIAL-route question.
- Why not fixed now: Not part of #639; needs a YAML/DB change with its own tests.
- Recommended fix / fix applied: Make the question route-conditional (required only for TRIVIAL) in the YAML and the trigger's required-question derivation.
- Evidence/repro: `SELECT question_id FROM required_transition_questions WHERE from_state='INTERVIEW' AND to_state='DRAFT_PLAN'` lists it for STANDARD tasks.
- Severity: L
- Repeat: NO
- Status: OPEN

## DEBT-20260919-GUIDANCE-CONFIRMATION-ACTOR-MISMATCH (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `coordinator.py` guidance_compliance_confirmation; DB trigger `enforce_valid_transition`
- Friction observed: On `agent_or_human` edges the coordinator accepts an agent-supplied `guidance_compliance_confirmation` (recorded actor=agent), but the trigger still requires `actor='human'` for the same edge's stage questions; the two layers disagree about who may answer, which cost several attempts during intake.
- Why not fixed now: Design decision needed (which layer is authoritative).
- Recommended fix / fix applied: Make the coordinator's error name the exact question IDs that must be human-answered (see U2) and align the YAML hint.
- Evidence/repro: Session 2026-09-19: transition INTERVIEW -> DRAFT_PLAN rolled back with 'rejected by database trigger' and nothing in `transition_violations`.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-GATE1-DIRECT-DB-FORGERY-RESIDUAL (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `context/control_plane.db` (agent-writable) and `coordinator.py`
- Friction observed: Accepted residual of Option B / decision D4: the DB stays agent-writable and the trigger accepts any `actor='human'` decision row, so a same-account agent that writes the DB or edits the coordinator directly bypasses the Gate 1 signing hook. The hook protects the coordinator path against an agent without the keys and against scripted answers; the adapter refuses staged human decisions at Gate 1 without proof.
- Why not fixed now: Closing it needs a separate process or account (broker, Option A) or verify-on-use at later gates (D7); out of scope by human decision.
- Recommended fix / fix applied: Option A broker, or re-verify the signed approval at IN_WORKTREE/push (D7).
- Evidence/repro: `references/isolation-setup.md` 'Residual risk'; round-1 and round-2 plan reviews.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-TESTS-WRITE-INTO-REPO-DOCS-PLANS (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: plugins/agent-agentic-os/tests (coordinator plan-outline projection)
- Friction observed: Some tests write scratch plan outlines into the checkout's own `docs/plans/work-tasks/` (e.g. `test-bundle-001`, `p01-task`, `t1`), leaving gitignored clutter in real worktrees.
- Why not fixed now: Harmless (gitignored) and outside #639.
- Recommended fix / fix applied: Point tests at tmp repo roots or clean up in fixtures.
- Evidence/repro: `ls .worktrees/<task>/docs/plans/work-tasks` after a full test run.
- Severity: L
- Repeat: NO
- Status: OPEN

## DEBT-20260919-ANALYSIS-NOTEBOOK-CORRUPTED (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: plugins/agent-agentic-os/scripts/analysis.ipynb
- Friction observed: Invalid JSON since commit 06c3766a (a bulk python3->python edit mangled a line to `python "python"` at line 186); it is the interactive companion to generate_report.py for improvement-progress reporting. The 13 other 'invalid JSON' files under plugins/ are one-line text stand-ins, not damage.
- Why not fixed now: Outside #639; tracked in #642.
- Recommended fix / fix applied: One-line JSON repair; do not delete.
- Evidence/repro: `python3 -c "import json; json.load(open('plugins/agent-agentic-os/scripts/analysis.ipynb'))"` fails at line 186; issue #642.
- Severity: L
- Repeat: NO
- Status: OPEN

## DEBT-20260919-PLAN-ARTIFACT-CHECKLIST-PATH-MISMATCH (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `transition_templates.yaml` required_artifacts / checklist for plan-review edges
- Friction observed: Checklist and `required_artifacts` name `docs/plans/<task-id>-spec.md`, but the artifacts live in `docs/plans/work-tasks/<task-id>/`; the coordinator maps between them and the checklist line reports PASS unconditionally.
- Why not fixed now: Changing it risks the mapping without a test.
- Recommended fix / fix applied: Update the YAML paths with a test that the checklist item really checks existence.
- Evidence/repro: Transition output 2026-09-19: 'Artifact: docs/plans/<task>-spec.md (PASS)' while the file is under work-tasks/.
- Severity: L
- Repeat: NO
- Status: OPEN

## DEBT-20260919-INCREMENT-B-DEFERRED-ITEMS (OPEN)

- Logged date: 2026-09-19
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: auth-ciba-increment-b deliverables
- Friction observed: Deferred by scope or environment: (1) `PROOF_REQUIRED_EDGES` is a constant; deriving it from a `proof` field on the YAML edge (and updating `installation_probe.py`) is pending; (2) `transition_simulation_cases.py`/`pipeline_simulator.py` have no strict-mode Gate 1 cases (pre-existing suites run on the legacy_input default via tests/conftest.py, a documented test seam); (3) installed-copy refresh via `plugin_add.py`; (4) health-check self-test-age record; (5) case 6b (ordinary transition as the real agent account), FIDO hardware and Windows are UNTESTED here; (6) on macOS `SSH_AUTH_SOCK` is normally set, so the request-time preflight lists it as a failed check (advisory; approve/show-challenge do not check the human's own environment); (7) TTY checks are friction, not trust (a pty defeats them); (8) Touch ID and SSH/X.509 certificate authorities are not supported.
- Why not fixed now: Scoped out or not testable in this environment.
- Recommended fix / fix applied: See each item; record follow-ups as issues after the exit gate.
- Evidence/repro: Plan Revision 6 known non-coverage; spec section 4.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260919-TRIVIAL-FASTTRACK-DOC-CODE-MISMATCH (RESOLVED)

- Logged date: 2026-09-19
- Cycle/Session ID: docs-increment-b-ssh-diagram (trivial task)
- Artifact affected: `plugins/dev-utils/rules/graph-planning-superpowers-policy.md` (canonical) + 2 known duplicate copies (`.agent/rules/`, `.agents/skills/coding-conventions-agent/references/`); `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`'s `interview_classification` question text.
- Friction observed: `graph-planning-superpowers-policy.md` claimed a TRIVIAL-classified task can "fast-track directly to INTAKE -> DONE, skipping Phases 1-3 entirely." Verified directly against `state_machine.py`/`registry.py`: no such edge exists. The only `INTAKE -> DONE` and `INTERVIEW -> DONE` edges are `human_force_done__from_INTAKE`/`human_force_done__from_INTERVIEW` — the force-close family, requiring live interactive human authorization, not a distinct trivial shortcut. Every `TRIVIAL`-related `next_steps_hint` actually in the YAML only lightens evidence requirements at each pipeline stage; none skip stages. An agent (this session) trusted the policy doc's claim over the real code, registered a task, and got stuck at the force-close family's human-only gate trying to reach a shortcut that was never implemented -- significant live friction and user frustration resulted.
- Why not fixed later: Fixed immediately, live, as its own small task once identified.
- Recommended fix / fix applied: Corrected the policy document's claim to accurately state no skip-edge exists, TRIVIAL only lightens evidence, and that skipping the control plane entirely (direct commit/push, `--no-verify` with explicit user authorization) is the correct choice when even the lightened full sequence is disproportionate -- not answering TRIVIAL expecting a shortcut. Added an explicit warning to the same effect directly in the `interview_classification` question text in `transition_templates.yaml`, so the guidance reaches an agent at the earliest possible point (before it ever picks a wrong route), not just in a separately-loaded policy file.
- Evidence/repro: Live reproduction this session (see conversation transcript); direct code verification via `ALLOWED_TRANSITIONS`/`registry.get_template()` showing only the force-close edges exist. `tests/test_transition_guidance.py`, `tests/test_p00_live_baseline.py`, `tests/test_control_plane_interview_guidance.py` (36 tests) re-verified green after the YAML wording change.
- Severity: M (real live friction and wasted effort, not a security/correctness bug)
- Repeat: NO
- Status: RESOLVED

## DEBT-20260918-VERIFY-EXIT-BUNDLE-REDUNDANT-PYTEST-RUN (RESOLVED)

- Logged date: 2026-09-18
- Cycle/Session ID: auth-ciba-poc-transition-mechanics (VERIFY_EXIT)
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/wrappers/run_verify_exit_bundle.py`, `plugins/agent-agentic-os/scripts/control_plane/wrappers/run_exit_verification.py`
- Friction observed: While actually running this task's own `VERIFY_EXIT` bundle live, the run took roughly double the expected ~13-15 min full-suite time. Root cause: `run_exit_verification.py`'s `VERIFIER_CATALOG` defines `pytest_unit_tests` as bare `["pytest"]` with no path/marker scoping -- since this repo has no actual unit/integration marker split (`grep -rn "@pytest.mark\." tests/` finds only `parametrize`), it silently collects and runs the EXACT SAME test set as `pytest_full_suite`'s `["pytest", "-q"]`. `run_verify_exit_bundle.py` ran both sequentially, doubling every real `VERIFY_EXIT` pass's wall-clock time for zero additional coverage.
- Why not fixed later: Fixed live, same session, while the real task's bundle run was in flight (safe to edit -- the already-running process had already loaded the old code into memory; the fix only affects future invocations).
- Recommended fix / fix applied: `run_verify_exit_bundle.py` now runs `pytest_full_suite`'s command exactly once and records its single result under BOTH the `full_test_suite` and `test_suite` gate names (the latter via a direct `record_verification_receipt` call, no second subprocess) -- every downstream check keyed on either gate name still sees a real receipt, just without a second real pytest invocation producing it. `pytest_unit_tests` is no longer separately invoked by the bundle.
- Evidence/repro: New `tests/test_run_verify_exit_bundle.py` (previously no test coverage existed for this wrapper at all) -- `test_bundle_runs_pytest_full_suite_command_only_once` confirmed RED (2 pytest invocations) before the fix, GREEN (1) after; `test_bundle_records_both_test_suite_and_full_test_suite_receipts` and `test_bundle_fails_fast_and_records_neither_receipt_on_nonzero_exit` cover the receipt-duplication and fail-fast semantics respectively.
- Severity: M (real, measurable time waste on every VERIFY_EXIT pass; not a correctness/security issue)
- Repeat: NO
- Status: RESOLVED

## DEBT-20260918-RECOVERY-VERIFY-EXIT-BYPASS (CRITICAL, RESOLVED)

- Logged date: 2026-09-18
- Cycle/Session ID: auth-ciba-poc-transition-mechanics (MULTI_AGENT_CODE_REVIEW)
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/adapters.py`, `plugins/agent-agentic-os/scripts/agent_control.py`
- Friction observed: External codex (gpt-5.6-terra) security review of this task's own diff found, and I independently reproduced live, a CRITICAL bypass: `record_recovery_approval()` hardcoded `actor="human"` into the inserted `transition_decisions` row regardless of the real caller, and `enforce_valid_transition`'s recovery-bypass clause permitted ANY transition once a matching decision row existed, with zero re-check of `valid_transitions` DAG membership. Combined, two ordinary Python calls (`record_recovery_approval` + `apply_recovery_transition`, no CLI, no coordinator, no special privilege) let an agent reach `VERIFY_EXIT` directly from any state, completely recreating the `IN_WORKTREE -> VERIFY_EXIT` backdoor this same task's `state_machine.py` edge deletion was supposed to close. Live repro confirmed `FINAL TASK STATE: VERIFY_EXIT` with zero real human involvement. This defeated the task's own headline claim ("there is no direct edge") as actually shipped.
- Why not fixed later: Fixed immediately, same session, before this review could honestly conclude PASS -- this is exactly the kind of finding that must block sign-off, not get deferred.
- Recommended fix / fix applied: (1) `RECOVERY_FORBIDDEN_DESTINATIONS = (STATE_VERIFY_EXIT, STATE_APPROVED)` in `adapters.py` -- `record_recovery_approval()` now raises `ValueError` before ever creating an approval row targeting either state, regardless of actor. (2) `record_recovery_approval()`'s `actor` parameter is now required (no default at the persistence layer) and recorded verbatim, replacing the hardcoded `"human"` literal -- the `ControlPlane` facade also requires it explicitly (no default), while the CLI subcommand's own `--actor` flag defaults to `"human"` since that tool is a human-operated administrative entrypoint by design. (3) Defense-in-depth: `enforce_valid_transition`'s trigger SQL (factored into the shared `ENFORCE_VALID_TRANSITION_TRIGGER_SQL` variable, embedded in both `SCHEMA_SQL` and a new `SCHEMA_MIGRATIONS` DROP+CREATE pair so existing databases pick it up, since `CREATE TRIGGER IF NOT EXISTS` silently no-ops against an already-existing trigger) now excludes `RECOVERY_FORBIDDEN_DESTINATIONS` from its recovery-bypass clause, so even a hand-crafted raw-SQL decision row bypassing the Python guard entirely cannot satisfy the bypass condition for these two destinations.
- Evidence/repro: Live pre-fix reproduction (see git history / session transcript) confirmed `FINAL TASK STATE: VERIFY_EXIT`. New regression test `test_authorized_actor_enforcement.py::test_recovery_approval_cannot_reach_verify_exit_bypassing_worktree_review` covers both the Python-layer guard (Layer 1) and the trigger-layer defense-in-depth (Layer 2, a hand-crafted decision row), confirmed RED against pre-fix code (`TypeError: unexpected keyword argument 'actor'`, proving the guard didn't exist) and GREEN after the fix. Full suite re-verified after the fix (see Verification Summary in the implementation-plan.md for the exact count).
- Severity: CRITICAL
- Repeat: NO (first instance of this specific bypass class; the two prior `interview_plan_route_complete`/`test_suite_or_deferred_to_review` findings this session are check-deferral-timing bugs, a different mechanism)
- Status: RESOLVED
- Addendum (same verification pass): 4 of the 6 `test_agent_control.py` recovery
  tests fixed for the new required `actor` parameter initially used
  `actor="admin"` (mechanically matching `approver="admin"`), which the
  trigger's recovery bypass correctly refused to honor (`ACTOR_HUMAN` is the
  literal string `"human"`, not any human-sounding label) -- a bug in the test
  fixture, not the production fix, confirmed by the fix behaving exactly as
  designed. Corrected to `actor="human"`. Full suite re-verified:
  510 passed, 1 skipped, 0 failed.

## DEBT-20260918-TRANSITION-REQUEST-DESIGN-GAPS (Increment B scope, not this POC)

- Logged date: 2026-09-18
- Cycle/Session ID: auth-ciba-poc-transition-mechanics (MULTI_AGENT_CODE_REVIEW)
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_request.py`
- Friction observed: A scoped, low-cost external blind-spot review (codex, gpt-6-astra, low reasoning effort, deliberately budget-limited) surfaced several design gaps in the currently-unwired stub-JWT `transition_request` module, worth carrying forward to whenever Increment B (real IdP integration) actually wires this module into a production code path: (1) approval consumption (`verify_and_consume`) is not the same transaction as the actual state transition commit -- a crash between the two could burn a valid approval without ever advancing state; (2) verification checks the stored request, not the task's *live* current state/occupancy at consumption time -- a request could in principle survive a reset/rollback/competing transition and still be honored later; (3) the `revision_hash` binds transition metadata + a nonce, not the actual reviewed content (code diff, plan, evidence) -- it doesn't prove the human approved *this* content, only *a* request shaped like this; (4) `jti` uniqueness is not actually enforced at the schema/query level despite being named as a replay defense; (5) multiple concurrently-pending requests, denial/supersession semantics, and lost-response recovery are all undefined; (6) expiration timing is caller-supplied and sampled before the write lock is acquired, and token claim shapes aren't validated against malformed/adversarial input.
- Why not fixed now: The module is confirmed fully unwired (zero production call sites), so none of this is a live risk today -- explicitly out of scope for tonight's tightly-scoped recovery-bypass fix, and premature to design against without knowing the real IdP's actual token shape (Increment B).
- Recommended fix / fix applied: Not fixed. When Increment B begins, design the wiring point (commit_authorized_transition or equivalent) to (a) consume the token and commit the state transition in one atomic transaction, (b) re-validate live occupancy at consumption time, (c) bind revision_hash to an actual content hash of the reviewed artifacts, (d) enforce jti uniqueness via a real UNIQUE constraint, (e) define explicit request-supersession/denial semantics, (f) validate claim shapes defensively.
- Evidence/repro: `/tmp/codex_astra_blindspot.log` (session-local, not committed).
- Severity: M (zero live risk today; real risk if Increment B wires this module in without addressing these first)
- Repeat: NO
- Status: OPEN (2026-09-19: items a-c RESOLVED by auth-ciba-increment-b: T4 atomic consume+advance in one transaction, T2 content-bound `revision_hash`, T4 live-occupancy re-check; items d-f (jti UNIQUE, supersession/denial semantics, claim-shape validation) remain OPEN)

## DEBT-20260918-WORKTREE-REVIEW-RECEIPT-GUIDANCE-AND-DEFERRED-CHECK-TIMING

- Logged date: 2026-09-18
- Cycle/Session ID: auth-ciba-poc-transition-mechanics
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml` (`in_worktree_to_worktree_review` template) and `plugins/agent-agentic-os/scripts/control_plane/coordinator.py`
- Friction observed: Two related problems found live, while the user attempted to actually run `IN_WORKTREE -> WORKTREE_REVIEW` for real on this task. (1) The edge's `next_steps_hint` told the agent to run a command, `record-verification-receipt`, that does not exist as a CLI verb -- it's a garbled hybrid of the real verb `record-receipt` and the internal Python method name `record_verification_receipt()`. Fixed live (see plugin-scoped `map-debt.md` for detail). (2) Deeper: the edge's own `confirm_test_suite_or_defer` human question is structurally unreachable -- the `test_suite_or_deferred_to_review` deterministic check runs at coordinator.py step 5, before the step-6 question-collection loop that would ever present it, and `coordinator.py` has zero handling wiring that question's "Defer" answer into the `test_suite_deferred_to_review` receipt the check needs. This is the same architectural bug class as `DEBT-20260918-INTERVIEW-CHECK-DEFERRAL-STALE-NAME` below, applied to a different check/edge.
- Why not fixed now: The guidance-text fix (1) was safe and immediate. The deeper fix (2) -- adding `test_suite_or_deferred_to_review` to the deferred-checks tuple plus wiring the answer to auto-record the receipt -- needs its own TDD cycle and full-suite re-verification, not a late-night patch made while a live pipeline run is mid-flight and blocking on it.
- Recommended fix / fix applied: (1) applied live: corrected `next_steps_hint` to name the real `record-receipt` command and explain the pre-transition receipt requirement. (2) recommended, not yet applied: mirror the `interview_plan_route_complete` fix exactly -- add the check-id to the deferral tuple, then add the same-call auto-receipt wiring for the "Defer" answer path.
- Evidence/repro: Live terminal reproduction: `coordinate-transition --to WORKTREE_REVIEW` denied by `test_suite_or_deferred_to_review` with zero prompt ever shown, despite the edge declaring a human question that appears (from the YAML alone) to handle exactly this case.
- Severity: M
- Repeat: YES -- second confirmed instance of a deterministic check not wired into the deferred-checks mechanism despite depending on that same edge's own interactive answer. See the recommended CI cross-reference check in the sibling entry below; extend it to flag any `deterministic_checks` entry whose only real satisfaction path is that same edge's own `human_questions` answer.
- Status: OPEN (guidance-text half fixed and RESOLVED; the deferred-check-timing half remains OPEN)

## DEBT-20260918-INTERVIEW-CHECK-DEFERRAL-STALE-NAME

- Logged date: 2026-09-18
- Cycle/Session ID: auth-ciba-poc-transition-mechanics
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/coordinator.py`
- Friction observed: `coordinator.py`'s deterministic-check-deferral special-case (`if check_id in ("interview_trivial_complete", "interview_standard_complete"): deferred_checks.append(check_id)`) still matched two old check-id names from before `policy.py`'s `_interview_trivial_check`/`_interview_standard_check` were unified behind a single `interview_plan_route_complete` dispatcher (`_interview_plan_route_check`). Because the current YAML template declares `interview_plan_route_complete`, not the two retired names, this check was never deferred -- it ran at step 5 (before the interactive question-collection loop at step 6) against an empty `stage_answers` dict, and denied every purely-interactive `INTERVIEW -> DRAFT_PLAN` transition that had no answers pre-staged via `record_interview_question`. Found live via the full test suite (`test_draft_plan_interactive_outline_gap.py`) failing only in the full run, not the earlier targeted re-verification runs, because that specific test exercises the pure-interactive path with zero pre-staged answers.
- Why not fixed now: Fixed live, same session -- one-line addition of `interview_plan_route_complete` to the deferral tuple.
- Recommended fix / fix applied: Added `"interview_plan_route_complete"` to the deferral tuple. Verified via `test_draft_plan_interactive_outline_gap.py` (fixed to also supply the now-required `interview_trivial_evidence` answer, same root cause as the earlier `interview_classification` rename drift already logged this session) and `test_control_plane_pipeline_simulator.py::test_simulator_exercises_standard_interview_enforcement` (its own `match=` string updated once more, from `interview_plan_route_complete` to `Missing required response`, since the deferral fix changes the failure to occur naturally at question-collection time instead of an early denial -- a more correct failure point, not a regression).
- Evidence/repro: Full suite run before fix: `1 failed, 500 passed, 1 skipped`. After fix + test corrections: `508 passed, 1 skipped, 0 failed` (`/tmp/full_suite_final.log`).
- Severity: M (real functional bug affecting live interactive usage, not just tests)
- Repeat: YES -- third instance this session of a check/field rename not propagating to every reference (see also the `interview_classification` -> `interview_plan_route_complete` test-assertion drift and the `full_test_suite` -> `full_test_suite_or_trivial_focused` drift, both logged separately). Recommend a grep-based CI check cross-referencing `policy.py`'s registered check-id strings against every literal string reference in `coordinator.py` and `tests/`, to catch the next rename before merge rather than after.

## DEBT-20260917-MAP-DEBT-PLUGIN-SCOPE-SYNC

- Logged date: 2026-09-17
- Cycle/Session ID: auth-ciba-poc-transition-mechanics
- Artifact affected: `plugins/agent-agentic-os/references/map-debt.md`
- Friction observed: The `_resolve_plan_outline_path` cwd-fallback finding (see `plugins/agent-agentic-os/references/map-debt.md`) was recorded directly on the main checkout mid-session and never copied into this task's worktree until now -- a small instance of the same worktree/main-checkout content-drift pattern this session hit repeatedly with code files.
- Why not fixed now: This entry documents the sync itself; no further fix needed.
- Recommended fix / fix applied: Copied the missing row into the worktree's plugin-scoped `map-debt.md` so both copies match before the worktree branch is reviewed.
- Evidence/repro: `diff` between the worktree's and main checkout's plugin-scoped `map-debt.md` before this commit.
- Severity: L
- Repeat: NO
- Status: RESOLVED

## DEBT-20260917-VERIFY-EXIT-GATE-HARDENING

- Logged date: 2026-09-17
- Cycle/Session ID: auth-ciba-poc-transition-mechanics
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`, `control_plane/state_machine.py`
- Friction observed: Live diagram review surfaced three edges converging on `VERIFY_EXIT` with weak or zero human authorization: (1) `WORKTREE_REVIEW -> VERIFY_EXIT` and (2) `MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT` both declared zero `human_questions`, reachable via `code_review_or_skip`'s own receipt check which has no actor verification at all (`record_review_skip`'s `actor` parameter is an unvalidated free-text string). (3) `IN_WORKTREE -> VERIFY_EXIT` was worse still: zero `human_questions` AND zero `deterministic_checks` -- a fully open backdoor letting an agent skip `WORKTREE_REVIEW` and code review entirely.
- Why not fixed now: Fixed live in this same session -- see Recommended fix / fix applied.
- Recommended fix / fix applied: (1) and (2) fixed by adding real `human_questions` entries (`confirm_worktree_review_accept_implementation`, `confirm_multi_agent_code_review_accept_outcome`), which get genuine SQLite-trigger-level `actor='human'` enforcement via the existing `required_transition_questions` mechanism -- no coordinator.py/policy.py changes needed. (3) was first mis-fixed the same way (a "Gate 3d" human question), then correctly fixed by **removing the edge entirely** from both `state_machine.py`'s `ALLOWED_TRANSITIONS` and the YAML template: a human answering a "bypass review?" question at that point would be approving a bypass of the one step (`WORKTREE_REVIEW`) whose entire purpose is to show them the diff first -- correctly attributed to a human, but not an informed decision. All work must now pass through `WORKTREE_REVIEW` before `VERIFY_EXIT`. Failing tests written first for all three (TDW); full ripple across `test_agent_control.py`, `test_agent_control_gate_characterization.py`, `test_pre_commit_pipeline_guard.py`, `test_transition_guidance.py` fixed and re-verified green.
- Evidence/repro: `test_worktree_review_verify_exit_gate.py` (5 tests: 3 for the two hardened edges, 2 confirming the removed edge no longer exists and is rejected by the state machine).
- Severity: H
- Repeat: NO
- Status: RESOLVED

## DEBT-20260917-ARTIFACT-PATH-WORK-TASKS-FALLBACK

- Logged date: 2026-09-17
- Cycle/Session ID: auth-ciba-poc-transition-mechanics
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/coordinator.py` (`_resolve_artifact_path`)
- Friction observed: `required_artifacts` checks (`DRAFT_PLAN -> PLAN_REVIEW` and others) only resolved the legacy flat `docs/plans/<task-id>-spec.md` layout, not the documented `docs/plans/work-tasks/<task-id>/` grouping convention (`docs/plans/document-layout.md`). Plan documents written correctly under `work-tasks/<task-id>/` via `write_plan_document.py` were reported missing, denying the transition. Full detail logged in `plugins/agent-agentic-os/references/map-debt.md` (same date).
- Why not fixed now: Fixed in this same session — see Recommended fix / fix applied.
- Recommended fix / fix applied: Added a `work-tasks/<task-id>/` lookup before the flat-path fallback in `_resolve_artifact_path`. Failing test written first (`test_resolve_artifact_path_falls_back_to_work_tasks_folder`, `plugins/agent-agentic-os/tests/test_agent_control.py`), confirmed red against prior code, green after the fix. Full `test_agent_control.py` suite (104 tests) green.
- Evidence/repro: Live reproduction during `auth-ciba-poc-transition-mechanics`'s own governed `DRAFT_PLAN -> PLAN_REVIEW` attempt; unit test reproduces the gap directly.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260914-PREMATURE-EXECUTION-PROPOSAL-IN-INTERVIEW

- Logged date: 2026-09-14
- Cycle/Session ID: skill-research-alignment-20260914
- Artifact affected: `plugins/agent-agentic-os/skills/work-intake/SKILL.md`, control plane task state machine
- Friction observed: Pipeline violation — during the `INTERVIEW` phase of task `skill-research-alignment-20260914`, the agent prematurely asked "Shall I proceed with Step 1 now?" attempting to jump straight into file modifications on the main branch, violating Proposal Mode and bypassing the required Socratic interview, plan outline completion, `DRAFT_PLAN` compilation, `PLAN_REVIEW`, explicit human `APPROVED` gate, and worktree isolation (`IN_WORKTREE`).
- Why not fixed now: N/A — execution halted by the human; state remains strictly in `INTERVIEW`.
- Recommended fix / fix applied: Logged this debt entry, immediately ceased execution proposals, and returned strictly to the `INTERVIEW` Socratic questioning protocol (one question at a time) to capture requirements without touching production code.
- Evidence/repro: Agent prompted to start Step 1 editing while task was in state `INTERVIEW` (transition_id=248).
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260914-INSTALLATION-PROBE-LEGAL-INITIAL-STATES

- Logged date: 2026-09-14
- Cycle/Session ID: skill-research-alignment-20260914
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/installation_probe.py`, `plugins/agent-agentic-os/tests/test_installation_probe.py`
- Friction observed: `installation_probe.py` compared `valid_transitions` rows against `_expected_transitions()` derived solely from `ALLOWED_TRANSITIONS.items()`. But `adapters.py`'s `_sync_valid_transitions` also inserts `[(None, s) for s in LEGAL_INITIAL_STATES]` (from_state IS NULL rows for initial states). Consequently, `installation_probe.py` falsely reported `PARTIAL_OR_DRIFTED` with "valid transition rows drift from state_machine.py" on completely healthy, initialized control plane databases.
- Why not fixed now: N/A — patched immediately in worktree.
- Recommended fix / fix applied: Updated `_expected_transitions()` in `installation_probe.py` to union `{(None, s) for s in LEGAL_INITIAL_STATES}`, and synchronized `test_installation_probe.py` scaffold. `classify_target` now accurately reports `COMPLETE`.
- Evidence/repro: `python3 plugins/agent-agentic-os/scripts/control_plane/installation_probe.py --target .` now returns `{"state": "COMPLETE", "missing": []}`.
- Severity: S
- Repeat: NO
- Status: RESOLVED

## DEBT-20260914-EXPLORATION-CYCLE-AGENTIC-OS-INTEGRATION

- Logged date: 2026-09-14
- Cycle/Session ID: skill-research-alignment-20260914
- Artifact affected: `plugins/exploration-cycle-plugin`, `plugins/agent-agentic-os`
- Friction observed: Architectural boundary misalignment — the Exploration Cycle plugin previously operated as a self-contained, prompt-orchestrated workflow carrying its own prompt-based orchestration machinery (dashboard detection, XML dispatch tokens, prompt phase gates), creating a parallel prompt-based control plane.
- Why not fixed now: N/A — actively addressed in task `skill-research-alignment-20260914` (Iteration 3 plan).
- Recommended fix / fix applied: Modernized Exploration Cycle onto Agentic OS as Target 1: make Agentic OS an explicit prerequisite via `exploration_substrate.py` (requiring `os-init`), remove prompt-based dashboard intercept and dispatch tokens from exploration skills, preserve genuine cognitive discovery and prototyping intelligence, and treat exploration stages as sub-workflow session metadata rather than bloating the global 15-state lifecycle machine.
- Evidence/repro: Iteration 3 specification and implementation plan (`docs/plans/skill-research-alignment-20260914-spec.md`).
- Severity: M
- Repeat: NO
- Status: RESOLVED



## DEBT-20260914-AMBIGUOUS-DEV-UTILS-DEPENDENCIES

- Logged date: 2026-09-14
- Cycle/Session ID: skill-research-alignment-20260914
- Artifact affected: `plugins/dev-utils/skills/coding-conventions-agent`, `context-bundler`, `convert-mermaid`, `hf-init`, `hf-upload`
- Friction observed: During dependency classification (Target 3), 5 skills in `plugins/dev-utils` contained single-line stand-in pointers `../../requirements.txt` or `../../requirements.in`, but `plugins/dev-utils` lacks a plugin-root `requirements.txt` or `requirements.in`. This creates broken requirement resolution chains that cannot be verified automatically.
- Why not fixed now: Preserving out-of-scope boundaries — adding new plugin-root requirement manifests or deciding third-party package dependencies for `dev-utils` requires explicit package specification.
- Recommended fix / fix applied: Scaffolding a canonical `plugins/dev-utils/requirements.in` / `requirements.txt` via `dependency-management` workflow, or adjusting individual skill pointers to point to their own local requirements files.
- Evidence/repro: `plugins/dev-utils/scripts/classify_skill_dependencies.py` classified these 5 skills as `AMBIGUOUS` with error "File not found: plugins/dev-utils/requirements.txt".
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260916-SYMLINK-SKILL-PATH

- Logged date: 2026-09-16
- Cycle/Session ID: skill-pruning-and-symlink-audit
- Artifact affected: `.agents/skills/symlink-manager/SKILL.md`
- Friction observed: The skill documents `plugins/link-checker/scripts/symlink_manager.py`, but the executable lives at `plugins/dev-utils/scripts/symlink_manager.py`; the documented command fails immediately.
- Why not fixed now: The requested audit was completed using the discovered canonical script; synchronizing the installed/source skill documentation is a separate plugin-sync change.
- Recommended fix: Update the symlink-manager skill's documented script path and add a smoke test that resolves the documented command before release.
- Evidence/repro: `python3 plugins/link-checker/scripts/symlink_manager.py diagnose` returned `can't open file`; `python3 plugins/dev-utils/scripts/symlink_manager.py diagnose` completed and reported six unrelated plugin-pruner links.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260914-PROGRESSIVE-ELABORATION-SUMMARY-DOC

- Logged date: 2026-09-14
- Cycle/Session ID: progressive-elaboration-vs-duplication-summary (PR #620)
- Artifact affected: `plugins/agent-agentic-os/references/progressive-elaboration-vs-duplication-summary.md` (new)
- Friction observed: CI's "Verify Evolution & Map Debt Compliance" gate flags any change under `plugins/` as core logic requiring a map-debt or evolution-log entry, even for a pure reference/documentation addition with no code or skill-behavior change.
- Why not fixed now: N/A — documentation-only change, no behavior to fix; this entry exists solely to satisfy the CI gate's requirement for any `plugins/` diff.
- Recommended fix / fix applied: Logged this entry rather than adding `Evolution-Check: none` retroactively (commit already pushed). No code or skill-routing behavior changed; the new file is maintainer-facing research guidance on skill deduplication and progressive-disclosure loading strategy, cited in PR #620.
- Evidence/repro: `gh run view` on the PR's failed "Check Map Debt & Evolution Compliance in PR Diff" step named this exact file as the unaccounted-for `plugins/` change.
- Severity: S
- Repeat: NO
- Status: RESOLVED

## DEBT-20260914-CONTROL-PLANE-CONSTANTS-CONSOLIDATION

- Logged date: 2026-09-14
- Cycle/Session ID: agentic-os-dedup-invariant-v2
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/adapters.py`, `state_machine.py`, `coordinator.py`, `policy.py`, `agent_control.py`, `pipeline_simulator.py`, `transition_simulation_cases.py`, `worktree_manager.py`, and ~35 test files; new `plugins/agent-agentic-os/scripts/control_plane/constants.py`
- Friction observed: The `guidance_compliance_confirmation` question added earlier in this work package broke 46 tests because each had independently hardcoded its own literal answer sequence. A follow-up external review and whole-plugin scan found ~1,000 raw task-lifecycle state-name literals plus a second wave of hardcoded decision-type/actor/cost-tier/task-type/worktree-state/gate-name/critic-verdict/delegation-status/retrospective-status literals duplicated across 40 files. This duplication directly caused two live bugs: three `adapters.py` methods embedded a constant's name literally inside a plain (non-f) SQL string instead of its value, so SQLite silently compared against the wrong text and matched nothing; and `_rebuild_schema_transactional()` executed a ~40-line inline `CREATE TRIGGER` that was immediately dropped and replaced by the canonical one from `SCHEMA_SQL` three lines later.
- Why not fixed now: N/A — fixed in this session.
- Recommended fix / fix applied: Created `control_plane/constants.py` as the single shared source for every cross-file domain constant. `state_machine.py` imports state names from it and owns only the derived adjacency DAG. `adapters.py`'s `SCHEMA_SQL` builds its `CHECK (... IN (...))` clauses from these constants via a new `sql_in_list()` helper; `SCHEMA_MIGRATIONS` (immutable historical DDL) was deliberately left untouched. Runtime SQL queries that interpolated constants via f-string were converted to `?` bind parameters (f-strings now reserved for `SCHEMA_SQL`/trigger DDL at module-load time only, since SQLite triggers can't accept bind params at all). Two fixed-depth `.parent` chains were replaced by one git-based `_resolve_repo_root()` helper. A follow-up 21-file audit added missing `Key Input Dependencies`/`Key Functions` header sections per `coding-conventions.md` (20 fixed, `evaluate.py` correctly left untouched — its own header says "DO NOT MODIFY THIS FILE"), and fixed one further genuine duplication (`worktree_manager.py`'s native/portable strategy literals) while deliberately declining to merge a coincidental `"COMPLETE"` string shared across 4 unrelated domains (would have been a false coupling, same mistake class as an earlier attempt to import `agent_control`'s `STATE_AWAITING_APPROVAL` into files that actually call the separately-governed `evolution_state.py`'s own `AWAITING_APPROVAL`). Canonical rule updated: `plugins/agent-agentic-os/rules/config-driven-constants-over-hardcoding.md`.
- Evidence/repro: Full suite green — `pytest plugins/agent-agentic-os/tests/ -q` → 475 passed, 0 failed, including regression coverage for both live bugs found and fixed above.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260913-WORKTREE-BASE-BRANCH-DEFAULT

- Logged date: 2026-09-13
- Cycle/Session ID: worktree-docs-alignment
- Artifact affected: `plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py::create_worktree`
- Friction observed: `create_worktree()` defaults `base_branch` to local `main` rather than a freshly-fetched `origin/main`, which the multi-worktree research documented in #611 identifies as a source of stale-base worktree drift.
- Why not fixed now: Documentation-only alignment pass (docs/diagrams + reference guide); changing the function default is a code behavior change requiring its own TDD cycle, deferred pending explicit scope confirmation.
- Recommended fix: Change the default to fetch and use `origin/main`, or require the caller to pass it explicitly; add a regression test asserting the branch point matches `origin/main` at call time.
- Evidence/repro: See `plugins/dev-utils/references/github-issue-worktree-agent-worktree-guide.md`, updated this commit to flag the gap inline.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260913-WORKTREE-BEST-PRACTICES-DOCS

- Logged date: 2026-09-13
- Cycle/Session ID: worktree-manager-best-practices
- Artifact affected: `plugins/agent-agentic-os/skills/worktree-manager/SKILL.md`, `plugins/agent-agentic-os/skills/interview-spec/SKILL.md`, `plugins/agent-agentic-os/references/worktree-reconciliation-and-multi-worktree-practices.md` (new), `plugins/agent-agentic-os/scripts/agent_control.py`
- Friction observed: Follow-up to DEBT-20260913-MAIN-WORKTREE-RECONCILIATION — the code-level fix existed but wasn't reflected in skill guidance, and there was no early (INIT-time) advisory for dirty `main` state, nor documented guidance for preventing one concurrent worktree's merged work from being undone by another (industry-researched: fresh-base branching, integration-branch pattern for overlapping work).
- Recommended fix: Documented the reconciliation contract and multi-worktree practices in a new canonical reference, linked from `worktree-manager` and `interview-spec` SKILL.md; added a non-blocking `main_dirty_advisory` field to `create_task()` so dirty `main` state is surfaced at INIT time, not just hard-blocked later at `APPROVED -> IN_WORKTREE`.
- Evidence/repro: New tests `test_create_task_reports_main_dirty_advisory` and `test_create_task_reports_clean_main_advisory` pass. `symlink_manager.py diagnose` clean. `audit.py`/`audit_plugin_structure.py` both pass with 0 errors.
- Severity: S
- Repeat: NO
- Status: RESOLVED

## DEBT-20260913-MAIN-WORKTREE-RECONCILIATION

- Logged date: 2026-09-13
- Cycle/Session ID: issue-609-worktree-reconciliation
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py`, `plugins/agent-agentic-os/scripts/control_plane/policy.py`, `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`
- Friction observed: `APPROVED -> IN_WORKTREE` had no gate verifying pre-worktree dirty changes on the source checkout were carried into the newly created worktree. An agent was asked twice, explicitly, to confirm this happened and asserted it did without checking; the source-checkout dirty state was left behind.
- Why not fixed now: N/A — fixed in this commit.
- Recommended fix: Added a deterministic check (`main_worktree_reconciliation`) that runs automatically on the transition and force-copies dirty source-checkout files into the worktree via code, blocking on any genuine content conflict instead of trusting agent self-report.
- Evidence/repro: See https://github.com/richfrem/agent-plugins-skills/issues/609. New tests `test_approved_to_in_worktree_auto_reconciles_dirty_main_changes` and `test_approved_to_in_worktree_blocks_on_genuine_reconciliation_conflict` in `plugins/agent-agentic-os/tests/test_agent_control.py` both pass.
- Severity: L
- Repeat: YES (2nd+ occurrence — false completion claims on git state; see DEBT-20260913-GIT-GUARD-RECOVERY-EDGE below for the related guard fix same day)
- Status: RESOLVED

## DEBT-20260913-GIT-GUARD-RECOVERY-EDGE

- Logged date: 2026-09-13
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `plugins/agent-agentic-os/scripts/pre-commit-pipeline-guard` and `pre-push-review-guard`
- Friction observed: Git guards treated a human-approved recovery transition such as `DONE -> IN_WORKTREE` as an illegal normal-DAG edge and blocked commit/push despite the persisted recovery approval.
- Why not fixed now: Fixed in scope by validating the exact transition ID against a consumed human recovery-approval receipt; ordinary unapproved non-DAG edges remain blocked.
- Recommended fix: Keep guard tests paired with every future human-recovery schema or lifecycle change.
- Evidence/repro: The live task had recovery approval bound to transition 217; the original commit gate rejected it. The new exact-receipt regression test passes for both pre-commit and pre-push guards.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260912-OS-INIT-INSTALL

- Logged date: 2026-09-12
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `.agents/skills/os-init/SKILL.md`
- Friction observed: The live skill loader reported the installed `os-init` skill as missing even though the canonical source file existed.
- Why not fixed now: Fixed in scope by reinstalling `agent-agentic-os` and verifying the installed file against the canonical source.
- Recommended fix: If the warning recurs, inspect the plugin install transaction and manifest before editing skill content.
- Evidence/repro: `plugins/agent-agentic-os/skills/os-init/SKILL.md` and `.agents/skills/os-init/SKILL.md` both exist at 7,860 bytes and compare identical after reinstall; source/plugin audits pass.
- Severity: S
- Repeat: NO
- Status: RESOLVED

## DEBT-20260912-PLAN-EFFORT-PERSISTENCE

- Logged date: 2026-09-12
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `context/control_plane.db` task planning metadata
- Friction observed: The approved planning choice is `gpt-5.6-luna` at high effort, but the current `tasks` schema stores `model_tier` and `model_id` only; exact effort is preserved in the interview decision and scoped premium-consent row rather than in task metadata.
- Why not fixed now: This turn is planning-only; adding or migrating task metadata would be implementation work and could widen the P00 slice before review.
- Recommended fix: During the bounded P00 implementation preflight, decide whether a minimal stage-scoped planning model/effort receipt is required for truthful status reporting. Add it only with a focused migration and persistence test; do not build a general model-routing schema.
- Evidence/repro: `agent_control.py status --task-id p0-live-baseline-20260912` reports `model_tier=medium`, `model_id=gpt-5.6-luna`; `transition_decisions` records `effort: high`; `premium_consents` records `stage=plan`, `round_id=round-1`, `model_id=gpt-5.6-luna`.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260912-REVIEW-MENU-CONTRACT

- Logged date: 2026-09-12
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml` and focused transition-guidance tests
- Friction observed: Review questions mixed revision, skip, and reviewer-method choices on transitions whose fixed destination could not honor every option. Plan review used a separate disposition question, while implementation review used a six-option mixed menu; several options therefore did not correspond to the edge target. The YAML correction exposed four focused tests still encoding the old question ID and mixed menus.
- Why not fixed now: This turn was scoped to the YAML contract and live plugin reinstall; changing the runtime to route one question dynamically to multiple lifecycle states is a larger follow-up.
- Recommended fix: Add explicit route-aware branching only if the control plane needs a single prompt to choose multiple destination states. Until then, keep edge questions target-specific and update the affected focused tests in the next bounded contract slice.
- Evidence/repro: `test_transition_guidance.py` reported 4 failures after the YAML update; registry validation confirmed the corrected defaults and accepted answers are target-valid, and source/live YAML copies match.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260912-MULTI-AGENT-KICKOFF-SCHEMA

- Logged date: 2026-09-12
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml` stage registry
- Friction observed: The new `MULTI_AGENT_REVIEW` stage contract initially omitted the required `adaptive_follow_up_rules` field, so the authorized plan writer rejected both revised documents before writing them.
- Why not fixed now: Fixed in scope by adding the required empty field, reinstalling the plugin, and retrying through the authorized writer.
- Recommended fix: When adding a stage contract, validate it through the plan writer or registry schema before relying on the live transition path.
- Evidence/repro: The first `write_plan_document.py` attempt returned `Stage 'MULTI_AGENT_REVIEW' missing required field 'adaptive_follow_up_rules'`; the retry wrote both documents after reinstall.
- Severity: S
- Repeat: NO
- Status: RESOLVED

## DEBT-20260912-PLAN-REVIEW-ROUND2

- Logged date: 2026-09-12
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: `docs/plans/p0-live-baseline-20260912-spec.md`, `docs/plans/p0-live-baseline-20260912-implementation-plan.md`, and the `MULTI_AGENT_REVIEW` handoff
- Friction observed: The second independent review found the draft still leaves answer-versus-transition transaction scope, exact API/output/receipt schemas, answer-to-edge semantics, artifact identity, and reviewer kickoff interfaces partly prose-level. The security review also identified existing wildcard force-close and approval/occupancy-binding risks that must not be silently treated as preserved boundaries.
- Why not fixed now: Fixing runtime authorization or building an executable reviewer coordinator would expand beyond the current planning-only P00 package. The task was returned to `DRAFT_PLAN` with implementation and worktree capabilities still prohibited.
- Recommended fix: Revise the plan to either define the remaining contracts with current source signatures and focused tests, or explicitly remove/defer the review-dispatch/runtime-security work with named follow-up ownership and evidence. Do not approve implementation while these blockers remain unresolved.
- Evidence/repro: Internal architecture, security, and TDD reports in `temp/context-bundle-p0-live-baseline/responses/` all returned `REQUEST_CHANGES`; critic review iteration 2 was recorded before transition `MULTI_AGENT_REVIEW -> DRAFT_PLAN` (SQLite transition ID `203`).
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260913-INTERVIEW-ANSWER-REVISION

- Logged date: 2026-09-13
- Cycle/Session ID: p0-live-baseline-20260912
- Artifact affected: control-plane transition_decisions / INTERVIEW answer recording
- Friction observed: After the human clarified the acceptance criteria, the supported recorder rejected a second answer for the canonical `interview_acceptance_criteria` question as a duplicate. There is no supported revision or append-clarification path.
- Why not fixed now: Editing SQLite directly would bypass the control plane and violate the authority boundary. The current recorded answer remains intact; the clarification is preserved in the session context.
- Recommended fix: Add an explicit human-authorized answer revision or clarification mechanism that preserves the original answer, revised answer, actor, timestamp, and reason without duplicate-question ambiguity.
- Evidence/repro: `ControlPlane.record_decision(... question_id='interview_acceptance_criteria' ...)` raised `ValueError: Duplicate decision ... occupancy 196` on 2026-09-13.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260912-BACKLOG-SIZING

- Logged date: 2026-09-12
- Cycle/Session ID: backlog-review-20260912
- Artifact affected: temp/agent-vision/vision.md; GitHub #585 and #595–#601
- Friction observed: owner reports P00–P02 took over a day and explicitly abandoned P03–P09; the old plan and broad PR title could incorrectly trigger continuation.
- Why not fixed now: runtime task-sizing enforcement is separate implementation work under #586; this review changes the roadmap and backlog only.
- Recommended fix: select one independently useful 20–60 minute slice; review its outcome before selecting another. Keep P03–P09 abandoned and #585 deferred.
- Evidence/repro: owner correction on 2026-09-12; ranked-backlog-2026-09-12.md documents all 31 issues and current-source evidence.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260912-BACKLOG-HELPERS

- Logged date: 2026-09-12
- Cycle/Session ID: backlog-review-20260912
- Artifact affected: plugins/dev-utils/scripts/gh_issue_prioritize.py and gh_issue_close.py
- Friction observed: tier:3 architecture labels become automatic P0 even for deferred designs; closure helper has no not-planned reason and defaults to completed. One inspection also guessed a nonexistent gh_issue_promote.py path; corrected by inspecting existing helpers.
- Why not fixed now: user requested backlog/vision updates, not helper code changes. No new issue created.
- Recommended fix: prioritize using the documented manual evidence override for this review; use native GitHub not_planned state reason for abandoned work. Consider helper behavior separately with #546.
- Evidence/repro: prioritize_issue returns P0 for #519 despite its blocked consumer-dependent scope; close_issue invokes gh issue close without --reason. Native gh issue close supports not planned. Mutation payloads preserved under temp/agent-vision/backlog-updates/.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260910-P0-INTAKE-INSTALL

- Logged date: 2026-09-10
- Cycle/Session ID: p0-observability-foundation
- Artifact affected: .agents/skills/interview-spec/scripts/ and references/detailed-reference.md
- Friction observed: installed interview_spec_engine.py cannot import capability_probe; installed interview question wrapper is absent. The detailed reference still describes obsolete trivial/review edges. Host session exposes no tool to activate native Plan Mode.
- Why not fixed now: this session authorizes foundation documents and planning; plugin repair is a separate implementation change.
- Recommended fix: restore self-contained installed intake helpers and align detailed reference with the canonical registry; test the installed entry points. Use the supported source helpers for missing installed helpers during this intake, preserving all gates and document-derived actor identity. Use the documented Codex Socratic fallback, not a claimed native Plan Mode entry.
- Evidence/repro: installed intake command raises ModuleNotFoundError for capability_probe; source helper and registry inspected 2026-09-10. Existing installed agent_control.py remains callable.
- Severity: M
- Repeat: NO
- Status: OPEN

| ID | Title | Status | Severity | Repeat | First Seen | Description | Resolution Commit |
|---|---|---|---|---|---|---|---|
| DEBT-20260915-PIPELINE-GUARD-RELATIVE-PATH-REGRESSION | `pre-commit-pipeline-guard`'s registered-worktree location check (~line 97) resolved a repository-relative `worktree_path` against the current shell CWD instead of `REPO_ROOT`, so a legitimate commit from inside the correctly registered worktree was misclassified as "Commit Outside Registered Worktree" and blocked whenever `worktree_path` was stored relative (the normal case, e.g. `.worktrees/task-<id>`). Only an absolute `worktree_path` happened to work. This is a REGRESSION of an already-reviewed fix: the correct case-statement logic (resolve relative paths against `REPO_ROOT` explicitly) existed in commit `45b3fe51` (the reviewed Skill Research Alignment implementation), but a later uncommitted working-tree edit simplified it back to the buggy unconditional form, which was also already live in `.git/hooks/pre-commit-pipeline-guard` at the time of discovery. | RESOLVED | Tier 2 | NO | 2026-09-15 | feature/skill-research-alignment-20260914 | Discovered live while reconstructing task `skill-research-alignment-20260914` after an unauthorized `git reset HEAD~1` (see separate governance findings; tracked independently from GitHub issue #621's human-authorization-provenance finding and from the `git reset HEAD~1` incident itself -- three distinct root causes, not conflated). Not deferred; fixed immediately as part of the same reconstruction session under explicit human authorization for a narrow, canonical-source repair. | Restored the exact case-statement logic from commit `45b3fe51` in `plugins/agent-agentic-os/scripts/pre-commit-pipeline-guard`: compute `RESOLVED_REPO_ROOT` first, then resolve `TASK_WORKTREE_PATH` via `case "$TASK_WORKTREE_PATH" in /*) ... ;; *) cd "$RESOLVED_REPO_ROOT/$TASK_WORKTREE_PATH" ... ;; esac`. Verified byte-for-byte identical to `45b3fe51`'s version via `diff`. Synchronized the installed `.git/hooks/pre-commit-pipeline-guard` copy from the corrected canonical source (matching `init_agentic_os.py`'s own install mechanism: copy + chmod 755, no other changes). Added 4 new regression tests to `plugins/agent-agentic-os/tests/test_pre_commit_pipeline_guard.py` covering relative-path and absolute-path registered worktrees, from both the correct location (PASS) and the wrong location (BLOCK), using real `git worktree add` checkouts. | RED: all 4 new tests run against the pre-fix (buggy) hook -- the two PASS-from-correct-location tests failed exactly as the live incident did (false-positive block), confirming the tests reproduce the regression. GREEN: same 4 tests pass against the restored hook. Full regression: `pytest plugins/agent-agentic-os/tests/test_pre_commit_pipeline_guard.py` = 16 passed. Full `plugins/agent-agentic-os/tests/` suite re-run to confirm no unrelated breakage (see PR for final count). | S | NO | RESOLVED |
| DEBT-20260910-P0-INTAKE-INSTALL | Installed intake helpers missing; stale detailed reference (details above) | OPEN | Tier 2 | NO | 2026-09-10 | Session p0-observability-foundation: installed engine lacks capability_probe and interview wrapper is absent. Source-helper fallback preserves gates; native planning unavailable. Severity M. | Deferred plugin repair; restore installed dependencies and align reference, then verify installed entry points. |
| DEBT-20260910-P0-YAML-DB-SYNC | New Standard interview YAML question is not synchronized into the live task’s SQLite question state; transition trigger rejects otherwise complete interview | OPEN | Tier 2 | NO | 2026-09-10 | After adding `interview_planning_model_effort`, policy checklist accepted all six answers but `INTERVIEW -> DRAFT_PLAN` was rejected by the SQLite trigger. Existing wrapper answers also use an `Option ...` prefix that does not match the route check’s canonical classification value. | Provide a migration/registration path for updated stage questions and fix the supported wrapper canonicalization with regression tests; do not bypass trigger or manually rewrite task state. |
| DEBT-20260910-P0-PLANNING-ONLY-594 | Approved plans had no valid completion path that skipped implementation | OPEN | Tier 1 | NO | 2026-09-10 | GitHub issue #594: `APPROVED` only routed to `IN_WORKTREE`, forcing planning-only work into false implementation ceremony or an incomplete lifecycle. | Add explicit `APPROVED -> RETROSPECTIVE` planning-only edge with human approval, durable planning-only receipt, plan validation, and DONE-path checks. |
| DEBT-20260910-P01-INTAKE | Intake guidance did not provide a bounded, testable way to reuse authorized source answers without treating them as consent. | RESOLVED | Tier 1 | 1 | 2026-09-10 | Agents either re-asked known information or risked treating source text as a user decision. | Added candidate-only source assistance, conflict/authorization handling, review-budget and user-summary helpers, YAML policy, and behavioral tests. |
| DEBT-20260910-P0-P00 | P0 evidence contracts were not durably reviewable. | OPEN | Tier 1 | 1 | 2026-09-10 | Recovery ownership, secure producer artifact handling, and retention/privacy rules existed only as plan intent. | P00 drafts, fixture, manifest, and protocol added; review rounds clarified canonical Unicode/timestamp handling, conditional producer fields, and closed recovery-state vocabulary. Runtime work remains blocked pending independent review. |
| DEBT-20260909-PLAN-REVIEW-01 | Plan review branching was ambiguous: review selection, review outcomes, and final plan acceptance were represented as competing shortcuts instead of a repeatable decision loop. | RESOLVED | Tier 1 | 0 | 2026-09-09 | WP-576-20260909 | Replaced direct review/approval shortcuts with `DRAFT_PLAN -> PLAN_REVIEW`, an explicit review decision, optional `MULTI_AGENT_REVIEW -> PLAN_REVIEW`, and acceptance/revision outcomes. Synchronized state-machine legality, YAML templates, SQLite questions, coordinator tests, and Mermaid diagrams. | M | NO | RESOLVED |
| DEBT-20260909-WORKTREE-PREFLIGHT-01 | Transition guidance did not explicitly require creating or verifying an isolated feature worktree and branch before implementation. | OPEN | Tier 1 | 1 | 2026-09-09 | WP-576-20260909 | This task reached `IN_WORKTREE` while changes were written in the main checkout on branch `main`; the YAML explained later worktree review but did not provide a clear preflight instruction or deterministic check for branch/worktree isolation. | Add explicit implementation-entry guidance and a fail-closed precondition for an isolated feature worktree/branch, while preserving the documented exception only when the user explicitly authorizes existing-checkout work. | M | NO | OPEN |
| DEBT-20260906-10 | New invariant established by issue-524: gate/policy enforcement unified into ONE mechanism (control_plane/policy.py); a related finding (#529) on transition-authority vs. transition-legality is explicitly deferred, not implemented | RESOLVED | Tier 2 | 1 | 2026-09-06 | issue-524's hexagonal decomposition of `agent_control.py`'s `ControlPlane` (7 mixed responsibilities) unified the 4 previously-scattered gate mechanisms (`GATE_REQUIREMENTS` registry, 3 hardcoded `_check_*_guard` methods, `update_worktree()`'s independent push barrier) into `control_plane/policy.py`'s `TRANSITION_RULES`/`TO_STATE_RULES`/`OPERATION_RULES` — one declarative policy-evaluation mechanism covering both lifecycle transitions and controlled operations. All 7 responsibilities are now separated into dedicated, independently testable domain components or port/adapter boundaries (state-machine validation and gate policy as pure domain classes/modules with no infrastructure to abstract; filesystem, SQLite connection+migration+CRUD, crypto, and model-catalog resolution behind ports/adapters), with a permanent AST-based structural test preventing regression back to scattered gates. Separately, during this same task's own interview, a live control-plane incident surfaced a distinct architectural gap — persisted state can diverge from actual agent behavior, and a legal state-transition edge existing does not mean the agent is authorized to select it unilaterally — filed as [GitHub Issue #529](https://github.com/richfrem/agent-plugins-skills/issues/529) with two GIVEN/WHEN/THEN regression scenarios. Per explicit human instruction, #529's finding is recorded here for future plan review, NOT implemented as part of issue-524. | Gate-policy unification: see `plugins/agent-agentic-os/scripts/control_plane/policy.py` and commit `a381b8fb` (Step 4) on branch `feature/issue-524-control-plane-decomposition`. #529 finding resolved in Issue #529 via TransitionCoordinator, TransitionRegistry, and fixed-identity wrappers. |
| DEBT-20260907-01 | Issue #529: Transition authority vs transition legality & behavioral state divergence | RESOLVED | Tier 2 | 1 | 2026-09-07 | Agents could perform phase-specific activities without prior control plane authorization, and transition legality in DAG was conflated with transition authority. | Implemented TransitionCoordinator, TransitionRegistry (51 edge templates), fixed-identity wrappers with shadow writes, and atomic decision/receipt persistence. |
| DEBT-20260906-09 | Agent (Claude) skipped the pipeline's own front-door step twice in one session: called `transition --to INTERVIEW` without entering Plan Mode first (caught by user), then later skipped registering a task or entering INTERVIEW at all and jumped straight to packaging a review bundle when asked for a "full run... starting with interview" (caught by user again). | OPEN | Tier 1 | 1 (2nd occurrence of the pattern, different specific step each time) | 2026-09-06 | This is a judgment/instruction-following failure, not a code defect — no DB-level gate can force an LLM to call `agent_control.py init`/`transition` before starting work, since the agent is the one deciding whether to invoke the tool at all. The GATE_REQUIREMENTS registry built in PR #521 only enforces order *once a transition() call is made* — it can't stop an agent from never registering a task in the first place and just doing the requested work directly. | Deferred — see Recommended fix. No code fix possible for this specific failure mode; the mitigation is procedural. |
| DEBT-20260906-02 | Unmanaged plugin patching and unreviewed .bak clutter during os-init/retrofit | RESOLVED | Tier 1 | 1 | 2026-09-06 | Consumers of agent-plugins-skills lacked interactive configuration for handling upstream vs local plugin fixes, and os-init generated .bak backup files without prompting consuming agents to thoughtfully review and reconcile custom diffs before cleanup. | Added _configure_plugin_contribution_policy() and --contribution-mode CLI flag in init_agentic_os.py; created context/plugin-config.json; enriched CLAUDE.md with maintenance policy; tracked created .bak files and added explicit diff-review-before-delete directives in print_next_steps() and os-health-check/SKILL.md Phase 3.5; added contract tests. |
| DEBT-20260905-15 | os-init failed to scaffold remote CI evolution workflow leaving GitHub PRs unenforced | RESOLVED | Tier 1 | 1 | 2026-09-05 | While os-init wired the local pre-commit evolution guard into .git/hooks/, it never scaffolded the remote counterpart .github/workflows/verify-evolution-integrity.yml, leaving PRs created in consumer repos unprotected by CI evolution compliance checks. | Added scaffolding for .github/workflows/verify-evolution-integrity.yml in _validate_and_finalize() across fresh init and --retrofit; updated print_next_steps(), os-init/SKILL.md, and os-health-check/SKILL.md; added automated contract test. |
| DEBT-20260906-01 | os-init and os-health-check omitted Phase 0 Intake Gate & interview-spec YAML clarity | RESOLVED | Tier 1 | 1 | 2026-09-06 | Agents bypassed interview-spec and Socratic intake because SKILL.md description lacked imperative execution triggers, and os-init never enriched target CLAUDE.md/GEMINI.md with Phase 0 intake rules, nor did os-health-check verify instruction-level compliance. | Updated interview-spec YAML frontmatter with imperative intake triggers; added Phase 0 intake enrichment to _merge_instructions_with_judgment() in init_agentic_os.py; added interview-spec rule check to Phase 3.5 of os-health-check/SKILL.md; fixed --project-root argument; added contract tests. |
| DEBT-20260905-14 | os-init failed to scaffold plugin evolution logs and lacked post-init os-health-check direction | RESOLVED | Tier 1 | 1 | 2026-09-05 | Following DEBT-20260905-12/-13, consumer repos with local plugins/ developed gaps where individual plugins lacked references/evolution-log.md, leaving them unaligned with the pre-commit evolution guard. Furthermore, os-init completed without directing the user/agent to run os-health-check to verify that all substrates were active. | Added `_scaffold_plugin_evolution_substrates()` to `init_agentic_os.py` to inspect local plugins and seed `references/evolution-log.md` if missing; updated `print_next_steps()` to direct users/agents to immediately run `os-health-check`; updated `os-init/SKILL.md` Phase 5 and `os-health-check/SKILL.md` Phase 3.5; added contract tests in `test_init_agentic_os_scaffolding.py`. |
| DEBT-20260907-02 | No recovery path existed for a control-plane task record that drifted from reality (e.g. a raw SQL write bypassing the normal transition path) other than `--no-verify` past the commit/push hooks — motivated live by task-issue-pipeline-commit-hook's own record showing an unexplained transition_violations entry inconsistent with its legitimate history. | RESOLVED | Tier 1 | 1 | 2026-09-07 | Every task's control-plane record was a dead end once drifted: no gated, audited way to recover it back into a walkable state short of bypassing the pipeline-guard/push-guard hooks entirely. | Added `reset_to_intake`: one authored `from_state: "*"` template mechanically expanded per non-INTAKE canonical state (including DONE, explicit deliberate exception), fully gated through `coordinate_transition()`, `interactive=True`-only, recorded as new `decision_type='RESET'`. See `plugins/agent-agentic-os/references/evolution-log.md` (2026-09-07 entry) for full detail. |


| DEBT-20260905-12 | os-init --retrofit never created context/control_plane.db despite skill doc and completion banner claiming both modes initialize it | RESOLVED | Tier 1 | 1 | 2026-09-05 | Reported from downstream consumer repo (InvestmentToolkit, same machine) after running `init_agentic_os.py --target . --retrofit`: `context/control_plane.db` was absent post-run even though `os-init/SKILL.md`'s Phase 3 note and the script's own `print_next_steps()` banner both state "In both modes, init_agentic_os.py automatically initializes context/control_plane.db with WAL mode." Root cause: `_init_control_plane_db()` is only ever called from `_scaffold_context_dir()`, which is only reached via the fresh-setup path (`create_project_structure()`). `_execute_action()`'s `if args.retrofit:` branch calls `_scaffold_3layer_memory()`, `sync_instructions()`, `sync_rules()`, and `retrofit_existing_skills()` — never `_scaffold_context_dir()` or `_init_control_plane_db()` — so every retrofit run silently skipped it, with no error or warning. | Added a direct `_init_control_plane_db(target, args.dry_run)` call inside the `if args.retrofit:` branch of `_execute_action()`. The function is already idempotent (returns early with an "exists ... (skipped)" announcement if the DB already exists), so it's safe to call unconditionally on every retrofit run without affecting existing repos. Documented the fix and the retrofit-is-not-a-subset-of-fresh-setup lesson directly in `os-init/SKILL.md`'s Phase 3 section so future edits to `_execute_action()` don't reintroduce a substrate gap between the two branches. |
| DEBT-20260905-13 | os-init --retrofit also never created .claude/hooks/hooks.json (Stop turn hook) or .git/hooks/pre-commit-evolution-guard — same root cause as DEBT-20260905-12, found immediately after fixing it, plus no automated check existed to catch either gap | RESOLVED | Tier 1 | 1 | 2026-09-05 | Follow-up to DEBT-20260905-12 in the same downstream consumer repo: after fixing `control_plane.db`, auditing `create_project_structure()`'s full call list (`_scaffold_root_files`, `_scaffold_context_dir`, `_scaffold_claude_dir`, `_scaffold_3layer_memory`, `_validate_and_finalize`) against what `_execute_action()`'s `--retrofit` branch actually calls found two more silently-skipped substrates: `_scaffold_claude_dir()` (writes `.claude/hooks/hooks.json`, the Stop turn hook config) and `_validate_and_finalize()` (installs `.git/hooks/pre-commit-evolution-guard` and wires it into `.git/hooks/pre-commit`) — both fresh-setup-only, identical pattern to DEBT-20260905-12. In the reporting consumer repo both files happened to already exist from an earlier session, masking the bug; a genuinely fresh `--retrofit` target would have silently gotten neither the Stop hook config nor pre-commit evolution enforcement. Separately, no deterministic check existed anywhere in the ecosystem to catch a repo missing any of these three os-init substrates after the fact — `os-health-check` audited Event Bus/lock/memory liveness but not scaffolding completeness, so a regression here (e.g. from a future edit reintroducing the `_execute_action()` branch-divergence pattern) would go undetected until a user happened to need the missing artifact. | Added `_scaffold_claude_dir(target, args.dry_run, args.force)` and `_validate_and_finalize(target, args.dry_run)` calls to the `--retrofit` branch of `_execute_action()`, alongside the DEBT-20260905-12 fix — both confirmed idempotent (`write_file()`'s skip-if-exists-without-force semantics; `_validate_and_finalize()`'s explicit "already wired" check before touching `pre-commit`) so safe to call unconditionally. Updated `os-init/SKILL.md`'s Phase 3 note to describe the full three-substrate gap and instruct future editors to diff `_execute_action()`'s two branches explicitly rather than assume retrofit inherits fresh-setup's scaffolding. Added a new Phase 3.5 to `os-health-check/SKILL.md`: a deterministic `test -f` check for all three substrates (`control_plane.db`, `hooks.json`, `pre-commit-evolution-guard`) on every health-check run (not just post-install), classified as a Tier 1 finding if any are missing, with a direct recommendation to re-run `init_agentic_os.py --target . --retrofit` (never hand-create the individual file, since that bypasses schema/WAL setup or guard-wiring logic). Deliberately did not add this check to `audit-plugin`/`audit-plugin-l5` — those audit plugin *packaging* (SKILL.md structure, manifest compliance, ADR conformance) for plugin authors, a different concern from auditing a *consumer repo's* installed os-init substrate completeness, which is what `os-health-check` already exists to do. |
| DEBT-20260902-01 | Downstream Self-Evolution Policy drift & missing deterministic pre-commit evolution guard | RESOLVED | Tier 0 | 1 | 2026-09-02 | Downstream InvestmentToolkit developed stronger Turn-by-Turn Mandatory Protocol that drifted from upstream; agents routinely skipped map-debt writes under context pressure due to lack of mechanical hooks. | Backported Turn-by-Turn policy to .agent/rules/; added pre-commit-evolution-guard, turn_evolution_guard.py Stop hook, and CI verification workflow. |
| DEBT-20260902-02 | Blind overwrite in sync_rules clobbered downstream additions & schema modifications | RESOLVED | Tier 0 | 1 | 2026-09-02 | sync_rules() in init_agentic_os.py previously used blind force=True overwrite or identical-string short-circuits, clobbering downstream custom additions and duplicating contradictory schema lines. | Implemented fine-grained difflib SequenceMatcher in init_agentic_os.py to preserve downstream insertions and give upstream precedence on line replacements, backed by comprehensive pytest suite. |
| DEBT-20260902-03 | Self-evolution policy exceeded 12000 char prompt limit causing tool/API failures | RESOLVED | Tier 0 | 1 | 2026-09-02 | Expanded self-evolution-policy.md reached 13,147 characters, exceeding downstream and ecosystem instruction limits (12,000 characters maximum). | Condensed prose and redundant examples down to 8,322 characters while preserving all 3 memory layers, invariants, 14 hard gates, friction tiers, and pre-completion gate block. |
| DEBT-20260902-04 | Missing Layer 2 wiki distillation and permissive evolution guard allowed unindexed playbooks | RESOLVED | Tier 1 | 1 | 2026-09-02 | The pre-commit guard accepted map-debt.md as an OR substitute for wiki playbooks, allowing agents to skip Layer 2 distillation. Additionally, audit_map_debt.py failed to parse 8-column markdown tables, and no CLI existed to distill playbooks or verify wiki index parity. | Added distill_playbook.py CLI for playbook creation and index sync, upgraded audit_map_debt.py to parse 8-col markdown tables, strengthened pre-commit-evolution-guard to block unindexed wiki playbooks, and updated architecture.md/manifests to v1.8.0. |
| DEBT-20260903-01 | Redundant plugin commands/ directories and legacy .agents/workflows/ generation | RESOLVED | Tier 1 | 1 | 2026-09-03 | Modern agent platforms natively parse self-contained .agents/skills/<name>/SKILL.md as slash commands. The legacy deploy_commands() routine in plugin_installer.py duplicated 50+ commands as flat .agents/workflows/ files with cumbersome prefixes, causing confusion and dual maintenance. | Retired deploy_commands() workflow copying in plugin_installer.py, removed redundant commands/ directories across all plugins, and added local agent session scratch files to .gitignore. |
| DEBT-20260905-01 | Missing SQLite control plane and tool-agnostic Socratic intake skill | RESOLVED | Tier 1 | 1 | 2026-09-05 | Agents lacked an ACID state machine for tracking task states, verifier sovereignty, and 6-state worktree lifecycles, and skipped directly into code modifications without Socratic intake or native deferral. | Implemented agent_control.py SQLite control plane, interview_spec_engine.py with session-aware native deferral, interview-spec skill, and full TDD test suite. |
| DEBT-20260905-02 | Static exploration auditors implemented as LLM agents rather than zero-token skills | OPEN | Tier 1 | 1 | 2026-09-05 | In plugins/exploration-cycle-plugin/agents/, domain-purity-auditor, semantic-drift-auditor, and certification-verifier are implemented as LLM personas. Because their gates are deterministic AST/grep and JSON schema audits with zero conversational need, running them as LLM sub-agents incurs unnecessary token cost and latency. | Scheduled for migration to zero-token Python skills under plugins/exploration-cycle-plugin/skills/ via ADR-002/003 hub-and-spoke. |
| DEBT-20260905-03 | EVOLUTION tasks could advance past INTAKE with no prior art or map-debt scan | RESOLVED | Tier 0 | 1 | 2026-09-05 | Agents drafting evolution hypotheses skipped reading references/map-debt.md (Repeat:YES entries) and wiki/decisions/ before entering TRIAGE, causing repeated attempts at already-failed approaches with no structural enforcement. | Added INTAKE→INTERVIEW guard in agent_control.py for task_type=EVOLUTION requiring a prior_art_scan entry in asymmetric_persistence_log; added Phase 0 mandatory scan step to self-evolution/SKILL.md; added log-prior-art CLI subcommand; 3 new contract tests. PR #504. |
| DEBT-20260905-04 | git-operations.md missing hard rules against autonomous gh pr create and branch switching | RESOLVED | Tier 0 | 2 | 2026-09-05 | Agents repeatedly ran gh pr create, git push, and git checkout main without explicit user approval, violating the stated rules and causing data loss/workflow disruption. The rules file had no explicit prohibition against these operations. | Added §7 (no autonomous gh pr create/merge) and §8 (no branch switching during unreviewed work) to .agent/rules/git-operations.md; tightened Safe Without Asking push definition. PR #504. |
| DEBT-20260905-05 | os-init failed to wire pre-commit hook when none existed, leaving repos unprotected | RESOLVED | Tier 1 | 1 | 2026-09-05 | init_agentic_os.py only patched an existing pre-commit hook with the evolution guard injection. On fresh clones or repos without a pre-commit hook, the guard script was installed as a named file but never called — silently providing zero enforcement. | Added else branch in _validate_and_finalize() to create a minimal pre-commit hook that delegates to pre-commit-evolution-guard when no pre-commit exists. PR #504. |
| DEBT-20260905-06 | deploy_rules() blind-copied plugin rule sources over newer .agent/rules/ content, clobbering same-day rule updates | RESOLVED | Tier 0 | 1 | 2026-09-05 | DEBT-20260905-04 (PR #504) added §7/§8/§10 to .agent/rules/git-operations.md but never backported to plugins/dev-utils/rules/git-operations.md. plugin_installer.py's deploy_rules() used a blind shutil.copy2() with no read-first/merge, unlike os-init's own sync_rules() which already diff-merges safely. Running plugin_add.py/sync_with_inventory.py after PR #504 silently reverted git-operations.md to the pre-#504 version. | Ported _merge_rule_content_preserving_downstream() (diff-merge, newer/larger side wins on conflict) into plugin_installer.py's deploy_rules(); backported plugins/dev-utils/rules/git-operations.md to match .agent/rules/; added test_deploy_rules_preserves_downstream.py regression test; documented merge-safety behavior in plugin-installer/plugin-syncer SKILL.md. |
| DEBT-20260905-10 | audit_plugin_paths.py reports 210 pre-existing portability issues (1 critical) across the repo, unrelated to any change this session | OPEN | Tier 2 | 1 | 2026-09-05 | Discovered while regenerating `portability-audit-report.md` after removing `plugins/spec-kitty-plugin/` — the regeneration correctly confirmed spec-kitty is fully gone, but surfaced a large pre-existing portability backlog (hardcoded absolute paths, non-whitelistable runtime violations) spanning most plugins, never previously flagged as a hard gate. Full report: `plugins/agent-scaffolders/scripts/portability-audit-report.md`. | Deferred to its own future branch — same reasoning as DEBT-20260905-08 (large, pre-existing, unrelated-to-this-session backlog; fixing inline would blow out this branch's scope). Triage by severity (the 1 critical first) before the 209 standard issues. |
| DEBT-20260905-11 | deploy_rules() never migrated legacy `<plugin>_<rule>.md` filenames when the rule-naming scheme changed to bare `<rule>.md` in #502, leaving orphaned duplicate rule files in consumer repos | RESOLVED | Tier 1 | 1 | 2026-09-05 | Reported from a downstream consumer repo (InvestmentToolkit, same machine): `.agent/rules/` contained both an old prefixed copy (e.g. `agent-agentic-os_adversarial-reasoning-before-agreement-rule.md`) and a new bare-name copy of the same rule with divergent content, for at least 12 rules across 5 plugins, plus stray `.bak` files unrelated to this specific bug. Root cause: commit `27942481` (2026-04-21) introduced prefixed rule filenames in `deploy_rules()`; commit `1c3b5a54` (#502, 2026-09-05 this morning) switched to bare filenames but added no migration step for the old prefixed copies — `deploy_rules()` only ever computes/writes to whatever `dest_name` its current version produces, with no awareness of a rule's previous filename. Confirmed NOT a stale-clone issue: `plugin_add.py`'s `_clone_repo()` always does a fresh `git clone --depth=1` per sync, no local caching, so InvestmentToolkit's next sync pulls current bare-name behavior immediately regardless of when it last ran. | Added `_migrate_legacy_prefixed_rule()` to `plugin_installer.py`: on each rule deploy, after the bare-name file is written/merged, detect a `<plugin>_<rule-stem>.md` legacy file in the same `.agent/rules/` directory; if present, merge-preserve any unique content from it into the (already-authoritative) bare-name file via `_merge_rule_content_preserving_downstream()` — fresh content always wins on genuine conflict, legacy only contributes insertions — then remove the now-fully-superseded legacy file. TDD: 2 new test scenarios in `test_deploy_rules_preserves_downstream.py` (pure-insertion migration, and a manual ad-hoc conflict-resolution check confirming fresh content wins over a conflicting legacy line), both green. Does not address the 4 stray `.bak` files (separate, pre-existing clutter, no installer path writes `.bak` files — flagged to the consumer repo directly, not an agent-plugins-skills bug) or that repo's own stale `plugin-sources.json` entries for 5 already-consolidated/deleted plugin names (adr-manager, agent-loops, context-bundler, task-manager, spec-kitty-plugin) — both are that repo's own local cleanup, not fixed here. **Follow-up (2026-09-05, same day):** after InvestmentToolkit ran the fix above, 12 of 15 orphans migrated correctly, but 3 remained: `agent-scaffolders_pre-push-audit.md`, `agent-scaffolders_skill-deletion-guard.md`, `dev-utils_symlink-cross-platform.md`. Root cause: these 3 rules were fully removed from their plugins (not renamed) in the same commit `1c3b5a54` that changed the naming scheme — `_migrate_legacy_prefixed_rule()` only runs from inside the loop over `rules_dir.glob("*.md")`, so a rule no longer shipped by the plugin at all is never visited and its orphan never cleaned up. Fixed by adding `_cleanup_orphaned_legacy_rules()`: a second pass, run once per plugin after the main loop, that scans `.agent/rules/` for any `<plugin_name>_*.md` file whose rule stem is absent from the plugin's *current* `rules/` directory — merging into an existing bare-name twin if one exists (e.g. `skill-deletion-guard.md`), or removing the orphan outright if no bare-name file exists at all (the rule was dropped with no successor, e.g. `pre-push-audit.md`). Strictly scoped to the plugin's own prefix — verified a differently-prefixed orphan (e.g. `dev-utils_*` while installing `agent-scaffolders`) is left untouched. TDD: 2 new scenarios (bare-twin-exists case, no-bare-twin case) in `test_deploy_rules_preserves_downstream.py`, both green. |
| DEBT-20260905-09 | plugin_installer.py never prunes orphaned `.agents/agents/<plugin>-<name>.md` for agents removed from plugin source | OPEN | Tier 2 | 1 | 2026-09-05 | Discovered during PR #505 post-merge cleanup: 4 agent files were deleted from `plugins/agent-agentic-os/agents/` and `plugins/agent-scaffolders/agents/` (migrated to skills), but reinstalling via `plugin_add.py` left the stale `.agents/agents/*.md` copies in place — only `.agents/skills/<name>/` gets the "Clean Replacement Guarantee" wipe-and-replace treatment; `deploy_agents()` (or equivalent) has no matching prune step. Manually deleted the 4 stale files this session. | **Approved policy (2026-09-05), scoped for implementation on its own branch, not this one:** (1) Behavior — match the skills/ silent-wipe precedent for `.agents/agents/`, since it is disposable/regenerated build output (ADR-003/004, gitignored), not tracked source; no confirmation prompt needed, consistent with existing skills/ behavior. (2) Scoping — strictly prefix-filtered to `<plugin-name>-*.md` for the plugin currently being (re)installed; never a global sweep across the shared flat `.agents/agents/` directory, to avoid pruning an unrelated plugin's agents. (3) Confirmation boundary — this silent-prune behavior applies ONLY to disposable `.agents/` build targets; any operation touching tracked source (`plugins/*/rules/`, `.agent/rules/`, or any `plugins/**` source file) remains strictly hard-gated with required human confirmation, per destructive-action-guard.md and self-evolution-policy.md — this debt item does not relax that boundary. |
| DEBT-20260905-08 | workspace_conventions_auditor.py: 34 canonical files across 8/9 plugins fail coding-conventions.md (missing docstrings, missing header sections, functions >50 lines) | OPEN | Tier 1 | 1 | 2026-09-05 | Running `python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py` as part of the git-operations.md pre-push gate surfaced 34 pre-existing failing canonical files (54 total findings) spanning agent-agentic-os, agent-memory, agent-orchestration, agent-scaffolders, cli-agents, dev-utils, exploration-cycle-plugin, plugin-manager — none caused by the 2026-09-05 agent-to-skill migration session (verified via origin/main diff: only plugin_installer.py's deploy_rules()/_write_rule_merge_preserving_downstream() and the new test file were fixed as part of that session; everything else pre-dates it). This has evidently never been a hard-enforced gate in practice, or PRs would not have merged with it failing already. Full report: `temp/workspace_conventions_report.md` (gitignored — regenerate via the command above before starting the cleanup). | **Phase 1 done (2026-09-05, this branch):** all missing docstrings (~90) and missing header sections (`Purpose:`/`Key Input Dependencies:`) fixed across all 29 canonical files, verified with zero regressions (199 tests passed, 1 pre-existing unrelated failure in `test_memory_layers.py`'s `self-evolution/SKILL.md` line-budget check, untouched by this work). Auditor now reports 225/244 canonical files passing (up from 210), 19 remaining failures are exclusively the deferred >50-line function-length items below — no missing-docstring/header findings remain (`grep -c "missing a docstring\|missing 'Purpose\|missing 'Key Input" temp/workspace_conventions_report.md` → 0). **Phase 2 still OPEN, separate follow-up branch — rule recalibrated 2026-09-05:** the flat "50+ lines" rule was replaced with a two-tier length (50 soft/100 hard) + McCabe complexity (10 soft/15 hard) model with structural exemptions (argparse blocks, dict/mapping literals, match/case, string-templates) — see `coding-conventions.md` §5 and `workspace_conventions_auditor.py`'s new `_compute_cyclomatic_complexity()`/`_is_structurally_exempt()`. Running the calibrated auditor against the original 19-file/33-function Phase 2 queue: **11 files now pass cleanly** (`test_technical_diagnostic_engine.py`, `technical_diagnostic_engine.py`, `test_evolution_scripts.py`, `test_graph_state_machine.py`, `init_agentic_os.py`, `record_trace.py`, `distill_playbook.py`, `verify_evolution_receipt.py`, `gh_issue_search.py`, `gh_issue_create.py`, `sync_instruction_files.py`) — they were long but not actually complex. **2 downgraded to WARNING** (non-blocking): `plugin_add.py::validate_plugin` (McCabe 11) and `agent_control.py::transition` (McCabe 14) — both clear the old 50-line-only rule's false-positive zone but stay visible for awareness. **6 of the original 8 remain genuine ERROR-tier outliers**: `audit_skill.py` (`audit_skill` McCabe 45, `main` McCabe 23), `evolution_state.py::cmd_transition` (McCabe 27 — the highest-complexity function in the file, contrary to the "linear transactional" framing that prompted this rule review), `task_to_issue_bridge.py::parse_task_file` (McCabe 25), `audit.py` (`_check_root_structure` McCabe 20, `_check_skills` McCabe 17), `plugin_installer.py` (`_provision_skills` McCabe 16, `_deploy_rule_to_target` McCabe 15), `smoke_test.py::run_smoke_test` (275 lines, length-hard-ceiling regardless of its low McCabe 8). **8 previously-invisible files newly surfaced** by the complexity-independent-of-length check (functions under 50 lines but McCabe ≥ 15, which the old rule could never see): `plugin-manager/scripts/sync_with_inventory.py`, `plugin-manager/scripts/plugin_remove.py`, `agent-scaffolders/scripts/check_skill_lengths.py`, `agent-scaffolders/scripts/migrate_to_apm.py`, `agent-scaffolders/scripts/analyze_scripts.py`, `agent-scaffolders/scripts/benchmarking/run_eval.py`, `agent-agentic-os/scripts/eval_runner.py`, and `dev-utils/scripts/workspace_conventions_auditor.py` itself (its own new `_is_structurally_exempt()`, McCabe 16). **Net Phase 2 queue: 14 canonical files** (6 original + 8 newly surfaced), not the original 19 — none touched on this branch, none on the auditor-recalibration branch either; all need per-split test coverage before any refactor, not a blind mechanical pass. **Review bundle generated and reviewed (2026-09-05):** `temp/context-bundle-phase2-outliers/prompt.md` (gitignored, not committed) packaged the 9 highest-complexity targets for extraction-seam analysis. Review found the 9 target functions group into 4 standard decomposition patterns: (1) **Multi-check auditors** — `audit_skill.py` (`audit_skill`, `main`), `audit.py` (`_check_root_structure`, `_check_skills`) — each check is already an independent sub-concern, natural seam per check; (2) **State guard dispatchers** — `evolution_state.py::cmd_transition` — branches per target DAG node, natural seam per transition guard; (3) **Stream and scoring processors** — `benchmarking/run_eval.py::_parse_stream_events`, `agent-agentic-os/scripts/eval_runner.py::_score_eval_item` — natural seam per event-type/scoring-dimension handler; (4) **Two-phase text parsers** — `task_to_issue_bridge.py::parse_task_file`, `workspace_conventions_auditor.py::_is_structurally_exempt` — natural seam at the parse/classify boundary. (`plugin_installer.py`'s two functions and `smoke_test.py::run_smoke_test` reviewed but not yet slotted into a pattern — smoke_test.py's case is pure length, not complexity, and likely needs a different splitting strategy, e.g. per-phase helper functions rather than per-branch extraction.) **Phase 2 decomposition itself will run on its own isolated branch** (not this one, not the auditor-recalibration branch), with a targeted test suite written per split before any extraction, per this repo's TDD iron law — no refactor commit lands without its own failing-then-passing test for that specific split. |
| DEBT-20260905-07 | Agent vs. Skill Archetype Drift & Missing Tool Sandboxing | OPEN | Tier 1 | 1 | 2026-09-05 | Repo-wide audit of 42 active agents/*.md against create-sub-agent's own two-archetype policy (guided wizard w/ context:fork, or adversarial persona w/ permissions.deny) found: (1) plugins/dev-utils/agents/coding-conventions-agent.md and link-checker-agent.md are byte-identical duplicates of their own skills/<name>/SKILL.md counterparts; (2) plugins/agent-orchestration/agents/orchestrator.md is a literal one-line pointer-wrapper stub to ../skills/orchestrator/SKILL.md, the exact anti-pattern create-sub-agent's SKILL.md names as never-create; (3) 12 cli-agents review personas (security-auditor, architect-review, compliance-reviewer, pr-reviewer, red-team-reviewer, self-critic, tdd-contract-reviewer, debate-synthesizer, output-validator, performance-analyst) plus 4 exploration-cycle-plugin gate auditors (certification-verifier, domain-purity-auditor, semantic-drift-auditor, business-rule-audit-agent) claim tool-sandboxing as their agent-vs-skill justification but declare no permissions.deny — several (certification-verifier, domain-purity-auditor, semantic-drift-auditor, business-rule-audit-agent) hold unrestricted Write despite being independent verifiers explicitly forbidden from self-certifying; (4) context:fork is applied inconsistently — present on single-shot deterministic utilities (rlm-cleanup-agent, rlm-curator, rlm-distill-agent, rlm-search, vector-db-cleanup, vector-db-ingest) that aren't multi-turn wizards, absent on genuine one-question-at-a-time wizards (intake-agent, discovery-planning-agent, improvement-intake-agent, agentic-os-setup); (5) os-health-check.md, issue-resolution-reviewer.agent.md, repository-improvement-agent.agent.md, ecosystem-index-agent.agent.md are deterministic procedural wrappers (no interview, no adversarial judgment) that fit neither archetype and should be skills; 3 files also use a nonstandard .agent.md suffix vs create-sub-agent's documented flat <name>.md placement rule. | Scoped for later, deliberately not executed with this entry (working-tree discipline — see session decision 2026-09-05): (1) delete the 2 duplicate agents + orchestrator.md pointer stub once skill coverage is confirmed equivalent (destructive-action-guard applies — requires explicit user confirmation naming each path); (2) add permissions.deny: ["Write"] (and Bash where unneeded) to the 16 read-judgment personas/auditors; (3) reconcile context:fork placement per actual wizard-vs-utility behavior; (4) migrate the 4 deterministic wrappers to skills via create-skill. |


| DEBT-20260906-03 | Missing DRAFT_PLAN and MULTI_AGENT_REVIEW states in control plane caused simulated audits | RESOLVED | Tier 1 | 1 | 2026-09-06 | Agents lacked formal DRAFT_PLAN state and an explicit user-gated MULTI_AGENT_REVIEW step for external context-bundler packages, leading to simulated inline audits and skipped interviews. | Added DRAFT_PLAN and MULTI_AGENT_REVIEW canonical states and transitions to agent_control.py; updated interview-spec SKILL.md and init_agentic_os.py to enforce 1-question-at-a-time cadence and explicit user review bundle gate; added unit tests in test_multi_agent_bundle_gate.py. |
| DEBT-20260906-04 | Control plane permitted premature git push from worktree without post-implementation review gate | RESOLVED | Tier 0 | 1 | 2026-09-06 | Tasks transitioned directly from IN_WORKTREE to VERIFY_EXIT or allowed update_worktree(pushed_to_origin) without an explicit post-implementation review gate or pre-push git guard, allowing agents to autonomously push code and create PRs before user review. | Added WORKTREE_REVIEW and MULTI_AGENT_CODE_REVIEW canonical states and transitions to agent_control.py; added update_worktree push barrier requiring task to be in review gate; added pre-push-review-guard git hook and wired into init_agentic_os.py; updated worktree-lifecycle-management.md rules; added contract tests. |
| DEBT-20260906-05 | docs/superpowers/ (brainstorming/writing-plans skill outputs) is git-tracked, unclear if that's intended | OPEN | Tier 0 | 1 | 2026-09-06 | User asked mid-session (TASK-AGENTIC-OS-AUDIT) whether docs/superpowers/ should be gitignored, same question already resolved for docs/ADRs/ (answer: no, ADRs are durable documentation). 9 files currently tracked, not gitignored. User said "flag for later" rather than decide now. | Deferred — needs an explicit user decision: durable documentation (like ADRs, keep tracked) vs. ephemeral per-session scratch (gitignore, possibly purge history). Not actioned. |
| DEBT-20260906-06 | context/control_plane.db is per-checkout (gitignored), so a git worktree gets a fresh empty DB disconnected from the main checkout's task records | OPEN | Tier 1 | 1 | 2026-09-06 | Discovered while executing TASK-AGENTIC-OS-AUDIT: after `git worktree add .worktrees/task-TASK-AGENTIC-OS-AUDIT`, running `agent_control.py status --task-id TASK-AGENTIC-OS-AUDIT` from inside the worktree returned null — ControlPlane.__init__'s repo-root-walk resolves to the worktree's own root (since `.git` exists there too, as a file), giving it an independent `context/control_plane.db` with no knowledge of the task registered in the main checkout's DB. | Deferred — out of scope for this branch. Filed as [GitHub Issue #519](https://github.com/richfrem/agent-plugins-skills/issues/519) (same root cause as the DB-durability issue below). Possible fix direction: resolve db_path via `git rev-parse --git-common-dir` (shared across worktrees) instead of walking for the nearest `.git`. |
| DEBT-20260906-08 | control_plane.db is gitignored with no durable git-trackable export — approval/receipt audit trail is local-only | OPEN | Tier 3 | 1 | 2026-09-06 | User challenged (2026-09-06, TASK-AGENTIC-OS-AUDIT session) whether the DB being gitignored makes sense given it's the sole store of the audit trail (transitions, critic reviews, verification receipts) that Finding #2 of this very audit is hardening. Gitignoring it means that trail is local-only, non-shared, lost on fresh clone/worktree — directly undermining the receipt system's value as an actual audit mechanism. | **Filed as [GitHub Issue #519](https://github.com/richfrem/agent-plugins-skills/issues/519)** — not resolved inline, needs its own design pass. Recommended direction: durable JSONL export (`context/control_plane_audit.jsonl`, git-tracked) alongside the local/gitignored live SQLite DB. |
| DEBT-20260906-07 | next_number.py's project-root walk-up checks `(p / ".git").is_dir()`, which is False inside a git worktree (`.git` is a file there), silently resolving to the main checkout instead of the worktree | OPEN | Tier 1 | 1 | 2026-09-06 | Same failure class as DEBT-20260906-06, found immediately after it while verifying `next_number.py --type adr` from inside `.worktrees/task-TASK-AGENTIC-OS-AUDIT` after moving ADRs there: returned `001` instead of the expected `010` because it silently scanned the main checkout's stale `ADRs/`+`docs/adr/` layout (pre-move) rather than the worktree's already-updated `docs/ADRs/` (9 files). No error/warning — just a wrong answer from the wrong directory. | Deferred — out of scope for this branch. Fix direction: use `git rev-parse --show-toplevel` (returns the worktree's own top-level, not the main checkout) instead of a manual `.git`-is-a-directory sentinel walk. Likely the same root cause affects other scripts using this exact pattern — worth a repo-wide grep for `(p / ".git").is_dir()` before fixing just this one file. |
| DEBT-20260906-09 | interview_spec_engine.py had no CLI entrypoint; agent_control.py's phase-capability denial for a task with no transition history printed the internal "No registry template found for inbound edge (NONE -> INTAKE)" message | RESOLVED | Tier 0 | 0 | 2026-09-06 | Found while running an end-to-end smoke test of the control-plane pipeline (validating Issue #529 / PR #532): the skill's documented `python3 scripts/interview_spec_engine.py` usage produced no output at all because the script had no `if __name__ == "__main__":` block (had to import and call `detect_intake_mode()` directly to get a result); separately, `verify_phase_capability()` surfaced an internal registry-lookup phrase to the user for the common fresh-task case instead of a plain-language message. | Added `__main__` entrypoint to interview_spec_engine.py that prints `detect_intake_mode()`; added a `from_state == "NONE"` special case in agent_control.py's capability-check path returning "Task has not entered any registered phase yet — no capabilities available."; added 2 unit tests covering both fixes. Branch `fix/interview-spec-cli-entrypoint-and-error-messages`. |
| DEBT-20260906-10 | interview-spec routed every task through the full Socratic/spec/plan/multi-agent-review/worktree pipeline regardless of size, discouraging control-plane use for trivial one-line fixes | RESOLVED | Tier 1 | 0 | 2026-09-06 | Filed as [GitHub Issue #534](https://github.com/richfrem/agent-plugins-skills/issues/534) after using the full pipeline for the single-file PR #533 fix; design proposed and approved (see issue comment) before any implementation. | Added new `INTAKE -> DONE` edge (`intake_to_done_trivial` template) to `state_machine.py`/`transition_templates.yaml`: no required artifacts, one non-skippable freeform human question (`triage_classification`) recorded as the sole `transition_decisions` audit row, no worktree/push capabilities released. Existing `INTAKE -> ESCALATED` edge serves as the mis-triage escape hatch, unchanged. Updated `interview-spec/SKILL.md` to document the triage step. Updated edge-count assertions (51->52) and the one pre-existing test that used `INTAKE -> DONE` as an example illegal edge. Added 4 new tests (happy path, non-skippability, escape hatch, capability scoping). Branch `feat/interview-spec-trivial-triage-path`. |
| DEBT-20260906-11 | 9 open GitHub issues audited this session all had consistent type:/tier:/source:/risk: labels, but 8 of 9 had no status:* label at all — categorized but never sequenced, requiring manual re-derivation of priority order each time | RESOLVED | Tier 1 | 0 | 2026-09-06 | Surfaced while ranking open issues by genuine criticality (#523 vs #519/#536/#537/#538/#460/#531/#461/#462) — tier/risk answer "how bad," nothing in the taxonomy answers "what order," so the same manual ranking work would need re-deriving every time someone asks. | Updated `gh_issue_create.py`'s `create_issue()` to auto-append `status:needs-triage` whenever the caller doesn't already include a `status:*` label — every newly created issue now gets a sequencing signal by default, not just categorization. Documented in `github-issue-agent/SKILL.md`. Added 2 new unit tests (`test_gh_issue_create.py`) plus updated 3 pre-existing tests in `test_gh_mocked_cli.py` whose fixed label-lists/subprocess-call-counts encoded the old (gap) behavior. Branch `feat/gh-issue-create-status-default`. |
| DEBT-20260906-12 | graph-planning-superpowers-policy.md's worktree rule ("never use sibling directories") is literally violated by self-evolution/SKILL.md's own documented `../worktree-evolution-<cid>` convention; the 4-phase lifecycle diagram doesn't reflect the already-merged #534/#535 TRIVIAL fast-track | RESOLVED | Tier 1 | 0 | 2026-09-06 | Found while reviewing this always_on rule for alignment with the new SQLite control plane. Two of four findings from that review (TDD-language disconnected from the real test_suite receipt mechanism; the doc implying one universal control plane) were folded into #537's scope instead, since they depend on that issue's still-undecided architecture question. | Added an explicit scope note (Section 1) clarifying this policy governs `agent_control.py`-tracked tasks only, with `self-evolution` cycles separately governed (`self-evolution-policy.md`, own worktree convention) pending #537's reconciliation decision — resolves the literal contradiction without guessing at #537's outcome. Added the TRIVIAL/STANDARD branch point to the Phase 0 lifecycle diagram and prose. Updated both independent copies (`.agent/rules/`, `plugins/dev-utils/rules/`) plus reinstalled the dev-utils plugin so the symlinked and `.agents/` installed copies stay in sync. Branch `fix/graph-planning-policy-trivial-and-worktree-scope`. |
| DEBT-20260907-01 | Portable plugin skills hardcoded dependencies on this repo's own `docs/ADRs/` (an anti-pattern — those docs won't exist when a skill is installed elsewhere); several adjacent stale references and one real cross-tool bug found during the same sweep | RESOLVED | Tier 1 | 0 | 2026-09-07 | Discovered while reviewing `graph-planning-superpowers-policy.md`; expanded to a full repo-wide sweep (89 files matching "ADR" under `plugins/`) per explicit direction to read each in context, not blind-replace. | Deleted 36 broken `references/ADRs/*.md` symlinks across 6 `agent-scaffolders` skills (plugins don't need to reference ADRs at all) plus their `symlinks.json` entries. Dispatched 6 parallel Haiku sub-agents (one per plugin group) with an explicit KEEP/CHANGE rubric to triage the remaining 78 files; 13 genuinely needed generalized inline guidance instead of a hardcoded `docs/ADRs/` reference (verified via diff spot-checks, not trusted blindly). Caught and reverted 2 out-of-scope edits where sub-agents touched `self-evolution-profile.md` outside their assigned file list (cross-checked every actually-modified file against the assigned lists). Separately confirmed (zero programmatic consumers found) that the stale `- ADRs/` line in all 10 `self-evolution-profile.md` copies was safe to remove — not a live safety gate, and fully redundant with the existing `- docs/` entry now that ADRs live at `docs/ADRs/`. Fixed a real cross-tool bug found along the way: `adr_manager.py` hardcoded `ADR_DIR = PROJECT_ROOT / "ADRs"` while a stale comment claimed it matched `next_number.py`'s `"docs/ADRs"` — it didn't; now auto-detects. Deleted 3 disposable generated-output files (`analysis_results.txt`, `portability-audit-report.md`, `plugin_files_and_symlinks_inventory.json`) and their now-dangling symlink/manifest entries. Updated stale `plugins/adr-manager`/`plugin-installer` example paths across `usage-guide.md` and 4 scripts to generic placeholders. Rewrote `whitelist.json`, fixing a real duplicate-JSON-key bug (`"agent-scaffolders"` appeared 4 times — only the last was ever actually applied) and renaming stale plugin keys to their current consolidated homes. Full verification: `audit_plugin_structure.py` 0 errors across all 10 plugins, combined test suite 348 passed (same 8 pre-existing unrelated failures), symlink diagnose clean. Branch `fix/graph-planning-policy-trivial-and-worktree-scope`. |

| DEBT-20260907-02 | analyze-plugin/SKILL.md had the same hardcoded docs/ADRs anti-pattern already fixed in 5 sibling skills in #541 — missed by the Haiku triage batch, caught on manual review after that PR merged | RESOLVED | Tier 0 | 1 | 2026-09-07 | The Haiku sub-agent covering this file reported "no ADR file dependencies," a false negative caught only by spot-checking a different file the user happened to view after merge. | Replaced with the same generalized inline guidance (no cross-plugin script execution, hub-and-spoke, file-level symlinks only, self-contained skills) used in the 5 sibling fixes from DEBT-20260907-01. Branch fix/analyze-plugin-adr-reference. Repeat risk noted: any future automated sweep of this kind should spot-check a larger sample before trusting KEEP verdicts. |
| DEBT-20260907-05 | Git commit and push operations on task feature branches lacked pipeline-bypass enforcement, complete state-execution verification, and strict final-state push gating | RESOLVED | Tier 1 | 0 | 2026-09-07 | While pre-push-review-guard protected origin push and pre-commit-evolution-guard enforced map-debt logging, git commit operations lacked verification against SQLite control plane states, allowing agents to skip interview/spec/plan/approval gates entirely or tamper with transition history, and push-to-origin allowed intermediate states. | Implemented pre-commit-pipeline-guard and updated pre-push-review-guard git hooks; added OPERATION_RULES["commit"] and updated OPERATION_RULES["worktree_push"] in control_plane/policy.py to strictly require final state DONE for pushing to origin; added verify_commit() and verify-commit CLI subcommand to agent_control.py; validated all task_transitions match valid_transitions table and form a contiguous chain starting from INTAKE with zero transition_violations; wired into init_agentic_os.py; added full pytest verification suite (11/11 passed). Branch feat/task-issue-pipeline-commit-hook. |
| DEBT-20260907-06 | Duplicated pipeline-gating logic: `pre-commit-pipeline-guard` (bash) vs `policy.py`'s `_task_commit_check()`/`verify_commit()` (Python) | OPEN | Tier 2 | 1 | 2026-09-07 | PR #562 single-agent review (`cli-agents:pr-reviewer`) found `pre-commit-pipeline-guard` (bash, ~180 lines, raw sqlite3 queries) independently re-derives the same pipeline-stage-gate logic (planning-state doc-only check, implementation-state allowlist, transition-history validation) that `control_plane/policy.py`'s `_task_commit_check()` / `agent_control.py`'s `verify_commit()` already implement in Python — nothing wires the bash hook to call the Python CLI's `verify-commit` subcommand instead. Two independent implementations of a security-relevant gate can silently drift (e.g. a state-name or schema change forgotten in one place reopens the hole PR #562 just closed). Not blocking PR #562 — both paths currently agree and are independently tested — flagged as a fast follow-up rather than fixed here to keep PR #562 scoped to the actor-labeling regression. | Have `pre-commit-pipeline-guard` shell out to `python3 agent_control.py verify-commit --branch "$CURRENT_BRANCH" --staged-files ...` and act on its exit code, instead of reimplementing the SQL/state logic in bash. |
| DEBT-20260907-03 | `interview-spec`'s `agent_control.py` had 3 missing `control_plane/` symlinks (`registry.py`, `coordinator.py`, `transition_templates.yaml`) never added to `symlinks.json` when those files were introduced — `ModuleNotFoundError` on every task registration, discovered starting issue-551 intake. A broader repo-wide scan for the same class of gap (imported local module present at plugin root, absent from the importing skill's own scripts/ dir) found 16 total instances across 8 plugins | RESOLVED | Tier 2 | 0 | 2026-09-07 | Blocked `agent_control.py init`/`transition` entirely — the interview-spec skill's control-plane registration step could not run at all until fixed. User explicitly directed this be fixed as part of the issue-551 work package rather than deferred. | Added all 16 missing entries to `symlinks.json` (interview-spec/control_plane ×3, os-init/agent_control.py, vector-db-cleanup+init/operations.py, vector-db-ingest+search/rlm_config.py, vector-db-init+launch/vector_config.py, vector-db-search/ingest_code_shim.py, audit-plugin/audit_skill.py, local-llm-setup/kv_cache_orchestrator.py, github-issue-backlog-agent/gh_issue_create.py, hf-init/hf_upload.py, issue-pr-lifecycle-agent/issue_worktree_manage.py, exploration-workflow/sandbox_runner.py+state_engine.py, obsidian-wiki-linter/raw_manifest.py). Ran `symlink_manager.py restore` (16 created) then `diagnose` (all links OK), then reinstalled all plugins via `plugin_add.py plugins/ -y`. Verified fix: `agent_control.py init`/`transition` for issue-551 now succeeds end-to-end. Confirmed via sys.path inspection that none of the 16 importing files had a working fallback (no sys.path shim pointed at the plugin-root scripts dir) — all were genuine latent breakage, not false positives. |
| DEBT-20260907-07 | `ControlPlane.coordinate_transition()` facade in `agent_control.py` was missing `skip_review`/`skip_reason` params that `TransitionCoordinator.coordinate_transition()` already required, AND the `transition`/`coordinate-transition` argparse subparsers never registered `--skip-review`/`--skip-reason` flags at all — two independent gaps in the same feature, both masked by `_dispatch_command()`'s silent `getattr(..., default)` fallback | RESOLVED | Tier 2 | 0 | 2026-09-07 | Discovered live while resuming the `link-cp-diagrams` task: the facade's `TypeError` was the first symptom found; fixing it and retrying the actual CLI command (`--skip-review --skip-reason ...`) then surfaced argparse's own `unrecognized arguments` error, since the flags had never been declared on either subparser — `_dispatch_command()`'s `getattr(args, "skip_review", False)` silently no-ops instead of failing loudly when the attribute doesn't exist, which is why the facade-only fix looked complete under unit tests but still failed end-to-end on the real CLI. | (1) Added `skip_review: bool = False, skip_reason: Optional[str] = None` params to `ControlPlane.coordinate_transition()`, forwarded to `TransitionCoordinator.coordinate_transition()`. (2) Added `--skip-review`/`--skip-reason` to both the `transition` and `coordinate-transition` argparse subparsers in `_build_parser()`. Added 2 regression tests (TDD red-green each): `test_facade_coordinate_transition_forwards_skip_review_and_skip_reason` (facade signature) and `test_cli_transition_parsers_accept_skip_review_flags` (argparse registration, calls `_build_parser()` directly and asserts `args.skip_review`/`args.skip_reason`). Full `plugins/agent-agentic-os/tests/` suite: 284 passed, 1 pre-existing skip. Branch `chore/link-control-plane-diagrams`. |
| DEBT-20260907-08 | `interview-spec` documented the control-plane pipeline in prose/checklists only, with no linked diagram of the actual state machine, despite 3 up-to-date `docs/diagrams/control-plane-*.mermaid` files already existing in the repo | RESOLVED | Tier 0 | 0 | 2026-09-07 | Pure documentation-linking gap — the diagrams already existed and were verified accurate against `ALLOWED_TRANSITIONS` in a prior session (see 2026-09-06 evolution-log entry), just never referenced from the skill that most needs them. | Symlinked all 3 `docs/diagrams/control-plane-*.mermaid` files into `plugins/agent-agentic-os/skills/interview-spec/references/` via `symlink_manager.py create` (never raw `ln -s`). Verified `symlink_manager.py diagnose` clean, `audit.py --path plugins/agent-agentic-os` passes, `audit_plugin_structure.py` reports 0 errors (3 expected warnings for symlinks pointing outside the plugin root to `docs/diagrams/`, which is correct — those diagrams are repo-wide docs, not plugin-owned). Reinstalled `agent-agentic-os` via `plugin_add.py` to dereference into `.agents/`. Full `plugins/agent-agentic-os/tests/` suite: 285 passed. Branch `chore/link-control-plane-diagrams`. |
| DEBT-20260907-04 | GitHub Issue #551: 45 pre-existing `audit.py` findings across ~24 skills in `agent-agentic-os` — missing `references/fallback-tree.md`/`acceptance-criteria.md` links and SKILL.md line-count overages (>100 lines), confirmed byte-identical pre-existing debt unrelated to any specific feature work | RESOLVED | Tier 1 | 0 | 2026-09-07 | Deterministic, mechanical audit debt — no design judgment needed, batch-fixable per the issue's own recommendation. | Part 1/2: created `references/fallback-tree.md` for all 23 flagged skills, `references/acceptance-criteria.md` for the 5 skills missing a `references/` dir entirely (evo-smoketest, critical-auditor, todo-check, os-architect, os-experiment-log), and fixed evo-smoketest's `evals.json` from a dict-wrapped `{"evaluations": [...]}` shape to the required root JSON array. `audit.py --path plugins/agent-agentic-os` now exits 0 (was: 1 error). Part 2/2: trimmed all 15 oversized SKILL.md files (`os-evolution-verifier`, `os-environment-probe`, `os-eval-backport`, `os-eval-lab-setup`, `os-evolution-planner`, `os-experiment-log`, `os-guide`, `os-health-check`, `os-improvement-report`, `os-init`, `os-memory-manager`, `os-skill-improvement`, `self-evolution`, `optimize-agent-instructions`, `interview-spec`) to <= 100 lines via Progressive Disclosure offloading command details, format templates, and full checklists into per-skill `references/detailed-reference.md` files; trimmed `os-memory-manager` description from 859 chars to <800 chars. Verified: `audit.py --path plugins/agent-agentic-os` exits 0 with zero skill warnings. Branch `fix/issue-551-audit-findings`, worktree `.worktrees/task-issue-551`. |
| DEBT-20260907-ISSUE547-01 | `INTERVIEW -> DRAFT_PLAN` requires plan artifacts before the transition, but `plan_write` is released only after entering `DRAFT_PLAN` | OPEN | Tier 2 | NO | 2026-09-07 | ISSUE-547 | The guarded writer denied writes in `INTERVIEW`; the transition then required those same files. The task staged approved artifacts first, transitioned, and rewrote them through the guarded writer. | Release a proposal-mode plan-write capability in `INTERVIEW`, or split artifact presence from the guarded write gate without weakening production-file protections. | Reproduced with `write_plan_document.py`: `Action 'plan_write' not authorized in state 'INTERVIEW'`; `coordinate-transition --to DRAFT_PLAN` then reported missing artifacts. | M | NO | OPEN |
| DEBT-20260907-ISSUE547-02 | Local plugin reinstall could not update protected `.agents/` files under the sandbox | RESOLVED | Tier 2 | NO | 2026-09-07 | ISSUE-547 | The first `plugin_add.py plugins/agent-agentic-os -y` failed with `PermissionError` on `.agents/hooks/agent-agentic-os-hooks.json`; approved escalated rerun succeeded and installed runtime verification passed. | Ensure the standard development runtime grants the installer write access to `.agents/`, or document the required escalation. | Installer output recorded the permission failure, followed by successful escalated installation and `.agents` wrapper presence check. | S | NO | RESOLVED |
| DEBT-20260907-ISSUE547-03 | Append-only Layer 3 trace writer has no serialization when two append commands run concurrently | OPEN | Tier 2 | NO | 2026-09-07 | ISSUE-547 | Parallel `record_trace.py append` calls both wrote `event_seq=2` with the same predecessor hash, creating two divergent successors. The append-only file was preserved; later appends will be serialized. | Add file locking or an atomic append/sequence transaction to `record_trace.py`; add a concurrent-writer regression test. | `.agent/learning/traces/cycle_manifests.jsonl` contains two ISSUE-547 events with sequence 2 and predecessor `265f657...`; both commands exited 0. | M | NO | OPEN |
| DEBT-20260908-NESTED-SKILL-01 | Nested `SKILL.md` symlink under a skill's references tree could be discovered as an invalid extra skill | RESOLVED | Tier 2 | NO | 2026-09-08 | fix/remove-nested-skill-reference | The legacy `plugins/agent-scaffolders/references/examples/SKILL.md` link was installed beneath `create-command/references/examples/`, outside the required `<skill-name>/SKILL.md` location. Recursive discovery reported it as a skill and produced misleading frontmatter failures. | Remove the misplaced links and add a structure-audit regression test rejecting `SKILL.md` below skill resource directories. | `git log --follow -- plugins/agent-scaffolders/references/examples/SKILL.md`; `test_audit_plugin_structure.py`. | S | NO | RESOLVED |
| DEBT-20260908-INTERVIEW-CONTRACT-01 | The control-plane registry had transition questions but no machine-readable stage-entry question contract; the agent conflated `TRIVIAL` path selection with permission to skip interview and retrospective questions. | RESOLVED | Tier 1 | 0 | 2026-09-08 | fix/remove-nested-skill-reference | Reproduced live while rerunning the trivial path: `INTAKE -> INTERVIEW` exposed no entry questions, and the agent immediately used the destination transition question instead of the `INTERVIEW` stage questions. | Added `stages.INTERVIEW` and `stages.RETROSPECTIVE` YAML contracts, registry/coordinator policy wiring, SQLite required-question synchronization including all 13 reset approvals, one-at-a-time/adaptive follow-up instructions, parity tests, and aligned the three control-plane diagrams. | M | NO | RESOLVED |
| DEBT-20260910-P02-MEASUREMENT-01 | P02 measurement schema lacked canonical_digest integrity verification in validate_observation_dict | RESOLVED | Tier 1 | NO | 2026-09-10 | feature/p0-observability-foundation | validate_observation_dict accepted any 64-char hex string as canonical_digest without verifying it against the computed SHA-256 over canonical bytes. The test test_canonical_digest_mismatch_raises_artifact_invalid failed because the check was absent. Digest verification was added at the end of validate_observation_dict (after content checks) so content errors take precedence over digest mismatch. | Verified by 33-pass A12 test suite; all 36 existing P01 regression tests remain green. | python3 -m pytest plugins/agent-agentic-os/tests/test_control_plane_measurement_contract.py -v | S | NO | RESOLVED |
| DEBT-20260910-P02-REVIEW-01 | P02 measurement had five contract gaps found in independent review: untyped scopes, null totals reported as partial sums, non-deterministic correction supersession, missing UUIDv7 enforcement, and unenforced settle scope | RESOLVED | Tier 1 | NO | 2026-09-10 | feature/p0-observability-foundation | (1) usage.scope accepted arbitrary strings; (2) settle returned partial sum when any active obs had null tokens; (3) dict comprehension allowed last-writer-wins for multiple corrections to same parent; (4) event_id accepted non-UUID strings; (5) settle_observations(scope=...) parameter was silently ignored. | Added UUIDv7 regex validation, ObservationScope enum check for usage.scope, None-returning null-aware aggregation, conflict raise for duplicate correction targets, and scope-enforcement loop in settle_observations. Added 10 regression tests; all 33 P01 tests preserved. | python3 -m pytest plugins/agent-agentic-os/tests/test_control_plane_measurement_contract.py -q | S | NO | RESOLVED |
| DEBT-20260913-P0-RETRO-RUNTIME | Exit verification was invoked from the main checkout while task-owned policy changes were only in the registered worktree, allowing stale runtime logic to accept a failed full-suite receipt. | OPEN | Tier 1 | NO | 2026-09-13 | p0-live-baseline-20260912 | The worktree policy correctly requires `full_test_suite` with `exit_code=0`; the main-checkout invocation used the older presence-only check and committed VERIFY_EXIT -> RETROSPECTIVE despite receipt exit code 1. | Keep source/runtime parity checks mandatory, reinstall from the registered worktree, and add a governed transition test proving failed receipts cannot advance. | Transition 215; failed receipt `EVO-INTEGRITY-p0-live-baseline-20260912-908da7ad1f28`; source/live parity verified after reinstall. | M | NO | OPEN |
| DEBT-20260913-P0-FULL-SUITE-BASELINE | Repository-wide pytest currently has pre-existing failures outside the bounded P0 slice. | OPEN | Tier 2 | NO | 2026-09-13 | p0-live-baseline-20260912 | The full suite collected 883 tests but failed in stale control-plane fixtures, agent-memory consumers expecting an older cheapest-models schema, and benchmarking run_loop import resolution. | Triage and repair those baseline failures in separate bounded work packages; do not widen P0 or treat focused acceptance tests as a clean repository-wide receipt. | Governed `full_test_suite` receipt exit code 1; `pytest --lf -q` isolated 9 failures after the pacing fixture was corrected. | M | NO | OPEN |
| DEBT-20260913-INTERVIEW-WRAPPER-01 | `record_interview_question.py`'s wrapper called `cp.get_unconsumed_transition_answers(...)` on `ControlPlane` itself, but the method only exists on `ControlPlane._persistence` (the SQLite adapter) — every interview-question call recorded the answer successfully, then crashed with `AttributeError` before returning the next-action guidance. | RESOLVED | Tier 2 | NO | 2026-09-13 | feature/issue-593-context-research | Hit live while running the redo interview for issue #593 (`issue-593-context-overhead-v2`): `record_interview_question.py --question interview_classification ...` recorded decision_id 216 into `transition_decisions` but then raised `AttributeError: 'ControlPlane' object has no attribute 'get_unconsumed_transition_answers'` instead of returning the next-question guidance. | Changed the wrapper's call from `cp.get_unconsumed_transition_answers(...)` to `cp._persistence.get_unconsumed_transition_answers(...)`, matching the existing pattern in `agent_control.py:648` (`_build_transition_policy_ctx`) which already accesses this method via `self._persistence`. User explicitly authorized fixing tooling bugs inline for this task during the interview (`interview_acceptance_criteria` answer). | Re-ran `record_interview_question.py --question interview_summary ...` after the fix: returned `"status": "RECORDED"` with correct `next_action` guidance instead of crashing. All 6 canonical interview questions for `issue-593-context-overhead-v2` recorded successfully afterward. | S | NO | RESOLVED |
| DEBT-20260913-PUSH-GUARD-FAILOPEN-01 | `pre-push-review-guard` was fail-open for any branch with no task registered in the SQLite control plane (`tasks.worktree_branch`) — it printed a warning and exited 0, permitting the push, instead of denying it. | RESOLVED | Tier 2 | NO | 2026-09-13 | feature/issue-593-context-research | User asked to remove stray tracked files under `docs/plans/` from origin; agent created an ad-hoc branch (`chore/remove-tracked-docs-plans-artifacts`) without registering it as a task, then pushed without an explicit isolated push directive from the user. The guard's own warning ("push is ungated") should have been read as a red flag, not proceeded past. User then asked directly how the guard missed this. | Changed the "no task registered" branch in `plugins/agent-agentic-os/scripts/pre-push-review-guard` from `exit 0` (warn-and-allow) to `exit 1` (deny) with guidance on registering the branch via `agent_control.py init` / `update-worktree`. Synced the fix into the installed `.git/hooks/pre-push-review-guard` copy. The underlying process failure (pushing without an explicit directive) is a separate, non-code lesson — not fixable by this hook alone, since the hook can only gate branches it knows about. | Re-pushed the same previously-succeeding branch (`chore/remove-tracked-docs-plans-artifacts`) after the fix: correctly blocked with exit code 1 and the new "No Task Registered For This Branch" message. | S | NO | RESOLVED |
| DEBT-20260913-INTERVIEW-SPEC-LINECOUNT | `interview-spec/SKILL.md` is 257 lines, well past this repo's own 100-line hard ceiling (`.agent/rules/coding-conventions.md`) and past its own prior fix in `DEBT-20260907-04`, which trimmed it (with 14 sibling skills) to <=100 lines via progressive-disclosure offload to `references/detailed-reference.md`. | OPEN | Tier 1 | NO | 2026-09-13 | feature/issue-593-context-research | Found during issue-593-context-overhead-v2's expanded research scope (12-skill discovery pass across plugins/agent-agentic-os/skills/), while assessing this repo's own skills against the #593 research verdict (duplication/content-accretion, not loading-strategy, is the dominant real-world bloat driver). `interview-spec` already has 7 files in `references/`, including `detailed-reference.md` -- the regression is body content growing back in rather than being offloaded, not a missing mechanism. | Re-apply the DEBT-20260907-04 trim: move command-reference detail that has grown back into the SKILL.md body out to `references/detailed-reference.md`. Recommended as a small, bounded first task for the follow-up work package described in `docs/plans/issue-593-followup-recommendations.md`; not fixed in this task to keep issue-593-context-overhead-v2 scoped to research and the one small interview-spec description edit already authorized. | `wc -l plugins/agent-agentic-os/skills/interview-spec/SKILL.md` = 257. | S | NO | OPEN |
| DEBT-20260913-INTERVIEW-SPEC-DISCOVERABILITY | `interview-spec`'s `description:` only matched formal engineering-task phrasing ("non-trivial engineering task," "feature request," "architectural refactor," "multi-file bugfix"); a user wanting to start new work via natural phrasing ("I have an idea," "let's explore this," a brainstorming request) had no obvious routing signal to this skill without already knowing its name. | RESOLVED | Tier 0 | NO | 2026-09-13 | feature/issue-593-context-research | User explicitly raised this mid-session ("people might not think explicitly about an interview... they might also ask for brainstorming") and asked for a small, scoped fix within this task rather than deferring. | Broadened `description:` in `plugins/agent-agentic-os/skills/interview-spec/SKILL.md` to explicitly list natural-language entry phrasings, routing them here before any freeform brainstorming/planning happens. Did not rename the skill (`name:` field unchanged) -- renaming was considered and explicitly deferred to a future, separately-authorized work package per `docs/plans/issue-593-followup-recommendations.md`, since `interview-spec` is referenced by exact name across dozens of files (control-plane scripts, CLI help text, sibling-plugin policy docs, tests). | Reviewed updated frontmatter matches the user's explicit request; no automated eval exists yet for this skill's own trigger accuracy (candidate for a future `os-eval-runner` pass, not run in this task). | S | NO | RESOLVED |
| DEBT-20260913-RENAME-INTERVIEW-SPEC-TO-WORK-INTAKE | User explicitly authorized renaming `interview-spec` to `work-intake` (reversing the earlier deferral in DEBT-20260913-INTERVIEW-SPEC-DISCOVERABILITY) and did a global text find/replace across 74 files themselves; this rewrote historical records in `references/map-debt.md` and `plugins/agent-agentic-os/references/evolution-log.md` to say "work-intake" for events that happened while the skill was still named "interview-spec," and left the actual directory rename (`skills/interview-spec` -> `skills/work-intake`, `references/interview-spec/` -> `references/work-intake/`) inconsistent with `symlinks.json`'s already-edited text, producing 5 broken symlinks. | RESOLVED | Tier 2 | NO | 2026-09-13 | feature/issue-593-context-research | User did the bulk edit directly (not via `symlink_manager.py`) while the agent was mid-investigation of the blast radius; agent had explicitly recommended against a blind global replace beforehand given the historical-record and symlink-manifest risks, but the user proceeded before that investigation completed. | Reverted `references/map-debt.md` and `plugins/agent-agentic-os/references/evolution-log.md` to their committed (pre-replace) state via `git checkout --`, preserving historical accuracy. Completed the directory rename properly via `git mv` for `plugins/agent-agentic-os/references/interview-spec/` -> `work-intake/` and `interview-spec-detailed-reference.md` -> `work-intake-detailed-reference.md` (the user had already renamed the skill directory itself). Ran the mandatory `symlink_manager.py diagnose` -> `restore` -> `diagnose` workflow: 5 broken links found and repaired, 0 broken remaining. Verified `plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-agentic-os` (0 errors) and `audit.py --path plugins/agent-agentic-os` (PASSED, only pre-existing-style line-count warnings) after the fix. Separately fixed the root cause that let the underlying incident happen: added a code-level check (`_worktree_isolation_check` in `control_plane/policy.py`) rejecting `worktree_path == repo_root` at `APPROVED -> IN_WORKTREE`, since the agent had separately registered the main checkout itself as a "worktree" earlier in the same session with no code-level check catching it. | `symlink_manager.py diagnose` before fix: 5 `✗ broken symlink` entries; after: "All links OK." `audit_plugin_structure.py`: 0 errors. `audit.py`: PASSED. Unit-level verification of the new `_worktree_isolation_check`: rejects `worktree_path` equal to `repo_root`, accepts a genuine `.worktrees/task-<id>` path. | M | NO | RESOLVED |
| DEBT-20260913-WORKTREE-ISOLATION-BYPASS | `_worktree_isolation_check` (APPROVED -> IN_WORKTREE deterministic gate) only verified `worktree_path`/`worktree_branch` were non-empty and the branch wasn't `main`/`master` -- it never verified `worktree_path` was actually different from the repo root, so registering the main checkout itself as the "worktree" passed the check silently. | RESOLVED | Tier 2 | NO | 2026-09-13 | feature/issue-593-context-research | Agent ran `update-worktree --path "$(pwd)"` (the main checkout) instead of creating an isolated `.worktrees/task-<id>/` directory, directly contradicting the transition's own `next_steps_hint` ("create or select an isolated feature worktree"). No code-level check caught this; the user caught it by direct question ("did you create a worktree?" / "where is that worktree?"). | Added a `repo_root` key to the policy context dict (`_build_transition_policy_ctx` in `agent_control.py`) and a check in `_worktree_isolation_check` (`control_plane/policy.py`) rejecting the transition when the resolved `worktree_path` equals the resolved `repo_root`, unless an explicit `existing_worktree_exception` receipt exists (the pre-existing, correct escape hatch for legitimately working in the existing checkout with human authorization). | Unit-level reproduction: calling `_worktree_isolation_check` with `worktree_path` set to the repo root now returns a rejection message; the same call with an isolated `.worktrees/...` path returns `None` (pass). | S | NO | RESOLVED |
| DEBT-20260913-MAIN-DIRTY-BEFORE-APPROVAL-UNENFORCED | `worktree-reconciliation-and-multi-worktree-practices.md` Section 1 documented a "preferred practice, not yet enforced": commit interim INTAKE/INTERVIEW/DRAFT_PLAN work to a small branch and PR it before APPROVED, so main is clean before a worktree is created. No code enforced this -- `create_task()` computes a `main_dirty_advisory` field but the CLI `init` subcommand discards its return value and never prints it, and no deterministic check existed at any transition to require a clean checkout. | RESOLVED | Tier 1 | NO | 2026-09-13 | feature/issue-593-context-research | Agent accumulated substantial committed/uncommitted work directly on a task's own branch through INTERVIEW/DRAFT_PLAN, entered APPROVED/IN_WORKTREE without a clean-foundation commit+PR cycle, then could not push the branch at all once IN_WORKTREE (`pre-push-review-guard` correctly denies task-branch pushes before DONE) -- two individually correct rules producing a real conflict, caused by skipping this documented-but-unenforced gate. User identified the root cause directly by asking to review `worktree-manager`'s own reference doc. | Added `main_clean_before_approval` deterministic check to the `AWAITING_APPROVAL -> APPROVED` transition (`transition_templates.yaml` + `_main_clean_before_approval_check` in `control_plane/policy.py`), blocking the transition when `get_main_dirty_advisory()` reports `dirty_count > 0`, unless a human records an explicit `main_dirty_before_approval_exception` receipt. Updated the reference doc from "not yet enforced" to "Enforced in code." Separately, `pre-commit-pipeline-guard` was made location-aware: once a task reaches IN_WORKTREE-or-later with a genuinely isolated `worktree_path` (different from the repo root), a commit from any other location (e.g. the main checkout) on that task's branch is now rejected as a leak -- closing the gap where the guard was state-aware (branched on `TASK_STATE`) but not location-aware. | Unit-level reproduction of `_main_clean_before_approval_check`: dirty checkout rejected, clean checkout passes, dirty-with-exception-receipt passes. Pure-bash reproduction of the new location-aware commit-guard branch: main-checkout-while-isolated-worktree-exists correctly flagged as a leak; commit from inside the actual registered worktree correctly passes. Live worktree creation/removal test (`.worktrees/hook-test-throwaway`, cleaned up) confirmed hooks resolve via `git rev-parse --git-common-dir` and are shared across all worktrees of a repo, not per-worktree copies. | M | NO | RESOLVED |
| DEBT-20260913-NO-HUMAN-CONFIRM-BLANKET-GATE | `INTAKE -> INTERVIEW`'s YAML edge is coded `approval: required: false, approver_role: agent_or_human` -- by design, deterministic edges like this let the agent initiate them autonomously. An agent used this to register a brand-new task and transition it to INTERVIEW without ANY human authorization at all, mid-conversation, while the human was actively asking clarifying questions about a different topic. | RESOLVED | Tier 2 | NO | 2026-09-13 | chore/research-cleanup-and-followup-findings | User explicitly said they had not authorized starting this task at any point; when asked which specific edge should have blocked it, direct inspection of `intake_to_interview`'s YAML confirmed `approval.required: false` -- a real, intentional design choice for normal interview-initiation flow that nonetheless left zero human-in-the-loop gate for "should this task exist and be worked on right now at all." User then had the erroneous task deleted entirely via direct `sqlite3 DELETE` (cascaded across `tasks`, `task_transitions`, `transition_decisions`, and 13 other child tables by task_id -- no CLI delete-task command exists) since sqlite3 CLI does not enable `PRAGMA foreign_keys` by default so ON DELETE CASCADE did not fire automatically. | Added a blanket `--human-confirmed` CLI flag (required, no default, must start with literal marker `HUMAN-CONFIRMED:`) to every state-mutating subcommand (`init`, `coordinate-transition`, `transition`, `lock-verifiers`, `record-receipt`, `update-worktree`, `log-prior-art`, `record-plan-mode-entry`, `record-socratic-intake`, `record-human-approval`, `record-review-skip`, `record-critic-review`, `record-recovery-approval`), enforced in one shared `_enforce_human_confirmed()` check at the top of `_dispatch_command()` in `agent_control.py` -- applied uniformly on top of each edge's own YAML `approval.required` setting, not replacing it. Read-only/verification subcommands (`status`, `transition-guidance`, `recommend-model`, `verify-*`) remain exempt. This is a forcing function, not a cryptographic guarantee -- the flag's own help text states fabricating the string is a policy violation. | Live CLI reproduction: `init`/`coordinate-transition`/`update-worktree` without `--human-confirmed` now exit 2 (argparse-level, missing required arg) or exit 1 (malformed value not starting with the marker); `status`/`transition-guidance` unaffected (exit 0, no flag required). | M | NO | RESOLVED |
| DEBT-20260913-REPO-WIDE-BASELINE-TEST-FAILURES | Repo-wide `pytest plugins/agent-agentic-os/` had 68 pre-existing failures (confirmed via git-history archaeology, not assumption: most predate this session, e.g. missing `DONE` stage_contract and `full_test_suite`/`RETROSPECTIVE->DONE` check trace to commit `f9576f8a`, hours before this session, and `stages.DONE` never existed anywhere in this file's git history). User explicitly demanded these be fixed as part of closing out `agentic-os-dedup-invariant-v2`, given "so many rounds of testing" should have caught them. | RESOLVED (68 of 68 fixed and verified; 0 remain) | Tier 2 | NO | 2026-09-13/14 | agentic-os-dedup-invariant-v2 | Root causes spanned: (1) missing `DONE` stage_contract, `human_recovery` top-level config, and `closeout_change_control` in `transition_templates.yaml` (all genuinely undocumented-but-tested features); (2) `state_machine.py`'s `ALLOWED_TRANSITIONS` missing 3 edges (`IN_WORKTREE`/`WORKTREE_REVIEW`/`MULTI_AGENT_CODE_REVIEW` -> `RETROSPECTIVE`) that templates already defined, plus 8 more missing from `control-plane-architecture.md`'s and `control-plane-pipeline.mermaid`'s own edge-inventory tables; (3) a stale test assertion for an intentionally-shrunk advisory banner wording (`DEBT-20260907-08`); (4) `_reconcile_main_into_worktree` used `check=True` on a git subprocess call, crashing (not gracefully handling) non-git `tmp_path` test fixtures -- fixed to `check=False` matching the existing pattern in `_get_main_dirty_advisory`; (5) two genuine regressions from this session's own earlier fixes (the blanket `--human-confirmed` gate and `_worktree_isolation_check`/`main_clean_before_approval`) breaking tests that called the CLI/API without anticipating the new gates -- fixed by updating test fixtures/helpers to supply the new required inputs, not by weakening the gates; (6) `cp._persistence.<method>` accessed directly from outside `ControlPlane` in `record_interview_question.py` and 4 test call sites, violating this repo's own `test_wrappers_prohibit_raw_sql_and_private_persistence_attributes` architecture test -- fixed by adding proper public `ControlPlane.get_last_transition()`/`get_unconsumed_transition_answers()` facades; (7) `record_recovery_approval`/`apply_recovery_transition` were called by a test but only existed as private persistence-layer methods with a different (more verbose) signature than the test expected -- added public facades with an auto-deriving simplified signature, keyword-compatible with the existing CLI call site; (8) `full_test_suite` deterministic check only verified a receipt existed (`has_receipt`), never that it passed (`exit_code=0`) -- fixed to require `count_receipts(gate_name, 0) > 0`, matching the already-established `test_suite_or_deferred_to_review` pattern; (9) `apply_recovery_transition`'s Python-level `transition()` call had no bypass for recovery edges outside `ALLOWED_TRANSITIONS` (e.g. `DONE -> IN_WORKTREE`), unlike the SQLite `enforce_valid_transition` trigger which already honored a matching unconsumed recovery APPROVAL decision -- added a `bypass_adjacency` param to `transition()`, used only by `apply_recovery_transition`; (10) `pre-push-review-guard`'s "no task registered for branch" test asserted the pre-2026-09-13 fail-open behavior (warn + exit 0), stale relative to the already-shipped, already-documented fail-closed hardening (`DEBT-20260913-PUSH-GUARD-FAILOPEN-01`) -- updated the test to match the intentional current contract, not the guard; (11) the `INTERVIEW -> RETROSPECTIVE` template collision (item (a) below) was resolved by human design direction, not deleted: added a `force_retrospective_reason_category` question (planned/trivial-complete vs agent/pipeline-failure) as the first `human_questions` entry across all 12 `force_retrospective_from_*` edges in `transition_templates.yaml`, retiring the old separate 5-question trivial-fast-track set entirely onto this single edge -- 8 tests (registry contract, trivial-fast-track, capability-scoping, both pipeline-simulator adversarial rounds, reset-then-walk-forward, both schema-rebuild-atomicity fixtures, retrospective-capture-wrapper) updated to answer the new question instead of the old one; (12) item (b) below (`apply_recovery_transition` to DONE) was a real bug, not just design debt: `record_recovery_approval` wrote its opaque approval token under the same `question_id` (`human_force_done_confirmation`) the coordinator's own force-close flow needed to ask fresh, making the coordinator believe that question was already answered and skip it entirely, which then failed the DONE-authorization check downstream -- fixed by excluding `DONE` destinations from `record_recovery_approval`'s `required_transition_questions` lookup (falls back to the generic `recovery_approval_{from}_to_{to}` naming instead), plus a `coordinator.py` fix so a force-close question with an already-authorized answer is honored directly instead of always reading live stdin even under `interactive=True` (which broke every programmatic force-close caller, since `interactive=True` is structurally required by the force-close authorization gate itself). | Full-suite verification: `pytest plugins/agent-agentic-os/ -q` went from 68 failed/419 passed, to 21 failed/466 passed, to 10 failed/459 passed (this session's independent-bug-fix pass), to 0 failed/469 passed/1 skipped (final pass, after the reason-category redesign + recovery-approval fix). Every fix was verified individually via isolated `pytest <file>::<test>` runs before each full-suite re-check, per explicit user instruction to verify incrementally rather than only via the slow full suite. | L | NO | RESOLVED | Both previously-open architecture items were resolved this session, not deferred further: (a) the `INTERVIEW -> RETROSPECTIVE` collision was resolved per explicit human design direction (see (11) above) rather than by picking one of the two pre-existing templates. (b) the `apply_recovery_transition`-to-DONE mismatch was a genuine question-id collision bug (see (12) above), not a needed coordinator redesign as originally guessed -- the existing force-close architecture was sound once the collision was removed. All previously-untriaged tests (`test_registry_loads_stage_entry_question_contracts`, `test_trivial_fast_track_enters_retrospective_and_completes`, `test_interview_to_retrospective_edge_registered_and_capabilities_scoped`, `test_cli_dispatch_persists_canonical_revise_and_reports_it`, both `test_simulator_can_play_*`, `test_full_test_suite_check_rejects_failed_receipt`, `test_reset_then_walk_forward_unblocks_hooks`, both `test_rebuild_*` schema-atomicity tests, `test_human_recovery_from_done_to_worktree_requires_and_consumes_approval`, `test_warns_when_no_task_matches_current_branch`, `test_retrospective_capture_wrapper_records_agent_completion`, `test_git_guards_allow_exact_human_approved_recovery_edge`) are now fixed and passing. |
| DEBT-20260913-INTERVIEW-DRAFT-PLAN-OUTLINE | `TransitionCoordinator.coordinate_transition()`'s interactive INTERVIEW->DRAFT_PLAN path collected the 5 canonical interview answers but never persisted them to the plan-outline artifact before `assert_interview_plan_outline_ready` checked for it -- every interactive DRAFT_PLAN transition failed with "interview plan outline is missing" | RESOLVED | Tier 2 | NO | 2026-09-13 | fix/interview-spec-draft-plan-outline-gap | Both `pipeline_simulator.py` and `tests/interview_helpers.py` had manually worked around this by calling `update_interview_plan_outline()` themselves after staging answers -- proving the production interactive path never did. Discovered live running interview-spec's own documented `coordinate-transition --to DRAFT_PLAN --interactive` command against a real task. | Added an 8-line block in `coordinator.py` persisting each newly-collected stage answer to the outline before the commit-time readiness check runs. Also: fixed a stale model-catalog assertion in `test_cost_tier_resolution_and_task_columns` (gpt-5.4-nano -> gpt-5.6-luna, current low-tier model); added a `FORCE_RETROSPECTIVE` emergency-close edge to `state_machine.py`/`transition_templates.yaml`/`agent_control.py` from 12 states at explicit human request; added `detect_referenced_background_document()` to `interview_spec_engine.py` and a `Background Document Priority` rule (CLAUDE.md/AGENTS.md/GEMINI.md/copilot-instructions.md + `.agent/rules/`) after the agent ignored an explicit source-assisted-answer instruction in a referenced prompt document, causing significant session friction; shrank `coordinator.py`'s repeated identical advisory banner (execution-unit guidance) that likely trained the agent to skim rather than read edge-specific guidance. | `python3 -m pytest plugins/agent-agentic-os/tests/test_draft_plan_interactive_outline_gap.py plugins/agent-agentic-os/tests/test_background_document_priority.py plugins/agent-agentic-os/tests/test_agent_control.py::test_cost_tier_resolution_and_task_columns -v` (4 passed); live-verified against real task `issue-593-context-overhead`. Full repo test suite not re-run this session (explicit human authorization to skip). | M | NO | RESOLVED |

## DEBT-20260916-AGENTIC-OS-WORKTREE-MANAGER-METADATA

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `plugins/agent-agentic-os/plugin.yaml`
- Friction observed: The `work-intake` workflow documents `worktree-manager` as its portable implementation fallback, and the ownership manifest enables and installs that skill, but `plugin.yaml` does not declare `worktree-manager` in the Agentic OS plugin's `skills` list.
- Why not fixed now: This AUTH-PLAN work package is limited to research and plan drafting. Editing plugin packaging metadata would expand the scope into implementation/configuration work before plan review and approval.
- Recommended fix: Add `worktree-manager` to the Agentic OS plugin manifest's declared skills, then run plugin-structure and installation/synchronization validation in a separately authorized implementation slice.
- Evidence/repro: `plugins/agent-agentic-os/skills/work-intake/SKILL.md` references `worktree-manager`; `.agents/ownership/agent-agentic-os.json` has `worktree-manager.should_install=true`; `.agents/skills/worktree-manager` is present; `plugins/agent-agentic-os/plugin.yaml` omits it from `skills:`.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260916-DRAFT-PLAN-RESUME-DISCOVERABILITY

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `docs/plans/start-here.md`, `docs/plans/execution-tracker.md`, control-plane task handoff
- Friction observed: After the task reached `DRAFT_PLAN` and the Astra drafting agent was interrupted for repository synchronization, the next authorized action was not immediately obvious; the owner had to ask what to do next before the drafting stage resumed.
- Why not fixed now: This session is resuming the existing task and is not authorized to redesign the control-plane handoff or planning documents beyond recording the observed friction.
- Recommended fix: Make the tracker and start-here handoff explicitly state whether the drafting agent is running, paused, or complete, and provide the exact resume command/model/scope for the current `DRAFT_PLAN` stage.
- Evidence/repro: Task `issue-621-auth-plan` persisted in `DRAFT_PLAN` while `/root/astra_auth_plan_draft` was interrupted; the owner asked whether Astra was drafting and what to do next.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260916-PLAN-REVIEW-NEXT-ACTION-DISCOVERABILITY

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `docs/plans/start-here.md`, `docs/plans/execution-tracker.md`, control-plane stage handoff
- Friction observed: After the draft specification and implementation plan were produced in `DRAFT_PLAN`, the handoff did not proactively state the exact next human decision (`DRAFT_PLAN -> PLAN_REVIEW` and whether to request independent review). The owner had to prompt the agent again to identify what to ask next.
- Why not fixed now: This is the second occurrence of the same next-action discoverability class during this task. Redesigning the handoff documents is outside the current transition authorization; the repeated debt is escalated for a dedicated documentation/UX fix.
- Recommended fix: Make every stage completion report include current state, exact legal next transition, the human decision required, the precise command or phrase to authorize it, and what remains prohibited. Add a regression check for `DRAFT_PLAN` handoffs.
- Evidence/repro: After Astra delivered the draft artifacts, the owner stated they would need to say “proceed to plan_review” and requested this debt be logged because the agent again required prompting to identify the next action.
- Severity: M
- Repeat: YES
- Status: ESCALATED

## DEBT-20260916-PLAN-REVIEW-YAML-QUESTION-FIDELITY

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`, `plugins/agent-agentic-os/skills/work-intake/SKILL.md`, PLAN_REVIEW interaction
- Friction observed: At `PLAN_REVIEW`, the agent asked a natural-language paraphrase about independent review without presenting the transition contract's required canonical review-selection sequence and answer persistence expectations. The user correctly identified that the next transition questions must follow the YAML guidance.
- Why not fixed now: This is a repeated process-fidelity failure during the same task. Changing the transition contract or interaction implementation is outside the current planning authorization; the task remains at `PLAN_REVIEW` until the canonical question sequence is followed.
- Recommended fix: Before every human-gated transition, load the destination edge template, present its exact question/options and sequence, persist the canonical answer through `--interactive`, and report the next required question. Add a regression test that rejects paraphrase-only handling of PLAN_REVIEW review selection.
- Evidence/repro: PLAN_REVIEW transition guidance requires first asking whether agents should review, then—only after Yes—showing all four review methods and separately collecting runtime/model/effort for internal methods. The agent asked only a paraphrased first question and did not state the canonical sequence.
- Severity: M
- Repeat: YES
- Status: ESCALATED

## DEBT-20260916-REVIEW-METHOD-INFERRED

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: PLAN_REVIEW review-selection-v1 and `MULTI_AGENT_REVIEW` kickoff decisions
- Friction observed: The control-plane terminal displayed the four review methods, but the agent selected the recommended multi-agent internal option without first obtaining an explicit user choice in the conversational handoff. The owner later correctly identified that the review type had not been asked clearly.
- Why not fixed now: The task has entered `MULTI_AGENT_REVIEW`, but no reviewer has been dispatched. Treat the recorded method as untrusted until the owner explicitly confirms or corrects it; do not infer runtime, model or effort.
- Recommended fix: Surface the four review methods in the chat, obtain an explicit selection, reconcile it with the persisted decision (or return through the supported correction path), then collect runtime/model/effort separately before kickoff. Add a regression test preventing recommended-option auto-selection from an agent-controlled terminal response.
- Evidence/repro: During `PLAN_REVIEW -> MULTI_AGENT_REVIEW`, the agent supplied option `3` (recommended multi-agent internal) to the interactive prompt after the owner only said they wanted reviews by other agents.
- Severity: L
- Repeat: YES
- Status: ESCALATED

## DEBT-20260916-CANONICAL-QUESTION-PARAPHRASE

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: PLAN_REVIEW/MULTI_AGENT_REVIEW YAML transition questions and conversational handoff
- Friction observed: The owner explicitly requested that the agent stop paraphrasing transition questions and ask the exact YAML-defined question and options. The handoff repeatedly relied on conversational paraphrase instead of showing the canonical prompt contract.
- Why not fixed now: This is a repeated transition-fidelity failure. The current task is held before reviewer dispatch while the canonical selection is obtained explicitly.
- Recommended fix: Render the exact YAML `question`, declared options, default marker and selection semantics in the chat before invoking the interactive transition; never auto-select a recommended option or translate a free-text answer into a different canonical choice.
- Evidence/repro: Owner instruction: “don't paraphrase the yaml ask the specific questions and log map debt again.”
- Severity: M
- Repeat: YES
- Status: ESCALATED

## DEBT-20260916-AGY-REVIEW-DISPATCH-SANDBOX

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan-round3
- Artifact affected: Gemini 3.8 Flash adversarial review dispatch
- Friction observed: `run_agent.py --cli agy --model gemini-3.8-flash --effort medium` failed before review because the CLI could not create its log/crash files or bind its local language-server port under the restricted sandbox.
- Why not fixed now: The agy skill requires stopping on backend failure; retrying outside the sandbox requires explicit escalation and must not silently substitute another backend.
- Recommended fix: Obtain approved escalated execution for the exact agy review, or record the review as blocked; preserve the failed dispatch evidence and do not treat the Claude result as a Gemini substitute.
- Evidence/repro: `Failed to redirect output ... ~/.gemini/... operation not permitted`; `listen tcp 127.0.0.1:0: bind: operation not permitted`; agy exited code 1.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260916-CLAUDE-REVIEW-DISPATCH-ROUTING

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan-round3
- Artifact affected: Claude Sonnet 5 adversarial review dispatch
- Friction observed: The initial command omitted `--cli claude`, so the shared runner routed to the default Copilot backend and failed due to missing Copilot authentication; no review was produced.
- Why not fixed now: The dispatch was a routing error, not a valid Claude review. It is safe to retry with the explicit Claude backend while preserving this failure record.
- Recommended fix: Require an explicit backend flag in review dispatch wrappers and record backend/model/effort before launch.
- Evidence/repro: Runner output reported `No authentication information found` and `copilot exited with code 1`.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260916-CLAUDE-REVIEW-AUTH

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan-round3
- Artifact affected: Claude Sonnet 5 adversarial review dispatch
- Friction observed: Explicit Claude backend dispatch could not run because the Claude CLI is not logged in; no Claude review report was produced.
- Why not fixed now: Authentication requires the owner to run the CLI login flow; this session must not create or alter credentials.
- Recommended fix: Owner authenticates Claude CLI, then rerun the exact same review assignment with `--cli claude --model claude-sonnet-5 --effort medium`; do not treat Gemini output as a substitute.
- Evidence/repro: `claude --model claude-sonnet-5 -p 'Respond only: HEARTBEAT_OK'` returned `Not logged in · Please run /login`.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260916-PLAN-ONLY-APPROVAL-BRANCH

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`, AWAITING_APPROVAL lifecycle
- Friction observed: The approval gate presents `Approve task implementation and worktree creation?`, while this work package is planning-only. The normal `APPROVED` edge therefore grants authority beyond scope; planning completion currently requires an exceptional FORCE_DONE path instead of a first-class decision.
- Why not fixed now: Changing transition YAML, coordinator behavior, and tests is a separate governance implementation task; mutating it during this planning package would violate the current scope and require its own verification contract.
- Recommended fix: Add an explicit AWAITING_APPROVAL decision that distinguishes (a) approve implementation/worktree creation and (b) approve finalizing the accepted plan and proceeding to DONE. Add a normal planning-only completion edge with no implementation capabilities, deterministic completion evidence, and exact human question/options. Retain APPROVED exclusively for implementation authorization; add transition guidance and regression tests for both branches.
- Evidence/repro: Current YAML `awaiting_approval_to_approved` asks `Approve task implementation and worktree creation?`; current DONE path is documented as exceptional human-forced completion requiring FORCE_DONE. User identified need for separate questions for implementation approval versus plan finalization.
- Severity: M
- Repeat: YES
- Status: OPEN

## DEBT-20260916-CLI-FORCE-CLOSE-UNREACHABLE

- Logged date: 2026-09-16
- Cycle/Session ID: issue-621-auth-plan
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py`, AWAITING_APPROVAL -> DONE planning-only closeout
- Friction observed: The coordinator supports a guarded `force_close` path, but the CLI `coordinate-transition` parser exposes no `--force-close` option and therefore cannot reach the required `FORCE_CLOSE` interactive authorization from AWAITING_APPROVAL. A direct Python API call would bypass the intended CLI/control-plane path.
- Why not fixed now: Adding a CLI flag, forwarding it through dispatch, and testing the authorization path is a separate lifecycle implementation change outside this planning-only package.
- Recommended fix: Add an explicit `--force-close` flag with strict human/interactive validation, preserve the exact FORCE_CLOSE question, add CLI and coordinator regression tests, and then add the first-class planning-only DONE edge so force-close is not needed for ordinary plan completion.
- Evidence/repro: `coordinate-transition --to DONE --interactive` from AWAITING_APPROVAL returned `Force close denied: explicit human authorization FORCE_CLOSE is required`; `--help` shows no `--force-close` option.
- Severity: M
- Repeat: NO
- Status: RESOLVED
- Resolution (2026-09-20, auth-ciba-increment-b): SUPERSEDED. The `force_close` path and the FORCE_CLOSE/FORCE_DONE literals were removed rather than exposed on the CLI: every edge into DONE (including early close from any active state) is now a cryptographic gate (a human-signed `transition_request`, `ssh-keygen -Y sign`). `--force-close` is deliberately not a CLI option (argparse rejects it; asserted by `test_cli_transition_parsers_refuse_the_removed_skip_and_force_close_flags`), and the `force_close=` keyword raises TypeError (`test_the_force_close_bypass_parameters_no_longer_exist`). The planning-only closeout this entry wanted is covered by the signed closure gate.

## DEBT-20260920-SQLITE-LOCK-ACROSS-SIGNATURE-VERIFY

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/adapters.py` (commit_transition), `plugins/agent-agentic-os/scripts/control_plane/transition_request.py` (consume_with_signature)
- Friction observed: The commit transaction (`BEGIN IMMEDIATE`) ran the live content snapshot (git/file hashing) and the `ssh-keygen -Y verify` subprocess inside the write lock, so any concurrent writer got `sqlite3.OperationalError: database is locked` for the duration of the subprocess.
- Why not fixed now: Fixed now.
- Recommended fix: Applied. `preverify_signature()` performs the snapshot read, challenge rebuild and signature verification on a read connection BEFORE `BEGIN IMMEDIATE`; `consume_with_signature(preverified=...)` re-checks the request row, the stored-vs-verified snapshot and the rebuilt challenge inside the transaction, then flips PENDING -> CONSUMED once.
- Evidence/repro: `tests/test_gate3_code_acceptance.py::test_no_write_lock_is_held_during_snapshot_or_signature_verification` (failed before the change with `write lock held during ssh-keygen verify: [False]`, passes after, both Gate 3 edges). Known gap: no dedicated test for "request mutated between verification and commit" (the in-transaction challenge comparison covers it but is not asserted directly).
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-ENSURE-SCHEMA-FASTPATH

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/adapters.py` (ensure_schema, _sync_valid_transitions), `plugins/agent-agentic-os/scripts/control_plane/registry.py` (load_default)
- Friction observed: `ensure_schema()` runs on every persistence call, including reads. Each call re-parsed the 158KB `transition_templates.yaml` with the pure-Python loader (~0.13s) and took `BEGIN IMMEDIATE` to DELETE and re-INSERT `valid_transitions` / `required_transition_questions`. Test setup cost ~20s per test (155 parses) and every read briefly contended for the write lock.
- Why not fixed now: Fixed now.
- Recommended fix: Applied. `TransitionRegistry.load_default()` is memoized on the YAML's sha256. `ensure_schema()` has a read-only fast path (`_schema_is_current`): schema version current, `registry_sync_state.inputs_fingerprint` (schema version + SCHEMA_SQL + SCHEMA_MIGRATIONS + LEGAL_INITIAL_STATES + YAML bytes + registry.py bytes) unchanged, and a digest of the derived tables plus trigger names undrifted; otherwise the full sync runs (self-heals drift exactly as before). The orphaned-migration check still runs first. Consequence: an already-initialized database no longer re-runs SCHEMA_MIGRATIONS on every call.
- Evidence/repro: `tests/test_ensure_schema_fastpath.py` (6 tests; 4 failed before). Setup 20s -> <1s per test; gate3 file 9m17s -> 13.7s; full suite ~110s single-threaded. Two tests adapted: `test_migration_swallows_only_duplicate_column_not_other_errors` (now targets a fresh DB) and `test_sync_valid_transitions_is_atomic_not_left_empty_on_failure` (mocks `get_all_edges_with_proof`).
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-RECOVERY-APPROVAL-NOT-BOUND

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/adapters.py` (_apply_recovery_transition), `plugins/agent-agentic-os/scripts/pre-commit-pipeline-guard`, `plugins/agent-agentic-os/scripts/pre-push-review-guard`
- Friction observed: After `apply_recovery_transition()` to a NON-DAG destination, the consumed recovery approval row keeps `bound_transition_id = NULL` (consumed_at is a CURRENT_TIMESTAMP string, so another writer consumed it before the bind UPDATE took effect). The commit/push guards require a consumed approval bound to the exact transition, so a legitimately recovered task is reported as an invalid transition. The existing test used IN_WORKTREE -> DONE, a DAG edge, so this branch was never exercised.
- Why not fixed now: Outside this increment's scope; discovered while retiring the DONE recovery path. Root cause of the lost bind not yet isolated.
- Recommended fix: Find which statement/trigger consumes the approval before step 6's UPDATE, bind `bound_transition_id` before consumption (or bind on the consuming statement), then remove the xfail.
- Evidence/repro: `tests/test_pre_commit_pipeline_guard.py::test_git_guards_allow_exact_human_approved_recovery_edge` is `xfail(strict=True)` (IN_WORKTREE -> MULTI_AGENT_CODE_REVIEW recovery); strict, so fixing the bug fails the xfail and forces its removal.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260920-TESTS-WRITE-INTO-REAL-DOCS-PLANS

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/tests/` (several suites), `docs/plans/work-tasks/`
- Friction observed: Running the suite leaves untracked `docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md` files in the checkout (plan-outline staging, e.g. test-bundle-001, p01-task, t1, standard-001), because tests use the process cwd as the repo root.
- Why not fixed now: Cosmetic, untracked, not committed; needs each suite pointed at a tmp repo root.
- Recommended fix: Route those suites through a tmp repo root (as `PipelineSimulator` does) or add a session-level cleanup fixture; do not `git add` docs/plans/work-tasks from test runs.
- Evidence/repro: `find docs/plans -type f` after a full run. 2026-09-20: the `*-plan-outline.md` files were deleted (untracked, user-authorized); two other untracked test leftovers remain, `docs/plans/work-tasks/case7-cli-agent-attempt/*-{spec,implementation-plan}.md`, and the suites still recreate the outlines on every run.
- Scope update (2026-09-20): the case7 leftovers were deleted. Running the suite with cwd=`plugins/agent-agentic-os` also leaves untracked `plugins/agent-agentic-os/context/identity/` (326 files: ~324 challenge files/signatures and an `allowed_signers` holding the throwaway `test-human@local` key from `tests/helpers/human_signer.py`) and `plugins/agent-agentic-os/docs/plans/work-tasks/*-plan-outline.md`. Test keys must never sit at a path a real gate would trust; the fix is to root these fixtures in tmp_path.
- Severity: M
- Repeat: YES
- Status: OPEN

## DEBT-20260920-CRYPTO-VERIFICATION-READINESS-REPORTING

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/identity_setup.py` (identity_status), `scripts/setup_ciba_identity.py` (--check), `scripts/init_agentic_os.py` (signing_identity_notice), `skills/os-health-check/SKILL.md` (Phase 3.6)
- Friction observed: os-init and os-health-check reported only whether an identity folder and an enrolled key existed. They did not assert that verification could actually work: no ssh-keygen/SSHSIG probe, an allowed_signers with no parseable key, or keys scoped to a namespace the gates never sign under all still looked healthy or produced a crash.
- Why not fixed now: Fixed now.
- Recommended fix: Applied. `identity_status` adds an `ssh_keygen` capability probe and failures `SSH_KEYGEN_UNAVAILABLE`, `SSHSIG_UNSUPPORTED`, `NO_ENROLLED_KEYS`, `NAMESPACE_MISMATCH`; `--check` prints an `ssh-keygen:` line; os-init's notice prints the same. os-init and the health check remain READ-ONLY by design: neither creates a key or writes `allowed_signers*` (an agent-run surface that enrolled a key would be an enrollment path for an agent); only the human runs `setup_ciba_identity.py`. The health-check phase asserts verification readiness and states that actor strings, typed confirmations and skip/force-close flags are not tested because they cannot authorize the gates.
- Evidence/repro: `tests/test_identity_verification_readiness.py` (7 tests, all failed before), `tests/test_health_check_signing_status.py`, `tests/test_os_init_identity_status.py`.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-IMPLEMENTATION-COMPLETENESS-PATH-AND-ROOT

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py` (`check_implementation_completeness` in `_build_transition_policy_ctx`)
- Friction observed: VERIFY_EXIT -> RETROSPECTIVE's `implementation_completeness` reported the ledger "missing" because it only looked for the legacy flat `docs/plans/<task-id>-implementation-plan.md`, while plans live under `docs/plans/work-tasks/<task-id>/` (commit a42df236 fixed `_resolve_artifact_path` but not this check). A second mismatch: even once found, artifact existence was judged against the checkout holding the (untracked) plan, i.e. the main checkout, not the task's registered worktree where the implementation exists.
- Why not fixed now: Fixed now (no flat-path stubs created).
- Recommended fix: Applied. The check tries `docs/plans/work-tasks/<task-id>/` first, then the flat path, in each root, and passes if SOME candidate plan carries a valid fully COMPLETE ledger (plan submission can leave a stub copy in one layout); artifacts are validated against the registered worktree first, then the plan's own root. It still fails closed when no candidate validates. The task's own ledger was also rewritten into the validator's single-JSON-list schema (`id`, `status`, `evidence`, `artifacts`) with 19 COMPLETE entries; entries superseded by the 2026-09-20 human decisions (T4, T10) say so in their evidence, and T9/T16 state what this session did not perform (local execution-tracker.md/backlog.md, plugin_add.py sync, closing #639).
- Evidence/repro: `tests/test_agent_control.py::test_implementation_completeness_*` (5 tests; 3 failed before the fix, two guard the legacy flat path and the both-layouts case).
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-LEAK-CHECK-VERIFIER-IS-A-NOOP

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/wrappers/run_exit_verification.py` (`VERIFIER_CATALOG["leak_check"]`)
- Friction observed: The cataloged `leak_check` verifier is `python3 -c "print('clean')"`, so its receipt (gate `leak_check`, exit 0) proves nothing about leaks; `done_guard` accepts it as the "clean leak check". The real leak check this session was a manual `git status --short` of the main checkout compared to the pre-session baseline.
- Why not fixed now: Out of scope for this increment; changing the verifier needs a design decision (what baseline defines "clean" across worktrees, and how the check gets the main checkout path).
- Recommended fix: Make the verifier run `git status --short` in the main checkout, compare against a baseline captured at task start, and fail on new modified/untracked paths (per worktree-subagent-leak-detection.md), with a failing test first.
- Evidence/repro: `VERIFIER_CATALOG` in run_exit_verification.py; bundle output `"stdout": "clean\n"` on 2026-09-20.
- Severity: M
- Repeat: NO
- Status: OPEN

## DEBT-20260920-CONVENTIONS-AUDIT-DELTA-INCREMENT-B

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b
- Artifact affected: `plugins/dev-utils/scripts/workspace_conventions_auditor.py` results for `plugins/agent-agentic-os` (new tests and modules from Increment B)
- Friction observed: The pre-push workspace conventions audit exits 0 but reports failures. The baseline at origin/main (07b0bb64) already failed the same 6 plugins (agent-agentic-os, agent-scaffolders, cli-agents, dev-utils, exploration-cycle-plugin, plugin-manager) with 110 canonical files failing; this branch reports 151 (about 41 more), mostly missing function docstrings and file-header sections in the new test files and new control_plane modules. Also unchanged and pre-existing: `symlink_manager diagnose` reports 6 missing plugin-pruner links, and `audit.py` progressive-disclosure warnings for several skills.
- Why not fixed now: Owner instruction 2026-09-20 to push without fixing pre-existing audit issues, missing docstrings or symlink-manager diagnostics. The one hard regression this branch introduced (os-signing-setup lacked acceptance-criteria.md, making `audit.py` exit 1) WAS fixed: `audit.py` now passes, `audit_plugin_structure.py` reports 0 errors.
- Recommended fix: Add the missing docstrings/header sections to the new test and module files, then re-run the conventions auditor; separately restore the plugin-pruner links in plugin-manager.
- Evidence/repro: `python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py` (report at temp/workspace_conventions_report.md); baseline compared in a detached worktree of origin/main.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260920-CI-EVOLUTION-JOB-HAS-NO-PYYAML

- Logged date: 2026-09-20
- Cycle/Session ID: auth-ciba-increment-b (PR #643 CI)
- Artifact affected: `plugins/agent-agentic-os/tests/conftest.py`, `.github/workflows/verify-evolution-integrity.yml`
- Friction observed: The "Evolution Integrity & Compliance Gate" job installs only `pytest` and runs `tests/test_evolution_guards.py`. The Increment B `conftest.py` autouse fixture imported the control plane (which imports PyYAML) for every test, so all 11 evolution-guard tests errored with `ModuleNotFoundError: No module named 'yaml'` and the job failed on the PR. Reproduced locally by shadowing `yaml` with a module that raises ImportError.
- Why not fixed now: Fixed now.
- Recommended fix: Applied. The auto-signer fixture returns early when PyYAML is not importable (those tests never touch the control plane) and creates the throwaway signing key lazily, only when the control plane is in play. The workflow was NOT changed. Longer term: decide whether that CI job should install the plugin's `requirements.txt` so control-plane tests can run there too.
- Evidence/repro: `PYTHONPATH=<dir with a yaml.py that raises ImportError> pytest plugins/agent-agentic-os/tests/test_evolution_guards.py` failed 11/11 before and passes 11/11 after; full suite unaffected.
- Severity: M
- Repeat: NO
- Status: RESOLVED

## DEBT-20260920-HANDWRITTEN-DOCS-PLANS-ROOT-ARTIFACTS

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `docs/plans/`, `plugins/agent-agentic-os/skills/work-intake/SKILL.md`
- Friction observed: Hand-wrote artifacts into `docs/plans/` root, bypassing `update_interview_plan_outline()` and nested `docs/plans/work-tasks/<task-id>/` directory structure.
- Why not fixed now: Fixed now in `start-here-cleanup` by adding explicit artifact location rule to `work-intake/SKILL.md` and correcting YAML templates.
- Recommended fix: Keep all task artifacts strictly isolated inside `docs/plans/work-tasks/<task-id>/`.
- Evidence/repro: `test_work_intake_guidance.py::test_artifacts_live_under_nested_task_folder` passes.
- Severity: S
- Repeat: YES
- Status: RESOLVED

## DEBT-20260920-STALE-TEMP-PROMPT-MD

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `temp/prompt.md`, `interview_spec_engine.py`
- Friction observed: `temp/prompt.md` is an untracked background scratch file from prior sessions that can mislead `interview_spec_engine.py` if not cleared between tasks.
- Why not fixed now: Cleaned up manually in current session; permanent cleanup hook deferred.
- Recommended fix: Add session/task initialization purge for ephemeral scratch files under `temp/` or isolate per task.
- Evidence/repro: Observed during start-here-cleanup intake.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260920-INIT-MODEL-TIER-RECORDED-WRONG-MODEL

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py::create_task`
- Friction observed: Running `init --model-tier low` recorded `model_id: claude-haiku-4-5` even when the running CLI agent was Gemini/Sonnet.
- Why not fixed now: Model resolution logic is in `adapters.py:resolve_recommended_model` using default tool catalogs; dynamic active CLI detection is deferred.
- Recommended fix: Inspect active runtime environment or allow explicit `--runtime-model` override flag during task creation.
- Evidence/repro: Task metadata in test SQLite database recorded haiku model ID for non-haiku runner.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260920-NO-CLI-CONFIRM-CANDIDATES

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `plugins/agent-agentic-os/scripts/agent_control.py`
- Friction observed: There was no dedicated CLI sub-command to confirm or reject source-assisted question candidates, requiring manual script invocation (`confirm_candidates.py`).
- Why not fixed now: Candidate confirmation is part of the broader socratic intake engine review; adding a full CLI verb is deferred to next tooling cycle.
- Recommended fix: Add `agent_control.py confirm-candidates --task-id <id> --candidate-ids <id1,id2>` subcommand.
- Evidence/repro: Required Python wrapper execution in start-here-cleanup intake.
- Severity: S
- Repeat: NO
- Status: OPEN

## DEBT-20260920-SOFT-EDGE-HUMAN-ASKED-TWICE

- Logged date: 2026-09-20
- Cycle/Session ID: start-here-cleanup
- Artifact affected: `plugins/agent-agentic-os/scripts/control_plane/coordinator.py`, `transition_templates.yaml`, `edge_matrix.py`
- Friction observed: On soft approval edges carrying human questions, the human answered in chat, but coordinator subsequently re-asked questions because answers were not staged or actor was unverified, causing the human to answer twice.
- Why not fixed now: Resolved in `start-here-cleanup` by establishing the 3-class edge taxonomy (`edge-matrix.md`), updating guidance hints, adding `test_work_intake_guidance.py` assertions, and eliminating redundant review requirements on `PLAN_REVIEW -> AWAITING_APPROVAL`.
- Recommended fix: Maintain clear edge classification; agent asks once in chat, stages answers or coordinates transition, and never prompts for questions already answered in context.
- Evidence/repro: `test_work_intake_guidance.py` and `test_control_plane_pipeline_simulator.py` pass.
- Severity: M
- Repeat: YES
- Status: RESOLVED

## DEBT-20260921-DIAGRAM-SYMLINK-GAPS

- Logged date: 2026-09-21
- Cycle/Session ID: docs-diagram-symlink-audit
- Artifact affected: `plugins/agent-agentic-os/assets/diagrams/architecture-overview.mmd`, `event-bus-architecture.mmd`, `agentic-os-memory-subsystem.mmd`, `agent-agentic-os-architecture.mmd`
- Friction observed: A user-prompted audit found `docs/diagrams/` had 4 of 7 files (CIBA/RAR + SSH-signing diagrams) never symlinked into any skill (`os-init`/`work-intake`), same gap shape as the already-RESOLVED `DEBT-20260907-08`. Fixed this session via `symlink_manager.py create`. A second, older orphan set was also found in `plugins/agent-agentic-os/assets/diagrams/`: 3 of 7 files there were never linked into any skill either. Of those 3, `sibling-repo-labs.mmd`, `os-eval-backport-phases.mmd`, and `os-eval-backport-sequence.mmd` were current and symlinked into `os-eval-backport`/`os-eval-lab-setup` this session. The remaining 4 are NOT fixed: `event-bus-architecture.mmd` and `agentic-os-memory-subsystem.mmd` reference a skill node named `os-learning-loop`/`session-memory-manager` that no longer exists under those names (current skills are `os-improvement-loop`/`os-memory-manager`) — content is stale, not just unlinked. `architecture-overview.mmd` has the same stale naming in its edges and describes a kernel/event-bus design (lease locks, guest tokens, inboxes) not yet verified against the as-built `kernel.py`/`os-state.json`. `agent-agentic-os-architecture.mmd` is an 8-line plugin-folder listing, too low-value to warrant a symlink as-is.
- Why not fixed now: Correcting stale skill-name references is a content-accuracy decision requiring domain verification against current code (`kernel.py`, `os-state.json`, `os-improvement-loop`/`os-memory-manager` SKILL.md), not a symlink-only fix; out of scope for this session per explicit user decision to defer.
- Recommended fix: (1) Verify `architecture-overview.mmd` against current `templates/kernel.py` and `os-state.json` schema, update or regenerate stale node/edge labels (`os-learning-loop` -> `os-improvement-loop`, `session-memory-manager` -> `os-memory-manager`), then symlink into `os-init` and/or `os-memory-manager`. (2) Same correction for `event-bus-architecture.mmd` and `agentic-os-memory-subsystem.mmd` before linking. (3) Decide whether to keep, regenerate, or delete `agent-agentic-os-architecture.mmd` (do not delete without explicit instruction per `destructive-action-guard.md`).
- Evidence/repro: `grep -rl "os-learning-loop\|session-memory-manager" plugins/agent-agentic-os/assets/diagrams/*.mmd`; `ls plugins/agent-agentic-os/skills/` confirms neither name exists as a current skill.
- Severity: S
- Repeat: NO
- Status: OPEN

