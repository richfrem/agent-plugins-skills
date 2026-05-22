# Session Memory

This document serves as the active, layered memory log for the current reengineering and modernization session. It prevents context collapse and ensures long-session survivability for executing agents.

---

## 1. Rolling Session Summary
*Brief, chronological log of what has been accomplished during this session, updated continuously.*

- **Initial State:** [Describe state of prototype/codebase at start of session]
- **Milestones Reached:**
  - [x] [Milestone 1]
  - [ ] [Milestone 2]

---

## 2. Invariant Extraction
*Core business invariants, mathematical constraints, and absolute behavior policies extracted from the prototype that MUST be preserved at all costs.*

- **Invariant #1:** [Describe invariant e.g. "Interest rate must never exceed 35% under any credit profile"]
  - **Confidence:** [HIGH | MEDIUM | LOW]
  - **Source Code Location:** `[file path / line number]`
- **Invariant #2:** [Describe invariant]
  - **Confidence:** [HIGH | MEDIUM | LOW]
  - **Source Code Location:** `[file path / line number]`

---

## 3. Resolved Decisions Ledger
*Authoritative record of architectural and business decisions resolved during exploration or reengineering.*

| ID | Decision Made | Rationale | Resolution Date | Approved By |
|----|---------------|-----------|-----------------|-------------|
| DEC-001 | [e.g., Use pure in-memory repository for domain testing] | [e.g., Decouples database latency from domain invariants validation] | [YYYY-MM-DD] | [Human / Agent] |

---

## 4. Unresolved Ambiguity Ledger
*Gaps in understanding, inferred rules requiring human verification, or missing constraints.*

| ID | Ambiguity / Question | Impact | Assumed Rule / Temporary Workaround | Confidence Tag |
|----|----------------------|--------|-------------------------------------|----------------|
| AMB-001 | [e.g., What happens if user session expires mid-calculation?] | [e.g., Potential calculation state loss] | [e.g., Assume transactional auto-save] | [LOW] |

---

## 5. Architectural Evolution Log
*Tracks changes made to packages, module boundaries, layers, and directory layouts.*

- **Evolution #1:**
  - **Action:** [e.g., Isolated calculation engine into `/domain/calculator.ts`]
  - **Trigger:** Purity compliance audit failure due to Express leakage.
  - **Files Impacted:** `[list of files]`
- **Evolution #2:**
  - **Action:** [Describe action]
  - **Trigger:** [Describe trigger]

---

## 6. Confidence Tagging Summary
*Synthesized statistical review of rule interpretations.*

- **High Confidence Rules:** [Number] (Validated by tests / spec)
- **Medium Confidence Rules:** [Number] (Inferred from vibe code, needs test coverage)
- **Low Confidence Rules:** [Number] (Unresolved ambiguities, blocked until human review)
