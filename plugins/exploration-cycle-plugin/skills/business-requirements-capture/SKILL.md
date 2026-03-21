---
name: business-requirements-capture
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
python3 ${CLAUDE_PLUGIN_ROOT}/skills/business-requirements-capture/scripts/execute.py \
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

When invoked interactively by a user, do not just run the batch command blindly. Follow this 3-stage co-authoring pattern to ensure high quality:

### Stage 1: Context Gathering
Before generating the document, ask the user:
1. Is there any specific scope boundary or critical constraint you want emphasized?
2. Ask any clarifying questions about obvious gaps in the input files.
*(If the user says "just generate it", proceed immediately).*

### Stage 2: Section-by-Section Refinement
Instead of presenting a massive markdown dump, build it iteratively:
1. **Brainstorm & Curate:** Present a numbered list of the *proposed* functional requirements or business rules. Ask the user which to keep, drop, or merge.
2. **Draft:** Run the `execute.py` script to generate the actual markdown based on their curated list.
3. **Iterate:** Ask the user if anything needs Surgical editing (e.g., "Combine rule 3 and 4").

### Stage 3: Reader Testing (Validation)
Once the draft is complete, perform a "Reader Test":
1. Predict 3-5 questions a downstream engineer reading this BRD might ask (e.g., error handling, edge cases, data retention).
2. Report those questions to the user. If the BRD lacks the answers, mark them as `[UNCONFIRMED]` in the `## Consolidated Gaps` section and update the file.

## Anti-Hallucination Rules

- Do NOT invent requirements not present in the source captures.
- Mark inferred items as `[UNCONFIRMED]` and confirmed decisions as `[CONFIRMED]`.
- Consolidate duplicate `[NEEDS HUMAN INPUT]` markers into a single `## Consolidated Gaps` section.
- Do NOT make architectural decisions — capture only.

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
