---
description: Extract validated direct dependencies (Level 1 only) for populating the "Validated...
---

---
description: Extract validated direct dependencies (Level 1 only) for populating the "Validated...
tier: 1
**Command:** `/investigate-direct-dependencies [TargetID]`

**Purpose:** Extract validated direct dependencies (Level 1 only) for populating the "Validated Dependencies" section of Overview documents.

**This is an ATOMIC workflow (Tier 1).**

**Called By:** `/codify-form`, `/codify-library`, `/codify-menu`, `/codify-report`, `/codify-db-*`



## Step 1: Get Upstream Callers (Level 1)

```bash
python scripts/dependencies.py --target [TargetID] --direction upstream --depth 1 --json > temp/[TargetID]_upstream.json
**What this captures:**
- Parent Forms that call this form (`CALL_FORM`, `OPEN_FORM`)
- Menus that launch this form
- Reports that call this form

## Step 2: Get Downstream Artifacts (Level 1)

```bash
python scripts/dependencies.py --target [TargetID] --direction downstream --depth 1 --json > temp/[TargetID]_downstream.json
**What this captures:**
- Child Forms opened by this form
- Reports called by this form
- Libraries attached/used

## Step 3: Get Database Dependencies (Direct)

```bash
python scripts/dependencies.py --target [TargetID] --type database --json > temp/[TargetID]_db_deps.json
**What this captures:**
- Tables directly referenced
- Views directly referenced
- Packages/Procedures called
- Sequences used

## Output

After running this workflow, these files are available for documentation:

| File | Contents |
|:---|:---|
| `temp/[TargetID]_upstream.json` | Parent artifacts that call this one |
| `temp/[TargetID]_downstream.json` | Child artifacts called by this one |
| `temp/[TargetID]_db_deps.json` | Database objects directly used |

## Usage in Parent Workflows

Replace inline dependency capture with:
```markdown
### Step N: Capture Validated Dependencies
/investigate-direct-dependencies [TargetID]
The parent workflow then reads the JSON files and populates the Overview's "Validated Dependencies" section.

// turbo-all