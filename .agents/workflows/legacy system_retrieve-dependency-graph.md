---
description: When to use. To understand what calls a given object and what it calls.
---

---



description: When to use: To understand what calls a given object and what it calls.
inputs: [TargetID]
tier: 1
**When to use:** To understand what calls a given object and what it calls.

**What it does:**
- **Downstream (Calls To):** Forms, Tables, Packages, Views that the target calls.
- **Upstream (Called By):** Objects that reference/call the target.
- Uses `dependency_map.json` for cached results.
- With `--deep`: Searches all source files for additional references.

**Command (Quick Lookup):**
```bash
python scripts/dependencies.py --target [TargetID]
**Command (Deep Search):**
```bash
python scripts/dependencies.py --target [TargetID] --deep
**Command (JSON Output):**
```bash
python scripts/dependencies.py --target [TargetID] --json
```
// turbo