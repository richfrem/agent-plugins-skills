---
name: co-pilot-loop
plugin: agent-loops
description: "Cooperative Multi-Agent Coordination Loop. Spawns a lightweight companion sub-agent (Gemini 3.5 Flash Low) to perform spec discovery, planning, and implementation. The primary agent (Claude) acts as the QA Director, answering Gemini's questions, approving the spec/plan, and running verification tests. Assumes the superpowers plugin is installed in the target repository."
allowed-tools: Bash, Read, Write
---

# Cooperative Co-Pilot Loop (Supervisor Protocol)

The **Co-Pilot Loop** splits software engineering tasks between a **Supervisor (Claude / Outer Loop)** and an **Executor (Gemini 3.5 Flash / Inner Loop)**. The Supervisor acts as the product manager and QA, while the Executor performs the coding in an isolated environment.

---

## 1. Setup & Orientation

### Bootstrapping the Sub-Agent
Before spawning, prompt the user for execution details (or use default configuration):
*   **CLI Backend**: `agy` (or `copilot`, `claude`)
*   **LLM Model**: `gemini-3.5-flash`

---

## 2. Strategy Packet & Handoff

Create a Git worktree or target branch to isolate the work. Generate the `Strategy Packet` containing:
1.  **Objective**: What feature/bug is being implemented.
2.  **Constraints**: Strict compliance with TDD rules (`test-driven-development.md`), symlinking policies, and coding conventions.
3.  **No Git Rule**: The Executor is strictly forbidden from running Git commands or editing version history.

Hand the Strategy Packet to the Executor (Gemini 3.5 Flash) and start the parallel session.

---

## 3. Supervision & Review Gates

You (Claude) must monitor the sub-agent's progress and enforce the following approvals:

### Gate 1: Design Spec Review
When Gemini generates a design spec (e.g. `docs/superpowers/specs/Y-M-D-spec.md`), audit it:
*   Ensure there are no vague placeholders ("TODO", "TBD").
*   Verify the architectural decisions align with the codebase's existing patterns.
*   *Action*: Approve to proceed, or reject with specific design feedback.

### Gate 2: Implementation Plan Review
Review Gemini's `implementation_plan.md` or `task.md`:
*   Ensure files are grouped logically by dependencies.
*   Ensure a clear verification test plan is included.
*   *Action*: Approve, or request updates.

### Gate 3: QA & Verification
Once Gemini signals completion, execute the verification suite:
*   Run tests: `python3 run_tests.py` or `npm run test`.
*   Inspect file deltas (`git diff`).
*   Classify issues into severity tiers:
    *   🔴 **CRITICAL**: Fails compiling or tests. (Action: Reject, pass error logs back to Gemini).
    *   🟡 **MODERATE**: Code works but violates conventions/ADRs. (Action: Flag for revision).
    *   🟢 **MINOR**: Stylistic naming updates. (Action: Fix directly and proceed).

---

## 4. Retrospective & Closure

Once all verification tests pass:
1.  Merge the worktree or checkout branch back to `main`.
2.  Update the language model (RLM) summaries in the cache profiles.
3.  Commit and push the changes to Git.
4.  Write a session retrospective capturing any optimizations to the prompt templates or skill instructions.
