# [OLBName] Object Library Overview

## Metadata
| Field | Value |
|-------|-------|
| **Library Name** | [OLBName] |
| **File Path** | `legacy-system/oracle-forms/XML/[OLBName]_olb.xml` |
| **Last Analyzed** | [Date] |
| **Status** | Active / Deprecated |

## Purpose & Scope
[Brief description of the OLB's purpose - what kind of reusable components it provides and which applications use it]

## Design-Time vs. Runtime
> **Note:** OLB files are **design-time** tools. Once forms (.fmb) are compiled to .fmx, the subclassed properties are baked in. The OLB must be on FORMS_PATH during compilation/editing.

---

## SmartClasses Inventory
SmartClasses are reusable item templates that enforce standards across forms.

| SmartClass Name | Type | Category | Description |
|-----------------|------|----------|-------------|
| **SC_REQUIRED_TEXT** | Item | Required Fields | Text item with required validation styling |
| **SC_READONLY_TEXT** | Item | Display Fields | Read-only text item with gray background |
| ... | ... | ... | ... |

### Categories
- **Required Fields**: SmartClasses for mandatory input items
- **Display Fields**: Read-only display items
- **Navigation**: Toolbar and navigation components
- **Alerts**: Standard alert dialogs

---

## Visual Attributes
Predefined color/font theming standards for UI consistency.

| VA Name | Foreground | Background | Font | Purpose |
|---------|------------|------------|------|---------|
| **VA_REQUIRED** | Black | Yellow | - | Required field indicator |
| **VA_READONLY** | Gray | LightGray | - | Read-only field styling |
| ... | ... | ... | ... | ... |

---

## ObjectGroups
Bundled components intended for subclassing into forms.

| ObjectGroup Name | Contents | Forms Using |
|------------------|----------|-------------|
| **OG_STANDARD_TOOLBAR** | Toolbar Block, Buttons | Multiple |
| ... | ... | ... |

---

## Triggers (Template)
Standard event handlers that forms can inherit.

| Trigger Name | Scope | Description |
|--------------|-------|-------------|
| **WHEN-NEW-FORM-INSTANCE** | Form | Standard initialization logic |
| **KEY-EXIT** | Form | Standard exit handling |
| ... | ... | ... |

---

## Consuming Forms (Subclass Usage)
Forms that subclass components from this OLB.

| Form ID | Components Used | Notes |
|---------|-----------------|-------|
| **[FORMID]** | SC_REQUIRED_TEXT, VA_REQUIRED | Main application form |
| ... | ... | ... |

---

## Modernization Notes
**Status:** 🟢 Mapped | 🟡 Partially Mapped | 🔴 Pending

### Design Token Mapping
| OLB Component | Modern Equivalent | BC Gov Token |
|---------------|-------------------|--------------|
| VA_REQUIRED | `--color-warning` | `var(--surface-color-forms-default)` |
| ... | ... | ... |

### Component Library Mapping
| OLB SmartClass | React Component | Notes |
|----------------|-----------------|-------|
| SC_REQUIRED_TEXT | `<Input required />` | Use Zod validation |
| ... | ... | ... |

---

## Technical Implementation
### Source Artifacts
- **XML**: [OLBName_olb.xml] (Link)
- **Markdown**: (if converted)

### Dependencies
- **Used by Forms**: (list)
- **Attached Libraries (PLL)**: (if any)
