# {FUNCTION_NAME} - Function Overview

## Object Information
| Property | Value |
|---|---|
| **Name** | `{FUNCTION_NAME}` |
| **Type** | Function |
| **Schema** | {SCHEMA_NAME} |
| **Package** | {PACKAGE_NAME} (if applicable) |
| **Source File** | `[Function.sql](../../oracle-database/Functions/{filename}.sql)` |
| **Last Analyzed** | {DATE} |

## Purpose
{Brief description of what this function computes or validates.}

## Signature
```sql
{FUNCTION_SIGNATURE}
```

## Return Value
| Type | Description |
|---|---|
| {RETURN_TYPE} | {DESCRIPTION} |

## Parameters
| Parameter | Direction | Type | Description |
|---|---|---|---|
| {PARAM_NAME} | IN/OUT/INOUT | {TYPE} | {DESCRIPTION} |

## Business Logic
{Detailed description of the key logic implemented, including:}
- **Calculations**: {Formulas or derivations}
- **Validation**: {Checks performed}
- **Determinism**: {Is result deterministic? Does it read DB state?}

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
| Rule ID | Description |
|---|---|
| BR-NNNN | {RULE_DESCRIPTION} |

## Notes
{Any additional observations or modernization considerations.}
