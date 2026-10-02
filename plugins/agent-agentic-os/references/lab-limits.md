# Lab Limits, Guardrails, and Reference Appendix

Reference material for os-improvement-loop. Active protocol steps are in SKILL.md.

## Contents
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Evaluation Budget Guard](#evaluation-budget-guard-enforced)
- [Bash Polling Pattern](#bash-polling-pattern)
- [Examples](#examples)
- [References](#references)

---

## Architecture

```
${CLAUDE_PROJECT_DIR}/context/
  events.jsonl                         <- shared event bus (append-only, atomic)
  agents.json                          <- permitted agent registry
  os-state.json                        <- shared counters and state
  agents/<id>.cursor                   <- per-agent read cursor (line-count)
  .locks/                              <- per-resource execution lock directories
  memory/YYYY-MM-DD.md                 <- session log written at every loop close
  memory/retrospectives/               <- per-agent self-assessment surveys
    survey_[DATE]_[TIME]_[AGENT].md    <- one file per agent per cycle
  memory.md                            <- L3 long-term facts (promoted from session logs)
  memory/hook-errors.log               <- hook failures (read by post_run_metrics.py)
```

Companion skills (all required for a complete loop):
- `triple-loop` — strategy packet format, correction packet protocol, verification
- `os-eval-lab-setup` — bootstrap experiment dirs (deploys program.md, evals.json, results.tsv); use **before** running any eval cycle on a new target
- `os-eval-runner` — single-skill evaluation loop (inner loop used by this skill)
- `os-eval-backport` — port validated skill improvements from test repo back to canonical source
- `os-memory-manager` — session log format, memory promotion protocol
- `os-improvement-report` — ASCII progress chart from improvement-ledger.tsv

---

## Dependencies

- Python 3.8+ (standard library only for core scripts)
- SQLite 3 (optional, for persistent memory backends)
- Claude Code CLI (or compatible host harness)

---

## Evaluation Budget Guard (enforced)

Before starting any loop iteration, check remaining budget:
- Max iterations per session: 10 (hard cap — stop and write session log even if target not met)
- Max consecutive DISCARD verdicts: 3 (triggers strategy review; switch to Triple-Loop Retrospective if stuck)
- Timeout per agent step: 300 seconds (kill and log failure event)

---

## Bash Polling Pattern

When waiting for events from another agent:

```bash
poll_for_event() {
  local agent="$1"
  local action="$2"
  local timeout="${3:-60}"
  local elapsed=0
  while [ $elapsed -lt $timeout ]; do
    if grep -q "\"agent\":\"$agent\".*\"action\":\"$action\"" context/events.jsonl 2>/dev/null; then
      echo "Event found: $action from $agent"
      return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "Timeout waiting for $action from $agent"
  return 1
}
```

---

## Examples

### Example 1: Continuous Improvement Loop
User: "run a continuous improvement loop on the os-eval-runner skill"
ORCHESTRATOR reads last survey (notes INNER_AGENT flagged eval_runner.py flag confusion as
biggest friction). Writes strategy packet incorporating that fix. INNER_AGENT runs, emits
friction event when hitting the confusing flag, completes eval, saves survey noting the fix
worked. PEER_AGENT runs os-eval-runner independently, produces KEEP verdict with
score delta, saves survey noting zero friction. ORCHESTRATOR applies edit, runs post_run_metrics
(friction count dropped from 3 to 0), writes session log with before/after scores, promotes
fix to memory.md. No Triple-Loop Retrospective trigger needed — friction threshold not crossed.

### Example 2: Parallel Multi-Skill Audit
User: "audit 3 skills in parallel"
ORCHESTRATOR dispatches 3 INNER_AGENTs via claim_task. Each emits friction events during work,
runs eval_runner.py, saves survey. ORCHESTRATOR collects all results, identifies lowest scorer,
writes correction packet. After correction cycle, runs post_run_metrics — 4 friction events
for same cause (wrong CLI syntax in eval_runner). Triggers Triple-Loop Retrospective Full Loop to patch
eval_runner documentation in the skill. Closes with session log and memory promotion.

### Example 3: Substrate Latency Comparison
User: "replace AGENT_COMMS.md with the event bus and track whether it's faster"
ORCHESTRATOR establishes bus, runs Pattern A turn-signal cycle, records round-trip latency.
INNER_AGENT and PEER_AGENT both complete post-run surveys noting any friction with polling syntax.
post_run_metrics emitted. Session log records latency delta vs AGENT_COMMS baseline.
Surveys compared — if both agents report same confusion point, Triple-Loop Retrospective patches SKILL.md.

---

## References

- This skill delegates to `agent-orchestration:triple-loop-learning` for the inner loop execution pattern. agent-orchestration is the execution substrate; os-improvement-loop adds the eval gate, experiment log, and lab isolation on top.
- `os-eval-runner` — eval_runner.py, KEEP/DISCARD, results.tsv
- `os-memory-manager` — session log template, L2/L3 promotion
- `triple-loop` agent — root cause analysis, Full Loop patching
- `os-improvement-report` — generate progress chart from improvement ledger
- [improvement-ledger-spec.md](memory/improvement-ledger-spec.md) — ledger format, Section 1/2/3 writing protocol
- [post_run_survey.md](memory/post_run_survey.md) — self-assessment survey template (all sections mandatory)
- [post_run_metrics.py](../scripts/post_run_metrics.py) — automated metric collection script
- [metrics.md](memory/metrics.md) — North Star metric definition and review cadence
