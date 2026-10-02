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

# Evolution Verifier (`os-evolution-verifier`)

Verifies that evolution agents cause real changes by checking for artifact presence (new files, handoff blocks, plan files) rather than relying on transcript text.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Artifact Verification Matrix](#artifact-verification-matrix)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Physical Artifact Verification**: Evolution is proven strictly by physical file existence and content presence, never conversational transcripts.
2. **Binary Pass/Fail Contract**: A run only passes if expected files exist and required handoff block fields are complete.
3. **Persist Results**: Always record verification outcomes to `os-experiment-log` before `temp/` is cleared.

## Quick start

Run verification on a single evolution scenario:

```bash
python3 scripts/run_evolution_scenario.py --scenario <path-to-scenario.json>
```

## Workflow

1. **Resolve Scenarios**: Locate target test scenario or scan `temp/os-evolution-verifier/scenarios/*.json`.
2. **Dispatch Simulation**: Dispatch `os-architect` in single-shot non-interactive simulation mode via subagent.
3. **Verify Artifacts**: Check physical existence of target files and validate `HANDOFF_BLOCK` integrity.
4. **Compile Report**: Append PASS/FAIL assessment block to test report.
5. **Persist Findings**: Invoke `os-experiment-log` to archive test outcomes permanently.

## Artifact Verification Matrix

| Evolution Type | Verification Target |
|---|---|
| Gap Fill (Path C) | `SKILL.md` present at expected spoke path |
| Update (Path B) | `tasks/todo/<slug>-plan.md` and prompt written |
| No-Op (Path A+) | No unexpected files; `HANDOFF_BLOCK` complete |
| Lab Setup | `run-config.json` written with valid configuration |

## Verification

Confirm test report is compiled and recorded:

```bash
test -f "temp/os-evolution-verifier/test-report.md" && echo "Report verified"
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Exact dispatch commands, EVOLUTION_VERIFICATION schema, and failure trees.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Pass/fail grading criteria and scenario formats.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when simulation or verification fails.
