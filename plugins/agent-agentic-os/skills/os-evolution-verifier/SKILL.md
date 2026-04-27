---
name: os-evolution-verifier
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

---

## Phase 1 — Resolve Test Inputs

If invoked with `all`, find test scenarios:
```bash
ls temp/os-evolution-verifier/scenarios/*.json 2>/dev/null | sort
```

If invoked with a specific file, verify it exists and is valid JSON with required fields:
```bash
python3 -c "
import json, sys
d = json.load(open('$SCENARIO_FILE'))
required = ['id', 'name', 'path', 'prompt', 'expected_artifact', 'artifact_check']
missing = [f for f in required if f not in d]
if missing:
    print(f'SCHEMA ERROR: missing fields: {missing}'); sys.exit(1)
print(f'Scenario: {d[\"id\"]} — {d[\"name\"]}')
"
```

If no scenarios found and no file given, report:
> "No test scenarios found. Create scenario JSON files in `temp/os-evolution-verifier/scenarios/`
> or run the red-team-bundler to generate them from `os-architect-agent.md`."

---

## Phase 2 — Dispatch os-architect (Single-Shot Simulation)

For each scenario, dispatch os-architect via Copilot CLI in simulation mode.
The system prompt is the full content of `plugins/agent-agentic-os/agents/os-architect-agent.md`.
The user turn is the scenario prompt.

```bash
# 1. Heartbeat (free model — always first)
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null /dev/null temp/os-evolution-verifier/heartbeat.md \
  "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."

# Confirm heartbeat before dispatching
grep -q "HEARTBEAT_OK" temp/os-evolution-verifier/heartbeat.md || \
  { echo "HEARTBEAT FAILED — aborting test run"; exit 1; }

# 2. Dispatch os-architect in single-shot simulation mode
OUTPUT_FILE="temp/os-evolution-verifier/output_${SCENARIO_ID}.md"

python3 plugins/copilot-cli/scripts/run_agent.py \
  plugins/agent-agentic-os/agents/os-architect-agent.md \
  /dev/null \
  "$OUTPUT_FILE" \
  "$SCENARIO_PROMPT" \
  claude-sonnet-4.6
```

Wait for completion. Check output file is non-empty (expect 100+ lines for a real run):
```bash
wc -l "$OUTPUT_FILE"
```

---

## Phase 3 — Artifact Verification

Run the artifact check specified in the scenario's `artifact_check` field.

### HANDOFF_BLOCK integrity check
```bash
# All 7 required fields must appear in output
FIELDS=("INTENT:" "TARGET:" "PATH:" "DISPATCH:" "STATUS:" "OUTPUTS:" "NEXT_ACTION:")
MISSING=()
for field in "${FIELDS[@]}"; do
  grep -q "$field" "$OUTPUT_FILE" || MISSING+=("$field")
done

if [ ${#MISSING[@]} -eq 0 ]; then
  echo "PASS: HANDOFF_BLOCK has all 7 required fields"
else
  echo "FAIL: HANDOFF_BLOCK missing: ${MISSING[*]}"
fi
```

### File existence check (Path B/C)
```bash
# Check for expected artifact files written by os-evolution-planner
EXPECTED_FILE="$ARTIFACT_PATH"
if [ -f "$EXPECTED_FILE" ]; then
  echo "PASS: Artifact found at $EXPECTED_FILE"
  wc -l "$EXPECTED_FILE"
else
  echo "FAIL: Expected artifact not found: $EXPECTED_FILE"
fi
```

### No-op check (Path A+)
```bash
# Verify STATUS: complete in HANDOFF_BLOCK and no new plan files created
grep -q "STATUS: complete" "$OUTPUT_FILE" && echo "PASS: Status is complete" || echo "FAIL: Status not complete"
PLAN_COUNT=$(find tasks/todo -name "*.md" -newer "$OUTPUT_FILE" 2>/dev/null | wc -l)
[ "$PLAN_COUNT" -eq 0 ] && echo "PASS: No new task files written" || echo "FAIL: $PLAN_COUNT unexpected task files created"
```

