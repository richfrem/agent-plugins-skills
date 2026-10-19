# Acceptance Criteria: Graph Planner

## 1. Trigger Verification
- [ ] Triggers on requests to design, architect, or compile a multi-step DAG, execution graph, or `graph-manifest.json`.
- [ ] Does **not** trigger for executing an existing manifest (that is `graph-execution`), single-file fixes, or strategy selection (`select-loop-strategy`).

## 2. Interview Discipline
- [ ] Reads caller briefs, specs, and any `--decision <path>` record before asking questions.
- [ ] Asks only about unresolved topology gaps: fan-out candidates, join barriers, verifier scripts, mutation targets, failure escalation.

## 3. Manifest Correctness
- [ ] Manifest passes `python3 scripts/validate_manifest.py <manifest>` with zero errors.
- [ ] Manifests intended for `--approval none` also pass with `--check-approval-none`.
- [ ] Every `command_or_eval` is an executable shell command (model tiers are invoked through a CLI inside the command, never as a bare prompt).
- [ ] Every `sequential_mutation` declares `mutation_targets`; no bare `*` or `**` targets.
- [ ] Mutations form one linear chain; fallbacks have the same type as their primary and the same preceding mutations.
- [ ] External or irreversible actions set `reversible: false` and depend on the approval gate.
- [ ] `verifier_hash` values are computed from the script file named in the command (or the command string when it names no file).

## 4. Handoff
- [ ] A Mermaid diagram of the DAG is presented alongside the manifest.
- [ ] Handoff states the manifest SHA256 for `--expect-manifest-sha256` and the intended `--approval` mode and workspace flag.
