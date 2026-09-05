# Context-Aware Instruction & Rule Synthesis Protocol

> **Core Directive: No Blind Overwrites**: The AI Agent MUST NEVER blindly overwrite or replace existing architecture files (`architecture.md`), instruction files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), or project rules (`.agent/rules/*.md`).
> Initializing or retrofitting the Agentic OS into an established repository cannot be treated as a pure, rigid, deterministic operation. The AI agent must act as an **intelligent context synthesizer**, understanding the intentions of the Agentic OS rules while deeply respecting and preserving the context, domain conventions, and constraints of the target repository.

---

## 1. Context Analysis & Intention Review

Before creating or updating any file in a destination project, the agent must perform an intentional audit:

1. **Understand Agentic OS Intentions**:
   - **Layered Memory (Layers 1/2/3)**: Keeps dynamic session tokens lean by persisting confirmed domain insights into `wiki/` playbooks and friction into `references/map-debt.md`.
   - **Control Plane Integrity**: Enforces state machine transitions and verification receipts in `context/control_plane.db`.
   - **Pre-Completion Receipt Gate**: Ensures agents verify existing capabilities and log map debt before completing a task.
   - **Non-Destructive Evolution**: Guarantees existing project code, build configurations, and conventions are never inadvertently deleted or replaced.

2. **Discover Target Repo Context**:
   - Inspect existing architecture documentation (`architecture.md`, `docs/architecture/`, `README.md`).
   - Identify existing build/test tooling (e.g. `npm`, `cargo`, `poetry`, `make`, `uv`, `gradle`).
   - Read existing custom instruction files and existing rule files in `.agent/rules/` or IDE-specific directories.
   - Identify existing naming conventions, ports, environment requirements, and domain business constraints.

---

## 2. Architecture Synthesis (`architecture.md`)

When executing `os-init` or retrofitting:

- **Case A: `architecture.md` Does Not Exist**:
  - Scaffold `architecture.md` using the canonical Agentic OS template.
  - Populate the project name, inferred language/framework stack, and directory structure reflecting the destination project's actual layout plus the new Agentic OS substrates (`context/`, `wiki/`, `references/map-debt.md`).
- **Case B: `architecture.md` Already Exists**:
  - **DO NOT OVERWRITE**. Read the existing document thoroughly.
  - Review how the project's existing components interact.
  - Add or update only the Agentic OS Substrate section (Layer 1 context, Layer 2 wiki playbooks, Layer 3 traces, and `control_plane.db`), integrating seamlessly into the existing architectural narrative.
  - Present the diff for review before applying.

---

## 3. Intelligent Instruction Blending (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`)

1. **Retain 100% of Domain Logic**:
   - Never remove existing run/build/test commands, port definitions, or application-specific guidelines.
2. **Inject Evolutionary Substrates**:
   - Merge `## 3-Layer Memory Architecture` and `## Pre-Completion Self-Evolution Gate` sections into the document.
   - For `GEMINI.md`, preserve any custom tool mappings or append the standard Gemini CLI tool mapping table.
   - For `.github/copilot-instructions.md`, maintain the required Copilot header while syncing core instructions.
3. **Diff Presentation**:
   - Highlight the non-destructive nature of the edits to give the user full visibility.

---

## 4. Context-Aware Rule Reconcilation (`.agent/rules/*.md`)

When syncing rules from Agentic OS:
1. **Never Clobber Custom Rules**: Existing project-specific rules in `.agent/rules/` (e.g., custom database rules, deployment standards) must remain intact.
2. **Preserve Downstream Additions**: If an existing ecosystem rule has local project customizations or specific map debt references, use three-way diff merging to preserve local blocks while adopting upstream security and capability improvements.
3. **Intentional Review**: Ask: *"Does this ecosystem rule conflict with how this target repository builds or deploys?"* If friction exists, log it into `references/map-debt.md` rather than breaking target repository workflows.
