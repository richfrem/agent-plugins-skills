# {TABLE_NAME} - Table/View Overview

## Object Information
| Property | Value |
|---|---|
| **Name** | `{TABLE_NAME}` |
| **Type** | Table / View |
| **Schema** | {SCHEMA_NAME} |
| **Source File** | `legacy-system/oracle-database/Tables/{filename}.sql` |
| **Last Analyzed** | {DATE} |

## Purpose
{Brief description of what data this table/view stores and its role in the system.}

## Columns
| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| {COLUMN_NAME} | {DATA_TYPE} | Yes/No | {DEFAULT} | {DESCRIPTION} |

## Primary Key
| Constraint | Columns |
|---|---|
| {PK_NAME} | {COLUMNS} |

## Foreign Keys
| Constraint | Column | References |
|---|---|---|
| {FK_NAME} | {COLUMN} | {PARENT_TABLE}.{PARENT_COLUMN} |

## Unique Constraints
| Constraint | Columns |
|---|---|
| {UK_NAME} | {COLUMNS} |

## Check Constraints
| Constraint | Condition | Business Rule |
|---|---|---|
| {CHK_NAME} | {CONDITION} | {BR_REFERENCE} |

## Indexes
| Index | Columns | Unique | Purpose |
|---|---|---|---|
| {INDEX_NAME} | {COLUMNS} | Yes/No | {PURPOSE} |

## View Definition (Views only)
```sql
{VIEW_SQL}
```

## Relationships
### Parent Tables (This table references)
| Table | Via FK | Relationship |
|---|---|---|
| {PARENT_TABLE} | {FK_NAME} | Many-to-One |

### Child Tables (Reference this table)
| Table | Via FK | Relationship |
|---|---|---|
| {CHILD_TABLE} | {FK_NAME} | One-to-Many |

## Used By
| Object | Type | Operations |
|---|---|---|
| {OBJECT_NAME} | Form/Report/Package | SELECT/INSERT/UPDATE/DELETE |

## Data Volume Estimate
{Estimated row count or growth pattern if known.}

## Business Rules Enforced
| Rule ID | Constraint/Trigger | Description |
|---|---|---|
| BR-NNNN | {CONSTRAINT_NAME} | {DESCRIPTION} |

## Notes
{Any additional observations or migration considerations.}
