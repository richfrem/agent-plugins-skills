# Architecture Decision Record (ADR)

*   **Status**: [Proposed | Approved | Rejected | Deprecated | Superseded]
*   **Deciders**: [Human architect, agents involved]
*   **Date**: [YYYY-MM-DD]
*   **Supersedes**: [ADR-NNN | N/A]
*   **Superseded By**: [ADR-NNN | active | N/A]

---

## 1. Context and Problem Statement

[What is the context? Describe the technical problem or business constraint we are trying to solve. What are we optimizing for?]

---

## 2. Decision Drivers

*   [e.g., Maintain 100% domain purity]
*   [e.g., Avoid vendor lock-in]
*   [e.g., Minimize model tokens / API costs]

---

## 3. Considered Options

*   **Option A:** [Describe option A]
*   **Option B:** [Describe option B]
*   **Option C:** [Describe option C]

---

## 4. Decision Outcome

*   **Selected Option:** [Option selected]
*   **Rationale:** [Why was this option chosen over others? Link to business invariants, complexity benchmarks, or cost savings.]

### 4.1 Positive Consequences (Pros)
*   [e.g., Decoupled persistence enables quick unit testing]
*   [e.g., 0% leakage verified by domain-purity-auditor]

### 4.2 Negative Consequences (Cons)
*   [e.g., Requires boilerplate adapter interfaces]

---

## 5. Architectural Fitness Verification

How will this decision be verified continuously by the system?
- **Purity Check:** [e.g., Static import audit of `/domain`]
- **Behavioral Check:** [e.g., Characterization tests in `/tests/characterization`]
