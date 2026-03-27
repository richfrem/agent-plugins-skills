
# [Form ID] - [Form Title]

## Form Information
| Property | Value |
|---|---|
| **Form ID** | [Form ID] |
| **Title** | [Form Title] |
| **Application** | [APP] ([App Name]) |
| **Type** | [Form Type] (e.g. Maintenance, Inquiry, Modal) |
| **Analysis Status** | Analyzed |

> **Source Documents:**
> - [Link to Functional Spec if available]

**Object ID:** [[Form ID]] [[overview]] (Reference Missing: [Form ID]-Overview.md) [[xml-md]] (Reference Missing: [Form ID lower]-FormModule.md) [[xml]] (Reference Missing: [Form ID lower]_fmb.xml)

## Purpose
[Brief summary of what the form does, who uses it, and its business value.]

## Validated Dependencies

### Upstream Dependencies
> **Who calls this form?** (Parent Callers)

| Calling Object | Type | Method |
| :--- | :--- | :--- |
| **[PARENT_ID] (Reference Missing: PARENT_ID-Overview.md)** | Form/Menu | `CALL_FORM` / Menu Item |

### Downstream Dependencies
> **Who does this form call?** (Child Calls)

| Called Object | Type | Method |
| :--- | :--- | :--- |
| **[CHILD_ID] (Reference Missing: CHILD_ID-Overview.md)** | Form | `OPEN_FORM` |

### Attached Libraries (PLL)
| Library | Purpose | Status |
| :--- | :--- | :--- |
| **[LIBNAME] (Reference Missing: LIBNAME-Library-Overview.md)** | Shared Utils | **Active** |

### Database Objects
| Object | Type | Usage |
| :--- | :--- | :--- |
| **[PKG_NAME] (Reference Missing: PKG_NAME.md)** | Package | Core Business Logic |

## Navigation
- **Menu Item:** `[Menu Path]`
- **Entry Point:** `[Call_Form Procedure Name]`
- **Parameter List:** `[Param List Name]`

## Application(s) with Access
> **Discovery Command:** `plugins/legacy system/inventory-manager/skills/inventory-manager/scripts/generate_applications_inventory.py --target [FormID]`

| Application | Main Menu | Notes |
|-------------|-----------|-------|
| **[APP](../../legacy-system/applications/JAS-Application-Overview.md)** | [FORM0000](../../legacy-system/oracle-forms-overviews/forms/FORM0000-Overview.md) | [Access Description] |

## Security
> [!IMPORTANT]
> Access is enforced at multiple layers: legacy configuration (UI/menu), triggers (workflow), and backend PL/SQL.

### User Roles
#### Active Roles
Roles verified in the current security inventory.

| Application | Allowed Roles |
| :--- | :--- |
| **[APP]** | **[ROLE_NAME]** |

#### Legacy / Deprecated Roles
Roles referenced in legacy documentation or code but not present in the active security inventory.

| Application | Restricted Roles |
| :--- | :--- |
| **[APP]** | `UNKNOWN_ROLE` |

> [!TIP]
> **Analysis Note (Application vs Role Variance):**
> Compare `Application(s) with Access` against `Active Roles`. If an app is reachable but has no explicit roles:
> - **Shared Role:** Access via cross-app role (e.g., `JAS_CEIS_USER` grants JAS users access via JCS).
> - **Legacy/Hidden:** App is deprecated or form is hidden from that app's users.
> - **Menu-Only:** Roles are defined at a parent menu level, not directly on this form.
## Business Rules

*   **[BR-XXXX] ([Title]):** [Description of the rule].
    *   *Technical Implementation:* [Trigger/Procedure] (`[Code Snippet/Variable]`)
*   **[BR-XXXX] ([Title]):** [Description of the rule].
    *   *Technical Implementation:* [Trigger/Procedure] (`[Code Snippet/Variable]`)

## Functionality
1.  **[Feature 1]:** [Description]
2.  **[Feature 2]:** [Description]

### UI Items & Role-Based Visibility
| Element | Condition | Effect |
|---------|-----------|--------|
| [Item Name] | [Logic] | [Effect] |

## Legacy UI Access Table (Key Items)
| Item Name | Type | Roles with Access | Roles with Display Only |
|---|---|---|---|
| **[MENU_ITEM]** | MIP | [Roles] | [Roles] |
| **[BUTTON]** | IP | [Roles] | - |

## Fine-Grained Access Control Rules
| Rule/Condition | Code Location | Description |
|---|---|---|
| **[BR-XXXX]** | [Source] | [Description] |

## Technical Implementation
- **Source Code:** [[xml]] (Reference Missing: [Form ID lower]_fmb.xml) [[xml-md]] (Reference Missing: [Form ID lower]-FormModule.md)
- **Attached Libraries:** [List]

## Source Artifact Traceability (Optional)
> Include links to source analysis artifacts when available.

*   [Form XML/Markdown] (Reference Missing: path)
*   [UI Access Table] (Reference Missing: path)
*   [Parent Callers Summary] (Reference Missing: path)

## Screenshots
![Form Screenshot] (Reference Missing: [ID].png)
