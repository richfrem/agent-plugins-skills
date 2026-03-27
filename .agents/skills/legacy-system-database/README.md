# legacy-system-database

Specialized workflows for codifying and investigating Oracle Database schema objects — Tables, Views, Packages, Procedures, Functions, Triggers, and more.

## Workflows

### Codify
| Command | Purpose |
|---|---|
| `/legacy-system-database_codify-db-package` | Document a PL/SQL Package |
| `/legacy-system-database_codify-db-procedure` | Document a Stored Procedure |
| `/legacy-system-database_codify-db-function` | Document a Database Function |
| `/legacy-system-database_codify-db-trigger` | Document a Database Trigger |
| `/legacy-system-database_codify-db-view` | Document a View |
| `/legacy-system-database_codify-db-table` | Document a Table |
| `/legacy-system-database_codify-db-type` | Document a User-Defined Type |
| `/legacy-system-database_codify-db-sequence` | Document a Sequence |
| `/legacy-system-database_codify-db-constraint` | Document Constraints |
| `/legacy-system-database_codify-db-index` | Document Indexes |

### Investigate
| Command | Purpose |
|---|---|
| `/legacy-system-database_investigate-db-package` | Analyze Package internals and dependencies |
| `/legacy-system-database_investigate-db-procedure` | Analyze Procedure logic |
| `/legacy-system-database_investigate-db-function` | Analyze Function logic |
| `/legacy-system-database_investigate-code-search` | Search PL/SQL codebase for patterns |

## Scripts

| Script | Purpose |
|---|---|
| `db_miner.py` | Extract structured DDL and logic from SQL dump files |
| `split_sql_dump.py` | Split a monolithic SQL dump into individual object files |
| `granulate_sql.py` | Break a SQL file into granular statements |
| `search_plsql.py` | Search PL/SQL source for terms or patterns |
| `extract_triggers.py` | Extract trigger definitions from SQL source |

## References

- `references/diagrams/workflows/db-package-discovery.mmd`
- `references/diagrams/workflows/db-function-discovery.mmd`
- `references/diagrams/workflows/db-procedure-discovery.mmd`
- `references/diagrams/workflows/db-table-discovery.mmd`
- `references/diagrams/workflows/db-trigger-discovery.mmd`
- `references/diagrams/workflows/db-view-discovery.mmd`
- `references/diagrams/workflows/db-constraint-discovery.mmd`
- `references/diagrams/workflows/db-index-discovery.mmd`
- `references/diagrams/workflows/db-sequence-discovery.mmd`
- `references/diagrams/workflows/db-type-discovery.mmd`
