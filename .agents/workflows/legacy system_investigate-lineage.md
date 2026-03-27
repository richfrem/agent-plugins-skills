---
description: When to use. To determine if a Form is reachable from the application menu and ide...
---

---



description: When to use: To determine if a Form is reachable from the application menu and ide...
inputs: [FormID]
tier: 2
**When to use:** To determine if a Form is reachable from the application menu and identify dead code candidates.

**What it calculates:**
- **Score 1.0:** Direct menu access (entry point).
- **Score 0.9-0.2:** Reachable via call chain (score decreases with depth).
- **Score 0.1:** Unreachable (dead code candidate).

**Output:**
- `score`: Reachability factor (0.0-1.0).
- `status`: Human-readable status.
- `path`: Call chain from menu entry to target.

**Command:**
```bash
/legacy-system-oracle-forms_investigate-lineage [FormID]
```

**Examples:**
```bash
/legacy-system-oracle-forms_investigate-lineage JCSE0086
/legacy-system-oracle-forms_investigate-lineage RCCE0147
```
**Use Cases:**
- Prioritize modernization (high-reachability forms first).
- Identify forms that may be deprecated.
- Validate navigation paths in documentation.

**See Also:**
- `/dependency-analysis_retrieve-dependency-graph [ID]` - Get full dependency graph
- `dependency_map.json` - Pre-computed relationships (36,000+ total)
// turbo