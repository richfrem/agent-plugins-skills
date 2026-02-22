# Business Rule Documentation Policy

> **Effective Date:** 2026-01-17
> **Related Standards:** 
> *   [Business Rule Strategy](.agent/tasks/done/0030-business-rule-extraction-strategy.md)
> *   [Business Rule Template](.agent/.agent/templates/outputs/business-rule-template.md)
> *   [Expert Persona](.agent/tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md) - Apply this role when analyzing
> *   [Architecture Diagram](.agent/docs/diagrams/architecture/legacy-oracle-architecture.mmd) - Reference for system structure
> *   **Subtask Prompts:** [Logic Extraction](.agent/tools/ai-resources/prompts/analysis/subtasks/Logic_Extraction_Prompt.md)

## 0. Human Overrides
**Rule File:** [std_human_overrides.md](.agent/rules/standards/std_human_overrides.md)

## 1. Knowledge Retrieval
**Mandatory Protocol:**
1.  **Search Existing Rules (Multiple Variants)**: 
    ```bash
    python tools/cli.py rules search "keyword"
    ```
    *   **Requirement**: Run multiple searches using different keywords (e.g., synonyms, technical terms, error codes) to ensure no existing rule is missed (e.g., search 'unique', then 'duplicate', then 'key'). Do NOT rely on a single search.
2.  **Review RLM Cache**: 
    - Run `cli.py bundle --target [ID]` to see if rules were already summarized in the RLM cache.
    - Check for descriptions matching your logic.
3.  **Search RAG Database**: 
    ```bash
    python tools/cli.py query "keyword context"
    ```
    - This searches the vector database for semantically similar rules or documentation.

(Standard Knowledge Retrieval applies: RLM, Vector DB search).

## 2. The Definition
A **Business Rule** is a logic statement that defines or constrains some aspect of the business. It is intended to assert business structure or to control or influence the behavior of the business.

**Examples:**
*   **Valid:** "An accused person under 18 must be processed as a Young Offender."
*   **Invalid:** "The textbox background turns red on error." (This is UI logic).

## 3. Hybrid Discovery Strategy

### Discovery Techniques
- **XML Mining**: Use `xml_miner.py` to find declarative properties (`Required`, `FormatMask`).
- **Trigger Analysis**: Use `search_plsql.py` to search `WHEN-VALIDATE-ITEM`, `PRE-INSERT`, `PRE-UPDATE` for PL/SQL logic.
- **Reachability**: Ensure the code is not "Dead" (Reachability > 0.5).

### Classification
| Type | ID Prefix | Description | Example |
|---|---|---|---|
| **Business Rule** | BR | Atomic logic, validation, calculation. | "Date must be in future", "Role X cannot see Y". |
| **Workflow** | BW | High-level process, state transitions. | "Submission Lifecycle", "Intake Process". |
| | | | |
| **Note**: IDs must be generated sequentially using the tool. Never guess an ID. |
| **Mandatory Protocol (ZERO TOLERANCE)**: |
| 1. **Search**: `python tools/cli.py rules search "term"` to find existing. |
| 2. **Register**: `python tools/cli.py rules register ...` to get the next ID. |
| 3. **Verify**: Ensure the file was created with the tool-assigned ID. |
| **PROHIBITED**: Never manually create a file (e.g., `write_to_file "BR-0099..."`). This bypasses the registry and causes duplicates.

## 4. Documentation Structure

### 4.1 File Location
All business rules must be stored in:
`legacy-system/business-rules/BR-NNNN-short-title.md`

### 4.2 Naming Convention
*   **Prefix:** `BR-`
*   **Sequence (NNNN):** 4-digit zero-padded number (e.g., 0001, 0015).
*   **Title:** Kebab-case, lowercase description.

## 5. Extraction Process
1.  **Analyze**: Use `Form_Complete_Analysis_Prompt.md` and `tools/cli.py bundle`.
2.  **Filter**: Separate Business Logic from UI Logic.
3.  **Cross-Reference**: Check for existing BRs.
4.  **Create/Link**: Create distinct BR document and link from Overview.

