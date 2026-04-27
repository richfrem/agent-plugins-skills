---
concept: business-requirements-document-brd
source: plugin-code
source_file: exploration-cycle-plugin/scripts/business_requirements_capture_execute.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.073644+00:00
cluster: source
content_hash: c076dbcbe8086ea1
---

# Business Requirements Document (BRD)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/exploration-cycle-plugin/scripts/business_requirements_capture_execute.py -->
#!/usr/bin/env python
"""
Purpose: Business Requirements Document (BRD) generator for the exploration cycle.
Reads exploration capture documents and produces a structured Markdown BRD with
numbered requirements, a business rules ledger, constraints and assumptions, and
an open-questions register. Markers: [CONFIRMED] and [UNCONFIRMED] indicate
human-reviewed vs. agent-inferred content.

Designed to be piped to/from the CLI dispatch pattern:
  cat session-brief.md problem-framing.md | pythonexecute.py --output brd-draft.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path


BRD_TEMPLATE = """\
# Business Requirements Document (BRD)
Source: {sources}
Mode: {mode}
Date: {today}
Status: DRAFT — Requires human review before formalisation

> **Agent Instructions**: Populate each section from the piped input context.
> For any field you cannot confidently extract, use: `[UNCONFIRMED: reason]`
> For confirmed decisions, use: `[CONFIRMED]`
> Consolidate duplicate unknowns into the Consolidated Gaps section only.
> Do NOT invent requirements not present in the source.

---

## 1. Document Purpose & Scope

- **Project / Feature**: [Extract from session brief]
- **Business Goal**: [Extract from problem framing — the WHY]
- **Scope**: [What is in scope vs. explicitly out of scope]
- **Primary Stakeholders**: [User groups identified in session brief]

---

## 2. Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | [Extract requirement 1 from captures] | High | [UNCONFIRMED] |
| FR-002 | [Extract requirement 2] | Medium | [UNCONFIRMED] |
| FR-003 | [NEEDS HUMAN INPUT: inadequate context in source] | — | Gap |

---

## 3. Non-Functional Requirements

| ID | Category | Requirement | Status |
|----|----------|-------------|--------|
| NFR-001 | Performance | [Extract from captures or mark gap] | [UNCONFIRMED] |
| NFR-002 | Security | [Extract from captures or mark gap] | [UNCONFIRMED] |
| NFR-003 | Scalability | [NEEDS HUMAN INPUT: not mentioned in source] | Gap |

---

## 4. Business Rules Ledger

| ID | Rule | Source | Status |
|----|------|--------|--------|
| BR-001 | [Extract decision logic / policy constraint from captures] | Capture | [UNCONFIRMED] |
| BR-002 | [NEEDS HUMAN INPUT: no rule described for this area] | — | Gap |

---

## 5. Constraints

- **Technical**: [Extract from captures]
- **Operational**: [Extract from captures]
- **Timeline / Budget**: [NEEDS HUMAN INPUT: not specified in source]
- **Regulatory / Compliance**: [NEEDS HUMAN INPUT: not mentioned in source]

---

## 6. Assumptions

- [Extract assumptions made in problem framing or BRD discussion]
- [NEEDS HUMAN INPUT: list any assumed conditions that need explicit confirmation]

---

## 7. Consolidated Gaps

List each unresolved decision ONCE here rather than repeating `[NEEDS HUMAN INPUT]` everywhere:

1. [Gap 1: decision or data point that cannot be confirmed from the input]
2. [Gap 2]
3. [Gap 3]

---

## 8. Clarifying Questions (for next pass)

1. [Map to Gap 1]
2. [Map to Gap 2]
3. [Map to Gap 3]

---

## 9. Success Measures

- [Extract success criteria or KPIs from problem framing or session brief]
- [NEEDS HUMAN INPUT: success measures not defined in source]
"""

RULES_TEMPLATE = """\
# Business Rules Ledger
Source: {sources}
Mode: rules-only
Date: {today}
Status: DRAFT

| ID | Category | Rule | Confidence | Notes |
|----|----------|------|------------|-------|
| BR-001 | [Category] | [Rule text from captures] | Low | [UNCONFIRMED] |
| BR-002 | [Category] | [NEEDS HUMAN INPUT] | — | Gap |

## Consolidated Gaps
1. [Unresolved rule or policy area]
"""

CONSTRAINTS_TEMPLATE = """\
# Constraints & Assumptions Register
Source: {sources}
Mode: constraints-only
Date: {today}
Status: DRAFT

## Constraints
| ID | Type | Description | Impact |
|----|------|-------------|--------|
| CON-001 | Technical | [Extract from captures] | [UNCONFIRMED] |
| CON-002 | Regulatory | [NEEDS H

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/business-requirements-capture/scripts/execute.py -->
#!/usr/bin/env python3
"""
Purpose: Business Requirements Document (BRD) generator for the exploration cycle.
Reads exploration capture documents and produces a structured Markdown BRD with
numbered requirements, a business rules ledger, constraints and assumptions, and
an open-questions register. Markers: [CONFIRMED] and [UNCONFIRMED] indicate
human-reviewed vs. agent-inferred content.

Designed to be piped to/from the CLI dispatch pattern:
  cat session-brief.md problem-framing.md | python3 execute.py --output brd-draft.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path


BRD_TEMPLATE = """\
# Business Requirements Document (BRD)
Source: {sources}
Mode: {mode}
Date: {today}
Status: DRAFT — Requires human review bef

*(combined content truncated)*

## See Also

- [[business-requirements-capture]]
- [[business-rule-audit-agent]]
- [[serialize-document-to-json-bytes]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/scripts/business_requirements_capture_execute.py`
- **Indexed:** 2026-04-27T05:21:04.073644+00:00
