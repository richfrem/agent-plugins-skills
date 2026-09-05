---
name: interview-spec
plugin: agent-agentic-os
version: 1.0.0
description: "Universal developer intake and 4-Pillar Spec compiler. Detects and defers to native host interview/plan capabilities (Claude Code, Antigravity) when present, and provides Socratic Defaulting fallback for Copilot CLI, Gemini, or headless loops."
allowed-tools: Bash, Read, Write
---

# Interview Spec (`interview-spec`)

## Purpose
Acts as the universal front-door intake for non-trivial engineering tasks across all supported AI agent runtimes. Enforces Proposal Mode (strictly read-only) before code implementation:

1. **Native-First Deferral:** Detects active host runtime capabilities and defers to native environments (e.g. Claude Code native interactive intake or Antigravity planning mode).
2. **Socratic Defaulting Fallback:** Interrogates the developer 1–3 questions at a time, providing structured options with explicit recommended defaults.
3. **4-Pillar Specification Compilation:** Compiles the agreed requirements into a standardized `TASK_SPEC.md` contract and initializes the task in the SQLite control plane.

---

## The 4 Pillars of `TASK_SPEC.md`

Every compiled specification must satisfy:
1. **The Job:** Clear, unambiguous description of the system change and target subsystem paths.
2. **The Why:** Core problem statement, architectural rationale, and user/system impact.
3. **Semantic Guardrails & Operational Reasons:** Non-negotiable boundaries paired with concrete justifications explaining why the constraint exists.
4. **Objective Definition of Done (DoD):** Programmatic verification commands (`exit 0` tests, linters, structural audits).

---

## Usage

### 1. Detect Intake Mode & Start Intake
```bash
python3 scripts/interview_spec_engine.py
```

Route on the returned mode — do not proceed to Socratic questions if a native mode is returned:

| Returned Mode | Required Next Action |
|---|---|
| `DEFER_CLAUDE_NATIVE` | Invoke `EnterPlanMode` (native Claude Code Plan Mode). Do not run Socratic Defaulting. |
| `DEFER_ANTIGRAVITY` | Invoke Antigravity's native planning mode. Do not run Socratic Defaulting. |
| `EXECUTE_SOCRATIC_FALLBACK` | Proceed to Socratic Defaulting (1-3 questions at a time, structured options with an explicit recommended default) and compile `TASK_SPEC.md` directly. |

### 2. Register Task in SQLite Control Plane
```bash
python3 scripts/agent_control.py init --task-id "<task-id>" --title "<title>" --runtime "<runtime>" --spec-path "docs/plans/<task-id>-spec.md"
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "INTERVIEW" --reason "Beginning Socratic intake"
```

### 3. Transition to Peer Review Gate
Once `TASK_SPEC.md` is compiled:
```bash
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "PLAN_REVIEW" --reason "4-Pillar Spec compiled"
```
Proceed to clean-context review via `critical-auditor` before requesting human approval.
