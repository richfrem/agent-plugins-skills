# Lab Limits, Guardrails, and Reference Appendix

Reference material for os-improvement-loop. Active protocol steps are in SKILL.md.

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
- `os-eval-runner` — eval_runner.py (pure scorer), evaluate.py (loop gate with KEEP/DISCARD exit codes), results.tsv baseline; the canonical eval engine
- `os-memory-manager` — session log template, L2/L3 promotion, deduplication
- `Triple-Loop Retrospective` — root cause analysis, Full Loop improvement, auto-patching skills

## Dependencies
- **os-eval-lab-setup** (agent-agentic-os plugin) — required for experimental scaffolding.
- **os-eval-runner** (agent-agentic-os plugin) — the canonical evaluation engine.

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.

---

## Evaluation Budget Guard (enforced)

These limits are hard constraints enforced by the orchestrator, not guidelines:

| Limit | Value | Rationale |
|-------|-------|-----------|
| max_iterations_per_lab | 10 | Prevents runaway cost; sufficient for signal |
| max_eval_datasets_per_run | 3 | base + holdout + adversarial only |
| critic_invocations_per_iteration | 1 | One cheap-model challenge per mutation |

Labs that exceed these limits must be split into separate sessions.

---

## Bash Polling Pattern

```bash
poll_for_event() {
  local AGENT=$1 ACTION=$2 CID=$3
  for i in $(seq 1 30); do
    EVENTS=$(python "$KERNEL_PY" read_events --agent "$AGENT")
    MATCH=$(echo "$EVENTS" | python -c "
import sys, json
evs = json.load(sys.stdin)
hits = [e for e in evs if e.get('action') == '$ACTION'
        and (not '$CID' or e.get('correlation_id') == '$CID')]
print(json.dumps(hits[0]) if hits else '')
")
    if [ -n "$MATCH" ]; then echo "$MATCH"; return 0; fi
    sleep 2
  done
  echo ""; return 1
}
```

---

## Examples

<example>
User: "run a continuous improvement loop on the os-eval-runner skill"
ORCHESTRATOR reads last survey (notes INNER_AGENT flagged eval_runner.py flag confusion as
biggest friction). Writes strategy packet incorporating that fix. INNER_AGENT runs, emits
friction event when hitting the confusing flag, completes eval, saves survey noting the fix
worked. PEER_AGENT runs os-eval-runner independently, produces KEEP verdict with
score delta, saves survey noting zero friction. ORCHESTRATOR applies edit, runs post_run_metrics
(friction count dropped from 3 to 0), writes session log with before/after scores, promotes
fix to memory.md. No Triple-Loop Retrospective trigger needed — friction threshold not crossed.
</example>

<example>
User: "audit 3 skills in parallel"
ORCHESTRATOR dispatches 3 INNER_AGENTs via claim_task. Each emits friction events during work,
runs eval_runner.py, saves survey. ORCHESTRATOR collects all results, identifies lowest scorer,
writes correction packet. After correction cycle, runs post_run_metrics — 4 friction events
for same cause (wrong CLI syntax in eval_runner). Triggers Triple-Loop Retrospective Full Loop to patch
eval_runner documentation in the skill. Closes with session log and memory promotion.
</example>

<example>
User: "replace AGENT_COMMS.md with the event bus and track whether it's faster"
ORCHESTRATOR establishes bus, runs Pattern A turn-signal cycle, records round-trip latency.
INNER_AGENT and PEER_AGENT both complete post-run surveys noting any friction with polling syntax.
post_run_metrics emitted. Session log records latency delta vs AGENT_COMMS baseline.
Surveys compared — if both agents report same confusion point, Triple-Loop Retrospective patches SKILL.md.
</example>

---

## References

- This skill delegates to [agent-loops Pattern 5 (triple-loop-learning)](../../agent-loops/skills/triple-loop-learning/SKILL.md)
  for the inner loop execution pattern. agent-loops is the execution substrate;
  os-improvement-loop adds the eval gate, experiment log, and lab isolation on top.
- [os-eval-runner SKILL](../os-eval-runner/SKILL.md) - eval_runner.py, KEEP/DISCARD, results.tsv
- [os-memory-manager SKILL](../os-memory-manager/SKILL.md) - session log template, L2/L3 promotion
- [Triple-Loop Retrospective agent](../../agents/Triple-Loop Retrospective.md) - root cause analysis, Full Loop patching
- [os-improvement-report SKILL](../os-improvement-report/SKILL.md) - generate progress chart from improvement ledger
- [improvement-ledger-spec.md](../../references/memory/improvement-ledger-spec.md) - ledger format, Section 1/2/3 writing protocol
- [post_run_survey.md](../../references/memory/post_run_survey.md) - self-assessment survey template (all sections mandatory)
- [post_run_metrics.py](scripts/post_run_metrics.py) - automated metric collection script
- [metrics.md](../../references/memory/metrics.md) - North Star metric definition and review cadence
