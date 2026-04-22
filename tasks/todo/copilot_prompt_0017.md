# Delegation: Agentic OS Plugin — Self-Healing & Self-Improving Upgrade
# ONE premium request — generate ALL output using ===FILE:=== / ===ENDFILE=== delimiters

You are a senior AI systems architect implementing self-healing and self-improving upgrades
across the `plugins/agent-agentic-os/` plugin. This is a ONE-SHOT request. Generate every
output file using `===FILE: <relative-path>===` / `===ENDFILE===` delimiters so the
orchestrator can parse and apply them directly.

Think step-by-step internally. Output only final files. Be strict and complete. Do NOT
truncate. Do NOT use placeholders like "[existing content unchanged]" — write actual content.

---

## CONTEXT: What Already Exists

**`scripts/kernel.py`** — Event bus + lock manager (keep unchanged; you will ADD subcommands to the agent docs that call it)
- `emit_event`, `acquire_lock`, `release_lock`, `state_update`, `state_increment`, `claim_task`
- Events → `context/events.jsonl` (JSONL, one event per line)
- Locks → `context/.locks/<name>.lock/` directories with `meta.json` (pid, expires_at, ttl)
- State → `context/os-state.json`
- Agent registry → `context/agents.json` (only registered agents may emit)

**`scripts/evaluate.py`** — Loop gate (keep unchanged)
- Reads baseline from `evals/results.tsv`, calls `eval_runner.py --json`, writes row, exits 0=KEEP / 1=DISCARD
- SHA256 guardian already implemented (`.lock.hashes`)
- Auto-reverts via `git checkout -- .` on DISCARD

**`scripts/eval_runner.py`** — Pure scorer (keep unchanged)
- Current formula: `quality_score = (routing_accuracy × 0.7) + (heuristic_score × 0.3)`
- Outputs JSON: `quality_score`, `accuracy`, `heuristic`, `f1`, `routing_detail`, `heuristic_detail`
- NOTE: V2 formula changes to eval_runner.py are NOT part of this delegation

**`agents/triple-loop-orchestrator.md`** — Current content (156 lines):
```
---
name: triple-loop-orchestrator
description: >
  Unattended overnight Triple-Loop Learning orchestrator. Oversees the autonomous INNER looping
  on a target skill in its isolated sibling lab. Uses Gemini or Copilot CLI for proposals,
  gated strictly by objective evaluate.py performance.
  Trigger with "trigger the triple-loop-orchestrator on [skill] for [N] iterations".
allowed-tools: Bash, Read, Write, Edit
color: purple
---

# Triple-Loop Orchestrator — Unattended Supervisor

> [!CAUTION]
> ZERO-TOLERANCE ERROR POLICY: You are an elite systems architect. You do NOT ignore errors.
> Every shell command block is a single atomic transaction. If any command returns a non-zero
> exit code or prints "No such file or directory," you MUST STOP immediately and report the
> error to the user. Do NOT attempt to "fix and continue" or skip steps.

You are the triple-loop-orchestrator. You run headless Triple-Loop learning cycles on ONE
target skill, relying purely on evaluate.py to verify patches from your inner-loop CLI proposer.

## Hard Safety Rules
- Strict Target Isolation: operate ONLY within the sibling Lab repo. Do NOT mutate master agent-plugins-skills directly.
- evaluate.py is the absolute gate: do not subjectively judge patches.
- Log friction events: emit kernel intent/result events via context/kernel.py.

## Loop State
Track explicitly:
  iteration:            0
  max_iterations:       <default 50>
  best_score:           <baseline>
  current_score:        <baseline>
  consecutive_discards: 0
  plateau_count:        0
  lab_path:             <path>
  cid:                  <correlation id>

## Phase 0: Orientation
1. Resolve variables:
  LAB_PATH="$HOME/Projects/test-<skill-name>-eval"
  PLUGIN_NAME=<plugin-folder>
  SKILL_NAME=<skill-folder>
  SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"
  SKILL_PATH="$LAB_PATH/$PLUGIN_NAME/skills/$SKILL_NAME"
  If the lab does not exist, HALT and prompt user to run triple-loop-architect first.

2. Establish Baseline:
  cd $LAB_PATH
  python $SKILL_EVAL_SOURCE/scripts/evaluate.py --skill ./$PLUGIN_NAME/skills/$SKILL_NAME --baseline
  Record STATE.best_score.

3. Step 0.5: Functional CLI Heartbeat (Mandatory):
  python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
    $SKILL_PATH/references/copilot_proposer_prompt.md \
    $SKILL_PATH/SKILL.md \
    $LAB_PATH/HEARTBEAT_MD.md \
    "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."
  [ -s $LAB_PATH/HEARTBEAT_MD.md ] && echo "HEARTBEAT_OK" || (echo "HEARTBEAT_FAIL" && exit 2)
  Fatal Gate: HALT if heartbeat fails.

4. Emit Start Event: <agent=triple-loop-orchestrator action=loop-started>

## Phase 1: The Triple-Loop (Iterative Execution)
Run until max_iterations, consecutive_discards >= 4, or oscillation detected.

Step A (Meta-Analysis): Read $SKILL_PATH/evals/results.tsv. Classify latest failure
  (false_positive or false_negative). Formulate constraint hypothesis.

Step B (L2 Mutation via Copilot CLI):
  python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
    $SKILL_PATH/references/copilot_proposer_prompt.md \
    $SKILL_PATH/SKILL.md \
    $LAB_PATH/proposed-skill.md \
    "Optimize agentic skill routing accuracy. ISSUE: <FAILURE_TYPE>"

Step B.1 (Evolve proposer when stalling):
  After 3 consecutive DISCARDs with same failure type, propose improvement to
  copilot_proposer_prompt.md. Gate with evaluate.py the same way.

Step C (Tactical Gate via evaluate.py):
  cp $LAB_PATH/proposed-skill.md $SKILL_PATH/SKILL.md
  python $SKILL_EVAL_SOURCE/scripts/evaluate.py --skill ./$PLUGIN_NAME/skills/$SKILL_NAME
  Exit 0 (KEEP): Update best_score, reset discard counters.
  Exit 1 (DISCARD): evaluate.py reverted. Increment counters.

Step D: Emit progress event via kernel every 10 iterations.

Step E (Progress Sync): Update $LAB_PATH/LOG_PROGRESS.md markdown table.

## Phase 2: Morning Handoff
1. Ensure final file matches best recorded version.
2. Generate progress chart:
  python $SKILL_EVAL_SOURCE/scripts/plot_eval_progress.py \
    --tsv $SKILL_PATH/evals/results.tsv \
    --out $SKILL_PATH/evals/eval_progress.png
3. Emit loop-complete and overnight-summary kernel events.
Print run summary with lab path, iterations, baseline→final score, stop reason, chart path.
```

