# {PROCEDURE_NAME} - Procedure/Function Overview

## Object Information
| Property | Value |
|---|---|
| **Name** | `{PROCEDURE_NAME}` |
| **Type** | Function / Procedure / Package |
| **Schema** | {SCHEMA_NAME} |
| **Package** | {PACKAGE_NAME} (if applicable) |
| **Source File** | `legacy-system/oracle-database/Procedures/{filename}.sql` |
| **Last Analyzed** | {DATE} |

## Purpose
{Brief description of what this procedure/function does and when it is called.}

## Validated Dependencies
| Name | Type | Usage |
|---|---|---|
| {DEPENDENCY_NAME} | Table/View/Package | Select/Insert/Call |

## Access & Security
### Applications with Access
| Application | Module | Context |
|---|---|---|
| {APP_CODE} | {FORM/MODULE} | {USAGE_CONTEXT} |

### Role Security
- [ ] Publicly Executable
- [ ] Restricted to Roles: `{ROLES}`

## Signature
```sql
{PROCEDURE_SIGNATURE}
```

## Parameters
| Parameter | Direction | Type | Description |
|---|---|---|---|
| {PARAM_NAME} | IN/OUT/INOUT | {TYPE} | {DESCRIPTION} |

## Return Value (Functions only)
| Type | Description |
|---|---|
| {RETURN_TYPE} | {DESCRIPTION} |

## Business Logic
{Detailed description of the key logic implemented, including:}
- Validation rules
- Calculations
- State transitions
- Error handling

## Database Operations
| Operation | Table/View | Purpose |
|---|---|---|
| SELECT | {TABLE} | {PURPOSE} |
| INSERT | {TABLE} | {PURPOSE} |
| UPDATE | {TABLE} | {PURPOSE} |
| DELETE | {TABLE} | {PURPOSE} |

## Called By
| Caller | Type | Context |
|---|---|---|
| {CALLER_NAME} | Form/Report/Package/Trigger | {CONTEXT} |

## Calls
| Callee | Type |
|---|---|
| {CALLEE_NAME} | Procedure/Function/Package |

## Business Rules Implemented
* **[{BR-ID}] ({TITLE})**: {DESCRIPTION}
* **[{BR-ID}] ({TITLE})**: {DESCRIPTION}

## Error Handling
{Description of error codes raised or exception handling logic.}

## Notes
{Any additional observations or migration considerations.}
