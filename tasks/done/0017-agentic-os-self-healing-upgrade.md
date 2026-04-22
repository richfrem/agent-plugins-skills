## 0017 — Agentic OS Plugin: Self-Healing & Self-Improving Upgrade

**Status:** In Planning  
**Priority:** P0  
**Effort:** L — spans agents, scripts, skills, and new reference layer across `plugins/agent-agentic-os/`  
**Metric:** V2 quality_score ≥ baseline on all modified skills; circuit-break + WAL patterns present and functional

---

## Problem Statement

The `plugins/agent-agentic-os/` plugin has a working eval-and-loop foundation but does NOT
implement the self-healing and self-improving control invariants defined in the v5 architecture.
Gaps span every layer — scripts, agents, skills, and references.

**Architecture reference:** `tasks/todo/agentic_os_self_healing_opportunities.md`

| Layer | File | Gap |
|:---|:---|:---|
| **Scripts** | `scripts/eval_runner.py` | Current formula is `(accuracy × 0.7) + (heuristic × 0.3)`. Missing C (execution efficiency) and F (friction reduction) dimensions for V2. No struggle signal tracking. |
| **Scripts** | `scripts/evaluate.py` | SHA256 guardian exists but no circuit-break state integration. No WAL write wrapper. |
| **Scripts** | `scripts/kernel.py` | Spinlocks exist but no WAL pattern (intent→execute→complete). No CIRCUIT_BREAK state enforcement. No heartbeat counter. |
| **Agents** | `agents/triple-loop-orchestrator.md` | No CIRCUIT_BREAK state written to `context/os-state.json`. No Invariant 6 gotcha gate before RECOVERY. No WAL calls. No cross-persona validation gate. No domain-pattern lookup before proposing. |
| **Agents** | `agents/triple-loop-architect.md` | Ignores `improvement/run-config.json` — re-asks user for all variables instead of consuming intake output. No invariant file seeding into lab. |
| **Agents** | `agents/improvement-intake-agent.md` | Handoff is prose-only. No kernel event emitted. No machine-readable HANDOFF_BLOCK. |
| **Skills** | `skills/os-eval-runner/SKILL.md` | No V2 formula documented. No struggle signal tier table. No domain-pattern lookup guidance. |
| **References** | `references/domain-patterns/` | Does not exist. Orchestrator has no pattern library to consult before inventing hypotheses. |

---

## Target State

After this upgrade, the plugin runs a coherent self-healing improvement loop:

```
User → improvement-intake-agent
       → HANDOFF_BLOCK + kernel event → context/events.jsonl
       → triple-loop-architect (reads run-config.json, seeds lab with invariants + gotchas)
       → triple-loop-orchestrator
           Phase 0: baseline + heartbeat
           Phase 1 per iteration:
             A. Classify failure
             B. Check domain-patterns/ first, then propose
             C. V2 evaluate.py gate
             [circuit break if consecutive_discards >= 4]
             [gotcha gate before RECOVERY — writes to target SKILL.md ## Gotchas]
             [WAL: intent → execute → complete on every state transition]
           Phase 2: gotcha backport + progress chart + Morning Handoff
       → os-eval-backport: cross-persona validation + SKILL.md ## Gotchas publish
```

---

## Workstream A — `scripts/eval_runner.py`: V2 Quality Formula

**A1. Add struggle signal tracking output**
- New output fields in `--json` mode: `struggle_events`, `c_score`, `f_score`
- `c_score` = success rate on first attempt (no retries, no exploratory commands before success)
- `f_score` = `1 - min(1.0, struggle_events / 10)`
- Struggle signal sources: Tier 1 (+2): `retry`, `error`, output mismatch. Tier 2 (+1): `ls`, `find`, `cat`, `--help` exploratory commands in eval interaction log

**A2. Update quality_score formula**
- New: `quality_score = (accuracy × 0.4) + (heuristic × 0.2) + (c_score × 0.2) + (f_score × 0.2)`
- Old: `quality_score = (routing_accuracy × 0.7) + (heuristic_score × 0.3)`
- Re-baseline all existing experiments after this change

**A3. Delta report in trace JSON**
- Per-iteration trace in `evals/traces/` must include A/H/C/F breakdown alongside existing fields
- Makes "why did the score change?" answerable from the trace alone

---

## Workstream B — `scripts/evaluate.py`: Circuit-Break Integration

**B1. Read circuit_break_scope before executing**
- At startup: read `context/os-state.json`. If `circuit_break_scope` is set and not `null`: refuse to run new proposals (Invariant 3 — Execution Freeze). Exit with `[evaluate.py] CIRCUIT_BREAK active — no proposals accepted` and exit code 3.

**B2. WAL wrapper for KEEP writes**
- Before appending KEEP row to results.tsv: write `INTENT: KEEP iter=N` to `context/wal.log`
- After appending: write `COMPLETE: KEEP iter=N`

---

## Workstream C — `scripts/kernel.py`: WAL + Circuit Breaker State

