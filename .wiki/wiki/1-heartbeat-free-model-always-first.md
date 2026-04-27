---
concept: 1-heartbeat-free-model-always-first
source: plugin-code
source_file: agent-agentic-os/skills/os-evolution-verifier/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.712024+00:00
cluster: architect
content_hash: da1edd41b2333cfa
---

# 1. Heartbeat (free model — always first)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
els

*(content truncated)*

## See Also

- [[1-basic-summarize-all-documents]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-copilot-gpt-5-mini]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-evolution-verifier/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.712024+00:00
