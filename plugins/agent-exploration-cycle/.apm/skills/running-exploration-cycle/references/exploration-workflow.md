# Exploration Workflow (exploration-workflow) (absorbed skill)

> Absorbed from the retired `exploration-workflow` skill into `running-exploration-cycle`; the full original body follows.
> Original trigger description: Orchestrates the Business Exploration Loop across greenfield, brownfield, discovery-only, and spike sessions. Manages state via exploration-dashboard.md, enforces phase gates, and routes execution to child skills.

Orchestrates the Business Exploration Loop, managing session state, living task ledgers, phase gates, and child skill dispatch.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Zero blind jumps: Never bypass Phase 1 discovery even if requested to start building immediately.
- Update `exploration/exploration-dashboard.md` immediately upon human approvals or scope revisions.
- All downstream implementation tasks must cite source discovery artifacts and preserve traceability.

## Quick start
1. Pre-flight tool availability and select dispatch strategy (`copilot-cli`, `gemini-cli`, `claude-subagents`, or `direct`).
2. Initialize session dashboard at `exploration/exploration-dashboard.md` with active session type.
3. Advance sequentially through gated phases (Discovery -> Behavioral Capture -> Prototyping -> Handoff).

## Workflow
1. **Phase 1 (Discovery)**: Invoke `discovery-planning`. Require explicit SME plan approval before prototyping.
2. **Phase 2 (Behavioral Capture)**: Invoke `visual-companion` or `vibe-behavioral-test-capture` for interface flows.
3. **Phase 3 (Prototyping)**: Delegate build slices to `subagent-driven-prototyping` or `prototype-builder` with TDD verifiers.
4. **Phase 4 (Handoff)**: Invoke `exploration-handoff` to synthesize artifacts into final deliverables.

## Verification
- Verify `exploration/exploration-dashboard.md` reflects current session state and completed milestones.
- Ensure all phase gate approvals are signed off prior to advancing.
- Validate that produced prototypes or specs satisfy discovery plan acceptance criteria.

## References
- [dispatch-strategies.md](dispatch-strategies.md)
- [exploration-orchestrator-guide.md](exploration-orchestrator-guide.md)
- phase3-execution-discipline.md (in the `building-interactive-prototypes` skill)
- requirements-doc-agent.md (in the `capturing-business-requirements` skill)
