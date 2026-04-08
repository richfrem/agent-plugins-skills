## 0017-enhance-os-eval-runner-skill.md

**Status:** Backlog  
**Priority:** High  
**Effort:** M+ (Requires scoring engine logic and external validation layer)  
**Metric:** Quality Score (V2)

---

## Purpose

Transition `os-eval-runner` from a "Librarian" (findability) to a **"Drill Sergeant"** (operational readiness). This update enforces a "Trust-but-Verify" Triple-Loop architecture that penalizes agent "struggle" and utilizes an external Guardian to prevent metric gaming or silent functional failures.

---

## The V2 Quality Formula

The score is calculated using deterministic, machine-checkable definitions:

$$quality\_score = (A \cdot 0.4) + (H \cdot 0.2) + (C \cdot 0.2) + (F \cdot 0.2)$$

* **A (Routing Accuracy) [40%]**: (Correct Skill Matches / Total Eval Prompts).
* **H (Heuristic Integrity) [20%]**: A binary checklist score for structural compliance (frontmatter, `<example>` tags, description).
* **C (Execution Efficiency) [20%]**: Success rate on Attempt #1 with zero fumbles.
* **F (Friction Reduction) [20%]**: Calculated as $1 - min(1, StruggleEvents / 10)$ to ensure mistakes have heavy impact.

---

## The Honesty Chain (Triple-Loop)

1.  **Innermost Agent (Developer)**: Proposes mutations to `SKILL.md`.
2.  **Middle Agent (Auditor)**: Executes tests, generates `interaction_log.json`, and scans for weighted "Struggle Signals".
3.  **Outer Agent (Guardian/Evolver)**: Validates the Auditor via recursive hash audits and manages **Trusted Sync**.

---

## Tasks

### Phase 1: Dynamic Scanning & Success Verification
* **Success Verification Layer**: Define `success` as `exit_code == 0 AND matches_expected_output_pattern`. Mismatches count as "Hard Fails".
* **Tiered Struggle Scoring**:
    * **Tier 1 (Hard Fail)**: +2 points per `retry`, `error`, or output mismatch.
    * **Tier 2 (Soft Signal)**: +1 point per exploratory command (`ls`, `find`, `cat`, `--help`).
* **Trace Attribution**: Log trace data per-input ID in `results.tsv` (success, A/H/C/F breakdown).

### Phase 2: Recursive Guardian Integrity
* **Expanded Integrity Scope**: Outer Agent must verify SHA256 hashes for the **entire skill directory** (recursive) to catch partial tampering or hidden dependency overrides.
* **Pre-KEEP Gate**: Block the loop if hashes mismatch; log the **Delta Report** (interpretability breakdown of the score change).
* **Trusted Sync**: Implement `--sync-master-hash` for legitimate architectural updates.

### Phase 3: Adversarial Lab Validation
* **The Cheating Test**: Manually modify `eval_runner.py` to auto-pass. Verify the Guardian blocks the commit.
* **The Overfitting Test**: Perturb eval inputs slightly. Verify the skill still passes (robustness) while overfitted "shortcuts" fail.

### Phase 4: Zero-Context Standards
* **Update `SKILL.md` Template**: Require a prescriptive **Zero-Context Operational Guide**:
    1.  **First Action**: Exact entry-point command.
    2.  **Success Signal**: Expected output pattern/code.
    3.  **Recovery**: Known failure modes.

---

## Acceptance Criteria

* **Integrity Verified**: Recursive hash audit passed; no unauthorized logic mutations.
* **Full KEEP Contract**:
    * `quality_score >= baseline` AND `A >= baseline_A`.
    * `H == 1.0` AND `C == 1.0`.
    * `F-score >= 0.9` AND `error_count == 0`.
* **Stage 6 Review**: Every run includes a **Delta Report** explaining *why* the score evolved.

