# Session Memory Partitioned Templates

This document outlines the templates for the 7 dedicated ledgers under the `/session-memory/` directory. These files prevent context collapse and ensure long-session survivability for executing agents.

---

## 1. rolling-summary.md
```markdown
# Session Memory: Rolling Summary
*Brief, chronological log of what has been accomplished during this session, compressed/truncated to max 20 lines at phase changes.*

- **Initial State:** [Describe state of prototype/codebase at start of session]
- **Milestones Reached:**
  - [x] Phase 1: Setup and initial discovery completed.
  - [ ] Phase 2: Behavioral test safety net capture.
  - [ ] Phase 3: Domain model extraction.
  - [ ] Phase 4: Vertical slice migration.
  - [ ] Phase 5: Final verification.
```

---

## 2. domain-invariants.md
```markdown
# Session Memory: Domain Invariants
*Core business invariants, mathematical constraints, and absolute behavior policies extracted from the prototype that MUST be preserved at all costs. These are NEVER compressed or paraphrased.*

- **Invariant #1:** [Describe invariant e.g. "Interest rate must never exceed 35% under any credit profile"]
  - **Confidence:** [HIGH | MEDIUM | LOW]
  - **Source Code Location:** `[file path / line number]`
  - **Validation Assertion:** `[test file and test name]`
```

---

## 3. decision-ledger.md
```markdown
# Session Memory: Decision Ledger
*Append-only record of architectural and business decisions resolved during exploration or reengineering, linking to ADRs.*

| ID | Decision Made | Rationale | Resolution Date | Approved By | ADR Reference |
|----|---------------|-----------|-----------------|-------------|---------------|
| DEC-001 | [e.g. Use pure domain ports] | [e.g. Decouple database dependencies] | [YYYY-MM-DD] | [Human / Agent] | [ADR-001] |
```

---

## 4. ambiguity-ledger.md
```markdown
# Session Memory: Ambiguity Ledger
*Gaps in understanding, inferred rules requiring human verification, or missing constraints. LOW confidence rules block certification.*

| ID | Ambiguity / Question | Impact | Assumed Rule / Temporary Workaround | Confidence Tag | Status |
|----|----------------------|--------|-------------------------------------|----------------|--------|
| AMB-001 | [e.g. Session expiry mid-calculation] | [Potential calculation loss] | [Assume transactional auto-save] | [LOW] | [UNRESOLVED] |
```

---

## 5. certification-ledger.md
```markdown
# Session Memory: Certification Ledger
*Machine-readable booleans and validator statuses for quality gates.*

*   **slice-certified:** false
*   **purity-certified:** false
*   **drift-certified:** false
*   **fixtures-portable:** false
*   **safety-precheck-passed:** false
*   **last-audit-timestamp:** "YYYY-MM-DDTHH:MM:SSZ"
```

---

## 6. artifact-ledger.md
```markdown
# Session Memory: Artifact Ledger
*Active artifact hashes, approvals, and expiry conditions to prevent stale context.*

| Path | SHA-256 Hash | Approval State | Expiry Condition | Last Modified |
|------|--------------|----------------|------------------|---------------|
| `specs/REQS.md` | `[hash]` | [PENDING | APPROVED] | [e.g. On route changes] | [timestamp] |
```

---

## 7. context-budget-tracker.md
```markdown
# Session Memory: Context Budget Tracker
*Token spends and model invocation cost tracking to optimize agent resource utilization.*

| Model | Invocation Type | Input Tokens | Output Tokens | Estimated Cost ($) | Phase / Purpose |
|-------|-----------------|--------------|---------------|--------------------|-----------------|
| `claude-sonnet-4.6` | `completion` | 24000 | 1500 | 0.095 | Step 6 Slice Migration |
| **TOTALS** | | | | **$0.095** | |
```