**C1. WAL log commands**
- Add `log_intent` and `log_complete` CLI subcommands
- Append `{"event": "intent"|"complete", "action": "...", "iter": N, "time": "..."}` to `context/wal.log`
- On startup: `check_wal` reads incomplete INTENT entries (no matching COMPLETE) and prints compensation warnings

**C2. Circuit breaker state in os-state.json**
- Add `set_circuit_break` CLI subcommand: writes `circuit_break_scope` and `circuit_break_since` to `context/os-state.json`
- Add `clear_circuit_break` CLI subcommand: clears both fields, writes `gotcha_emitted: true` as confirmation gate

**C3. Heartbeat counter**
- Add `heartbeat_increment` CLI subcommand: atomically increments `heartbeat_counter` in os-state.json
- `acquire_lock` lease check: add optional `--require-heartbeat-delta N` flag — fails if heartbeat_counter has not advanced by N since lock was last acquired

---

## Workstream D — `agents/triple-loop-orchestrator.md`

**D1. Loop State — add fields**
```
circuit_break_scope: null        # null | hypothesis | skill | system_halt
consecutive_discards_in_scope: 0
gotcha_emitted: false
```

**D2. Phase 0.6 — Domain Pattern Lookup**
Before establishing baseline, read `references/domain-patterns/` for the target skill's category.
If a matching pattern file exists: load it as the initial hypothesis context for Step A.
Log: "Domain pattern found: <file>" or "No domain pattern — fresh hypothesis mode."

**D3. Phase 1 Step A — Domain-Pattern-Informed Failure Classification**
When classifying failure, check if the failure type matches a known pattern in `references/domain-patterns/<skill-type>.md`.
If match: use the pattern's documented escape as the Step B proposal.
If novel: formulate new hypothesis and note it as a candidate for `references/domain-patterns/` after a KEEP.

**D4. Phase 1 Step C — Circuit Breaker Block**
After each DISCARD:
- Increment `consecutive_discards_in_scope`
- If `consecutive_discards_in_scope >= 4` AND `circuit_break_scope == null`:
  ```bash
  python scripts/kernel.py set_circuit_break --scope hypothesis --agent triple-loop-orchestrator
  python scripts/kernel.py log_intent --action circuit-break-entered --iter $ITER
  ```
  → Enter second-order mutation: propose change to `copilot_proposer_prompt.md` or a domain-pattern file
  → Reset `consecutive_discards_in_scope = 0`
- If second-order mutation also fails 4 times: escalate to `skill` scope. Stop and report to operator.

**D5. Phase 1 Step C — Invariant 6 Gotcha Gate (before RECOVERY)**
When exiting CIRCUIT_BREAK (a KEEP is achieved after being in circuit-break):
1. Write gotcha entry to target `SKILL.md` under `## Gotchas`:
   ```
   - **[<date>]** <Failure hypothesis that kept failing>. Escape: <what finally worked>.
     `discovery_source: agent_discovered`
   ```
2. Write intent + complete WAL entries
3. Call `kernel.py clear_circuit_break` ONLY after gotcha is written and committed
4. If gotcha not written: RECOVERY is blocked — loop emits kernel event `recovery-blocked` and halts

**D6. Phase 1 WAL Wrappers**
All state transitions call:
```bash
python scripts/kernel.py log_intent --action <transition> --iter $ITER
# ... execute transition ...
python scripts/kernel.py log_complete --action <transition> --iter $ITER
```

**D7. Phase 1 Step C — Cross-Persona Gate (optional)**
If `run-config.json` has `cross_persona_validation: true`:
After evaluate.py exits 0, pipe proposed SKILL.md through secondary gpt-5-mini judge:
```bash
python .agents/skills/copilot-cli-agent/scripts/run_agent.py /dev/null \
  $SKILL_PATH/SKILL.md /tmp/persona-judge.md \
  "Score this skill 0-100 for routing accuracy. Output only: APPROVE <score> or REJECT <score> <reason>"
```
Block KEEP if REJECT or if score delta > 10 vs evaluate.py result.

**D8. Phase 2 — Gotcha Backport Required Output**
Morning Handoff must include:
- Progress chart (existing)
- Summary of gotchas written to target SKILL.md `## Gotchas` this run (new — required output)
- Novel KEEPs flagged for `references/domain-patterns/` contribution (new)

---

## Workstream E — `agents/triple-loop-architect.md`

**E1. Phase 0.0 — Intake Config Check (new first step)**
Before resolving skill path or asking any user questions:
```bash
[ -f improvement/run-config.json ] && echo "config found" || echo "config missing"
```
If found: extract `target_skill`, `partition_id`, `run_depth`, `dispatch_strategy`, `seed_gotchas` from it.
Skip Phase 0.1 (skill path find) — set variables directly from config.
If not found: proceed with existing 0.1 user-prompted flow.

