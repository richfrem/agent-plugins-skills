# Dual-Loop Meta-Tasks
<!-- To be included in Session Task List for any Dual-Loop Execution -->

## Phase A: Strategy (Outer Loop)
- [ ] **Verify planning artifacts**: Confirm spec, plan, and task documents exist
- [ ] **Create worktree**: Create an isolated workspace for the Inner Loop (or use branch-direct mode)
- [ ] **Generate Strategy Packet**: Create a targeted markdown packet holding context and acceptance criteria for the inner loop

## Phase B: Hand-off & Execution
- [ ] **Hand off to Inner Loop**: Launch the inner agent with the strategy packet (e.g., `claude "Read handoffs/task_packet_NNN.md. Execute the mission. Do NOT use git."`)
- [ ] **Inner Loop completes**: All acceptance criteria met, no git commands used

## Phase C: Verification (Outer Loop)
- [ ] **Verify result**: Run tests, check deltas, and validate output against the strategy packet
- [ ] **Verify clean state**: Ensure no git rules were violated and the inner loop workspace is clean
- [ ] **On PASS**: Commit in worktree, update task lane to `done`
- [ ] **On FAIL**: Hand off `correction_packet_NNN.md`, repeat Phase B

## Phase D: Closure
- [ ] **Seal**: Validate changes and record current state
- [ ] **Persist**: Sync session traces to long term memory
- [ ] **Retrospective**: Analyze session performance
- [ ] **End**: Push to remote and close domain
