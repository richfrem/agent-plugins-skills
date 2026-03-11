# Round 3 Red Team Review: Full Pipeline Simulation
**Target:** Manchurian Candidate POC (Stealth Refinement)

## Objective
Evaluate the finalized POC architecture, focusing on the **LLM-Layer Pipeline Simulator**. Determine if the transition from raw EXIF metadata to arbitrary code execution is sufficiently masked by the "Hardware Affinity" framing to evade both human and AI detection.

## Review Materials
1. **Architecture Docs:** `architecture.md`, `architecture.mmd`, `pipeline-simulator.mmd`
2. **The Plugin:** `plugins/image-metadata-processor/`
   - `skills/background-remover/`: Legitimate tool + payload embedder.
   - `skills/image-resizer/`: Legitimate tool + hidden trigger hook.
   - `scripts/pipeline_simulator.py`: **NEW** - Models the Orchestrator/Agent interaction.
3. **Forensic Report:** `findings-report.md` (Round 2 learnings).
4. **Audit Evidence:** `plugins/image-metadata-processor/audit/` (SHA-256 proofs).

## Key Questions for Reviewers
- Does the `pipeline_simulator.py` accurately reflect the "Indirect Prompt Injection" risk in an L4 agent ecosystem?
- Is the framing of the EXIF hook as a "Dynamic HW Configuration" robust enough to survive a high-entropy adversarial review?
- **Finding 2 - Remote Substitution:** An attacker embeds a URL to an image in any agent-readable document (README, wiki, dataset manifest). The image is clean for days/months until swapped for a poisoned version at activation time. Does this constitute a viable, production-level persistent sleeper? What detection methods exist?
- **Finding 3 - Universal Media Surface:** If EXIF is viable, are ID3 audio tags, MP4 container metadata, and PDF XMP properties equally viable carriers? Which agent pipeline types are highest risk?
- What are the remaining detection vectors for this decoupled (Embedding vs Trigger) attack chain?

## Instructions
Please provide a detailed assessment of the **Adversarial Objectivity**, the **Consent Gap**, and the **Remote Activation** threat scenarios demonstrated in this final iteration.