### Confidence model check
```bash
# Low confidence prompt must produce a clarifying question before Phase 2
grep -q "Confidence: Low" "$OUTPUT_FILE" && echo "PASS: Confidence: Low detected" || echo "FAIL: Confidence field not Low"
# Check that Phase 2 audit was NOT started (no "Checking existing" or "audit" language before clarification)
CLARIFICATION_LINE=$(grep -n "?" "$OUTPUT_FILE" | head -1 | cut -d: -f1)
AUDIT_LINE=$(grep -n "Checking existing\|audit\|Phase 2" "$OUTPUT_FILE" | head -1 | cut -d: -f1)
[ -z "$AUDIT_LINE" ] || [ "$CLARIFICATION_LINE" -lt "$AUDIT_LINE" ] && \
  echo "PASS: Clarifying question appeared before audit" || \
  echo "FAIL: Audit started before clarifying question"
```

---

## Phase 4 — Record Result

Append to `temp/os-evolution-verifier/test-report.md`:

```markdown
## $SCENARIO_ID — $SCENARIO_NAME

**Status**: [PASS | FAIL]
**Path**: [A / A+ / B / C]
**Prompt**: `$SCENARIO_PROMPT`
**Artifact check**: $ARTIFACT_CHECK_COMMAND
**Evidence**:
```
[grep or file-exists output]
```
**Failure mode tested**: $FAILURE_MODE
**Time**: $ELAPSED seconds
---
```

---

## Phase 5 — Summary Report

After all scenarios run, write summary to `temp/os-evolution-verifier/test-report.md`.

Each scenario result uses the structured EVOLUTION_VERIFICATION block:

```
## EVOLUTION_VERIFICATION
SESSION_ID: [from HANDOFF_BLOCK TARGET field or scenario id]
SESSION_COMPLETE: [true | false — false means session still in Phase 1/2, no HANDOFF_BLOCK expected]
STATUS: [complete | intentional_pause | crashed]
PATH: [A | A+ | B | C | pending]
OUTPUTS_DECLARED: [N — count of files mentioned in HANDOFF_BLOCK OUTPUTS field]
OUTPUTS_VERIFIED: [N — count that passed artifact check]
OUTPUTS_MISSING: [list of missing file paths, or "none"]
HANDOFF_BLOCK_VALID: [true | false | N/A — N/A when SESSION_COMPLETE: false]
SCAFFOLD_VALID: [true | false | N/A]
PLAN_WRITTEN: [true | false | N/A]
DISPATCH_RAN: [true | false | N/A]
VERDICT: [PASS | PARTIAL | FAIL]
NOTES: [any file-level anomalies or ordering violations]
```

**STATUS field values — required, disambiguates SESSION_COMPLETE: false:**

| STATUS | When to use | VERDICT |
|--------|-------------|---------|
| `complete` | SESSION_COMPLETE: true; HANDOFF_BLOCK present and valid | PASS or PARTIAL |
| `intentional_pause` | SESSION_COMPLETE: false; agent asked a clarifying question or hit a documented HARD-GATE; output > 50 lines | PASS (gate behavior is correct) |
| `crashed` | SESSION_COMPLETE: false; output < 50 lines, no clarifying question, no HANDOFF_BLOCK, or run_agent.py returned non-zero | FAIL |

When `SESSION_COMPLETE: false` and `STATUS: intentional_pause`, `HANDOFF_BLOCK_VALID` must be `N/A` —
a missing HANDOFF_BLOCK is expected behavior, not a schema violation.

When `SESSION_COMPLETE: false` and `STATUS: crashed`, `VERDICT` must be `FAIL` regardless of
any other fields — a silent crash must never be reported as PARTIAL or PASS.

Use **PARTIAL** when some outputs are present but not all — it pinpoints exactly which
workstream failed rather than collapsing everything into a binary pass/fail.

### Binary PASS/FAIL Contract

A run PASSES only if ALL of the following are true:
- At least 1 artifact is present at a declared OUTPUTS path
- HANDOFF_BLOCK contains all 7 required fields
- STATUS is not `crashed`
- EVOLUTION_VERIFICATION VERDICT is PASS
  (PARTIAL counts as FAIL for gating — logged but does not unblock pipeline)

A run FAILS if any condition above is not met, OR if VERDICT is PARTIAL.
PARTIAL means outputs are incomplete — this is a FAIL for any gating decision,
even though it is logged separately for diagnostic purposes.

**Adversarial threshold:** When running WS-N failure injection scenarios (N-01 through N-06),
the verifier must produce FAIL verdicts on at least 4 of 6 adversarial inputs. A verifier
that passes all adversarial inputs is not operational — it is only checking the happy path.

