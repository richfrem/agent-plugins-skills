# Reuse map: agent-agentic-os plugin vs the shared learning loop

Checked against the plugin source (`plugins/agent-agentic-os`, MISSION-055 bundle review). Rule: reuse what exists; do not duplicate.

| Agentic OS capability | Relationship | Decision |
|---|---|---|
| `control_plane/measurement.py` (P02 closed measurement-observation schema: provenance measured/reported/estimated/unavailable, null vs zero, UUIDv7 ids, canonical SHA-256 digest, idempotent settlement, privacy allowlist) | Same problem the loop's usage ledger solves | REUSED: the loop writes `attempts/<id>/measurement.json`, one P02 observation per backend attempt (`accounting.to_measurement_observation`), digest computed by the control plane's own canonicalizer when installed (draft-fixture form otherwise), validated in tests with `validate_observation_dict` and `settle_observations`. The attempt ledger stays the loop's admission state (it needs a budgeted total and reservations, which P02 does not model); P02 is the export/interchange format. Known gap: P02 has no total-only slot, so a vendor-reported combined total is recorded as provenance `reported` with null splits and the reason. |
| `improving-skills-in-lab` (KEEP/DISCARD loop, locked scorer, `evals/results.tsv`, traces, backport) | Improves a SKILL's wording/behavior against evals | OPTIONAL downstream: when a recorded lesson is about a skill's own behavior and has verified reuse, promote it into the skill through the lab instead of a free-standing lesson. Not needed for ordinary work. |
| `distill_playbook.py` (wiki playbooks, index sync, confidence decay) | Durable promotion of confirmed invariants | OPTIONAL promotion target for lessons with several verified `helped` uses; the lesson store (`lessons.py`) is the working store. Needs a `wiki/` layout the neutral repo may not have. |
| `running-control-plane` gates, signed human approvals, task pipeline, event bus (`context/events.jsonl`) | Governance of a multi-step pipeline | UNRELATED to single-item delegation; use it when a repository adopts the control plane. The loop never writes to or reads `context/`. Authorization in the loop stays the contract's `authorization` field. |
| `setting-up-agentic-os` | Project bootstrap and signing identity | UNRELATED. |

Callers: `improving-skills-in-lab` templates invoke `cli-agent/scripts/run_agent.py` (named flags; unchanged and compatible). `transition_templates.yaml` names `agent_orchestrator.py` under a path without `.apm/` (unverified; not changed here).
