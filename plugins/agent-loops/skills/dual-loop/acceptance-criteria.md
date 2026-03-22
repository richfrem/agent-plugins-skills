# Acceptance Criteria: Dual-Loop

## 1. Strategy Packet Fidelity
- [ ] Outer Loop ALWAYS generates an explicit, written markdown Strategy Packet containing constraints, file paths, and the "NO GIT" mandate before delegating.
- [ ] The Inner Loop is only fed the packet and necessary files, drastically isolating its context window.

## 2. Anti-Simulation Checks
- [ ] Outer Loop NEVER marks a task "Done" without manually checking the file deltas and mechanically running lint/test commands.
- [ ] "Assume it works" behavior results in an immediate audit failure.

## 3. Structured Correction
- [ ] Failed verifications are NEVER manually patched by the Outer Loop without feedback, unless tagged as `MINOR` (naming/style).
- [ ] Critical and Moderate failures are routed back to the Inner Loop via structured Markdown Correction Packets citing the exact failure logs.