**E2. Phase 1.2b — Seed Gotchas into Lab**
After copying plugin files:
```bash
if [ $(jq '.seed_gotchas | length' improvement/run-config.json) -gt 0 ]; then
  echo "## Seed Gotchas (human_authored)" >> $LAB_PATH/gotchas.md
  jq -r '.seed_gotchas[]' improvement/run-config.json | while read g; do
    echo "- $g (discovery_source: human_authored)" >> $LAB_PATH/gotchas.md
  done
fi
```

**E3. Phase 1.2c — Write invariants.json into Lab**
```bash
cat > $LAB_PATH/invariants.json << 'EOF'
{
  "single_active_executor": "At most one RUNNING agent per partition_id",
  "no_unvalidated_promotion": "PROMOTING only if previously VALIDATING AND validation_passed == true",
  "execution_freeze": "No proposals accepted when circuit_break_scope is set",
  "memory_bounding": "Memory store size <= MAX_SIZE before GC triggers",
  "lease_sovereignty": "Only confirmed lease_owner_id may extend active lease",
  "transition_triggered_learning": "Every CIRCUIT_BREAK or DEGRADED exit MUST emit gotcha before RECOVERY"
}
EOF
```

---

## Workstream F — `agents/improvement-intake-agent.md`

**F1. Phase 4c — Kernel Event Emission**
After writing `run-config.json` and `session-brief.md`:
```bash
python scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "Intake complete for <target_skill> — <run_depth> run configured"
```
If `context/agents.json` does not list `improvement-intake-agent`, add it first.

**F2. Phase 5 — Machine-Readable HANDOFF_BLOCK**
Replace prose-only handoff with HANDOFF_BLOCK code fence (keep the user-facing message):
```
## HANDOFF_BLOCK
CONFIG: improvement/run-config.json
BRIEF: improvement/session-brief.md
ENTRY_STATE: IDLE
FIRST_ACTION: [baseline | hypothesis_0]
CROSS_PERSONA: [true | false]
SEED_GOTCHAS: [N]
DISPATCH: [copilot-cli | gemini-cli | claude-subagents]
```

---

## Workstream G — `skills/os-eval-runner/SKILL.md`

**G1. Add V2 Quality Formula section**
Insert before "# Skill Improvement Evaluator":
- V2 formula definition (A/H/C/F with weights)
- Struggle Signal tier table
- Instruction to check domain-patterns before proposing
- Guardian hash gate description (already implemented in evaluate.py, needs documenting)
- Zero-Context Operational Guide requirements for evaluated SKILL.md files

**G2. Add Domain Pattern guidance**
Under Phase 1 Step A: add instruction to check `references/domain-patterns/<skill-type>.md` before classifying failure. Novel KEEPs that represent new patterns → propose domain-pattern file contribution.

---

## Workstream H — `references/domain-patterns/` (New Layer)

**H1. Scaffold directory and initial files**
Create `references/domain-patterns/` with:
- `routing-skill.md` — known mutation strategies for skills primarily graded on routing accuracy (description keywords, `<example>` blocks, adversarial negatives)
- `python-script.md` — known strategies for Python module skills (type hints, error handling, function naming)
- `README.md` — how to read these files, how to contribute new patterns after a novel KEEP

**H2. Pattern file structure**
Each file follows:
```markdown
# Domain Patterns: <category>
## When to use this file
## Known Successful Mutations (ranked by frequency)
### Pattern 1: <name>
- Hypothesis: <what to change>
- Evidence: <which evals it fixed>
- Escape: <how to exit if this fails>
## Novel Candidates (awaiting 2nd KEEP confirmation)
```

---

## Delegation Strategy

This task is delegated as ONE premium Copilot request (`claude-sonnet-4-6`).

**Prompt file:** `temp/copilot_delegation_0017.md`  
**Output file:** `temp/copilot_output_0017.md`  
**Expected:** `===FILE:===` delimited patches for all workstream targets  
**Scope:** Workstreams C (kernel.py additions), D (orchestrator agent), E (architect agent), F (intake agent), G (eval-runner SKILL.md additions), H (domain-patterns scaffold)  
**Excluded from delegation:** Workstreams A and B (eval_runner.py + evaluate.py scripts) — Python script changes should be reviewed and applied by the main session, not delegated to a prompt-only model

---

## Acceptance Criteria

- `context/wal.log` is written during a live triple-loop run
- CIRCUIT_BREAK state appears in `context/os-state.json` after 4 consecutive discards
- Invariant 6: gotcha written to target SKILL.md `## Gotchas` before RECOVERY is permitted
- `triple-loop-architect.md` reads `improvement/run-config.json` in Phase 0 without asking user
- `improvement-intake-agent.md` emits kernel event and outputs `HANDOFF_BLOCK`
- `references/domain-patterns/routing-skill.md` exists with at least 2 documented mutation patterns
- `skills/os-eval-runner/SKILL.md` documents the V2 formula and struggle signal tiers
- All modified agent files pass existing evals.json routing tests with no regression
