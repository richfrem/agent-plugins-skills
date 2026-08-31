---
name: dual-loop
plugin: agent-orchestration
description: "(Industry standard: Sequential Agent / Agent as a Tool) Primary Use Case: Delegating a well-defined task to a worker agent, verifying its execution, and repeating if necessary. Inner/outer agent delegation pattern via strategy packets, with verification and correction loops."
allowed-tools: Bash, Read, Write
---

# Dual-Loop (Inner/Outer Agent Delegation)

The **Dual-Loop** architecture splits work between a strategic **Outer Loop** (Supervisor/Director) and an execution-focused **Inner Loop** (tactical coding sub-agent). The Outer Loop organizes tasks, delegates via Strategy Packets, verifies output, and generates Correction Packets.

---

## 1. Setup & Interactive Orientation (Outer Loop)
1. **Decomposition**: Break work down into atomic, testable Work Packages (WPs).
2. **Interactive CLI & Model Selection**: Ask user for preferred CLI (`agy`, `claude`, `copilot`, `codex`, `llama`) and model. Consult `references/cheapest_models.json`.
3. **Workspace Isolation**: Receive isolated git worktree or directory branch from orchestrator.

---

## 2. Strategy Packet Generation & Dispatch
1. Author Strategy Packet (`handoffs/task_packet_NNN.md`):
   - Scope, target files, acceptance criteria, and explicit "NO GIT" rule for the Inner Loop.
2. Dispatch sub-agent with standard input redirected (`< /dev/null` to prevent `SIGTTIN` halts):
   ```bash
   python scripts/run_agent.py handoffs/task_packet_001.md <target_file> handoffs/result.md \
     "Execute strategy packet exactly." --cli <cli> --model "<model>" < /dev/null
   ```

---

## 3. Supervised Verification Gates
Upon completion signal, the Outer Loop verifies output:
1. **Delta Audit**: Run `git diff` to verify only authorized paths were modified; zero stub placeholders (`TODO`, `TBD`).
2. **Automated Test Run**: Run unit and integration tests mechanically.
3. **Outcome Resolution**:
   - **PASS**: Mark complete, update task tracker, proceed to closure.
   - **FAIL**: Issue a Correction Packet categorized by severity:
     - 🔴 **CRITICAL**: Fails compile/tests. Return immediate error diagnostics.
     - 🟡 **MODERATE**: Breaks architecture/conventions. Cite specific rule.
     - 🟢 **MINOR**: Style only. Supervisor fixes directly.

---

## 4. Retrospective & Closure
1. Conduct post-run self-assessment survey (`references/post_run_survey.md`).
2. If friction reoccurs 3+ times, flag for triple-loop escalation.
3. Merge verified branch and emit handoff summary.

---

## Operational References
* **Architecture Diagram**: [`references/diagrams/dual_loop_architecture.mmd`](references/diagrams/dual_loop_architecture.mmd)
* **Acceptance Criteria**: [`references/acceptance-criteria.md`](references/acceptance-criteria.md)
* **Fallback Protocol**: [`references/fallback-tree.md`](references/fallback-tree.md)
