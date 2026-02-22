---
trigger: always_on
---

# Oracle Menu Documentation Policy V2

> **Effective Date:** 2026-01-18
> **Related Standards:**
> *   [Form Documentation Policy](.agent/rules/legacy-system-analysis/form_documentation_policy.md)
> *   [Expert Persona](.agent/tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md)

## 0. Objective
Standardize the documentation of Oracle Menus (`.mmb`/`.mmx`). Menus define the navigation structure and security access points of the application. Unlike simple navigation, Oracle Menus often contain significant routing logic and state management.

## 1. Context Gathering
Before documenting a menu, gather:
*   **Source XML**: `legacy-system/oracle-forms/XML/[ID]_mmb.xml`
*   **Associated App**: Which application uses this menu? (e.g., `RccM0000` is for RCC).

## 2. Documentation Structure
All Menu Overviews (`legacy-system/oracle-forms-overviews/menus/[ID]-Menu-Overview.md`) must follow this structure:

### I. Header & Metadata
*   **Menu ID**: e.g., `POSMENU`
*   **Link**: Path to source XML.

### II. Roles
List roles defined in the menu module itself. Note if RBAC is handled here or externally.

### III. Menu Hierarchy (The Navigation Tree)
Visualize the full structure of the menu.
*   **Format**: Indented List.
*   **Separators**: Render as horizontal rules (`---`) to denote grouping.
*   **Properties to Include**:
    *   **Label**: The text user sees.
    *   **Target (Smart Link)**: If item opens a form, it MUST be linked: `(Opens: [FORM_ID])`.
    *   **Logic Snippet**: If extracting custom PL/SQL (e.g., `Update_Status`), show brief command.
    *   **Roles**: If item is restricted to specific roles, list them: `(Roles: CLERK, ADMIN)`.

### IV. Logic & Commands
Document significant PL/SQL logic and Program Units attached to the menu.
*   **Program Units**: Full code blocks for procedures defined in the menu (e.g., `Run_Report`).
*   **Heuristics**: If command is hidden (triggered via `ItemClick('CODE')`), you MUST resolve the `CODE` to its destination (Form/Report) using regex or lookups.

### V. Dependencies
*   **Attached Libraries**: Link to `.pll` or `.xml` sources.
*   **Called Forms**: List of dependencies derived from the hierarchy.

### VI. Modernization Insights (Expert Analysis)
Provide specific guidance for migrating this menu to a modern web stack (React/Next.js).
*   **Navigation Pattern**: Sidebar vs Top Nav vs Mega Menu (based on item count).
*   **State Management**: Identify `HIDEMODULEITEMS` or similar logic that implies dynamic state visibility.
*   **RBAC Strategy**: How map Oracle Roles to Identity Provider scopes.

## 3. Tooling
*   **Mining**: Use `tools/cli.py bundle` (Runs menu_miner).
*   **Batch Processing**: `batch_process_menus.py` applies heuristics to extract targets from obscure commands.
*   **Enrichment**: `enrich_links_v2.py` ensures Smart Links resolve.