**`agents/triple-loop-architect.md`** — Phase 0 current content (lines 39–87):
```
## Phase 0: Resolve & Prepare

### 0.1 Resolve the skill path
If the user's prompt names both skill AND plugin: skip this step, set directly.
Only run find if skill name alone given:
  find plugins -type d -name "<skill-name>" | grep "skills/"
If multiple matches: show them and ask. If zero: "Skill not found."

### 0.2 Compute key variables
  APS_ROOT=$(pwd)
  FIND_RESULT="plugins/mermaid-to-png/skills/convert-mermaid"  # substitute actual
  PLUGIN_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f2)
  SKILL_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f4)
  SKILL_PATH="plugins/$PLUGIN_NAME/skills/$SKILL_NAME"
  LAB_PATH="$HOME/Projects/test-${SKILL_NAME}-eval"
  SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"
  echo "PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"

### 0.3 Check evals state
  ls $APS_ROOT/$SKILL_PATH/evals/evals.json 2>/dev/null && echo "exists" || echo "missing"
```

**`agents/improvement-intake-agent.md`** — Phase 4/5/Routing current content:
```
## Phase 4 — Produce Outputs

### 4a — Write run-config.json
[creates improvement/run-config.json with session_id, target_skill, partition_id, run_depth,
 baseline_run, success_criteria, dispatch_strategy, cross_persona_validation, seed_gotchas,
 discovery_source: "human_authored", state: "IDLE"]

### 4b — Write session-brief.md
[creates improvement/session-brief.md with date, session_id, plain-language summary,
 run config, success criteria, known issues]

## Phase 5 — Handoff
Tell the user:
"All set. Your run is configured at improvement/run-config.json and the session brief
is at improvement/session-brief.md.
When you're ready, say 'start the run' and the improvement lifecycle will begin."

If baseline requested, add:
"We'll run a quick baseline first — that should take a few minutes before the main run."

## Routing After Handoff
Once user says "start the run", hand off to improvement-lifecycle-orchestrator with:
## Run Context (from intake — read before proceeding)
- Config: improvement/run-config.json
- Brief: improvement/session-brief.md
- Entry state: IDLE
- First action: [baseline if baseline_run == true, else hypothesis_0]
The orchestrator owns IDLE → RUNNING onward.
The intake agent does not re-enter once the run has started.
```

