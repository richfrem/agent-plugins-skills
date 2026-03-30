---
trigger: always_on
---

# Oracle Forms Documentation Policy V2

> **Effective Date:** 2026-01-18
> **Related Standards:**
> *   [Process Standard](plugins/legacy system/resources/ORACLE_FORMS_AI_ENRICHMENT_PROCESS.md)
> *   [Overview Template](plugins/legacy system/resources/plugins/legacy system/resources/templates/outputs/form-overview-template.md)
> *   [Expert Persona](plugins/legacy system/resources/tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md)

## 0. Human Overrides: The Single Source of Truth
**Rule File:** [std_human_overrides.md](plugins/legacy system/resources/rules/human_overrides_policy.md)
**Rule File:** [std_context_first_analysis.md](plugins/legacy system/resources/rules/context_first_analysis_policy.md)
> [!CRITICAL]
> **ALWAYS check `legacy-system/human-overrides/` before documenting.**
> Information in `human-overrides` supersedes all code analysis.

## 0.1 Pre-Analysis: Task & Planning
*   **Task Creation**: Create a task file (e.g., `tasks/todo/NNNN-analyze-target.md`) defining the scope and subtasks. See [task_creation.md](plugins/legacy system/resources/rules/task_creation.md).
*   **Review Existing**: Check if an Overview file already exists to avoid overwriting manual enhancements.

## 1. Knowledge Retrieval

> [!CRITICAL]
> **READ RLM SUMMARIES FIRST** before viewing raw source files.
> The RLM cache contains LLM-generated summaries that provide instant context.
> Only dive into source code if gaps exist in the cached summary.

### Step 1: Run Context Initialization (Smart Bundle)
**Primary Tool:** `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [ID] --type form`

> [!CRITICAL]
> **STRICT PROHIBITION:**
> **NEVER** use `cat` on `rlm_summary_cache.json`.
> **ALWAYS** use the CLI command below.

This single command initializes your context:
1.  **Resets Manifest**: Loads the Base Form Manifest.
2.  **Consults Intelligence**: Adds RLM cache and dependencies.
3.  **Generates Bundle**: Creates `temp/context-bundles/[ID]_context.md`.

### Step 2: Review Generated Context
**BEFORE viewing source markdown/XML**, review the generated bundle:
- File: `temp/context-bundles/[ID]_context.md`
- Check: Does it contain the Form interactions? The dependencies?
- Check: `legacy-system/oracle-forms-overviews/forms/[ID]-Overview.md` (if exists)

**Context Validity Loop**:
- If `[ID]_context.md` is missing critical files (e.g., a specific config file), you MUST **Augment** the manifest (`tools/context-bundler/file-manifest.json`) and re-run `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle` manually.
- Only proceed when you have a **Complete Context**.

### Step 3: Deep Source Review (Only If Needed)
Only proceed to view raw source files if:
- RLM cache is empty/missing for this artifact
- Specific technical details are needed (trigger code, exact parameters)
- Business rule verification requires line-level inspection

**Deep Dive Tools** (when RLM is insufficient):
*   **Vector Search**: `plugins/vector-db/scripts/query.py "concept"`
*   **Deep Code Search**: `python tools/investigate/search/search_plsql.py --file [PATH] --term "TERM"`
*   **Reachability**: `reachability.py --target [ID]`

## 2. Documentation Standards (Mandatory Deep Dives)
Conduct specific rigorous analysis for each section of the template, following these standards:

### A. Access & Security
**Rule File:** [std_security_access.md](plugins/legacy system/resources/rules/security_access_policy.md)
*   Validate Active Roles against Inventory.
*   Identify Legacy Roles.
*   Document Code-Level Restrictions.

### B. Validated Dependencies
**Rule File:** [std_validated_dependencies.md](plugins/legacy system/resources/rules/validated_dependencies_policy.md)
*   Distrust CSVs validation; verify via Code (`CALL_FORM`).
*   Distinguish Active vs Conditional vs Inactive.

### C. Business Rules & Workflows
**Rule File:** [std_business_rules.md](plugins/legacy system/resources/rules/business_rule_documentation_policy.md)

### 1. Discovery & Verification (CRITICAL)
Before creating ANY new business rule, follow the **Mandatory 3-Step Protocol**:

**Step 1: Search Existing Rules (CLI)**
```bash
python "plugins/legacy system/legacy-system-database/skills/legacy-system-database/scripts/search_plsql.py" "keyword"
```

**Step 2: Review RLM Cache (CLI Bundle)**
Run `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle --target [ID]` and check the RLM Summary. Does it already describe this rule?

**Step 3: Semantic Search (RAG)**
```bash
python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py query "keyword context"
```

**Outcome:**
- **Match Found**: Use the existing `BR-XXXX` ID.
- **No Match**: Register a new rule via CLI.
  ```bash
  python "plugins/legacy system/inventory-manager/skills/inventory-manager/scripts/business_rules_inventory_manager.py" --source [ID] --description "..." --priority P2
  ```
This creates a new file in `legacy-system/business-rules/BR-XXXX-slug.md`.

> **⚠️ DO NOT** invent IDs like `BR-JCSE0013-001`. Always use the sequential BR-XXXX format from the folder.

