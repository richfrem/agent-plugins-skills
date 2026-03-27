---
description: Command..
---

---



description: Command:.
inputs: [RoleName]
tier: 2
**Command:**
```bash
python scripts/split_roles.py "[RoleName]"
**Action 2: Scan Artifact for Usage (Deep verification)**
```bash
python scripts/split_roles.py --target [ArtifactID]
**What it does:**
- Returns "Active" or "Legacy" based on `roles_inventory.json`.
- Scans the target file (XML/Source) to see if the role is actually used.
- **Rule**: If "Unknown", do not document without human approval.

**Reference Data:**
- `legacy-system/reference-data/inventories/roles_inventory.json`
- `legacy-system/reference-data/master_object_collection.json` (roles included)

**See Also:**
- `search_collection.py --target [ROLE_NAME]` - Look up role in Master Collection
- `dependencies.py --target [FORM] --deep` - Find all dependencies including security checks
// turbo-all