# Oracle Forms Modernization: Master Strategy & Transitional Architecture

## 1. Executive Summary
This document serves as the **Single Source of Truth** for the Oracle Forms to .NET/React modernization strategy. It unifies the technical conversion process, the architectural vision, and the "Transitional Architecture" currently in place (centered around the Python CLI and RLM).

**Goal**: Transform a legacy Oracle Forms monolith into a modern, distributed, cloud-native application on OpenShift.

**Status**: *Transitional / Hybrid*.
*   **Logic**: extracting/mining business logic (miners).
*   **Database**: **Zero-Change Policy** (Existing Query/PL/SQL reused via ODP.NET).
*   **Security**: **Direct Oracle Login** (Preserving Role/VPD security).

## 2. The Strategy: "Context-First" Modernization
Unlike "Big bang" rewrites or black-box migration tools, our strategy is **Context-First**:
1.  **Mining (Not Just Parsers)**: We don't just "parse" XML; we "mine" for *logic*, *dependencies*, and *business rules* (using `xml_miner`, `pll_miner`, `db_miner`).
2.  **Intelligence Layer (RLM)**: We build a "Reactive Ledger Memory" (JSON Cache) and Vector Database to allow AI agents to "understand" the system before writing code.
3.  **Spec-Driven Implementation**: Actual code generation is guided by human-verified Specifications (`spec.md`), ensuring the new code is architecturally sound, not just a line-by-line translation of legacy debt.

### 3. Transitional Architecture Diagram
The current system uses a "Bridge" architecture where Python tools mediate between the Legacy Forms and the Modern Stack.

![Transitional Architecture](../diagrams/architecture/transitional_architecture.png)
*(Source: [transitional_architecture.mmd](../diagrams/architecture/transitional_architecture.mmd))*
**[See Detailed Transitional Architecture Guide](transitional_architecture_details.md)**

## 4. Key Architectural Components

### A. The "Bridge" Tools (Existing)
*   **CLI (`plugins/cli.py`)**: The orchestrator.
*   **Miners**: Specialized scripts that extract logic (e.g., `find_xml_file` logic, `RG_PAAS_AGENCIES` extraction).
*   **Analysis Artifacts**: `task.md`, `implementation_plan.md`, `walkthrough.md`.
*   **Ref**: [Code Conversion Tool Development Approach](../../development/code-conversiontool-development-approach.md)

### B. The Mapping Strategy (How we convert)
We follow a strict "Type-to-Pattern" mapping logic.
*   **Ref**: [Mapping Oracle Types to React/.NET](../potential-future-state/Oracle_Forms_Migration_Matrix.md)
*   **Ref**: [Record Group Logic Pattern](../../_archive_modernization/patterns/record_group_logic_pattern.md) (New)

### C. Future State (Target)
*   **Stack**: React Frontend + .NET Core API + Oracle DB (Hybrid Cloud).
*   **Deployment**: OpenShift (Emerald).
*   **Ref**: [Target Technology Stack](../potential-future-state/target-technology-stack.md)
*   **Ref**: [Deployment Planning](../potential-future-state/deployment-planning-react-and-dotnetapis-toopenshift-emerald.md)

## 5. Specific Conversion Flows

### Flow 1: UI Modernization (Form -> React)
1.  **Element Analysis**: [Element Processing Strategy](../element_processing_strategy.md)
2.  **Conversion**: `investigate-form` -> Extract Blocks/Items -> Map to MUI Components.
3.  **Pattern**: "Single Modal for Complex Logic" (e.g., Access Details) vs "Inline Components" (e.g., Text Fields).

### Flow 2: Logic Extraction (Trigger -> C#)
1.  **Extraction**: `xml_miner` extracts `WHEN-VALIDATE-ITEM`.
2.  **Refactoring**: Identify *Built-ins* vs *Business Logic*.
3.  **Implementation**: Logic moves to C# Service Layer; UI Events trigger API calls.

### 4. Data Access Layer
*   **Repository Pattern**: All database access via `Repositories`.
*   **Legacy Logic Encapsulation**: Complex PL/SQL logic remains in the DB, called via `LegacySharedService`.
*   **Hybrid Approach**:
    *   New Features: EF Core (Code First).
    *   Legacy Features: ODP.NET (Database First) or EF Core with existing tables.
*   **Record Groups**: See **[Record Group Strategy](../_archive_modernization/patterns/record_group_strategy.md)** for handling static vs dynamic data structures.

### Flow 3: Record Groups (Query -> API)
*   **Discovery**: Identify `RG_` elements.
*   **Logic Check**: Does the query contain hidden filters (e.g., User Preferences)?
*   **Decision**:
    - *Replicate*: If security-critical.
    - *Modernize*: If purely preference-based (transparency).
    - **Ref**: [Record Group Logic Pattern](../../_archive_modernization/patterns/record_group_logic_pattern.md)

## 6. Documentation Map
| Document | Purpose |
| :--- | :--- |
| [Oracle Forms Conversion Process](../Oracle_Forms_Conversion_Process.md) | Technical steps (FMB -> XML). |
| [Code Conversion Tool Plan](../../_archive_modernization/code-conversiontool-plan.md) | Roadmap for the Python tooling. |
| [Mapping Oracle Types](Oracle_Forms_Migration_Matrix.md) | Detailed Type-to-Type lookup table. |
| [Element Processing Strategy](../element_processing_strategy.md) | How to handle specific Form elements. |

---
**Version**: 1.0
**Author**: Antigravity (AI Agent)
**Date**: Feb 2026
