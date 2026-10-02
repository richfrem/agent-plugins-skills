---
name: business-workflow-doc
plugin: exploration-cycle-plugin
description: >
  Generate Mermaid flowcharts documenting business processes, state machines,
  and workflow logic from session captures. Use when you need to map multi-step
  processes, approval flows, user journeys, or decision trees during exploration.
allowed-tools: Bash, Read, Write
---

# Business Workflow Documentation (`business-workflow-doc`)

Generates visual Mermaid flowcharts from exploration session captures and briefs.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Constraints

- **Anti-hallucination**: Never invent process steps or decision branches not described in source captures.
- **Ambiguity marking**: Mark ambiguous sequence orders or unconfirmed branches with `[NEEDS HUMAN INPUT]`.
- **Draft status**: Mark all generated diagrams as `DRAFT` until explicitly confirmed by the human explorer.

## Quick start

```bash
# Generate Mermaid flowchart from session capture
python ./scripts/generate_workflow.py \
  --input <capture_file> \
  --output exploration/captures/workflow.md \
  --type flowchart
```

## Workflow

1. **Input Analysis**: Ingest session notes, BRDs, or user journey captures.
2. **Diagram Type Selection**:
   - `flowchart`: Multi-step processes with decision branches.
   - `stateDiagram`: Object lifecycle and status transitions.
   - `sequenceDiagram`: Actor-to-system interactions.
3. **Mermaid Generation**: Render markdown document containing syntax-checked Mermaid code blocks.
4. **Human Review**: Flag any open decisions in an `## Open Questions` section for explorer validation.

## Verification

```bash
# Verify output file exists and contains valid mermaid fence
test -f exploration/captures/workflow.md && grep -q "```mermaid" exploration/captures/workflow.md
```
