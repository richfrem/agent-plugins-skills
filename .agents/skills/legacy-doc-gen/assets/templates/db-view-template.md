# {VIEW_NAME} - View Overview

## Object Information
| Property | Value |
|---|---|
| **Name** | `{VIEW_NAME}` |
| **Type** | View |
| **Schema** | {SCHEMA_NAME} |
| **Source File** | `legacy-system/oracle-database/Views/{filename}.sql` |
| **Last Analyzed** | {DATE} |

## Purpose
{Brief description of what data this view exposes and its role in the system.}

## View Definition
```sql
{VIEW_SQL}
```

## Columns
| Column | Source | Type | Description |
|---|---|---|---|
| {COLUMN_NAME} | {SOURCE_TABLE.COLUMN} | {DATA_TYPE} | {DESCRIPTION} |

## Base Tables
| Table | Alias | Join Type |
|---|---|---|
| {TABLE_NAME} | {ALIAS} | INNER/LEFT/RIGHT |

## Filter Logic (WHERE Clause)
| Condition | Purpose | Business Rule |
|---|---|---|
| {CONDITION} | {PURPOSE} | BR-XXXX |

## Aggregations (if applicable)
| Column | Function | Group By |
|---|---|---|
| {COLUMN} | SUM/COUNT/AVG | {GROUP_COLUMNS} |

## Dependencies
### Tables Used
| Table | Operations |
|---|---|
| {TABLE_NAME} | SELECT |

### Views Used
| View | Purpose |
|---|---|
| {VIEW_NAME} | {PURPOSE} |

## Used By
| Object | Type | Context |
|---|---|---|
| {OBJECT_NAME} | Form/Report/Package | {CONTEXT} |

## Business Rules Encoded
| Rule ID | Filter/Calculation | Description |
|---|---|---|
| BR-XXXX | WHERE clause/CASE | {Description} |

## Performance Notes
{Any observations about view complexity, materialization recommendations, etc.}

## Modernization Notes
{How to migrate this view - API endpoint, GraphQL resolver, etc.}

## Notes
{Any additional observations.}
