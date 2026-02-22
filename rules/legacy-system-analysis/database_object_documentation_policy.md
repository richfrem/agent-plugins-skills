# Oracle Database Object Documentation Policy V2

> **Effective Date:** 2026-01-18
> **Related Standards:**
> *   [Business Rules Standard](.agent/rules/legacy-system-analysis/standards/std_business_rules.md)
> *   [Placeholder Creation](.agent/rules/legacy-system-analysis/standards/std_placeholder_creation.md)
> *   [Smart Linking](.agent/rules/legacy-system-analysis/standards/std_smart_linking.md)

## 0. Human Overrides: The Single Source of Truth
**Rule File:** [std_human_overrides.md](.agent/rules/legacy-system-analysis/standards/std_human_overrides.md)
> [!CRITICAL]
> **ALWAYS check `legacy-system/human-overrides/` before documenting.**

## 1. Overview

This policy governs the documentation of **ALL** Oracle Database objects:
- **Tables** → Store data, enforce constraints
- **Views** → Abstract queries, derived data
- **Packages** → Grouped procedures/functions, core business logic
- **Procedures** → Transaction processing, data manipulation
- **Functions** → Calculations, transformations
- **Types** → Custom data structures, collections
- **Triggers** → Automated event-driven logic (audit, validation, integration)

> [!IMPORTANT]
> Database Packages often contain the **MOST CRITICAL business logic** of the system.
> They MUST be analyzed for Business Rules and Workflows with the same rigor as Forms.

## 2. Object Type Reference

| Type | Source Location | Template | Output Directory |
|---|---|---|---|
| Tables | `oracle-database/Tables/*.sql` | `db-table-template.md` | `database-overviews/tables/` |
| Views | `oracle-database/Views/*.sql` | `db-table-template.md` | `database-overviews/views/` |
| Packages | `oracle-database/source/Packages/*.sql` | `db-package-template.md` | `database-overviews/packages/` |
| Procedures | `oracle-database/Procedures/*.sql` | `db-procedure-template.md` | `database-overviews/procedures/` |
| Functions | `oracle-database/Functions/*.sql` | `db-procedure-template.md` | `database-overviews/functions/` |
| Types | `oracle-database/Types/*.sql` | `db-type-template.md` | `database-overviews/types/` |
| Triggers | `oracle-database/Triggers/*.sql` | `db-trigger-template.md` | `database-overviews/triggers/` |

## 3. CLI Quick Reference
```bash
# Batch Processing (Recommended)
python scripts/documentation/batch_process_db_objects.py --type all

# Single Object
python tools/codify/documentation/overview_manager.py --id OBJECT_NAME --type db_table --create

# Enrichment
python scripts/documentation/enrich_links_v2.py
```

---

## 4. Documentation Standards by Type

### A. Tables & Views
**Template:** `db-table-template.md`
**Focus:** Data model, relationships, constraints as business rules

#### Required Sections
1. Object Information (Name, Schema, Source)
2. Purpose
3. Columns (Name, Type, Nullable, Description)
4. Constraints → **Business Rules**
5. Indexes
6. Relationships (Parent/Child tables)
7. Used By (Forms/Reports)
8. Business Rules Enforced

#### Business Rule Discovery
- **CHECK Constraints** → `BR-XXXX` (Validation Rule)
- **NOT NULL** → `BR-XXXX` (Required Field Rule)
- **Foreign Keys** → Document relationships
- **Unique Constraints** → `BR-XXXX` (Uniqueness Rule)

---

### B. Packages (CRITICAL)
**Template:** `db-package-template.md`
**Focus:** API surface, business logic, workflows

#### Required Sections
1. Object Information
2. Purpose
3. **Contains** (Member Procedures, Functions, Types)
4. **Business Rules Discovered**
5. **Workflows Discovered**
6. Error Handling
7. Dependencies
8. Called By
9. Security/Roles
10. Modernization Notes

#### Business Rule Discovery
**Rule File:** [std_business_rules.md](.agent/rules/legacy-system-analysis/standards/std_business_rules.md)

