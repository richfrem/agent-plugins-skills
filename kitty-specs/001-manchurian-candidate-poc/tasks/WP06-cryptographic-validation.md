# WP06: Cryptographic Validation Script

**Goal**: Implement the standalone orchestrator to prove the vulnerability executes correctly.

## Context
We need empirical proof that the payload executed. We will use a dedicated script to record SHA-256 hashes of the files *before* trigger, *during* infection, and *after* restoration.

## Execution Steps

1. **Write `verify_poc.py`**:
   - Create the script in `plugins/manchurian-candidate-poc/verify_poc.py`.

2. **Pre-Execution Hashes**:
   - Calculate and print the SHA-256 hash of `execute.py` and `SKILL.md`.

3. **Code Infection Target**:
   - Run `execute.py` against `tests/artifacts/poison_code_payload.jpg`.
   - Re-hash `execute.py` and assert it is *different* from the pre-execution hash.

4. **Doc Infection Target**:
   - Run `execute.py` against `tests/artifacts/poison_doc_payload.jpg`.
   - Re-hash `SKILL.md` and assert it is *different* from the pre-execution hash.

5. **Restoration**:
   - Programmatically revert `execute.py` and `SKILL.md` (e.g., via `git checkout` or holding backup strings in memory).
   - Re-hash and assert they match the pre-execution hashes, printing success.
