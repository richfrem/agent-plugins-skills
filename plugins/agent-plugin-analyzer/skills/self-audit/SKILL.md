---
user-invocable: true
argument-hint: "[optional: path to plugin]"
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Self-Audit: Analyze the Analyzer

Run the `analyze-plugin` skill against the `agent-plugin-analyzer` itself and the test fixtures. This is a regression smoke test that verifies the analyzer produces consistent, expected results.

## Execution Steps

1. **Run inventory on self (security scanning is on by default):**
   ```bash
   python3 ./inventory_plugin.py --path plugins/agent-plugin-analyzer --format json
   ```

2. **Run scanner against test fixtures:**
   ```bash
   python3 ./inventory_plugin.py --path ./tests/gold-standard-plugin --format json
   python3 ./inventory_plugin.py --path ./tests/flawed-plugin --format json
   ```

3. **Validate deterministic scanner results:**

   **Self-analysis scanner must confirm:**
   - `security_flags` = [] (zero security findings in the analyzer itself)
   - `issues` = [] (zero structural violations)

   **Gold-standard fixture scanner must confirm:**
   - `security_flags` = [] (zero security findings)
   - `issues` = [] (zero structural violations)
   - `warnings` = [] (zero missing components)

   **Flawed fixture scanner must confirm:**
   - `security_flags` count ≥ 4 (network calls + env access; obfuscated credential is LLM-only)
   - `issues` count ≥ 1 (bash script violation)
   - `warnings` count ≥ 2 (missing acceptance criteria + references)
   - See `./README.md` for the full expected findings manifest

   **To run assertions programmatically:**
   ```bash
   python3 ./assert_audit.py --fixture flawed --json-output <path-to-scan-output.json>
   ```

4. **Run the full 6-phase analysis on each fixture:**
   - `tests/gold-standard-plugin/` — should score maturity ≥ L2, zero Critical, at least 2 patterns identified
   - `tests/flawed-plugin/` — LLM must additionally detect: missing README file tree, missing plugin manifest

5. **Validate self-analysis (full 6-phase on the analyzer itself):**
   - Maturity Level ≥ L3
   - Security score ≥ 4/5
   - Structure score ≥ 4/5
   - Pattern catalog governance model present with lifecycle states

6. **Report deviations:**
   ```
   ⚠️ SELF-AUDIT REGRESSION: [dimension] expected [X] got [Y]
   ✅ SELF-AUDIT PASSED: [N] scanner checks passed, [M] fixtures validated, [K] 6-phase checks passed
   ```

## When to Run
- After any modification to the analyzer's own files
- Before creating a bundle for external review
- Before pattern catalog updates (to verify governance compliance)
