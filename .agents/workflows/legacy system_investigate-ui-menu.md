---
description: Discovers and exports menu configuration for a target form.
tier: 2
---
# Menu Discovery Workflow

**Input:** `[FormID]` (e.g., `FORM0000`, `FORM0001`)

## Step 1: Query Legacy Rules
Query the inventory to see what menu items are defined for this form.
```bash
/legacy-system-oracle-forms_investigate-ui-menu [FormID] (Query Mode)
```
## Step 2: Export Configuration
Generate `[App]_[FormID].json` in the sandbox configuration directory.
This command merges global menu definitions with form-specific overrides.
```bash
/legacy-system-oracle-forms_investigate-ui-menu [FormID] (Export Mode)
```
## Step 3: Verify Output
Check that the file was created in `sandbox/ui/public/config/`.
```bash
ls sandbox/ui/public/config/*[FormID]*.json
## Step 4: React Integration
Ensure your component uses the hook:
```typescript
const { menuSections } = useMenuConfig('[FormID]', 'ROLE_NAME');
```
