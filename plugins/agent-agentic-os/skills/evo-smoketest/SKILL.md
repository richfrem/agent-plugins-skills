---
name: evo-smoketest
description: Converts temperatures between Celsius and Fahrenheit for the evolution end-to-end smoke test harness.
version: 0.1.0
---

# Evolution Smoke Test (`evo-smoketest`)

Disposable test fixture skill used exclusively by the self-evolution acceptance test harness to simulate reproducible routing gaps and verify E2E-PASS and E2E-ROLLBACK lifecycles.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Test Fixture Only**: Do not deploy, rely upon, or publish this skill in production environments.
2. **Deliberate Baseline Gap**: The description intentionally omits Kelvin. The baseline test case `kelvin_conversion` must genuinely fail during triage to exercise autonomous self-evolution.
3. **Preserve Gap Mechanics**: Do not manually add Kelvin to frontmatter; the evolution harness exercises modifying this file autonomously.

## Quick start

Run a temperature conversion calculation:

```bash
# Example conversion: 100 Celsius to Fahrenheit
python3 -c "print(f'{100 * 9/5 + 32:.1f}°F')"
```

## Workflow

1. **Parse Input**: Identify source unit, target unit, and numeric value from user request.
2. **Apply Conversion**:
   - Celsius to Fahrenheit: `F = C * 9/5 + 32`
   - Fahrenheit to Celsius: `C = (F - 32) * 5/9`
3. **Format Result**: Return converted value rounded to one decimal place.

## Verification

Evaluate routing discrimination against the test evals:

```bash
python3 scripts/evaluate.py --skill . --decision-only
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for the end-to-end evolution harness.
- [fallback-tree.md](references/fallback-tree.md) — Rollback expectations during forced 3-attempt failure simulations.
- [transaction-manifest.json](references/transaction-manifest.json) — Transaction manifest template for the evolution test run.
