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
| CON-002 | Regulatory | [NEEDS HUMAN INPUT] | Gap |

## Assumptions
| ID | Assumption | Risk if Wrong |
|----|------------|---------------|
| ASM-001 | [Extract from captures] | [UNCONFIRMED] |
"""


MODE_TEMPLATES = {
    "brd": BRD_TEMPLATE,
    "rules": RULES_TEMPLATE,
    "constraints": CONSTRAINTS_TEMPLATE,
}


def load_input(paths: list[str]) -> str:
    chunks = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"Warning: input file not found: {p}", file=sys.stderr)
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Business Requirements Document (BRD) generator for the exploration cycle. "
            "Reads exploration captures and scaffolds a structured BRD for agent population."
        )
    )
    parser.add_argument(
        "--input",
        nargs="+",
        metavar="PATH",
        default=[],
        help="Input files: session brief, problem framing, prior BRD draft. "
             "If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--mode",
        choices=["brd", "rules", "constraints"],
        default="brd",
        help="Output mode: 'brd' (full document), 'rules' (rules ledger only), "
             "'constraints' (constraints and assumptions). Default: brd",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default="exploration/captures/brd-draft.md",
        help="Output Markdown file path (default: exploration/captures/brd-draft.md)",
    )

    args = parser.parse_args()

    if args.input:
        content = load_input(args.input)
        sources = ", ".join(args.input)
    else:
        content = sys.stdin.read()
        sources = "stdin"

    if not content.strip():
        print(
            "Error: no input content. Provide --input files or pipe content via stdin.",
            file=sys.stderr,
        )
        sys.exit(1)

    template = MODE_TEMPLATES[args.mode]
    output_text = template.format(sources=sources, mode=args.mode, today=date.today().isoformat())

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    print(f"BRD scaffold ({args.mode}) written to: {output_path}")


if __name__ == "__main__":
    main()