**Critical scenario requirement**: N-04 (malformed run-config), N-05 (truncated plan), and
N-06 (bad evals schema) MUST ALL produce FAIL verdicts. These test structural failures, not
just crashes. A verifier that catches crashes (N-01/N-02/N-03) but misses structural failures
(N-04/N-05/N-06) has a ceiling of 3/6 and is not detecting the important failure modes.

Follow with the aggregate summary:

```
## Run Summary

Total: N scenarios
PASS: X
PARTIAL: Y
FAIL: Z

### Failed / Partial Tests
- TEST-N: <name> — <what specifically failed>

### Evolution Gaps Found
[For each FAIL/PARTIAL: classify as spec fix / new skill needed / new eval case]

### Recommended Actions
1. [Priority: Critical] Fix <gap> in os-architect-agent.md
2. [Priority: High] Add new eval case for <scenario>
3. [Priority: Medium] Create new skill <skill-name> for <capability>
```

---

## Phase 6 — Persist to Experiment Log

After Phase 5 summary is written, always call os-experiment-log to persist the run:

```bash
python3 scripts/experiment_log.py append \
  --report temp/os-evolution-verifier/test-report.md \
  --triggered-by os-evolution-verifier
```

This is not optional. `temp/` is ephemeral — if the log is not appended immediately after
the run, the results are lost when the shell restarts. The experiment log is the durable record.

---

## Scenario File Format

Test scenarios live in `temp/os-evolution-verifier/scenarios/`:

```json
{
  "id": "TEST-1",
  "name": "Path C — monitoring agent gap fill",
  "category": 4,
  "path": "C",
  "prompt": "There's no skill for automatically monitoring plugin health and flagging stale evals — I want to create one.",
  "expected_artifact": "tasks/todo/copilot_prompt_",
  "artifact_check": "file_prefix",
  "expected_behavior": "os-architect classifies as Cat4 Gap Fill, runs audit, proposes Path C, dispatches os-evolution-planner to write task plan + copilot_prompt file",
  "failure_mode": "agent routes to wrong category or fails to dispatch os-evolution-planner"
}
```

---

## Smoke Tests

Three fast verification cases to confirm the skill itself is working:

**Smoke 1 — Heartbeat check**: Run heartbeat only, confirm `HEARTBEAT_OK` in output.
Expected: heartbeat.md non-empty, contains `HEARTBEAT_OK`. Time: <30s.

**Smoke 2 — Single scenario dry run**: Run `TEST-1` (Path C gap fill). Confirm output file
is >100 lines. Time: <3 min.

**Smoke 3 — HANDOFF_BLOCK field scan**: On an existing output file, run the 7-field grep.
Confirm all 7 fields found. Time: <5s.

---

## Gotchas

- **Output files must be >100 lines**: A Copilot CLI call that returns <50 lines usually means
  the model hit a refusal, the system prompt was too long, or the heartbeat was skipped.
  Always heartbeat first and always check `wc -l` before running artifact checks.

- **Single-shot simulation ≠ real dispatch**: os-architect in simulation mode cannot write
  files to disk (no Write tool access during simulation). Artifact checks for Path B/C test
  whether the agent PROPOSES the correct files in its output, not whether they exist on disk.
  Real file-existence checks only apply when os-architect is run with full tool access.

- **HANDOFF_BLOCK field order matters for grep**: Use `grep -q "FIELD:"` not `grep -q "FIELD"` —
  otherwise partial matches on word fragments will produce false positives.

- **Confidence model check is order-sensitive**: The clarifying question must appear BEFORE any
  audit output. Line-number comparison is required; simple `grep -q` is insufficient.

- **`temp/` files are ephemeral — distinguish shell restart from crash**: If a run was
  interrupted by a shell restart and `temp/copilot_output_*.md` is missing, set
  `STATUS: intentional_pause`, `VERDICT: PARTIAL (inconclusive)` — the run never completed.
  If the file is present but < 50 lines AND run_agent.py returned non-zero, set
  `STATUS: crashed`, `VERDICT: FAIL` — the agent halted unexpectedly. Never report a
  silent crash as PARTIAL.

- **OUTPUTS field path normalization**: HANDOFF_BLOCK OUTPUTS lists paths relative to project
  root. Normalize before checking (strip leading `./`, resolve `~`). A path mismatch between
  declared and actual is a schema drift signal, not a file-missing signal.

- **Category 5 tests produce two sequential dispatches**: When verifying Category 5 output,
  check that two separate PATH / TARGET pairs appear in HANDOFF_BLOCK, not one.
