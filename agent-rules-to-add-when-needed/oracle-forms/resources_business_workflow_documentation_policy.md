# Business Workflow Documentation Policy

> **Effective Date:** 2026-01-17
> **Related Standards:** 
> *   [Business Workflow Strategy](plugins/legacy system/resources/tasks/done/0031-business-workflow-strategy.md)
> *   [Workflow Template](plugins/legacy system/resources/plugins/legacy system/resources/templates/meta/workflow-definition-template.md)
> *   [Expert Persona](plugins/legacy system/resources/tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md) - Apply this role when analyzing
> *   [Architecture Diagram](plugins/legacy system/resources/docs/diagrams/architecture/legacy-oracle-architecture.mmd) - Reference for system structure
> *   **Subtask Prompts:** [State Transition](plugins/legacy system/resources/tools/ai-resources/prompts/analysis/subtasks/State_Transition_Prompt.md) | [Workflow Tracing](plugins/legacy system/resources/tools/ai-resources/prompts/analysis/subtasks/Workflow_Tracing_Prompt.md)

## CLI Quick Reference
```bash
# Get next available BW number
python tools/business-rule-extraction/plugins/adr-manager/scripts/next_number.py --type bw
# Output: BW-0003

# Create workflow document from template
python tools/codify/documentation/overview_manager.py --id BW-0003-workflow-name --type workflow --create

# Create and sync to RLM + Vector DB
python tools/codify/documentation/overview_manager.py --id BW-0003-workflow-name --type workflow --create --sync

# View all next available numbers
python tools/business-rule-extraction/plugins/adr-manager/scripts/next_number.py --type all
```


## 0. Human Overrides
**Rule File:** [std_human_overrides.md](plugins/legacy system/resources/rules/human_overrides_policy.md)

## 1. Knowledge Retrieval
**Mandatory Sequence:**
1.  **RLM Cache Search**
2.  **Vector DB Search**
3.  **Deep Code Search** (e.g. `CALL_FORM` tracing)

See [std_business_rules.md](plugins/legacy system/resources/rules/business_rule_documentation_policy.md) or Form Policy for CLI commands.

### Step 4: Document Findings
Create or update workflow documentation using the [Workflow Template](plugins/legacy system/resources/plugins/legacy system/resources/templates/meta/workflow-definition-template.md).

### Step 5: Post-Processing
(Standard RLM/Enrichment apply).

## 2. Documentation Structure

### 1.1 File Location
All business workflows must be stored in:
`legacy-system/business-workflows/BW-NNNN-short-title.md`

### 1.2 Naming Convention
*   **Prefix:** `BW-`
*   **ID:** 4-digit sequence (0001, 0002...)
*   **Format:** `BW-NNNN-kebab-cased-title.md`

## 2. Extraction Process

### 2.1 Logic Trace
1.  **Identify Process:** Look for chains of form calls (`CALL_FORM`) or status lifecycle transitions (`BLD` -> `SUB`).
2.  **Extract:** Create a new `BW-NNNN` file using the Template.
3.  **Link:** Reference involved Forms and Rules.

### 2.2 Metadata Requirements
*   **Trigger:** What starts the workflow?
*   **Actors:** Roles involved.
*   **Steps:** Sequential list of actions.
*   **Outcomes:** Success/Failure states.

## 3. Tooling Reference

The following tools **MUST** be used during the enrichment process:
*   **Link Enrichment:** `scripts/documentation/enrich_links.py` - Run after updates
*   **Link Generation:** `scripts/documentation/find_source_links.py` - Locates source files and builds links

## 4. Anti-Patterns (DO NOT DO)

> [!CAUTION]
> The following shortcuts are PROHIBITED:

1. **Stub updating only** - Adding just a NOTE without analyzing the source
2. **Copying existing content without verification**
3. **Missing visual flows** - Workflows MUST have a Mermaid diagram
4. **Generic descriptions** - "Process data" is not acceptable
5. **Ignoring roles** - Must specify WHO performs the action

## 5. Quality Checklist

Before marking a workflow as complete:

- [ ] Reviewed source forms for `CALL_FORM` chains
- [ ] Created Mermaid Sequence Diagram
- [ ] List all Actors/Roles involved
- [ ] Linked referenced Business Rules (`[[BR-NNNN]]`)
- [ ] Run enrich_links.py after updates

## 6. Mandatory Post-Analysis Updates

### 6.1 Update Inventories
After creating or modifying a workflow, run:
```bash
python scripts/inventory/business_workflows_inventory_manager.py
python scripts/inventory/build_master_collection.py --full
```

### 6.2 Update ai_analysis_tracking.json (If applicable)

### 6.3 Flag Follow-Up Work in TODO.md
If complex logic requires deeper investigation or stakeholder validation, add to `TODO.md`.

## 7. Continuous Improvement
*   Updates to this policy must be reflected in the [Transformation Process](plugins/legacy system/resources/ORACLE_FORMS_AI_ENRICHMENT_PROCESS.md).
*   New patterns discovered should be added to the [Template](plugins/legacy system/resources/plugins/legacy system/resources/templates/meta/workflow-definition-template.md).
