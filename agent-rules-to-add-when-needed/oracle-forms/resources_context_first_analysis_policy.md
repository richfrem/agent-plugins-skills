# Standard: Context-First Analysis Workflow
`plugins/spec-kitty/docs/diagrams/workflows/context-first-analysis.mmd` (Simplified)
`plugins/spec-kitty/docs/diagrams/workflows/context-first-analysis-detailed.mmd` (Detailed)

## 1. Objective
Ensure every analysis session starts with **Rigorous, Constructed Context**, preventing hallucinations and ensuring all project standards are active.

## 2. The 5-Phase Protocol

### Phase 1: Initialize
**Command:** `/context-bundler_init --target [ID] --type [TYPE]`

Actions performed by CLI:
1. Load `plugins/context-bundler/resources/base-manifests/base-[TYPE]-file-manifest.json`
2. Query RLM Cache for summaries
3. Query `dependency_map.json` for dependencies
4. Auto-add source & dependency files
5. Write `tools/context-bundler/file-manifest.json`
6. Generate `temp/context-bundles/[ID]_context.md`

### Phase 2: Review Context
**Command:** `view_file temp/context-bundles/[ID]_context.md`

Check:
- [ ] Source files (MD/XML) present?
- [ ] Key dependencies listed?
- [ ] RLM summaries included?
- [ ] Template & Policy in bundle?

### Phase 3: Augment (if gaps found)
If context is incomplete:
1. `/context-bundler_add --file [PATH]`
2. Add **only** missing files identified
3. Regenerate: `/context-bundler_bundle`
4. Loop back to Phase 2

**Max iterations:** 3 (then escalate to human)

### Phase 4: Execute Deep Dive
Once context is complete:
1. Execute `[TYPE]_Analysis_Prompt.md` (via specialized analysis workflow)
2. Follow `[TYPE]_documentation_policy.md`
3. Apply all `std_*.md` standards
4. Register BRs: `/legacy-system-business-rules_codify-business-rule`

### Phase 5: Post-Process
1. `/legacy-system-oracle-forms_curate-enrich-links --file [DOC]`
2. `/legacy-system-oracle-forms_curate-audit-log --id [ID]`
3. `/rlm-factory_distill --file [DOC]`
4. `/inventory-manager_curate-inventories`

## 3. Key Principle
> **⛔ NEVER** read `rlm_summary_cache.json` directly.
> **✅ ALWAYS** use CLI commands or context bundles to access intelligence.

---

## 4. ⚠️ CRITICAL: Zero-Tolerance Anti-Patterns

> [!CRITICAL]
> **The following shortcuts are PROHIBITED. Violation breaks the workflow and produces incorrect documentation.**

### ❌ DO NOT:
1. **Skip the bundle/context command** - Running post-processing without first gathering context produces shallow documentation.
2. **Mark forms as "Analyzed" after only running post-processing** - Post-processing is Step 5, not the entire workflow.
3. **Invent BR references without searching first** - ALWAYS run `/legacy-system-business-rules_investigate-business-rule` BEFORE referencing or creating any BR-XXXX.
4. **Reference BR-XXXX IDs without verifying the rule matches** - Read the BR file to confirm the logic matches what you found.
5. **Rush through multiple forms** - Each form requires the full 5-phase process. Quality over quantity.

### ✅ CORRECT Workflow (Every Form):
```bash
1. /context-bundler_init --target [ID]   # Gather context
2. view_file existing-overview           # Check what exists
3. view_file source-markdown             # Deep dive source
4. /legacy-system-business-rules_investigate-business-rule "keyword" # Search
5. Update/enhance overview               # Document findings
6. /legacy-system-oracle-forms_curate-enrich-links # Post-process
7. /legacy-system-oracle-forms_curate-audit-log    # Update tracking
```

### Hallmarks of Rushed/Incorrect Work:
- Overview has no changes but marked as "analyzed"
- BR references point to unrelated rules
- No source code was actually viewed
- Post-processing ran but no content changes