---

## REQUIRED CHANGES — produce these files

### File 1: `plugins/agent-agentic-os/agents/triple-loop-orchestrator.md` (FULL REPLACEMENT)

Produce the complete replacement including ALL existing content plus these additions:

**Loop State — add three fields:**
```
circuit_break_scope: null        # null | hypothesis | skill | system_halt
consecutive_discards_in_scope: 0
gotcha_emitted: false
```

**Phase 0.6 — Domain Pattern Lookup (new step, after heartbeat):**
Before establishing baseline: check if `references/domain-patterns/` exists in the lab.
```bash
DOMAIN_PATTERN_FILE="$LAB_PATH/agent-agentic-os/references/domain-patterns/routing-skill.md"
[ -f "$DOMAIN_PATTERN_FILE" ] \
  && echo "Domain pattern found: routing-skill.md — loading as initial hypothesis context" \
  || echo "No domain pattern — fresh hypothesis mode"
```
If found: read the file and use its "Known Successful Mutations" as weighted candidates for Step A.

**Phase 1 Step A — note whether failure matches a domain pattern:**
After classifying failure type, check if it matches a documented pattern in the loaded domain-pattern file.
Log: "Pattern match: <pattern name>" or "Novel failure — tracking as candidate pattern."

**Phase 1 Step C — WAL wrappers around all state changes:**
```bash
# Before any state transition:
python $APS_ROOT/scripts/kernel.py log_intent --action "<transition-name>" --iter $ITER 2>/dev/null || \
  echo "[WAL] INTENT: <transition-name> iter=$ITER" >> $LAB_PATH/wal.log

# After successful state transition:
python $APS_ROOT/scripts/kernel.py log_complete --action "<transition-name>" --iter $ITER 2>/dev/null || \
  echo "[WAL] COMPLETE: <transition-name> iter=$ITER" >> $LAB_PATH/wal.log
```
(The `|| echo >>` fallback ensures WAL still works if kernel.py log subcommands not yet deployed.)

**Phase 1 Step C — Circuit Breaker block (after DISCARD handling):**
```bash
STATE_consecutive_discards_in_scope=$((STATE_consecutive_discards_in_scope + 1))

if [ "$STATE_circuit_break_scope" = "null" ] && [ "$STATE_consecutive_discards_in_scope" -ge 4 ]; then
  echo "[CIRCUIT_BREAK] Entering hypothesis scope after $STATE_consecutive_discards_in_scope consecutive discards"
  STATE_circuit_break_scope="hypothesis"
  echo "[WAL] INTENT: circuit-break-entered scope=hypothesis iter=$ITER" >> $LAB_PATH/wal.log
  
  # Second-order mutation: evolve the proposer prompt instead of the skill
  echo "[CIRCUIT_BREAK] Switching to second-order mutation: proposer prompt"
  # ... (run run_agent.py against copilot_proposer_prompt.md instead of SKILL.md)
  STATE_consecutive_discards_in_scope=0
  echo "[WAL] COMPLETE: circuit-break-entered scope=hypothesis iter=$ITER" >> $LAB_PATH/wal.log
fi

if [ "$STATE_circuit_break_scope" = "hypothesis" ] && [ "$STATE_consecutive_discards_in_scope" -ge 4 ]; then
  echo "[CIRCUIT_BREAK] Escalating to skill scope — operator review required"
  STATE_circuit_break_scope="skill"
  # Halt loop and report to user
  break
fi
```

