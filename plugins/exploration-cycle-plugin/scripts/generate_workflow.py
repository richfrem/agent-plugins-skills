#!/usr/bin/env python3
"""
generate_workflow.py (CLI)
=====================================

Purpose:
    Generate a Mermaid workflow diagram skeleton from an exploration
    capture document. Outputs a structured Markdown file containing a fenced Mermaid
    block and an open-questions section. Intended to be used as the deterministic script
    layer behind the business-workflow-doc skill.

Layer: Infrastructure / Tooling

Usage Examples:
    python3 generate_workflow.py --input captures/brd.md --output workflow.md --type sequenceDiagram

Supported Object Types:
    Exploration captures (.md)

CLI Arguments:
    --input: Input file(s): session brief, BRD draft, etc.
    --output: Output Markdown file path
    --type: Mermaid diagram type (flowchart, stateDiagram, sequenceDiagram)
    --title: Diagram title

Input Files:
    - Session brief or requirements draft (.md)

Output:
    - Structured Mermaid skeleton (.md)

Key Functions:
    load_input(): Concatenates multiple input files
    build_output(): Scaffold construction with diagram injection
    main(): Argument parsing and execution

Script Dependencies:
    argparse
    sys
    os
    datetime
    pathlib

Consumed by:
    exploration-cycle-orchestrator-agent.md
    exploration-workflow/SKILL.md
"""

import argparse
import sys
import os
from datetime import date
from pathlib import Path


DIAGRAM_TEMPLATES = {
    "flowchart": """\
```mermaid
flowchart TD
    A[Start: Trigger Event] --> B{{Validation Gate}}
    B -->|Pass| C[Step 1: Process Action]
    B -->|Fail| D[Error: Notify Stakeholder]
    C --> E[Step 2: Apply Business Rule]
    E --> F{{Approval Required?}}
    F -->|Yes| G[Approval Workflow]
    F -->|No| H[Auto-Proceed]
    G --> I[End: Complete]
    H --> I
```""",
    "stateDiagram": """\
```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: Submit
    Submitted --> UnderReview: Assign Reviewer
    UnderReview --> Approved: Approve
    UnderReview --> Rejected: Reject
    Approved --> Active: Activate
    Rejected --> Draft: Revise
    Active --> [*]: Close
```""",
    "sequenceDiagram": """\
```mermaid
sequenceDiagram
    actor User
    participant System
    participant Approver

    User->>System: Submit Request
    System->>System: Validate Input
    System-->>User: Validation Result
    System->>Approver: Notify Pending Approval
    Approver->>System: Approve / Reject
    System-->>User: Decision Notification
```""",
}


def load_input(paths: list[str]) -> str:
    """Read and concatenate one or more input files."""
    chunks = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"Warning: input file not found: {p}", file=sys.stderr)
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(chunks)


def build_output(title: str, diagram_type: str, sources: "list[str]", content: str) -> str:
    """Build the full Markdown output document."""
    today = date.today().isoformat()
    source_label = ", ".join(sources) if sources else "stdin"
    template = DIAGRAM_TEMPLATES.get(diagram_type, DIAGRAM_TEMPLATES["flowchart"])

    preview_end: int = 800
    content_preview: str = content[:preview_end].strip()
    truncation_note: str = "...[truncated]" if len(content) > preview_end else ""

    return f"""# Business Workflow: {title}
Source: {source_label}
Date: {today}
Diagram Type: {diagram_type}
Status: DRAFT — agent-generated skeleton, human review required

> **Instructions for agent**: Replace the skeleton Mermaid diagram below with an
> accurate flowchart extracted from the input captures. Do NOT add steps that are
> not present in the source material. Mark any ambiguous transitions with
> `[NEEDS HUMAN INPUT]` in the Open Questions section below.

---

## Core Process Flow

{template}

---

## Open Questions

- [NEEDS HUMAN INPUT: Confirm the exact steps and ordering from the session captures]
- [NEEDS HUMAN INPUT: Identify any error/rejection paths not described in captures]
- [NEEDS HUMAN INPUT: Are there parallel paths or concurrent steps in this process?]

---

## Source Context (Summary)

The following input was used to generate this diagram:

```
{content_preview}{truncation_note}
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a Mermaid workflow diagram skeleton from exploration capture documents. "
            "Use as the deterministic script layer behind the business-workflow-doc skill."
        )
    )
    parser.add_argument(
        "--input",
        nargs="+",
        metavar="PATH",
        default=[],
        help="Input file(s): session brief, BRD draft, or problem framing capture. "
             "If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default="exploration/captures/workflow-map.md",
        help="Output Markdown file path (default: exploration/captures/workflow-map.md)",
    )
    parser.add_argument(
        "--type",
        dest="diagram_type",
        choices=["flowchart", "stateDiagram", "sequenceDiagram"],
        default="flowchart",
        help="Mermaid diagram type to scaffold (default: flowchart)",
    )
    parser.add_argument(
        "--title",
        default="Core Business Process",
        help="Diagram title (default: 'Core Business Process')",
    )

    args = parser.parse_args()

    # Load input from files or stdin
    if args.input:
        content = load_input(args.input)
        sources = args.input
    else:
        content = sys.stdin.read()
        sources = ["stdin"]

    if not content.strip():
        print("Error: no input content found. Provide --input files or pipe content via stdin.",
              file=sys.stderr)
        sys.exit(1)

    output_text = build_output(args.title, args.diagram_type, sources, content)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    print(f"Workflow diagram scaffold written to: {output_path}")


if __name__ == "__main__":
    main()
