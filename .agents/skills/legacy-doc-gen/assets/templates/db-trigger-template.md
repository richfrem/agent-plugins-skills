# {TRIGGER_NAME} - Trigger Overview

## Object Information
| Property | Value |
|----------|-------|
| **Object ID** | {TRIGGER_NAME} |
| **Object Type** | Trigger |
| **Schema** | {SCHEMA_NAME} |
| **Target Table** | {TABLE_NAME} |
| **Trigger Type** | {BEFORE/AFTER} {INSERT/UPDATE/DELETE} |
| **Row Level** | FOR EACH ROW |
| **Status** | Active / Disabled |

## Purpose
{Brief description of what this trigger does and why it exists.}

## Triggering Event
| Event | Triggered |
|-------|-----------|
| INSERT | Yes/No |
| UPDATE | Yes/No |
| DELETE | Yes/No |

**Timing:** BEFORE / AFTER

## Trigger Logic
### Summary
{High-level description of the logic flow.}

### Key Operations
1. {Operation 1}
2. {Operation 2}
3. {Operation 3}

### PL/SQL Code Reference
```sql
-- Key logic excerpt
{Abbreviated code snippet}
```

## Business Rules Implemented
| Rule ID | Description | Priority |
|---------|-------------|----------|
| [BR-XXXX] (Reference Missing: BR-XXXX.md) | {Description} | P1/P2/P3 |

## Dependencies
### Packages Called
| Package | Procedure/Function | Purpose |
|---------|-------------------|---------|
| `APPL_AUDIT` | `SetAuditFields` | Set audit columns |
| `{APPLICATION}_AUDIT_TRIGGERS` | `{TABLE}_JN_TRG` | Journal table population |

### Tables Affected
| Table | Operation | Purpose |
|-------|-----------|---------|
| `{TABLE_NAME}_JN` | INSERT | Audit journal |

## Audit Information
*(For audit triggers only)*
- **Audit Type:** Row-level / Statement-level
- **Fields Tracked:** ENT_DTM, ENT_USER_ID, UPD_DTM, UPD_USER_ID
- **Journal Table:** `{TABLE_NAME}_JN`

## Performance Notes
- **Index Impact:** {Notes on index usage}
- **Transaction Scope:** Autonomous / Same transaction

## Modernization Notes
### Modern Equivalent
- **Pattern:** Event Sourcing / Change Data Capture
- **Implementation:** Database triggers → Application-level events
- **Considerations:** Audit logging via Kafka/Event Hub

## Source Artifacts
- [Trigger SQL] (Reference Missing: {TRIGGER_NAME}.sql)