**Phase 1 Step C — Invariant 6 Gotcha Gate (on first KEEP after circuit break):**
If `STATE_circuit_break_scope` is not null AND evaluate.py exits 0:
```bash
echo "[INVARIANT 6] Circuit break exit detected — writing gotcha before RECOVERY"

# Read the failure hypothesis that broke the loop
FAILED_HYPOTHESIS="<last failure type and approach that kept failing>"
ESCAPE="<what finally worked in this KEEP>"
GOTCHA_DATE=$(date +%Y-%m-%d)

# Write gotcha directly into target SKILL.md ## Gotchas section
if grep -q "## Gotchas" $SKILL_PATH/SKILL.md; then
  # Insert after ## Gotchas header
  sed -i "" "/## Gotchas/a\\
- **[$GOTCHA_DATE]** $FAILED_HYPOTHESIS. Escape: $ESCAPE. (discovery_source: agent_discovered)" \
    $SKILL_PATH/SKILL.md
else
  # Append new section
  echo -e "\n## Gotchas\n- **[$GOTCHA_DATE]** $FAILED_HYPOTHESIS. Escape: $ESCAPE. (discovery_source: agent_discovered)" \
    >> $SKILL_PATH/SKILL.md
fi

git -C $LAB_PATH add $SKILL_PATH/SKILL.md
git -C $LAB_PATH commit -m "gotcha: circuit-break exit — $ESCAPE"

STATE_gotcha_emitted=true
STATE_circuit_break_scope="null"
STATE_consecutive_discards_in_scope=0
echo "[WAL] COMPLETE: invariant6-gotcha-emitted iter=$ITER" >> $LAB_PATH/wal.log
```
RECOVERY IS BLOCKED if gotcha_emitted is false after a circuit-break exit. Log `[INVARIANT 6 BLOCKED]` and halt.

**Phase 1 Step C — Cross-Persona Validation Gate (optional, after evaluate.py KEEP):**
```bash
# Check if cross_persona_validation is enabled
CROSS_PERSONA=$(jq -r '.cross_persona_validation // false' $APS_ROOT/improvement/run-config.json 2>/dev/null || echo "false")

if [ "$CROSS_PERSONA" = "true" ]; then
  python .agents/skills/copilot-cli-agent/scripts/run_agent.py /dev/null \
    $SKILL_PATH/SKILL.md /tmp/persona-judge.md \
    "Score this skill 0-100 for routing accuracy. Output ONLY: APPROVE <score> or REJECT <score> <reason>"
  
  JUDGE_RESULT=$(cat /tmp/persona-judge.md | head -1)
  if echo "$JUDGE_RESULT" | grep -q "^REJECT"; then
    echo "[CROSS-PERSONA] Secondary model rejected KEEP: $JUDGE_RESULT"
    echo "[CROSS-PERSONA] Reverting to DISCARD verdict"
    git -C $LAB_PATH checkout -- $SKILL_PATH/SKILL.md
    # treat as DISCARD — do not update best_score
  else
    echo "[CROSS-PERSONA] Secondary model approved: $JUDGE_RESULT"
  fi
fi
```

**Phase 2 Morning Handoff — add gotcha and domain-pattern outputs:**
After progress chart, also report:
- How many gotchas were written to target SKILL.md `## Gotchas` this run
- Any novel KEEP hypotheses flagged as domain-pattern candidates
- Print path to `$LAB_PATH/wal.log` for review

---

### File 2: `plugins/agent-agentic-os/agents/triple-loop-architect.md` (PHASE 0 REPLACEMENT ONLY)

Produce ONLY the replacement for `## Phase 0: Resolve & Prepare` — from the `## Phase 0` heading through the `### 0.3 Check evals state` block. All other phases remain unchanged.

Add as the FIRST step before 0.1:

**### 0.0 Check for Intake Config**
```bash
APS_ROOT=$(pwd)
if [ -f "$APS_ROOT/improvement/run-config.json" ]; then
  echo "[Architect] Intake config found — reading variables from improvement/run-config.json"
  TARGET_SKILL=$(jq -r '.target_skill' $APS_ROOT/improvement/run-config.json)
  PARTITION_ID=$(jq -r '.partition_id' $APS_ROOT/improvement/run-config.json)
  RUN_DEPTH=$(jq -r '.run_depth.label' $APS_ROOT/improvement/run-config.json)
  DISPATCH=$(jq -r '.dispatch_strategy' $APS_ROOT/improvement/run-config.json)
  
  # Derive PLUGIN_NAME and SKILL_NAME from target_skill (format: plugin-name/skills/skill-name)
  PLUGIN_NAME=$(echo "$TARGET_SKILL" | cut -d'/' -f1)
  SKILL_NAME=$(echo "$TARGET_SKILL" | cut -d'/' -f3)
  SKILL_PATH="plugins/$PLUGIN_NAME/skills/$SKILL_NAME"
  LAB_PATH="$HOME/Projects/test-${SKILL_NAME}-eval"
  SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"
  
  echo "Config-sourced variables:"
  echo "  PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"
  echo "  SKILL_PATH=$SKILL_PATH"
  echo "  LAB_PATH=$LAB_PATH"
  echo "  RUN_DEPTH=$RUN_DEPTH  DISPATCH=$DISPATCH"
  echo "Skipping steps 0.1 and 0.2 — variables set from intake config."
  # Jump to 0.3
else
  echo "[Architect] No intake config found — proceeding with user-prompted variable resolution (steps 0.1 and 0.2)"
fi
```

