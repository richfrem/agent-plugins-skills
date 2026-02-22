# Dual-Loop Meta-Tasks
<!-- To be included in Session Task List for any Dual-Loop Execution -->

## Phase A: Strategy (Outer Loop)
- [ ] **Verify planning artifacts**: Confirm spec, plan, and task documents exist
- [ ] **Create worktree**: Create an isolated workspace for the Inner Loop (or use branch-direct mode)
- [ ] **Generate Strategy Packet**: `python3 plugins/orchestrator/dual_loop/generate_strategy_packet.py --tasks-file <PATH> --task-id <WP-ID>`

## Phase B: Hand-off & Execution
- [ ] **Hand off to Inner Loop**: Launch the inner agent with the strategy packet (e.g., `claude "Read handoffs/task_packet_NNN.md. Execute the mission. Do NOT use git."`)
- [ ] **Inner Loop completes**: All acceptance criteria met, no git commands used

## Phase C: Verification (Outer Loop)
- [ ] **Verify result**: `python3 plugins/orchestrator/dual_loop/verify_inner_loop_result.py --packet <PATH> --verbose`
- [ ] **Verify clean state**: `python3 plugins/orchestrator/verify_workflow_state.py --wp <WP-ID> --phase review`
- [ ] **On PASS**: Commit in worktree, update task lane to `done`
- [ ] **On FAIL**: Hand off `correction_packet_NNN.md`, repeat Phase B

## Phase D: Closure
- [ ] **Seal**: Validate changes and record current state
- [ ] **Persist**: Sync session traces to long term memory
- [ ] **Retrospective**: Analyze session performance
- [ ] **End**: Push to remote and close domain
