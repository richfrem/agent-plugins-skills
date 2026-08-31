---
name: evo-smoketest
description: Converts temperatures between Celsius and Fahrenheit for the evolution end-to-end smoke test harness.
version: 0.1.0
---

# evo-smoketest

A disposable fixture skill used only by the evolution end-to-end acceptance suite. It exists to give
a real self-evolution cycle a controlled, reproducible routing gap to triage, fix (E2E-PASS), or fail
three times (E2E-ROLLBACK). Do not deploy or depend on this skill in production.

## Purpose

Provide deterministic temperature-unit conversions so the router has a concrete capability to score
against `evals/evals.json`.

## When to use

Use this skill when the user asks to convert a temperature between Celsius and Fahrenheit.

## Deliberate baseline gap (do not remove without updating evals)

The description above intentionally names only Celsius and Fahrenheit. `evals/evals.json`'s
`kelvin_conversion` case ("How warm is 300 Kelvin?") shares zero 4+ char keywords with this
description, so the routing evaluator genuinely MISSES it at baseline (not merely for a lower score --
correctness map-debt 2026-08-31 found the original query, "Convert 300 Kelvin to Celsius.", already
contained the word "Celsius" and so passed at baseline for the wrong reason, never exercising this gap
at all).

- E2E-PASS: the evolution cycle closes the gap by broadening the `description` and `When to use`
  section to include Kelvin (K = C + 273.15), which flips the failing eval case to green
  (`evaluate.py --decision-only` exit 0) for the right reason -- because "kelvin" is now a matched
  keyword, not by coincidence.
- E2E-ROLLBACK: an intentionally wrong "fix" that does NOT add Kelvin fails the verifier three
  times, forcing the controller into ROLLBACK.

## Procedure

1. Identify the source unit, target unit, and numeric value in the request.
2. Apply the conversion:
   - Celsius to Fahrenheit: `F = C * 9/5 + 32`
   - Fahrenheit to Celsius: `C = (F - 32) * 5/9`
3. Return the converted value rounded to one decimal place.
