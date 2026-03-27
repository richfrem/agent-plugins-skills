# {LIBRARY_NAME} - Library Overview

## Library Information
| Property | Value |
|---|---|
| **Library ID** | `{LIBRARY_ID}` |
| **Source File** | `legacy-system/oracle-forms/pll/{filename}.txt` |
| **Type** | PL/SQL Library (PLL) |
| **Classification** | Core / Domain / Utility |
| **Last Analyzed** | {DATE} |

## Purpose
{{Brief description of the library's purpose and what shared functionality it provides.}}

---

## API Specification (Public Contract)

### Packages
| Package | Description |
|---|---|
| `{{PACKAGE_NAME}}` | {{Brief description}} |

### Procedures
| Procedure | Package | Parameters | Description |
|---|---|---|---|
| `{{PROCEDURE_NAME}}` | {{PKG}} | {{PARAMS}} | {{DESCRIPTION}} |

### Functions
| Function | Package | Returns | Description |
|---|---|---|---|
| `{{FUNCTION_NAME}}` | {{PKG}} | {{RETURN_TYPE}} | {{DESCRIPTION}} |

---

## Global State Management
*Variables read or written by this library. Indicates if library is a "State Manager" (sets globals) or "Consumer" (reads only).*

| Variable | Direction | Purpose |
|---|---|---|
| `{{VAR_NAME}}` | Read / Write | {{PURPOSE}} |

---

## Dependencies

### Upstream Dependencies (Who Calls Me?)
*Forms, Reports, and other Libraries that attach or call this library.*

| Caller | Type | Usage |
|---|---|---|
| **`{{FORM_ID}}`** | Form | {{USAGE_DESCRIPTION}} |
| **`{{REPORT_ID}}`** | Report | {{USAGE_DESCRIPTION}} |
| **`{{LIB_ID}}`** | Library | {{USAGE_DESCRIPTION}} |

### Downstream Dependencies (What I Call)
*Database packages, other libraries, or external calls made by this library.*

| Callee | Type | Operations |
|---|---|---|
| **`{{DB_PACKAGE}}`** | DB Package | {{OPERATIONS}} |
| **`{{OTHER_LIB}}`** | Library | {{OPERATIONS}} |

### Database Objects Used
| Object | Type | Operations |
|---|---|---|
| **`{{TABLE_NAME}}`** | Table | SELECT / INSERT / UPDATE / DELETE |
| **`{{VIEW_NAME}}`** | View | SELECT |

---

## Application(s) with Access
*Derived from upstream callers. Use `/retrieve-dependency-graph [LIB_ID] --upstream` to discover.*

| Application | Primary Consumer Forms |
|---|---|
| **RCC** | `RCCE0010`, `RCCE0020` |
| **JCS** | `JCSE0030`, `JCSE0040` |
| **JRS** | `JRSE0010`, `JRSE0020` |
| **JAS** | `JASE0016` |
| **LEA** | `LEAE0070` |

---

## Business Rules Implemented
*List format preferred. Use BR-XXXX IDs from the codified inventory.*

*   **[BR-XXXX] ({{Title}}):** {{Description of the rule implemented in this library}}.
*   **[BR-YYYY] ({{Title}}):** {{Description}}.

---

## Security Considerations
*Role checks, access control logic, or sensitive data handling in this library.*

| Check Type | Location | Description |
|---|---|---|
| Role Check | `{{UNIT_NAME}}` | {{e.g., "Validates `JUS$ADMINISTRATOR_YN`"}} |

---

## Complexity Assessment
| Factor | Rating | Notes |
|---|---|---|
| **Code Volume** | Low / Medium / High | {{e.g., "~500 LOC across 10 units"}} |
| **State Coupling** | Low / Medium / High | {{e.g., "Heavy GLOBAL variable usage"}} |
| **DB Coupling** | Low / Medium / High | {{e.g., "Direct DML on 5 tables"}} |
| **Consumer Count** | Low / Medium / High | {{e.g., "Attached by 30+ forms"}} |

---

## Technical Implementation

### Source Artifacts
| Artifact | Location |
|---|---|
| **PLL Source (TXT)** | [View Source] (Reference Missing: {filename}.txt) |
| **XML-MD** | [View Markdown] (Reference Missing: {filename}_pll.md) |

---

## Notes
{{Any additional observations or migration considerations.}}

> [!TIP]
> **Analysis Note:**
> {{Document any discrepancies, legacy patterns, or modernization recommendations here.}}
