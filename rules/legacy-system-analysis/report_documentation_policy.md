
# Oracle Report Documentation Policy

> **Effective Date:** 2026-01-18
> **Related Standards:**
> *   [Form Documentation Policy](.agent/rules/legacy-system-analysis/form_documentation_policy.md)

## 0. Objective
Standardize the documentation of Oracle Reports (RDF/XML). Reports are data-centric artifacts where the **SQL Query** and **Layout Logic** are the critical components.

## 1. Context Gathering (Mandatory RLM-First Protocol)

> [!CRITICAL]
> **RLM FIRST PROTOCOL**
> You MUST execute the following verification steps **BEFORE** reading raw XML source.
> RLM summaries exist for these objects. Do not waste them.

**Mandatory Sequence:**
**Mandatory Sequence:**
1.  **Initialize Context**:
    ```bash
    python plugins/cli.py context --target [REPORT_ID] --type report
    ```
2.  **Review Bundle**:
    - Open `temp/context-bundles/[ID]_context.md`.
    - Check for RLM Summary and `report_miner` output.
3.  **Check Callers**:
    - Use `dependency_map.json` to find calling forms.

## 2. Documentation Structure
All Report Overviews (`legacy-system/oracle-forms-overviews/reports/[ID]-Report-Overview.md`) must follow this structure:

### I. Header & Metadata
*   **Report ID**: e.g., `RCCR0100`
*   **Title/Name**: Derived from the Report Module Name or Title property.
*   **Purpose**: Brief description.

### II. Data Sources (SQL)
The core of any report is its data query.
*   **Format**: SQL Code Block.
*   **Requirement**: Extract the main query from `dataSource` elements.
*   **Groups**: List the data groups (Master/Detail relationships).

### III. Parameters
List all user parameters defined in the report.
*   **Format**: Table.
*   **Columns**: `Name`, `Datatype`, `Default Value`, `Description/Label`.

### IV. Triggers & Program Units
Document PL/SQL logic embedded in the report.
*   **Report Triggers**: `Before Report`, `After Report`, `Between Pages`.
*   **Format Triggers**: Field-level conditional formatting logic.
*   **Formulas**: Document calculated fields (CF_*) and their logic.

### V. Layout & Design
*   **Orientation**: Portrait/Landscape.
*   **Sections**: Header, Main, Trailer.

### VI. Dependencies (Smart Linking)
*   **Attached Libraries**: List all `.pll` files. Wrap in brackets and UPPERCASE (e.g., `[AGLIB]`).
*   **Database Objects**: List tables/views/packages used in queries. Wrap in brackets (e.g., `[JUSTIN_AGENCIES]`).

## 3. Tooling
*   **Mining**: Use `python plugins/investigate/miners/report_miner.py [XML_FILE]` to extract structured metadata.
*   **Enrichment**: Run `python scripts/documentation/enrich_links_v2.py` to resolve links.
