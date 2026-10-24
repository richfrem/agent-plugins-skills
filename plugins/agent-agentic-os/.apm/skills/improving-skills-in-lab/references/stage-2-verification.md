# Stage 2: PEER_AGENT Verification Protocol

Every time PEER_AGENT receives `signal.wakeup` for eval, it MUST:

1. **Read the INNER_AGENT output file** at the path in the wakeup summary.
2. **Run the `score` mode independently** — do NOT read the score from the INNER_AGENT event.
   The scorer's `evaluate.py` compares against the `results.tsv` baseline and returns exit
   code 0=KEEP or 1=DISCARD. PEER_AGENT runs it from its OWN session.
3. DISCARD if exit code 1. Note: `results.tsv` is the authoritative per-experiment baseline
   (written by the `score` mode). The improvement-ledger.md tracks cross-cycle OS-level trajectory.
4. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
5. Emit `eval.result` with KEEP/DISCARD verdict, score delta, and survey path:
   ```bash
   python "$KERNEL_PY" emit_event \
     --agent PEER_AGENT --type result --action eval.result \
     --status success --to ORCHESTRATOR --correlation-id "$CID" \
     --summary "verdict:KEEP score-before:0.82 score-after:0.89 gaps:adversarial survey:retrospectives/survey_DATE_PEER_AGENT.md"
   ```
