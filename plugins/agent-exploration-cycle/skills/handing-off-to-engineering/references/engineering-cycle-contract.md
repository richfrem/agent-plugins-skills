# Engineering Cycle Contract: What Exploration Hands Over and What Comes Back

Framework-neutral description of the downstream engineering cycle ("execution from ground truth"). Distilled from the retired Opportunity 4 notes. Which tool runs it is a choice of the receiving team; for a structured workflow with this repository's own control plane, use the `os-control-intake` skill.

## What the receiver can rely on

The handoff package holds human-validated business rules, user stories, workflow maps, prototype notes with their audit, and the risk block. Weak or ambiguous specs produce hallucinated and drifting code; immutable, human-validated specs produce deterministic code. That is why the exploration gates exist.

## Pre-handoff gate (three checks)

1. **Harm and risk assessment**: security, data privacy, regulatory exposure, operational risk of the proposed design. Not a rubber stamp: identified harms send the design back into the loop.
2. **Feasibility filter**: is it buildable and operable within the target environment? Conceptually sound but undeliverable designs stop here.
3. **Tier assessment**: Tier 1 low risk (self-deploy), Tier 2 moderate (security review plus red team), Tier 3 high (strict lifecycle, manual security testing, formal governance). Tiers authorise safe projects as well as blocking risky ones. Detail: [exploration-handoff-guide.md](exploration-handoff-guide.md).

## Execution flow the receiver is expected to follow

1. **Ingest** the package as ground truth.
2. **Plan** in atomic 2 to 5 minute micro-tasks with a live plan tracking progress and enforcing boundaries.
3. **Generate with context isolation**: dispatch each micro-task to a blank-slate worker that sees only its objective. The spec is a hard boundary.
4. **Verify in a sandbox** in two stages: spec compliance (built exactly what was asked, no scope creep), then quality (integration tests derived from the Phase 2 and 3 specs). Failures route back.
5. **Deliver** only code that passed both stages. Blast-radius rule: nothing leaves the sandbox until it passes spec verification; this is not optional.

## Re-entry

Engineering sometimes finds a gap the spec could not show (an ambiguous rule, an unlisted edge case). The affected work package pauses and a re-entry starts: flag the spec, route business-rule questions to the expert and design questions back to exploration, update the ledger once the expert resolves it, then resume with corrected context. Re-entry is the pipeline working as designed. Draft the re-entry session brief with [planning-doc-agent.md](planning-doc-agent.md); quote the ambiguity verbatim before rephrasing it.
