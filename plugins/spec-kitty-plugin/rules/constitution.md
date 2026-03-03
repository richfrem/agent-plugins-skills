---
trigger: always_on
---

# Project Ecosystem Constitution V3

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation without EXPLICIT user approval.
> "Sounds good" is NOT approval. Only "Proceed", "Go", "Execute" is approval.
> **VIOLATION = SYSTEM FAILURE**

## I. The Hybrid Workflow (Project Purpose)
All work MUST follow the **Universal Hybrid Workflow**.
**START HERE**: `/project-start`

### Workflow Hierarchy
```
/project-start (UNIVERSAL)
├── Routes to: Learning Loop (cognitive sessions)
│   └── /project-learning-loop → Audit → Seal → Persist
├── Routes to: Custom Flow (new features)
│   └── /spec-kitty.implement → Manual Code
└── Both end with: /project-retrospective → /project-end
```

- **Track A (Factory)**: Deterministic tasks (Codify, Curate).
- **Track B (Discovery)**: Spec-Driven Development (Spec → Plan → Tasks).
- **Pre-Execution Mindset**: Agents MUST map their execution using `spec-kitty-workflow`'s visual constraint diagram.

## II. The Learning Loop (Cognitive Continuity)
For all cognitive sessions, you are bound by **Protocol 128**.
**INVOKE**: `/project-learning-loop` (called by `/project-start`)

- **Boot**: Read `cognitive_primer.md` + `learning_package_snapshot.md`
- **Close**: Audit → Seal → Persist (SAVE YOUR MEMORY)
- **Constraint**: The Learning Loop implements Protocol 128 (Cognitive Continuity) natively via RLM Cache.

### Identity Layers (Boot Files)
| Layer | File | Purpose |
|:------|:-----|:--------|
| **1. Contract** | `ecosystem_boot_contract.md` (Local Context) | Immutable constraints |
| **2. Primer** | `cognitive_primer.md` (Local Context) | Role Orientation |
| **3. Snapshot** | `learning_package_snapshot.md` (Local Context) | Session Context |

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
- **fallback IS PROHIBITED**: If `tool_chroma.py` fails, you MUST STOP and ask user to refresh cache.
- **ALWAYS** use **Tool Discovery**: `python plugins/tool-inventory/skills/tool-inventory/scripts/tool_chroma.py search "keyword"`. It's your `.agent/skills/SKILL.md`
- **ALWAYS** use defined **Slash Commands** (`/workflow-*`, `/spec-kitty.*`) over raw scripts.
- **ALWAYS** use underlying `.sh` scripts e.g. (`scripts/bash/project-start.sh`, `scripts/bash/project-learning-loop.sh`) and the specialized Python scripts living in the `plugins/` directory.

## V. Governing Law (The Tiers)

### Tier 1: PROCESS (Deterministic)
| File | Purpose |
|:-----|:--------|
| [`workflow_enforcement_policy.md`](01_PROCESS/workflow_enforcement_policy.md) | **Slash Commands**: Command-Driven Improvement |
| [`tool_discovery_enforcement_policy.md`](01_PROCESS/tool_discovery_enforcement_policy.md) | **No Grep Policy**: Use `tool_chroma.py` |
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
- **ALWAYS** run `/project-retrospective` then `/project-end`.
- **PERSIST** your learnings to the Soul (HuggingFace) and **INGEST** to Brain (RAG).

**Version**: 3.7 | **Ratified**: 2026-02-01