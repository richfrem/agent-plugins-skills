---
name: discovery-planning
plugin: exploration-cycle-plugin
description: >
  Guides a Subject Matter Expert through a structured discovery session to create and approve a Discovery Plan before any building begins. This is the HARD-GATE brainstorming skill — no prototype can be built until the SME explicitly approves the plan. Trigger phrases: "start a discovery session", "let's plan this out", "help me figure out what we're building", "I have an idea I want to explore", "let's start from scratch"
allowed-tools: Read, Write
---

# Discovery Planning (`discovery-planning`)

Guides a Subject Matter Expert through a structured discovery session to create and approve a Discovery Plan before any building begins.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Hard-gate rule**: No prototype files may be written until the SME explicitly confirms the discovery plan ("YES", "approved").
- **Sequential questioning**: Ask questions one at a time and reflect understanding before asking the next.
- **Intervention check**: Verify whether software is truly required, or if a process or policy change solves the root issue.
- **Database authority**: Record state transitions in the authoritative SQLite state engine.

## Quick start

```bash
# Check existing session brief before initiating discovery interview
test -f exploration/session-brief.md && cat exploration/session-brief.md
```

## Workflow

1. **Pre-Discovery**: Ingest `exploration/session-brief.md` and select session track (Greenfield, Feature, Spike, etc.).
2. **Interactive Interview**: Ask targeted questions one by one across context, users, and constraints.
3. **Plan Compilation**: Draft discovery plan at `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`.
4. **Approval Gate**: Present plan to SME and wait for explicit affirmation ("YES") before advancing.
5. **Handoff**: Emit `HANDOFF_BLOCK` and return control to `exploration-workflow`.

## Verification

```bash
# Verify discovery plan exists and is approved in state engine
python3 plugins/exploration-cycle-plugin/scripts/state_engine.py status
```

## References

- [discovery-planning-tracks.md](references/discovery-planning-tracks.md) — All 7 session tracks, question scripts, and plan format.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for discovery planning.
