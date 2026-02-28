---
trigger: always_on
---

# Project Sanctuary Constitution V3

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation without EXPLICIT user approval.
> "Sounds good" is NOT approval. Only "Proceed", "Go", "Execute" is approval.
> **VIOLATION = SYSTEM FAILURE**

## I. The Hybrid Workflow (Project Purpose)
All work MUST follow the **Universal Hybrid Workflow**.
**START HERE**: `python tools/cli.py workflow start` (or `/sanctuary-start`)

### Workflow Hierarchy
```
/sanctuary-start (UNIVERSAL)
├── Routes to: Learning Loop (cognitive sessions)
│   └── /sanctuary-learning-loop → Audit → Seal → Persist
├── Routes to: Custom Flow (new features)
│   └── /spec-kitty.implement → Manual Code
└── Both end with: /sanctuary-retrospective → /sanctuary-end
```

- **Track A (Factory)**: Deterministic tasks (Codify, Curate).
- **Track B (Discovery)**: Spec-Driven Development (Spec → Plan → Tasks).
- **Reference**: [ADR 035](../../ADRs/035_hybrid_spec_driven_development_workflow.md) | [Diagram](../../docs/diagrams/analysis/sdd-workflow-comparison/hybrid-spec-workflow.mmd)

## II. The Learning Loop (Cognitive Continuity)
For all cognitive sessions, you are bound by **Protocol 128**.
**INVOKE**: `/sanctuary-learning-loop` (called by `/sanctuary-start`)

- **Boot**: Read `cognitive_primer.md` + `learning_package_snapshot.md`
- **Close**: Audit → Seal → Persist (SAVE YOUR MEMORY)
- **Reference**: [ADR 071](../../ADRs/071_protocol_128_cognitive_continuity.md) | [Diagram](../../plugins/guardian-onboarding/resources/protocols/protocol_128_learning_loop.mmd)

### Identity Layers (Boot Files)
| Layer | File | Purpose |
|:------|:-----|:--------|
| **1. Contract** | [boot_contract.md](../learning/guardian_boot_contract.md) | Immutable constraints |
| **2. Primer** | [cognitive_primer.md](../learning/cognitive_primer.md) | Role Orientation |
| **3. Snapshot** | [snapshot.md](../learning/learning_package_snapshot.md) | Session Context |

## III. Zero Trust (Git & Execution)
- **NEVER** commit directly to `main`. **ALWAYS** use a feature branch.
- **NEVER** run `git push` without explicit, fresh approval.
- **NEVER** "auto-fix" via git.
- **HALT** on any user "Stop/Wait" command immediately.

### Defined: State-Changing Operation
Any operation that:
1. Writes to disk (except /tmp/)
2. Modifies version control (git add/commit/push)
3. Executes external commands with side effects
4. Modifies .agent/learning/* files
**REQUIRES EXPLICIT APPROVAL ("Proceed", "Go", "Execute").**

## IV. Tool Discovery & Usage
- **NEVER** use `grep` / `find` / `ls -R` for tool discovery.
- **fallback IS PROHIBITED**: If `query_cache.py` fails, you MUST STOP and ask user to refresh cache.
- **ALWAYS** use **Tool Discovery**: `python plugins/rlm-factory/skills/rlm-curator/scripts/query_cache.py`. It's your `.agent/skills/SKILL.md`
- **ALWAYS** use defined **Slash Commands** (`/workflow-*`, `/spec-kitty.ty.*`) over raw scripts.
- **ALWAYS** use underlying `.sh` scripts e.g. (`scripts/bash/sanctuary-start.sh`, `scripts/bash/sanctuary-learning-loop.sh`) and the `tools/cli.py` and `tools/orchestrator/workflow_manager.py`

## V. Governing Law (The Tiers)

### Tier 1: PROCESS (Deterministic)
| File | Purpose |
|:-----|:--------|
| [`workflow_enforcement_policy.md`](01_PROCESS/workflow_enforcement_policy.md) | **Slash Commands**: Command-Driven Improvement |
| [`tool_discovery_enforcement_policy.md`](01_PROCESS/tool_discovery_enforcement_policy.md) | **No Grep Policy**: Use `query_cache.py` |
| [`spec_driven_development_policy.md`](01_PROCESS/spec_driven_development_policy.md) | **Lifecycle**: Spec → Plan → Tasks |

### Tier 2: OPERATIONS (Policies)
| File | Purpose |
|:-----|:--------|
| [`git_workflow_policy.md`](02_OPERATIONS/git_workflow_policy.md) | Branch strategy, commit standards |

### Tier 3: TECHNICAL (Standards)
| File | Purpose |
|:-----|:--------|
| [`coding_conventions_policy.md`](03_TECHNICAL/coding_conventions_policy.md) | Code standards, documentation |
| [`dependency_management_policy.md`](03_TECHNICAL/dependency_management_policy.md) | pip-compile workflow |

## VI. Session Closure (Mandate)
- **ALWAYS** run the 9-Phase Loop before ending a session.
- **NEVER** abandon a session without sealing.
- **ALWAYS** run `/sanctuary-retrospective` then `/sanctuary-end`.
- **PERSIST** your learnings to the Soul (HuggingFace) and **INGEST** to Brain (RAG).

**Version**: 3.7 | **Ratified**: 2026-02-01