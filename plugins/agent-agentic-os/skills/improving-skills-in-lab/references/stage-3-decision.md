# Stage 3: ORCHESTRATOR Decision Protocol

On **KEEP** verdict:
1. Apply the approved changes to the canonical skill or workflow doc.
2. Emit `orchestrator.decision`.
3. Update task tracking to Done.

On **DISCARD** verdict:
1. Write a correction packet to `handoffs/correction-${CID}.md` using severity schema:
   - CRITICAL: feature missing or tests fail
   - MODERATE: works but violates architecture or standards
   - MINOR: works, style issues only
2. Re-signal INNER_AGENT with correction packet for next sub-cycle.
3. Do NOT emit `orchestrator.decision` until KEEP is received.
