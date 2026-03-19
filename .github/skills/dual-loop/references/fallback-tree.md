# Procedural Fallback Tree: Dual-Loop

## 1. Inner Loop Refuses NO GIT Constraint
If the inner loop agent (e.g., Copilot or a sub-process) repeatedly attempts to commit code or run git commands despite instructions:
- **Action**: The Orchestrator (Outer Loop) must intervene, revert the git state, and generate a Correction Packet explicitly citing a Protocol Violation. Instruct the Inner Loop to only edit the files and STOP.

## 2. Inner Loop Modifies Out-of-Scope Files
If delta verification shows the Inner Loop modified files unlisted in the Strategy Packet:
- **Action**: Fail the verification gate. Revert the out-of-scope files. Generate a Correction Packet warning the Inner Loop of scope creep. The Outer Loop must never auto-merge unauthorized filesystem modifications.

## 3. Test Suite Missing or Broken
If the Outer Loop attempts to mechanical verify via tests, but the repository has no tests or they were already broken:
- **Action**: The Outer Loop must manually run the code or instantiate a new, minimal regression test specific to the Strategy Packet to verify the behavior before merging.

## 4. Inner Loop Stuck in Correction Loop (Max Iterations)
If the Inner Loop has received 3+ Correction Packets and is still failing the acceptance criteria:
- **Action**: Break the loop. The Orchestrator reclaims the task. Refactor the Strategy Packet (it was likely too broad or ambiguous) or swap the Inner Loop engine for a higher reasoning model (e.g., Opus instead of Haiku).