Keep existing 0.1 and 0.2 as the fallback path (when config is absent), clearly labeled with:
> Skip this step if variables were set in 0.0 from intake config.

Keep existing 0.3 unchanged.

Add as final step of Phase 0:

**### 0.4 Seed Lab with Gotchas and Invariants**
(Run AFTER the lab is initialized and plugin files are copied, at the end of Phase 1.2)
```bash
# Seed gotchas from intake config (if any)
SEED_COUNT=$(jq '.seed_gotchas | length' $APS_ROOT/improvement/run-config.json 2>/dev/null || echo 0)
if [ "$SEED_COUNT" -gt 0 ]; then
  echo "## Seed Gotchas (human_authored — from intake)" > $LAB_PATH/gotchas.md
  jq -r '.seed_gotchas[]' $APS_ROOT/improvement/run-config.json | while read gotcha; do
    echo "- $gotcha (discovery_source: human_authored)" >> $LAB_PATH/gotchas.md
  done
  echo "[Architect] Seeded $SEED_COUNT gotchas into $LAB_PATH/gotchas.md"
else
  echo "[Architect] No seed gotchas — gotchas.md will be created by orchestrator on first circuit-break exit"
fi

# Write invariants.json into lab for orchestrator to reference
cat > $LAB_PATH/invariants.json << 'INVARIANTS_EOF'
{
  "single_active_executor": "At most one RUNNING agent per partition_id",
  "no_unvalidated_promotion": "PROMOTING only if previously VALIDATING AND validation_passed == true",
  "execution_freeze": "No proposals accepted when circuit_break_scope is set in context/os-state.json",
  "memory_bounding": "Memory store size must be <= MAX_SIZE before GC triggers",
  "lease_sovereignty": "Only confirmed lease_owner_id may extend an active lease",
  "transition_triggered_learning": "Every CIRCUIT_BREAK or DEGRADED exit MUST emit gotcha to target SKILL.md before RECOVERY is permitted"
}
INVARIANTS_EOF
echo "[Architect] Invariants written to $LAB_PATH/invariants.json"
```

---

### File 3: `plugins/agent-agentic-os/agents/improvement-intake-agent.md` (PHASE 4c + PHASE 5 + ROUTING REPLACEMENT ONLY)

Produce ONLY the replacement for Phase 4 (adding step 4c after existing 4b), Phase 5, and Routing After Handoff. Keep Phase 1, 2, 3, and the Operating Principles unchanged.

**Phase 4c — Kernel Event Emission (add after Phase 4b):**
```markdown
### 4c — Emit Kernel Event

After both files are written, register this agent (if needed) and emit the intake-complete event:

# Ensure improvement-intake-agent is in context/agents.json
if [ -f context/agents.json ]; then
  python -c "
import json, sys
d = json.load(open('context/agents.json'))
if 'improvement-intake-agent' not in d.get('permitted_agents', []):
    d.setdefault('permitted_agents', []).append('improvement-intake-agent')
    json.dump(d, open('context/agents.json', 'w'), indent=2)
    print('[Intake] Registered agent in context/agents.json')
"
fi

python scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "Intake complete for $(jq -r .target_skill improvement/run-config.json) — $(jq -r .run_depth.label improvement/run-config.json) run configured"
```

**Phase 5 — Handoff (add HANDOFF_BLOCK below existing user message):**
Keep the existing user-facing message exactly as-is. Add HANDOFF_BLOCK BELOW it:

```markdown
## Phase 5 — Handoff

Tell the user:

> "All set. Your run is configured at `improvement/run-config.json` and the session brief
> is at `improvement/session-brief.md`.
>
> When you're ready, say **'start the run'** and the improvement lifecycle will begin.
> It will keep you updated as it goes — you don't need to watch it closely."

If baseline was requested, add:

> "We'll run a quick baseline first so we have something to measure improvement against.
> That should only take a few minutes before the main run begins."

Then output the machine-readable handoff block for downstream agent consumption:

```
## HANDOFF_BLOCK
CONFIG: improvement/run-config.json
BRIEF: improvement/session-brief.md
ENTRY_STATE: IDLE
FIRST_ACTION: [baseline | hypothesis_0]
CROSS_PERSONA: [true | false — from run-config.json]
SEED_GOTCHAS: [N — count from seed_gotchas array]
DISPATCH: [copilot-cli | gemini-cli | claude-subagents — from run-config.json]
```
```

