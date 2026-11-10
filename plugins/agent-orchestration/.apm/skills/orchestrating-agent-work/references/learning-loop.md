# Learning loop (repository-independent)

Supported entry point for ONE work item: `python3 scripts/work_loop.py run CONTRACT --cli claude --model M --instruction-file TASK.md [--executable PATH]`
(or `work_loop.run_item(...)`). It is a sequential loop on top of `cli-agent/run_agent.py`; it is not a scheduler. `graph_runner.py` (DAG manifests) and
`swarm_run.py` (bulk jobs) do not call `cli-agent`; use them for those shapes and pass the `run_agent.py` flags yourself if you need the same launch controls.

## What the code does (enforced)
1. **Contract** - `start` validates goal, scope, acceptance, failure conditions, authorization and the budget (semantics below).
2. **Lessons** - up to 3 relevant lessons are retrieved before any dispatch and saved in `plan.json`.
3. **Per attempt (`dispatch`)** - in this order: acquire the unit claim (unique token) -> admit and reserve under a file lock (attempt + token budget) ->
   allocate an immutable attempt id and `attempts/<attempt-id>/` -> write `input.md` (task + bounded lessons block + repair notes) -> context readiness
   (when the contract requires isolation) -> executable preflight in the worker environment -> run `run_agent.py` with the pre-acquired claim token ->
   record every backend attempt and its usage -> release the claim (only with the holder's token). A refused duplicate or budget refusal changes no attempt files.
4. **Assess** - `evaluate` checks the criteria against the repository state, writes `evaluations/<id>.json` (history kept) and `findings.json`, and
   writes `accepted.json` naming the accepted attempt when all required criteria pass.
5. **Repair** - `run_item` returns unmet criteria to the next attempt as a "Repair required" section; it stops on acceptance, a blocker, escalation
   at the attempt cap, a preflight refusal, a duplicate, or budget exhaustion.
6. **Usage** - backends that report no tokens keep usage unknown, except `claude`: its unknown usage is attributed from Claude's own project transcripts (existing `usage_measure.claude_tokens_between`, exact worker cwd, attempt window; skipped when another session was active or no transcript exists). Budgeted total = input + output + cache-write; cache reads are recorded but excluded.
7. **Measurement export** - each finished attempt also gets `measurement.json`: one control-plane P02 observation per backend attempt (see [agentic-os-reuse-map.md](agentic-os-reuse-map.md)).
8. **Evidence** - attempts, results, outputs, refusals and evaluations are append-only/immutable; `lesson_candidates` lists failed-then-repaired attempts.

## What stays agent-supervised
Writing lessons (`lessons.py add` from the candidates), confirming `manual` criteria, deciding whether a lesson helped (`observe_lessons` needs cited
attempt ids; supplying a lesson never marks it helped), reviews, integration, any use of authorization, and anything outside the loop's repository state.

## Budget semantics (per WORK ITEM, across all units, backends and fallback attempts)
`max_attempts` (required positive integer): execution attempts; preflight refusals and evaluation calls do not count. `max_tokens` (optional positive
integer): ceiling over measured/charged tokens. `per_attempt_token_reserve` (optional, needs `max_tokens`): charged for any attempt whose usage is unknown or
still running. With a token ceiling and unknown usage but no reserve, further launches are REFUSED (never assume zero). Backends cannot enforce a hard
token ceiling; limits are admission control plus the output/turn/time limits the backend supports (`--timeout`, `--max-tokens` for llama).

## Ownership boundary
Claims stop a second claimant of the same unit and give the holder a token. They do not stop an unrelated process from writing the same files, and a
hard-killed holder leaves a stale claim (no expiry). On timeout/cancellation the executor stops the worker's whole process group and confirms cleanup
before the claim is released or a fallback starts; descendants that start their own session are out of reach.

## Experimental readiness
A contract with `"isolation": {"required": true}` makes the loop refuse any launch until `dispatch_guard.py probe-context` has succeeded for the EXACT
configuration (backend, model, executable path and version, clean flags, cwd policy). One probe covers all trials with that configuration; any change voids
it. Ordinary repository work (no `isolation`) keeps its repository context. Unobserved context is reported, never assumed.

## Ownership of capabilities
| Capability | Owner |
|---|---|
| Outcome loop, attempt ledger, admission, lesson briefs | `orchestrating-agent-work` |
| Launch controls (claim token, cwd, executable, process-group timeout, clean context, readiness probe), structured result with per-backend attempts | `cli-agent` |
| Findings, attempt/usage arithmetic, budget validation, claim-specific validity, scoring, lessons | `evaluating-agent-outcomes` |
| Mission lifecycle, hypotheses, verdicts, governance | the consuming repository (e.g. Sanctuary) |
