---
name: os-evolution-verifier
plugin: agent-agentic-os
description: >
  Verifies that os-architect actually causes evolution — not just words.
  Dispatches os-architect in single-shot simulation mode for a given test scenario,
  then checks for real artifact presence (new files, HANDOFF_BLOCK, plan files).
  Reports PASS / FAIL with grep evidence. Accumulates results into a test report.
  Use after any changes to os-architect, os-evolution-planner, or improvement-intake-agent.
argument-hint: "[test-scenario-file | all]"
tools: ["Bash", "Read", "Write"]
---

## Overview

After evolving os-architect or its downstream agents, you need proof that the changes
actually work. This skill dispatches os-architect in single-shot simulation mode for
each test scenario and verifies artifact presence — not by reading the transcript, but
by checking that expected files exist or expected content appears in output.

**Evolution is verified by artifact presence, not by transcript review.**

---

## Artifact Verification Table

| Evolution Type | What to Check |
|---|---|
| Path C (Gap Fill) | `SKILL.md` present at expected path |
| Path B (Update) | `tasks/todo/<slug>-plan.md` AND `tasks/todo/copilot_prompt_<slug>.md` written |
| Path A+ (No-op) | No new files written; HANDOFF_BLOCK contains `STATUS: complete` |
| Category 3 (Lab Setup) | `improvement/run-config.json` written AND HANDOFF_BLOCK emitted |
| HANDOFF_BLOCK integrity | All 7 fields present: INTENT, TARGET, PATH, DISPATCH, STATUS, OUTPUTS, NEXT_ACTION |
| Confidence model | Low confidence prompt → clarifying question appears before Phase 2 audit |
| Evolution Integrity Gate | When logic in `plugins/` changes, `references/map-debt.md` or `evolution-log.md` is updated, or `Evolution-Check: none` is present |

---

## Procedure

1. **Resolve Test Inputs** — `all` scans `temp/os-evolution-verifier/scenarios/*.json`; a specific
   file is validated for required fields (`id`, `name`, `path`, `prompt`, `expected_artifact`,
   `artifact_check`). If none found, report that scenarios must be created or generated via
   context-bundler red-team mode.
2. **Dispatch os-architect** — single-shot simulation via `copilot-cli-agent`: heartbeat check
   first (`gpt-5-mini`), then main dispatch (`claude-sonnet-4.6`, non-interactive) with
   `plugins/agent-agentic-os/agents/os-architect-agent.md` as system prompt and the scenario
   prompt as the user turn. Verify output is non-empty before proceeding.
3. **Artifact Verification** — run the check named in the scenario's `artifact_check` field:
   HANDOFF_BLOCK integrity (7 required fields), file existence (Path B/C), no-op check (Path A+),
   or confidence-model ordering check.
4. **Record Result** — append a per-scenario PASS/FAIL block to
   `temp/os-evolution-verifier/test-report.md`.
5. **Summary Report** — after all scenarios, write the structured `EVOLUTION_VERIFICATION` block
   per scenario plus an aggregate Run Summary. A run PASSES only if an artifact exists, HANDOFF_BLOCK
   has all 7 fields, STATUS isn't `crashed`, VERDICT is PASS (not PARTIAL), and the Evolution
   Integrity Gate is satisfied. Adversarial WS-N scenarios must FAIL at least 4 of 6 — passing all of
   them means the verifier isn't operational.
6. **Persist to Experiment Log** — always call `os-experiment-log` to append the report; `temp/` is
   ephemeral and results are lost on shell restart otherwise.

Exact bash commands, the EVOLUTION_VERIFICATION field table, the Binary PASS/FAIL contract, and the
Run Summary format are in `references/detailed-reference.md`.

---

## Detailed Reference

Full commands for each phase, output formats, scenario file JSON format, smoke tests, and gotchas
(output-length checks, simulation vs. real dispatch, HANDOFF_BLOCK grep patterns, confidence-model
ordering, temp/ ephemerality, OUTPUTS path normalization, Category 5 dual-dispatch) are all in
`references/detailed-reference.md`.