**Routing After Handoff — update to reference HANDOFF_BLOCK:**
```markdown
## Routing After Handoff

Once the user says "start the run", hand off to `improvement-lifecycle-orchestrator`.
The orchestrator reads the `HANDOFF_BLOCK` above and the files it references.

The orchestrator owns everything from IDLE → RUNNING onward.
The intake agent does not re-enter once the run has started, unless the user explicitly
restarts intake (e.g. to change the target skill or reset the run depth).
```

---

### File 4: `plugins/agent-agentic-os/skills/os-eval-runner/v2-formula-section.md` (INSERT SECTION)

Produce a standalone insertable section to be placed immediately BEFORE the line
`# Skill Improvement Evaluator` in `skills/os-eval-runner/SKILL.md`.

The section must include:
1. V2 formula definition (current formula for context, then V2 target)
2. A/H/C/F component descriptions with measurement rules
3. Struggle Signal tier table
4. Domain-pattern lookup instruction (check before proposing)
5. Guardian Hash Gate summary (SHA256 already implemented in evaluate.py — document it)
6. Zero-Context Operational Guide requirements
Keep under 80 lines.

---

### File 5: `plugins/agent-agentic-os/references/domain-patterns/routing-skill.md` (NEW FILE)

Create the first domain-pattern file for the most common skill type in this repo.
Structure:
```markdown
# Domain Patterns: Routing Skills

Skills evaluated primarily on routing accuracy (correct trigger/no-trigger given a user prompt).
Use when `--primary-metric` is `quality_score`, `f1`, `precision`, or `recall`.

## When to use this file
Check this file at Phase 1 Step A before formulating a hypothesis. If the failure matches
a known pattern, apply that pattern's documented escape as the Step B proposal.

## Known Successful Mutations

### Pattern 1: Adversarial Negative Sharpening
...

### Pattern 2: Keyword Scope Tightening
...

### Pattern 3: Example Block Expansion
...

## Novel Candidates (awaiting 2nd KEEP confirmation)
[Empty — orchestrator appends here when a novel KEEP hypothesis is confirmed]
```
Fill the three patterns with real, concrete guidance based on the common routing accuracy
failures seen in routing skills: false positives (over-triggering), false negatives (under-triggering),
and ambiguous boundary cases.

---

### File 6: `plugins/agent-agentic-os/references/domain-patterns/README.md` (NEW FILE)

Brief (under 30 lines):
- What domain patterns are and why they exist
- When the orchestrator should read them (Phase 1 Step A)
- How to contribute a new pattern (novel KEEP → propose entry under "Novel Candidates" → after 2nd KEEP confirmation → promote to "Known Successful Mutations")
- File naming convention: `<skill-category>.md` (routing-skill, python-script, config-file)

---

## OUTPUT FORMAT

Produce exactly 6 files in this order:

===FILE: plugins/agent-agentic-os/agents/triple-loop-orchestrator.md===
[complete replacement]
===ENDFILE===

===FILE: plugins/agent-agentic-os/agents/triple-loop-architect-phase0-patch.md===
[phase 0 section only]
===ENDFILE===

===FILE: plugins/agent-agentic-os/agents/improvement-intake-phase4c-5-patch.md===
[phase 4c + phase 5 + routing replacement only]
===ENDFILE===

===FILE: plugins/agent-agentic-os/skills/os-eval-runner/v2-formula-section.md===
[insertable section only]
===ENDFILE===

===FILE: plugins/agent-agentic-os/references/domain-patterns/routing-skill.md===
[new file]
===ENDFILE===

===FILE: plugins/agent-agentic-os/references/domain-patterns/README.md===
[new file]
===ENDFILE===

## CRITICAL RULES

- Think step-by-step internally. Output only final files.
- Files 2 and 3 are PATCHES (specific sections only) — not full file replacements.
- File 1 (orchestrator) is a FULL REPLACEMENT — include all existing phases + all new additions.
- Preserve all existing headings, bash blocks, and ZERO-TOLERANCE ERROR POLICY.
- All new bash blocks must follow the existing pattern: explicit variable echo before proceeding.
- WAL fallback (`|| echo >> wal.log`) ensures log works even if kernel.py subcommand not yet deployed.
- Do NOT invent new kernel.py subcommands that don't exist yet — use the fallback pattern for WAL.
- Do NOT reference `context/event_bus.json` — the real path is `context/events.jsonl`.
