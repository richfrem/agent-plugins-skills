---
name: business-requirements-capture
plugin: exploration-cycle-plugin
description: >
  Captures and refines business requirements, including functional requirements,
  non-functional requirements, business rules, constraints, assumptions, and
  success measures. Produces structured BRD-style documents with [CONFIRMED] and
  [UNCONFIRMED] confidence markers. Trigger with "capture requirements",
  "generate a BRD", "document business rules", "list the constraints", or
  "create a requirements document".
allowed-tools: Bash, Read, Write
---

# Business Requirements Capture

Generate structured Business Requirements Documents from exploration session captures.

## Usage

```bash
python ./scripts/execute.py \
  --input <file> [<file2>...] \
  --mode <brd|rules|constraints> \
  --output <output_file.md>
```

**Modes:**
- `brd` *(default)*: Full Business Requirements Document — functional/non-functional requirements, business rules, constraints, assumptions, success measures.
- `rules`: Business rules ledger only — decision logic, policy constraints, workflow conditions.
- `constraints`: Constraints and assumptions register only.

**Flags:**
- `--input PATH [PATH ...]` : Session brief, problem framing, BRD draft, or prior captures
- `--output PATH` : Destination file (default: `exploration/captures/brd-draft.md`)
- `--mode MODE` : Output scope (default: `brd`)

## Interactive Co-Authoring Workflow

When invoked interactively, follow this 3-stage pattern. Do not dump a full document at once.

### Stage 1: Context Gathering
Ask all three questions in a single message before reading or generating anything:

1. **Input:** Resolve input in this priority order — do not scan the filesystem before asking:
   - If the user passed a problem statement or context inline — use that as primary input (mark as `[UNCONFIRMED]` source)
   - If input files were named — read them after this question; note any that are missing
   - If neither exists — halt here and ask for input before proceeding
   *(Check `exploration/` only if no inline input and no files named.)*
2. **Output scope:** Which mode fits your need?
   - `brd` — full Business Requirements Document (functional + non-functional requirements, business rules, constraints, assumptions, success measures)
   - `rules` — business rules ledger only (decision logic, policy constraints, workflow conditions)
   - `constraints` — constraints and assumptions register only
3. **Emphasis:** Any specific area, stakeholder concern, or hard constraint that must be front and centre?

After the user responds: read each input file they identify. Note any that are missing or incomplete.

### Stage 2: Section-by-Section Refinement
Build iteratively — do not present a massive markdown dump.

**[CONFIRMED] / [UNCONFIRMED] decision rule** (apply throughout this stage):
- Mark `[CONFIRMED]` only when: the user explicitly stated it, OR it appears clearly in an input file.
- Mark `[UNCONFIRMED]` when: you inferred it, extrapolated it, or the source is ambiguous.
- When in doubt, use `[UNCONFIRMED]` and surface it for human sign-off.

1. **Brainstorm & Curate:** Based on the input files, present a numbered list of proposed requirements or rules (lightweight — title + one sentence each). Ask: *"Which of these should we keep, cut, or merge? Anything missing?"*
2. **Draft section by section:** Present all approved items as drafts in a **single message** — one 2–4 sentence block per item, [CONFIRMED]/[UNCONFIRMED] marked. Ask: *"Accurate? Flag any item to revise before we move on."* Apply all edits in one pass, then proceed.
3. **Consolidate gaps:** Collect all `[UNCONFIRMED]` items and any `[NEEDS HUMAN INPUT]` markers into a single `## Consolidated Gaps` section at the end.

### Stage 3: Reader Testing (Validation)
Once all sections are drafted:

1. **Select the first reader** using this heuristic — state your choice and one sentence of reasoning:
   - Technical constraints, data flows, system behavior → **engineer or tech lead**
   - Policy, compliance, approval gates → **PM or auditor**
   - Cost, timeline, stakeholder sign-off → **executive sponsor**
   - When multiple apply → pick the reader with the **most to lose from an ambiguity** in this specific document
2. Predict exactly 3 questions that reader would ask after reading this document that it does not yet answer. Make questions specific to this document's content (not generic).
3. Report: *"If [reader type] reads this, they'll ask: [Q1], [Q2], [Q3]. Should we answer these inline or add them to `## Consolidated Gaps`?"*
4. Apply whatever the user decides.

## Anti-Hallucination Rules

- Do NOT invent requirements not present in the source captures.
- Apply [CONFIRMED]/[UNCONFIRMED] markers per the Stage 2 decision rule — do not skip marking.
- Do NOT make architectural decisions — capture only what was said or decided.
- Do NOT proceed without input — inline problem statements are valid input, but a BRD generated with neither files nor inline context is pure hallucination.

<example>
Context: User has completed problem framing and wants a formal BRD.
user: "Generate a BRD from our session captures."
assistant: "I'll run `business-requirements-capture` in `brd` mode to scaffold a formal document from your captures."
</example>

<example>
Context: User wants only the business rules extracted.
user: "Document the business rules we identified."
assistant: "I'll use `business-requirements-capture --mode rules` to extract a business rules ledger."
</example>

<example>
Context: Pre-handoff review.
user: "List all constraints and assumptions before we hand off to engineering."
assistant: "I'll run `business-requirements-capture --mode constraints` to produce a constraints and assumptions register."
</example>