### ❌ Common Mistakes (PROHIBITED):
1. **Referencing BR without reading it** - You assumed BR-0010 was "sitting day validation" but it's actually "Auto-Accept Logic" for a different form.
2. **Inventing rule names like "Access Level Validation"** - Rule IDs must be BR-XXXX format from the registry.
3. **Not searching with multiple keywords** - One search is not enough. Search synonyms.
4. **Assuming existing overview BR references are correct** - Previous documentation may have errors. Verify.

### ✅ If No BR Exists for the Logic:

> [!CRITICAL]
> **After searching and finding no existing BR, you MUST assess whether to register new rules.**

If you find validation logic but no existing BR covers it:

#### Step 1: Classify the Logic
| Classification | Criteria | Action |
|----------------|----------|--------|
| **P1 (Critical)** | Security, data integrity, legal compliance | **MUST register** via `cli.py rules register --priority P1` |
| **P2 (Major)** | Core business constraints, workflow controls, external integrations | **SHOULD register** via `cli.py rules register --priority P2` |
| **P3 (Minor)** | UI behavior, field defaults, simple validations | **MAY register** or document as form-level validation |

#### Step 2: Take Action
- **If P1 or P2**: Run `cli.py rules register --source [FORM_ID] --description "..." --priority [P1/P2] --type br`
- **If P3 and simple**: Document as "Form-Level Validation" table only

#### Step 3: Update Overview
After registering, update the overview's Business Rules table to reference the new BR-XXXX.

## 6. Reference Data Sources (CRITICAL)

> [!IMPORTANT]
> Use `legacy-system/reference-data/` to validate all entries.

| File | Purpose | How to Use |
|------|---------|------------|
| **`dependency_map.json`** | Core graph structure | Trace logic across forms |
| **`roles_inventory.json`** | Valid Role Names | Validate roles in access rules |
| **`granular_sql/tables/`** | Database Constraints | Validate data integrity rules against DDL |
| **`pll_inventory.json`** | Shared Logic | Identify if rule is centralized in PLL |

## 7. Tooling Reference

The following tools **MUST** be used during the enrichment process:
*   **Unified Discovery**: `tools/cli.py bundle` - Runs miners & gathering
*   **Logic Density:** `tools/investigate/search/lds_scorer.py` - Prioritize work
*   **Reachability:** `tools/investigate/search/reachability.py` - Filter dead code
*   **Link Enrichment:** `scripts/documentation/enrich_links.py` - Run after updates
*   **Code Search:** `findPLSQLTermAttributeKeyword.py` - Verify logic across multiple files

## 6. Anti-Patterns (DO NOT DO)

> [!CAUTION]
> The following shortcuts are PROHIBITED:

1. **Documenting UI as Business Rules** - "Button X is blue" is NOT a business rule.
2. **Duplicating Rules** - Always check if `BR-NNNN` exists before creating a new one.
3. **Missing Source Traceability** - Every rule must link back to the Form/Trigger where it was found.
4. **Vague Definitions** - A rule must be precise and testable.
5. **Ignoring Shared Logic** - Failing to check if a rule is actually in a PLL (Global) vs Form (Local).
6. **Ignoring Consumers** - Failing to list the Forms/Reports that *consume* or *enforce* the rule (The Impact Radius).

## 7. Quality Checklist

Before marking a rule as complete:

- [ ] Rule ID matches filename
- [ ] Logic separated from UI mechanics
- [ ] Source forms/triggers explicitly linked (Definition)
- [ ] Known Consumers (Affected Forms) listed (Impact)
- [ ] Related Data Elements (Tables/Columns) listed
- [ ] Run enrich_links.py after updates

## 8. Mandatory Post-Analysis Updates

### 8.1 Update Inventories
After creating or modifying a business rule, run:
```bash
python scripts/inventory/business_rules_inventory_manager.py
python scripts/inventory/build_master_collection.py --full
```

### 8.2 Update ai_analysis_tracking.json
Mark the source form as analyzed.

### 8.3 Flag Follow-Up Work in TODO.md
If the rule seems contradictory or obsolete, flag it for human review.

## 9. Continuous Improvement
*   Updates to this policy must be reflected in the [Transformation Process](.agent/ORACLE_FORMS_AI_ENRICHMENT_PROCESS.md).
