# Stage 2: PEER_AGENT Verification Protocol

Every time PEER_AGENT receives `signal.wakeup` for eval, it MUST:

1. **Read the INNER_AGENT output file** at the path in the wakeup summary.
2. **Run `evaluate.py` independently** — do NOT read the score from the INNER_AGENT event.
   Use `evaluate.py` (loop gate) for KEEP/DISCARD; it compares against `results.tsv` baseline
   automatically and returns exit code 0=KEEP or 1=DISCARD.
   ```bash
   python ./scripts/evaluate.py --skill path/to/target/
   # Note: PEER_AGENT runs this from its OWN session independently.
   ```
3. DISCARD if exit code 1. Note: `results.tsv` is the authoritative per-experiment baseline
   (written by os-eval-runner). The improvement-ledger.md tracks cross-cycle OS-level trajectory.
4. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
5. Emit `eval.result` with KEEP/DISCARD verdict, score delta, and survey path:
   ```bash
   python "$KERNEL_PY" emit_event \
     --agent PEER_AGENT --type result --action eval.result \
     --status success --to ORCHESTRATOR --correlation-id "$CID" \
     --summary "verdict:KEEP score-before:0.82 score-after:0.89 gaps:adversarial survey:retrospectives/survey_DATE_PEER_AGENT.md"
   ```
