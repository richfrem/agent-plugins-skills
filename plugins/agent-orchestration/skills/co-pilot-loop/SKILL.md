---
name: co-pilot-loop
plugin: agent-orchestration
description: "Cooperative Multi-Agent Coordination Loop. Spawns a lightweight companion sub-agent (Gemini 3.5 Flash Low) to perform spec discovery, planning, and implementation. The primary agent (Claude) acts as the QA Director, answering Gemini's questions, approving the spec/plan, and running verification tests. Assumes the superpowers plugin is installed in the target repository."
allowed-tools: Bash, Read, Write
---

# Cooperative Co-Pilot Loop (Supervisor Protocol)

The **Co-Pilot Loop** splits software engineering tasks between a **Supervisor (Outer Loop — you)** and an **Executor (Inner Loop — a lightweight companion sub-agent)**. The Supervisor acts as the product manager and QA director, while the Executor performs spec writing, planning, and coding inside an isolated worktree.

You do not know which CLI or chat interface the user is using — and that's fine. The skill is model-agnostic. It reads the cheapest model for the active CLI at runtime.

---

## 1. Setup & Orientation

### Step 1A — Determine the active CLI backend
Ask the user once (or detect from context):
> "Which CLI backend is available for the sub-agent? (`agy`, `claude`, `copilot`, `codex`, `llama`)"

### Step 1B — Look up the cheapest model for that backend
Consult `plugins/agent-orchestration/references/cheapest_models.json` (or `references/cheapest_models.md`) to select the cheapest model for the detected CLI backend.

### Step 1C — Spawn the sub-agent
Use `run_agent.py` with the resolved CLI and model:
```bash
# For agy (recommended — cheapest Gemini)
python ./scripts/run_agent.py <PERSONA_FILE> <PACKET_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  --cli agy --model "Gemini 3.5 Flash (Low)" < /dev/null

# For claude CLI
python ./scripts/run_agent.py <PERSONA_FILE> <PACKET_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  --cli claude --model claude-haiku-4.5 < /dev/null

# For copilot CLI
python ./scripts/run_agent.py <PERSONA_FILE> <PACKET_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  --cli copilot --model gpt-5.4-nano < /dev/null
```

> **CRITICAL**: Always append `< /dev/null` to prevent `SIGTTIN` process suspension in background execution.

---

## 2. Strategy Packet & Handoff

Create an isolated Git worktree or branch for the Executor. Generate a `Strategy Packet` (via `scripts/agent_orchestrator.py packet`) containing:

1. **Objective** — what feature/bug is being implemented.
2. **Constraints** — TDD rules, symlink policy, coding conventions, no deletions.
3. **No-Git Rule** — the Executor is strictly **forbidden** from running any `git` commands.
4. **Spec output path** — e.g. `docs/superpowers/specs/YYYY-MM-DD-<feature>-spec.md`.
5. **Plan output path** — e.g. `implementation_plan.md`.

Hand the Strategy Packet to the Executor and start the parallel session.

---

## 3. Supervision & Review Gates

You (the Supervisor) enforce the following sequential gates. **No gate may be skipped.**

### Gate 1 — Design Spec Review
When the Executor generates a design spec, audit it:
- No vague placeholders (`TODO`, `TBD`, `REPLACE`).
- Architectural decisions align with existing ADRs and codebase patterns.
- *Action*: Approve → proceed to Gate 2. Reject → pass specific written feedback back to Executor.

### Gate 2 — Implementation Plan Review
Review the Executor's `implementation_plan.md` / `task.md`:
- Files grouped logically by dependency layer.
- A clear automated verification plan is included.
- *Action*: Approve → proceed to Gate 3. Reject → return with specific revision notes.

### Gate 3 — QA & Verification
Once Executor signals completion, run the verification suite:
```bash
python3 run_tests.py    # or npm run test / npm run build
git diff                # inspect all changed files
```

Classify issues using the severity schema:
- 🔴 **CRITICAL** — fails compile or tests. Return error logs to Executor immediately.
- 🟡 **MODERATE** — works but violates conventions or ADRs. Return with specific ADR.
- 🟢 **MINOR** — stylistic only. Fix directly yourself.

Generate correction packets via:
`python ./scripts/agent_orchestrator.py correct --packet handoffs/task_NNN.md --feedback "Reason"`

---

## 4. Retrospective & Closure
Once all verification tests pass:
1. Merge branch to `main` (from repo root only, never inside worktree).
2. Update RLM summaries and write session retrospective (`scripts/agent_orchestrator.py retro`).
3. Commit validated changes.
