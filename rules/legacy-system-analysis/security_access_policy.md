---
trigger: always_on
---

# Standard: Access & Security Documentation

## 1. Objective
To document who can access the form, what roles they use, and what specific restrictions apply, ensuring alignment with the authoritative Security Inventory.

## 2. Checklist
- [ ] **Identify Active Roles**:
    - Query associated menus mmb for the target form (or its parent menu).
    - Map technical application roles
- [ ] **Verify Against Inventory (CRITICAL)**:
    - You **MUST** verify every role against `legacy-system/reference-data/inventories/roles_inventory.json`.
    - **Use the CLI**: `python plugins/cli.py roles verify [ROLE_NAME]`
    - **Active**: If the CLI returns `✅ ACTIVE`.
    - **Legacy**: If the CLI returns `⚠️ LEGACY`.
- [ ] **Document Roles**:
    - Place Active Roles in the **Active Roles** table (Linked).
    - Place Legacy Roles in the **Legacy / Deprecated Roles** table (Unlinked).
- [ ] **Exhaustive Access Table**:
    - For Application Overviews, create a table of all menu items and their roles.
- [ ] **Code-Level Restrictions**:
    - Check `PRE-FORM` or `WHEN-NEW-FORM-INSTANCE` triggers for `GLOBAL.KEY_ROLE` checks.
    - Document any hardcoded `IF User = 'SCOTT' THEN ...` logic.

## 3. Role Validator Algorithm
1.  **Main Menu Check**: Query  associated mmbs for the Application's Main Menu Form.
2.  **Breadth-First Traversal**: Identify direct descendant forms and query their roles.
3.  **Verification**: For every discovered role, run `cli.py roles verify`.
4.  **Consolidation**: Merge unique roles into the Overview, segregated by status.

## 4. Output Format (Mandatory)
You MUST use this exact structure for the "User Roles" section. Do not list roles as a simple bulleted list.

### User Roles

#### Active Roles
Roles verified in the current security inventory.

| Application | Allowed Roles |
| :--- | :--- |
| **[App Code]** | **[ROLE_NAME] (Reference Missing: role_name.md)** |

#### Legacy / Deprecated Roles
Roles referenced in legacy documentation but **NOT** present in the `roles_inventory.json`.

| Application | Allowed Roles |
| :--- | :--- |
| **[App Code]** | `LEGACY_ROLE` |

> [!CRITICAL]
> **Orphaned Role Rule**: If you cannot find a role in `legacy-system/justin-roles/`, you **MUST** place it in the "Legacy / Deprecated Roles" table. Do not simple omit it.
