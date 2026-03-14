---
name: sanctuary-orchestrator-integration
description: "Sanctuary-specific integration skill connecting the Guardian to the Agent Loops Orchestrator. Maps the Separation of Concerns between strategic workflow definition (Spec-Kitty), cognitive execution (Orchestrator tracks), and environmental sovereignty (Guardian closures)."
---

# Sanctuary Orchestrator Integration

**Status:** Active
**Domain:** Project Sanctuary
**Depends on:** `agent-loops/orchestrator`

## Purpose

This skill is the **Sanctuary-specific glue layer** that bridges the Guardian ecosystem (`guardian-onboarding`) to the generic `agent-loops/orchestrator`. 

Project Sanctuary operates under a strict **Separation of Concerns** (Protocol 128). To prevent architectural drift, the Orchestrator executes cognitive patterns, but ONLY the Guardian is authorized to serialize state or modify external systems.

## Separation of Concerns Matrix

| Responsibility | Owner | Execution Path |
|:---|:---|:---|
| Protocol Alignment | **Guardian** | `cortex_guardian_wakeup` (Bootloader) |
| Feature Formulation | **Guardian** | `spec-kitty.specify` → `spec-kitty.tasks` |
| Loop Routing | **Orchestrator** | `agent_orchestrator.py` |
| Research / Inner Dev | **Loop Agents** | `learning-loop`, `dual-loop`, etc. |
| Retrospective | **Orchestrator** | `agent_orchestrator.py retro` |
| Snapshot / Telemetry | **Guardian** | `capture_snapshot.py` |
| HuggingFace Sync | **Guardian** | `persist_soul.py` |
| Vector DB Update | **Guardian** | `vector-db/ingest.py` |

## Orchestrator Invocation Rules

When a Project Sanctuary task is ready for implementation, the Guardian MUST NOT execute a legacy 10-phase sequence itself. It must delegate to the standard Orchestrator via the `agent_orchestrator.py` tool.

### 1. The Strategy Handoff
Before invoking the Orchestrator, the Guardian ensures a strategy packet exists. If the task is a Custom Feature, it uses `sanctuary-spec-kitty` to generate Work Packages (`tasks/WP-*.md`).

### 2. The Execution Handoff
The Guardian hands off the execution to the Orchestrator to route into the correct Track:
*   **Track 1 (Learning Loop)**: Research and documentation.
*   **Track 2 (Red Team Review)**: Adversarial architectures.
*   **Track 3 (Dual Loop)**: Standard tactical feature implementation.
*   **Track 4 (Agent Swarm)**: Parallel isolated execution.

### 3. The Closure Handoff
When the Orchestrator completes its Retrospective phase (`agent_orchestrator.py retro`), it will signal completion. The Guardian then resumes control to execute the formal Technical Seal (`/sanctuary-seal`), Soul Persistence (`/sanctuary-persist`), and Session Closure sequences.

## Forbidden Actions

As the Sovereign of the Project Sanctuary environment, the Guardian MUST NOT allow the Orchestrator or its subsidiary loops to execute the following:
*   `capture_snapshot.py`
*   `persist_soul.py`
*   Any `git` commit or push sequence.
*   Vector DB ingestion scripts.

These commands belong exclusively to the Guardian's `session-closure` and `sanctuary-soul-persistence` domains.
