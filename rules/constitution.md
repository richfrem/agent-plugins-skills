---
trigger: always_on
---

# Oracle Forms Analysis Constitution v4.2

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation without EXPLICIT user approval.
> "Sounds good" is NOT approval. Only "Proceed", "Go", "Execute" is approval.
> **VIOLATION = SYSTEM FAILURE**

## I. The Hybrid Workflow (Project Purpose)
All work MUST follow the **Universal Hybrid Workflow**.
**START HERE**: `/agent-orchestrator_plan` or `spec-kitty specify`

### Workflow Hierarchy
```
/agent-orchestrator_plan (UNIVERSAL)
├── Routes to: Standard Flow (deterministic SOPs)
│   └── /legacy-system-oracle-forms_codify-form, /legacy-system-oracle-forms_investigate-form
├── Routes to: Custom Flow (new features)
│   └── /spec-kitty.specify → /spec-kitty.plan → /spec-kitty.tasks → /spec-kitty.implement
└── Both end with: /spec-kitty_retrospective → /spec-kitty.merge
```

- **Track A (Factory)**: Deterministic tasks (Codify, Curate). SOPs must be followed rigidly.
- **Track B (Discovery)**: Spec-Driven Development (Spec → Plan → Tasks).
- **Reference**: [ADR 0029](../../docs/ADRs/0029-hybrid-spec-driven-development-workflow.md) | [Diagram](../../docs/diagrams/analysis/sdd-workflow-comparison/hybrid-spec-workflow.mmd)

## II. The Documentation First Imperative
**"The Specification is the Source of Truth."**

- **Spec Before Code**: No code shall be written without a defined User Story or Requirement.
- **Prescriptive Workflows**: Workflows like `/legacy-system-oracle-forms_codify-form` must be followed rigidly.
- **Open-Ended Workflows**: Workflows like `/task-manager_create` MUST define a `spec.md` (What) and `plan.md` (How) before execution.
- **Living Documentation**: If the code diverges from the Spec/Plan during execution, the Spec/Plan MUST be updated.

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
- **ALWAYS** use **Tool Discovery**: `python plugins/tool-inventory/scripts/query_cache.py`. It's your `.agent/skills/SKILL.md`
- **ALWAYS** use defined **Slash Commands** (e.g., `/legacy-system-oracle-forms_*`, `/spec-kitty.*`, `/tool-inventory_*`) over raw scripts.
- **ALWAYS** use underlying `.py` scripts in `plugins/` through their respective skill pathways where applicable.
- **NEVER** substitute manual analysis for a defined Slash Command. Reading source files and writing outputs directly when a skill exists for that task = **workflow simulation**. The Slash Command exists to produce standardized artifacts with traceability. Invoke it via the Skill tool.

## V. Definition of Done
**No task is complete until verified, documented, and synchronized.**

- [`documentation_granularity_policy.md`](legacy-system-analysis/documentation_granularity_policy.md) - **Granularity**: Sub-task tracking.
- [`rlm_legacy_system_distillation_policy.md`](legacy-system-analysis/rlm_legacy_system_distillation_policy.md) - **Intelligence Sync**: RLM/Vector updates.
- [`qa_template_completion_policy.md`](legacy-system-analysis/qa_template_completion_policy.md) - **Quality Assurance**: Template checklist.

## VI. Governing Law (The Tiers)

### Tier 1: PROCESS (Deterministic)
| File | Purpose |
|:-----|:--------|
| [`workflow_enforcement_policy.md`](01_PROCESS/workflow_enforcement_policy.md) | **Slash Commands**: Command-Driven Improvement |
| [`tool_discovery_enforcement_policy.md`](01_PROCESS/tool_discovery_enforcement_policy.md) | **No Grep Policy**: Use `query_cache.py` |
| [`spec_driven_development_policy.md`](01_PROCESS/spec_driven_development_policy.md) | **Lifecycle**: Spec → Plan → Tasks |
| [`workflow_artifacts_integrity.md`](01_PROCESS/workflow_artifacts_integrity.md) | **Integrity**: Anti-simulation standards |

### Tier 2: OPERATIONS (Policies)
| File | Purpose |
|:-----|:--------|
| [`git_workflow_policy.md`](02_OPERATIONS/git_workflow_policy.md) | Branch strategy, commit standards |

### Tier 3: TECHNICAL (Standards)
| File | Purpose |
|:-----|:--------|
| [`coding_conventions_policy.md`](03_TECHNICAL/coding_conventions_policy.md) | Code standards, documentation |
| [`dependency_management_policy.md`](03_TECHNICAL/dependency_management_policy.md) | pip-compile workflow |
| [`technical_implementation_policy.md`](legacy-system-analysis/technical_implementation_policy.md) | **Traceability**: Source linking checklist |
| [`security_access_policy.md`](legacy-system-analysis/security_access_policy.md) | **Security**: Role verification standards |
| [`validated_dependencies_policy.md`](legacy-system-analysis/validated_dependencies_policy.md) | **Legacy Verification**: Oracle Forms dependencies |
| [`smart_linking_policy.md`](legacy-system-analysis/smart_linking_policy.md) | **Linking**: Enrichment standards |

### Domain-Specific Standards (Oracle Forms Analysis)
| File | Purpose |
|:-----|:--------|
| [`form_documentation_policy.md`](legacy-system-analysis/form_documentation_policy.md) | **Forms**: FMB analysis standards |
| [`library_documentation_policy.md`](legacy-system-analysis/library_documentation_policy.md) | **Libraries**: PLL analysis standards |
| [`menu_documentation_policy.md`](legacy-system-analysis/menu_documentation_policy.md) | **Menus**: MMB analysis standards |
| [`report_documentation_policy.md`](legacy-system-analysis/report_documentation_policy.md) | **Reports**: RDF analysis standards |
| [`database_object_documentation_policy.md`](legacy-system-analysis/database_object_documentation_policy.md) | **Database**: Tables, Views, Packages |
| [`business_rule_documentation_policy.md`](legacy-system-analysis/business_rule_documentation_policy.md) | **Business Rules**: BR-XXXX registration |
| [`business_workflow_documentation_policy.md`](legacy-system-analysis/business_workflow_documentation_policy.md) | **Workflows**: BW-XXXX registration |
| [`application_documentation_policy.md`](legacy-system-analysis/application_documentation_policy.md) | **Apps**: Application-level overviews |
| [`human_overrides_policy.md`](legacy-system-analysis/human_overrides_policy.md) | **Override Authority**: human-overrides directory |
| [`context_first_analysis_policy.md`](legacy-system-analysis/context_first_analysis_policy.md) | **Context**: RLM-first discovery protocol |

## VII. Session Closure (Mandate)
- **ALWAYS** run `/spec-kitty_retrospective` then `/spec-kitty.merge` before ending a session.
- **NEVER** abandon a session without proper closure.
- **PERSIST** intelligence updates to RLM cache and Vector DB.

**Version**: 4.2 | **Ratified**: 2026-02-16