### 2. Mine, Classify, and Register Candidates
*   **Mine**: Extract logic from triggers/PLSQL (use XML-MD source).
*   **Classify**: Decide if it's a Business Rule (BR) or Workflow (BW).
*   **Register**: YOU MUST USE `"plugins/legacy system/inventory-manager/skills/inventory-manager/scripts/business_rules_inventory_manager.py"`. Do not manually create files.
    *   Command: `python "plugins/legacy system/inventory-manager/skills/inventory-manager/scripts/business_rules_inventory_manager.py" --source [ID] --description "..."`

### 3. Assign Priorities
| Priority | Criteria | Examples |
|----------|----------|----------|
| **P1 (Critical)** | Security, Data Integrity, Legal Compliance | Role checks, YCJA sealing, audit logging |
| **P2 (Major)** | Core business logic, key validations | Required field checks, status transitions |
| **P3 (Minor)** | UI behavior, default values | Field enablement, date formatting |

**Rule File:** [std_placeholder_creation.md](plugins/legacy system/resources/rules/database_object_documentation_policy.md)
*   When BR/BW discovered, create placeholder file if not exists.
*   Ensures links resolve and inventory stays complete.

### D. Technical Implementation
**Rule File:** [std_technical_implementation.md](plugins/legacy system/resources/rules/technical_implementation_policy.md)
*   Link Source Artifacts (FMB/XML).
*   List Attached Libraries.

### E. Application Menus (App Overviews Only)
**Rule File:** [std_application_menus.md](plugins/legacy system/resources/rules/menu_documentation_policy.md)

### F. Smart Linking
**Rule File:** [std_smart_linking.md](plugins/legacy system/resources/rules/smart_linking_policy.md)
*   Use `enrich_links_v2.py` to enforce syntax.

### H. QA & Template Completion
**Rule File:** [std_qa_template_completion.md](plugins/legacy system/resources/rules/qa_template_completion_policy.md)
*   Must pass the "Template Verification Checklist" before completion.
*   All sections from the template MUST be present (even if "None Detected").

## 3. Tooling Reference

### Environment Requirements
| Tool | Environment | Notes |
|------|-------------|-------|
| `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle` | Windows or WSL | Primary discovery tool |
| `enrich_links_v2.py` | Windows or WSL | Link enrichment |
| `distiller.py` (RLM) | Windows or WSL | Uses Ollama API (lightweight) |
| `ingest.py` (Vector DB) | **WSL Only** | Requires `chromadb`, `torch` |
| `query.py` (Vector DB) | **WSL Only** | Requires `chromadb` |

> **Note:** Vector DB tools must be run from WSL with `.venv` activated:
> ```bash
> source .venv/bin/activate
> python plugins/vector-db/scripts/ingest.py --file [PATH]
> ```

### Tool Commands
*   **BR Inventory Rebuild** (after creating new BRs):
    ```bash
    python scripts/inventory/business_rules_inventory_manager.py
    python scripts/inventory/build_master_collection.py --full
    ```
*   **Enrichment** (after inventory rebuilt):
    ```bash
    python scripts/documentation/enrich_links_v2.py --file [PATH]
    ```
*   **Discovery (Recommended)**: `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle --target [ID]`
*   **RLM Distill**: `plugins/rlm-factory/scripts/distiller.py --file [PATH]`
*   **Vector Ingest**: `plugins/vector-db/scripts/ingest.py --file [PATH]` (WSL only)

## 4. Analysis Tracking
Update `legacy-system/reference-data/ai_analysis_tracking.json` after every Deep Dive.

**Mandatory Command:**
```bash
python scripts/documentation/update_analysis_tracking.py [FORM_ID] --notes "Brief summary of analysis"
```
*   This ensures the "Last Analyzed" timestamp is current.
*   This feeds the `summarize_unanalyzed_forms.py` report invoked by humans.

## 5. Continuous Evolution
If you identify gaps in tools, templates, or prompts during analysis:
1.  **Reflect**: Is this a one-off or a systemic issue?
2.  **Improve**:
    *   **Templates**: Update `plugins/legacy system/resources/templates/` if sections are consistently missing or redundant.
    *   **Prompts**: Refine `tools/ai-resources/prompts/` if the agent (you) consistently misses instructions.
    *   **Policies**: Update `plugins/legacy system/resources/rules/` if the standard is unclear.
    *   **Checklists**: Update `tools/ai-resources/checklists/` if steps are missing.

---

## 6. ⚠️ Quality Gates (MANDATORY)

> [!CRITICAL]
> **A form is NOT "analyzed" until ALL of the following are true.**

### Pre-Completion Checklist:
- [ ] **Context gathered** - `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle --target [ID]` was run
- [ ] **Source code viewed** - At least the Form Markdown was reviewed (not just the overview)
- [ ] **BR verification** - If BRs are referenced, the BR files were read and verified to match
- [ ] **Overview enhanced** - The overview file has substantive changes (not just enriched links)
- [ ] **Post-processing run** - `enrich_links_v2.py`, `update_analysis_tracking.py` executed

### ❌ Analysis is INCOMPLETE if:
- You only ran post-processing scripts
- You marked it "analyzed" without viewing source code
- BR references were copied from existing (incorrect) documentation without verification
- The overview has zero content changes

### One Form at a Time
**Do NOT** batch-process multiple forms in rapid succession. Each form requires:
1. Full context gathering
2. Source code review
3. BR search and verification
4. Documentation updates
5. Post-processing

**Quality over quantity.** A properly analyzed form is worth more than 10 rushed ones.

