# Domain Preservation Classification Template

This template defines the standardized schema for the PRESERVE vs. REPLACE classification ledger (`preservation-classification-ledger.md`) generated during Phase 5 (Domain Extraction) operations. All domain extraction agents must record classified elements using this exact structure to ensure reliability and automated diff capabilities across sessions.

---

## 1. Classification Entries

For each business entity, function, or logic block analyzed, append an entry structured as follows:

```markdown
### [CLASSIFICATION-ID] [Element Name]
*   **entity_name:** `element_name` (e.g. `calculateCompoundInterest`)
*   **classification:** `PRESERVE | REPLACE | UNCERTAIN | RECLASSIFIED`
*   **original_classification:** `(If reclassified, record original; else N/A)`
*   **reclassification_reason:** `(If changed, detail why; else N/A)`
*   **reclassified_by:** `human | agent | N/A`
*   **confidence:** `HIGH | MEDIUM | LOW | UNKNOWN`
*   **source_file:** `relative/path/to/prototype/source/file.ts`
*   **line_range:** `L120-L145`
*   **rationale:** `Detailed technical description explaining the business value (if PRESERVE) or the infrastructure/framework coupling (if REPLACE).`
*   **downstream_artifacts_affected:** `[tests/characterization/test-file.js, /domain/entities/file.ts]`
*   **cascade_status:** `PENDING | COMPLETE | N/A`
```

---

## 2. Purity & Preservation Rules

1.  **PRESERVE (Gems):** Applied to core business logic, mathematical equations, domain-specific state calculations, validation rules, and specialized UI flows that represent unique intellectual property. These must be decoupled and moved cleanly to `/domain` or `/shared-pure`.
2.  **REPLACE (Debt):** Applied to database calls, network integrations, Express request/response processing, hardcoded local files, environments, or specific vendor/platform APIs. These must be quarantined in the `/infrastructure` layer as Adapters implementing Ports.
3.  **UNCERTAIN:** Requires immediate SME review. Blocks vertical slice migration until resolved to PRESERVE or REPLACE.
4.  **Reclassification Cascade:** If a previously classified item's classification changes mid-session, all downstream artifacts in `downstream_artifacts_affected` must be flagged for review and updated. The slice cannot be certified while any item has a `cascade_status` of `PENDING`.
