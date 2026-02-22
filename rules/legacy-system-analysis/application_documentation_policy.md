---
trigger: always_on
---

# Application Documentation Policy

> **Effective Date:** 2026-01-17
> **Related Standards:** 
> *   [Application Overview Strategy](.agent/tasks/done/0032-application-overview-strategy.md)
> *   [Application Template](.agent/.agent/templates/outputs/application-overview-template.md)
> *   [Expert Persona](.agent/tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md) - Apply this role when analyzing
> *   [Architecture Diagram](.agent/docs/diagrams/architecture/legacy-oracle-architecture.mmd) - Reference for system structure
> *   **Subtask Prompts:** [Menu Analysis](.agent/tools/ai-resources/prompts/analysis/subtasks/Menu_Analysis_Prompt.md) | [Dependency Analysis](.agent/tools/ai-resources/prompts/analysis/subtasks/Dependency_Analysis_Prompt.md) | [Role Identification](.agent/tools/ai-resources/prompts/analysis/subtasks/Role_Identification_Prompt.md)

## 0. Human Overrides
**Rule File:** [std_human_overrides.md](.agent/rules/legacy-system-analysis/standards/std_human_overrides.md)

## 1. Knowledge Retrieval (MANDATORY - DO THIS FIRST)

> [!IMPORTANT]
> **BEFORE** analyzing code or creating documentation, you MUST search the knowledge base.

### Step 1: Search RLM Cache
Search for existing summaries of the application or related forms:
```bash
# Search RLM cache for relevant terms
grep -i "JCS\|application\|your-search-term" .agent/learning/rlm_summary_cache.json
```

### Step 2: Search Vector DB (Semantic Search)
Run semantic search to find conceptually related documents:
```bash
python plugins/vector-db/scripts/query.py "application overview JCS court services"
```

### Step 3: Review Found Documents
If the RLM/Vector search finds relevant documents, **READ THEM** before proceeding:
- If existing analysis is sufficient, **reference it** instead of duplicating
- If existing analysis is partial, **extend it** rather than creating new files
- Only create new documents when the topic is genuinely novel

### Step 4: Distill New Work
After creating documentation, update the knowledge base:
```bash
python plugins/rlm-factory/scripts/distiller.py --file path/to/new/file.md
```

## 2. Documentation Structure

### 1.1 File Location
All application overviews must be stored in:
`legacy-system/applications/[Acronym]-Application-Overview.md`

### 1.2 Naming Convention
*   **Format:** `[Acronym]-Application-Overview.md` (e.g., `FIS2-Application-Overview.md`).

## 3. Extraction Process (Application-Specific Subtasks)

### Subtask A: Menu Analysis
### Subtask A: Menu Analysis
**Objective:** Document the navigational structure from legacy configuration.

**Checklist:**
- [ ] **Tabular Format**: List `Menu Item`, `Screen Label`, and `Roles`.
- [ ] **Role Linking**: Ensure all listed roles are linked using Smart Linking syntax.

**Formatting:**

*   **Structure**: See "Scope Distinction" below.

### 1.3 Scope Distinction (App Overview vs Main Menu)
*   **Application Overview (`*-Application-Overview.md`)**:
    *   **Purpose**: Master document defining high-level purpose, user roles, key modules, and integration strategy.
    *   **Content**: Business context, comprehensive role lists, key workflows.
*   **Main Menu Form (`*M0000-Overview.md`)**:
    *   **Purpose**: Technical implementation of the menu form itself.
    *   **Content**: `SecureDisableButtons` logic, internal flag management.
    *   **Constraint**: Must explicitly link back to Application Overview. Avoid duplicating module lists.

### Subtask B: Dependency Analysis
**Rule File:** [std_validated_dependencies.md](.agent/rules/legacy-system-analysis/standards/std_validated_dependencies.md)
*   **Query**: `form_relationships.csv`.
*   **Verify**: Trace calls from Main Menu.

### Subtask C: Role Identification
**Rule File:** [std_security_access.md](.agent/rules/legacy-system-analysis/standards/std_security_access.md)
*   **Inventory Check**: Validate against `roles_inventory.json`.
*   **Classification**: Active vs Legacy.

### Subtask D: Content Assembly
1.  **Application Profile:** Code, Name, Users, Entry Point
2.  **Functional Modules:** Group forms by purpose
3.  **Integration Points:** Document cross-application connections
4.  **Security Model:** Summarize access control patterns

## 4. Reference Data Sources (CRITICAL)

> [!IMPORTANT]
> Use `legacy-system/reference-data/` to validate all entries.

| File | Purpose | How to Use |
|------|---------|------------|
| **`dependency_map.json`** | Core graph structure | Look up Form IDs to find connections |
| **`roles_inventory.json`** | Valid Role Names | Validate user roles (Active vs Legacy) |
| **`form_relationships.csv`** | Form Dependencies | Source for Validated Dependencies table |

## 5. Tooling Reference

The following tools **MUST** be used during the enrichment process:
*   **Link Enrichment:** `scripts/documentation/enrich_links.py` - Run after updates
*   **Link Generation:** `scripts/documentation/find_source_links.py` - Locates source files and builds links

## 4. Anti-Patterns (DO NOT DO)

> [!CAUTION]
> The following shortcuts are PROHIBITED:

1. **Stub updating only** - Adding just a NOTE without analyzing the source
2. **Copying existing content without verification**
3. **Missing dependency links** - All forms listed must be linked
4. **Ignoring Legacy Roles** - Deprecated roles MUST be listed in their own section
5. **Incomplete Menus** - Must include ALL menu items, not just top 10

## 5. Quality Checklist

Before marking an application as complete:

- [ ] Validated Main Menu Form structure
- [ ] Confirmed all Menu Items are listed
- [ ] Verified Roles against Inventory
- [ ] Linked all Dependencies
- [ ] Run enrich_links.py after updates

## 6. Mandatory Post-Analysis Updates

## Discovered Candidates
If application analysis reveals business rules or workflows:

```bash
# Add BR candidate (Application-Level Rule)
python3 tools/investigate/search/priority_candidates.py --add-br --form APP_ID --desc "App-level rule" --priority P2

# Add Workflow
python3 tools/investigate/search/priority_candidates.py --add-bw --form APP_ID --desc "End-to-end workflow" --priority P2
```

## Post-Processing (Single File Operations)
Always update the knowledge base after editing:

```bash
# 1. Enrich links
python3 scripts/documentation/enrich_links_v2.py --file path/to/file.md

# 2. Distill to RLM (Summary)
python3 plugins/rlm-factory/scripts/distiller.py --file path/to/file.md

# 3. Ingest to Vector DB
python3 plugins/vector-db/scripts/ingest.py --file path/to/file.md
```

## 7. Continuous Improvement
*   Updates to this policy must be reflected in the [Transformation Process](.agent/ORACLE_FORMS_AI_ENRICHMENT_PROCESS.md).
*   New patterns discovered should be added to the [Template](.agent/.agent/templates/outputs/application-overview-template.md).