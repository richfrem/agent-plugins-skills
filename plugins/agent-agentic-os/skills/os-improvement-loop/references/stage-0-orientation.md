# Stage 0: Setup and Orientation

**Goal**: Every agent orients before any work begins. No agent starts cold.

> **New target?** Before running any eval cycle on a target skill for the first time, use
> `os-eval-lab-setup` to bootstrap the experiment dir. This deploys:
> - `evals/evals.json` — test prompts with `should_trigger` boolean schema (REQUIRED — legacy
>   `expected_behavior` string fields score 0.0 and will destroy accuracy)
> - `evals/results.tsv` — baseline ledger (written when you run `evaluate.py --baseline`)
> - `references/program.md` — your optimization goal, target score, and max iterations
>
> Without this setup, `evaluate.py` will fail with exit code 2 (missing experiment structure).

1. **ORCHESTRATOR reads (in order):**
   - `context/memory/improvement-ledger.md` — cross-session OS-level trajectory per skill, survey-to-action trace, north star trend
   - `<target-experiment-dir>/evals/results.tsv` — per-experiment baseline and iteration history (written by os-eval-runner's evaluate.py); this is the authoritative score history for the specific target being improved
   - `context/memory/tests/registry.md` — what has been tested, what was recommended next
   - `context/memory.md` (L3 long-term facts)
   - Last session log: `context/memory/YYYY-MM-DD.md`
   - Last retrospective surveys: `context/memory/retrospectives/` (most recent per agent)
   - `context/events.jsonl` last 100 lines for friction patterns from prior cycle
   - `plugins/<active-plugin>/references/map-debt.md` — open Map Debt entries; surface any with `Repeat: YES` as the first priority before writing the strategy packet
2. **ORCHESTRATOR answers before writing any strategy packet:**
   - What does the improvement ledger show for this target's score trajectory? (flat = try a different approach; declining = revert last change)
   - Is the north star completion rate regressing 2+ sessions in a row? (if yes, trigger Triple-Loop Retrospective before this cycle)
   - What does the test registry say was the recommended next test?
   - Has this hypothesis already been confirmed or falsified? (check registry — do not re-run)
   - Which survey friction items from prior cycles have not been acted on yet? (Section 2 gaps)
3. Confirm `agents.json` lists all participating agents.
4. Each agent emits `agent_start`:
   ```bash
   python "$KERNEL_PY" emit_event \
     --agent ORCHESTRATOR --type agent_start --action registered \
     --summary "ORCHESTRATOR online — registry read, designing test from prior results"
   ```
5. **ORCHESTRATOR documents the test scenario** in `context/memory/tests/[CYCLE_ID]_[TARGET_SLUG].md`
   per `references/testing/test-registry-protocol.md` — hypothesis, acceptance criteria, failure criteria,
   prior results consulted, known weaknesses — BEFORE emitting `loop.start`.
6. Add row to `context/memory/tests/registry.md` with status IN PROGRESS.
7. ORCHESTRATOR emits `loop.start`:
   ```bash
   CYCLE_ID="cycle-$(date +%Y%m%d-%H%M%S)"
   python "$KERNEL_PY" emit_event \
     --agent ORCHESTRATOR --type intent --action loop.start \
     --correlation-id "$CYCLE_ID" \
     --summary "target:[TARGET_SLUG] hypothesis:[one-line] scenario:tests/${CYCLE_ID}_[TARGET_SLUG].md"
   ```
8. ORCHESTRATOR writes strategy packet informed by the test scenario, prior survey
   recommendations, and friction patterns from the last cycle.