Scan for these patterns:
```sql
-- Validation (Business Rule)
IF condition THEN 
    RAISE_APPLICATION_ERROR(-20xxx, 'Message');
END IF;

-- State Transition (Workflow)
UPDATE table SET status = 'NEW_STATE' WHERE ...;

-- Access Control (Security Rule)
IF NOT pkg_security.has_role('ROLE_NAME') THEN ...;

-- Calculation (Business Rule)
v_total := v_quantity * v_price * (1 - v_discount);
```

---

### C. Procedures & Functions
**Template:** `db-procedure-template.md`
**Focus:** Signature, logic, callers

#### Required Sections
1. Object Information (Must link to Parent Package if applicable)
2. Purpose
3. Signature
4. Parameters
5. Return Value (Functions)
6. Business Logic
7. Dependencies (Downstream - Tables/Views/Packages)
8. Called By (Upstream - Forms/Packages)
9. Business Rules Implemented
10. Error Handling

---

### D. Types
**Template:** `db-type-template.md`
**Focus:** Data structure definition, usage context

#### Required Sections
1. Object Information
2. Purpose
3. Type Definition (SQL)
4. Attributes (Object Types)
5. Methods (Object Types)
6. Collection Details (if applicable)
7. Used By
8. Modernization Notes (TypeScript/Java mapping)

---

### E. Triggers
**Template:** `db-trigger-template.md`
**Focus:** Event handling, audit trails, data integrity enforcement

#### Required Sections
1. Object Information (Name, Schema, Trigger Type)
2. Purpose
3. **Triggering Event** (BEFORE/AFTER, INSERT/UPDATE/DELETE)
4. **Target Table**
5. Trigger Logic (PL/SQL summary)
6. Business Rules Implemented
7. Dependencies (Packages called, Tables affected)
8. Audit/Journal Info (if audit trigger)
9. Performance Notes
10. Modernization Notes

#### Business Rule Discovery
- **Audit Triggers** → Document fields tracked
- **Validation Triggers** → `BR-XXXX` (Data Integrity)
- **State Change Triggers** → `BW-XXXX` (Workflow events)
- **Integration Triggers** → Document external system interactions (DEMS, CCD)

---

## 5. Business Rules & Workflows (Shared Standard)

### Discovery Checklist
1.  **Check Existing Rules**: `legacy-system/business-rules/`
2.  **Search Inventory**: Grep `master_object_collection.json`
3.  **DO NOT CREATE DUPLICATES**. Link to existing BR-XXXX IDs.

### Classification
*   **P1 (Critical)**: Security, Data Integrity, Legal Compliance
*   **P2 (Major)**: Core business logic, key validations
*   **P3 (Minor)**: Default values, formatting

### Registration
**Rule File:** [std_placeholder_creation.md](.agent/rules/legacy-system-analysis/standards/std_placeholder_creation.md)
When BR/BW discovered, create placeholder file immediately.

---

## 6. Context Gathering Workflow (MANDATORY)

> [!CRITICAL]
> **RLM FIRST PROTOCOL**
> You MUST execute the following verification steps **BEFORE** reading raw source code.
> Failing to check existing context leads to duplicate work and hallucinated rules.

### For Each Object (Table, View, Proc, Package, Trigger):

1.  **Initialize Smart Context**:
    ```bash
    python tools/cli.py context --target [OBJECT_NAME] --type [TYPE]
    ```
    *(where TYPE is table, view, package, procedure, trigger)*

2.  **Review Bundle**:
    - Open `temp/context-bundles/[NAME]_context.md`.
    - Check RLM Summary and Dependencies.

3.  **Check Existing Overview**:
    - Verify if an overview file already exists in `database-overviews/`.
    - `cat` the file to read manual annotations.

4.  **Parse Source SQL**: Only AFTER context implies gaps.
5.  **Identify Business Rules**:
    - Use `cli.py rules search "term"` to match against existing inventory.
    - Register new candidates via `cli.py rules register`.

---

## 7. Post-Processing

1. Run `enrich_links_v2.py` for smart linking
2. Create BR/BW placeholders for discovered rules
3. Update `master_object_collection.json` with new artifacts
4. Update RLM cache
5. Update Vector DB

---

## 8. Tooling Reference

| Tool | Purpose |
|---|---|
| `batch_process_db_objects.py` | Generate all overviews |
| `doc_manager.py` | Single object processing |
| `enrich_links_v2.py` | Smart link resolution |
| `build_master_collection.py` | Inventory management |
